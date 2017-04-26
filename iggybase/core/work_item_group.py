from flask import request, g, session, url_for
import json
from collections import OrderedDict
from iggybase import g_helper
from .workflow import Workflow
from .field_collection import FieldCollection
from iggybase.core.constants import WorkflowStatus, Timing, ActionType
from iggybase.core.action import Action
import logging

# Retreives work_item_group info and processes steps and actions
class WorkItemGroup:
    def __init__ (self, work_item_group_name, workflow_name, show_step = None):
        self.name = work_item_group_name  # can be new
        self.rac = g_helper.get_role_access_control()
        self.oac = g_helper.get_org_access_control()
        self.workflow = Workflow(workflow_name)

        # sql alchemy results will populate these capitalized vars
        self.WorkItemGroup = None
        self.work_items = {}
        self.parent_work_item = None
        self.parent_table = None
        self.review_items_link = None
        self.get_work_item_group()

        # which step is the wig currently on
        self.step = self.get_step()
        self.step_num = self.step.Step.order

        # which step is requested for show
        if show_step and show_step != self.step_num:
            self.show_step_num = int(show_step)
            self.step = self.get_step(show_step)
        else:
            self.show_step_num = self.step_num

        # default set on init, actions can change this
        self.next_step = self.show_step_num + 1

        # not all steps are necessary depending on items
        self.active_steps = self.get_active_steps(self.workflow.steps)
        self.buttons = []
        self.saved_rows = {}
        self.dynamic_params = {}

        # do before step actions, if current step
        if self.show_step_num == self.step_num:
            self.do_step_actions(Timing.BEFORE)

        # set the url and dynamic params for current step
        self.endpoint = self.step.Module.name + '.' + self.step.Route.url_path
        self.dynamic_params = self.set_dynamic_params()
        self.url = self.workflow.get_step_url(self.show_step_num, self.name)


    def get_work_item_group(self):
        if self.name != 'new':
            wig = self.oac.work_item_group(self.name)
            if wig:
                self.WorkItemGroup = wig
                work_items = self.oac.work_items(self.WorkItemGroup.id)
                # store work_items by table
                for item in work_items:
                    if not item.WorkItem.parent_id:
                        name = self.oac.get_attr_from_id(item.WorkItem.table_object_id,
                                item.WorkItem.row_id, 'name')
                        self.parent_work_item = name
                        self.parent_table = item.TableObject.name
                    if item.TableObject.name in self.work_items:
                        self.work_items[item.TableObject.name].append(item)
                    else:
                        self.work_items[item.TableObject.name] = [item]

    def get_step(self, step_num = None):
        # which step is the wig currently on
        if self.WorkItemGroup and not step_num:
            step = self.workflow.steps_by_id[self.WorkItemGroup.step_id]
        elif step_num:
            step = self.workflow.steps[step_num]
        else:
            step = self.workflow.steps[1]
        return step

    def get_buttons(self, context_btns = None):
        submit_btn = False
        for btn in context_btns:
            if btn['type'] == 'submit':
                submit_btn = True
                break
        if not submit_btn:
            workflow_button = {
                'type': 'submit',
                'value': 'Next Step',
                'id': 'next_step',
                'name': 'next_step',
                'class': 'btn btn-default',
                'special_props': '',
                'submit_action_url': '',
                'context': ''
            }
            if len(self.active_steps) == self.show_step_num: # last step
                workflow_button['value'] = 'Complete'
                workflow_button['id'] = 'complete'
                workflow_button['name'] = 'complete'
            self.buttons.append(workflow_button)

    def set_saved(self, saved_rows):
        self.saved_rows = saved_rows

    def update_step(self):
        self.do_step_actions() # after step actions
        # next_step can be altered by actions, by default it is incremented by one
        if not self.is_complete() and self.next_step != self.step_num:
            success = self.oac.update_rows(
                    'work_item_group',
                    {'step_id': self.workflow.steps[self.next_step].Step.id, 'before_action_complete': 0},
                    [self.WorkItemGroup.id]
            )
            if not success:
                logging.error('Workflow: next step failed.  Work Item Group: ' +
                        self.name + ' Step: ' + self.step.Step.name)
        if self.is_complete() and self.step_num == self.show_step_num:
            url = self.workflow.get_complete_url(self.name)
        else:
            url = self.workflow.get_step_url(self.next_step, self.name)
        return url

    def do_step_actions(self, time = Timing.AFTER):
        # first perform any actions on this step
        # if new then insert work_item_group
        logging.info('pre do_step_actions')
        action = Action(ActionType.STEP, action_step=self.step.Step.id, action_timing=time)

        action_status = action.execute_action(workflow_id=self.workflow.id, step_id=self.step.Step.id)
        logging.info('post do_step_actions')

        if action_status:
            self.name = action.results['name']
            self.WorkItemGroup = self.oac.get_row('work_item_group', {'id': action.results['id']})
        elif action.results is not None:
            self.dynamic_params.update(action.results)

    def set_dynamic_params(self):
        args = []
        if self.endpoint in session['routes']:
            args = session['routes'][self.endpoint]
        dynamic_params = {'page_context':'workflow,' + self.workflow.name + "_" + str(self.show_step_num)}
        if 'table_name' in args:
            dynamic_params['table_name'] = self.step.TableObject.name
        if 'facility_name' in args:
            dynamic_params['facility_name'] = g.facility
        if 'row_name' in args:
            params = self.get_dynamic_param_from_items()
            if params:
                dynamic_params['row_name'] = params[0]
            else:
                dynamic_params['row_name'] = 'new'
        if 'row_names' in args:
            params = self.get_dynamic_param_from_items()
            if params:
                dynamic_params['row_names'] = json.dumps(params)
        return dynamic_params

    def get_dynamic_param_from_items(self):
        params = []
        if self.step.Field:
            field_table = self.oac.get_table_object({'id':self.step.Field.table_object_id})
            if field_table.name in self.work_items:
                items = self.work_items[field_table.name]
                for item in items:
                    if item.WorkItem.row_id:
                        name = self.oac.get_attr_from_id(item.WorkItem.table_object_id,
                                item.WorkItem.row_id, 'name')
                    else:
                        name = 'new'
                    if name:
                        params.append(name)
        return params

    def get_active_steps(self, all_steps):
        work_steps = OrderedDict()
        for num, step in all_steps.items():
            url = self.workflow.get_step_url(num, self.name)
            classes = []
            if num == self.show_step_num:
                classes.append('current')
            if num > self.step_num:
                classes.append('disabled')
            work_steps[step.Step.name] = {'url': url, 'value':num,
                    'class':' '.join(classes)}
            if self.is_complete() and self.step_num == num:
                break # show no optional steps if complete
        return work_steps

    def is_complete(self):
        if self.WorkItemGroup and self.WorkItemGroup.status == WorkflowStatus.COMPLETE:
            return True
        else:
            return False

    def is_previous_step(self):
        if self.show_step_num < self.step_num:
            return True
        else:
            return False

    def is_future_step(self, step):
        if step > self.step_num:
            return True
        else:
            return False

    def unnecessary_steps(self):
        unnecessary_steps = []
        if self.is_complete() and self.step_num < len(self.workflow.steps):
            for step in self.workflow.steps:
                if step > self.step_num:
                    unnecessary_steps.append(step)
        return unnecessary_steps

    def get_breadcrumbs(self, skip_steps = False):
        breadcrumbs = OrderedDict()
        breadcrumbs['workflow_summary'] = {'url': self.workflow.get_summary_url(),
                'value':'Back to Summary'}
        if not skip_steps:
            breadcrumbs.update(self.active_steps)
        return breadcrumbs

    def set_complete(self):
        self.do_step_actions() # after step actions
        if self.WorkItemGroup.status != WorkflowStatus.COMPLETE:
            self.oac.update_rows('work_item_group', {'status': WorkflowStatus.COMPLETE}, [self.WorkItemGroup.id])

    def set_review_items_link(self):
        if self.parent_work_item and self.parent_table:
            url = url_for('core.data_entry', facility_name = g.rac.facility.name,
                table_name = self.parent_table, row_name =
                self.parent_work_item)
        else:
            url = url_for('core.data_entry', facility_name = g.rac.facility.name,
                table_name = 'work_item_group', row_name =
                self.WorkItemGroup.name)
        self.review_items_link = url

    '''
    below are workflow action functions
    '''

    def insert_work_item(self, items, parent = None):
        success = True
        for tbl in items:
            if tbl in self.saved_rows:
                tbl_items = self.saved_rows[tbl]
                if parent and parent in self.saved_rows:
                    # assume there will only be one parent
                    parent = self.saved_rows[parent][0]
                # insert any new items, keep in mind we could have resaved an
                # existing row or added a row to an already existing table
                # set_work_items will handle that logic
                success = self.oac.set_work_items(self.WorkItemGroup.id, tbl_items, parent, getattr(self.work_items, tbl, None))
        # TODO: handle failure
        self.get_work_item_group()
        return success

    def insert_row(self, tables):
        for table in tables:
            values = self.get_insert_values(table)
            row = self.oac.insert_row(table, values)
            if table in self.saved_rows:
                self.saved_rows[table].append({'table': table, 'name': row.name, 'id': row.id})
            else:
                self.saved_rows[table] = [{'table': table, 'name': row.name, 'id':row.id}]

    def get_defaults(self):
        # gets defaults from work_items
        defaults = {}
        for table, rows in self.work_items.items():
            defaults[table] = rows[0].WorkItem.row_id
        return defaults

    def get_insert_values(self, table, fields = {}):
        # gets defaults from field collection
        fc = FieldCollection(None, table)
        fc.set_fk_fields()
        defaults = self.get_defaults()
        fields.update(defaults)
        fc.set_defaults(fields)
        values = {}
        for field in fc.fields.values():
            if field.default:
                values[field.Field.display_name] = field.default
        return values

    def check_item_field_value(self, item, field, name):
        if item in self.saved_rows:
            work_items = self.saved_rows[item]
            # get the price_item_id for sample
            table = field.replace('_id', '')
            sam = self.oac.get_row(table, {'name': name})
            sam_items = []
            if sam:
                skip_step = True
                # see if any items are samples
                for work_item in work_items:
                    res = self.oac.get_row(item, {'id': work_item['id']})
                    if res and getattr(res, field) == sam.id:
                        sam_items.append(res)
                        skip_step = False

                if skip_step: # if there are no samples
                    self.next_step = self.step_num
                    self.oac.update_rows('work_item_group', {'status': WorkflowStatus.COMPLETE},
                                         [self.WorkItemGroup.id])

