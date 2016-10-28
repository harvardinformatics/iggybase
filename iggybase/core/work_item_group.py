from flask import request, g, url_for, session
import json
from collections import OrderedDict
from iggybase import utilities as util
from iggybase import g_helper
from .workflow import Workflow
from .field_collection import FieldCollection
import logging

class status:
    IN_PROGRESS = 2
    COMPLETE = 3
    FINAL = 4

class timing:
    BEFORE = 1
    AFTER = 2

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

        # set the url for current step
        self.endpoint = self.step.Module.name + '.' + self.step.Route.url_path
        self.dynamic_params = self.set_dynamic_params()
        self.url = url_for(self.endpoint, **self.dynamic_params)

        # default set on init, actions can change this
        self.next_step = self.step_num + 1

        # not all steps are necessary depending on items
        self.active_steps = self.get_active_steps(self.workflow.steps)
        self.buttons = []
        self.saved_rows = {}

        # do before step actions, if current step
        if self.show_step_num == self.step_num:
            self.do_step_actions(timing.BEFORE)


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

    def do_step_actions(self, time = timing.AFTER):
        # first perform any actions on this step
        # if new then insert work_item_group
        if self.step_num == 1 and self.name == 'new' and not self.is_complete():
            table = 'work_item_group'
            # TODO: this should be in a generic locaion, maybe the data_instance
            # class
            fields = {'workflow_id': self.workflow.id,
                'status': status.IN_PROGRESS, 'step_id': self.step.Step.id}
            fc = FieldCollection(None, table)
            fc.set_fk_fields()
            fc.set_defaults()
            for field in fc.fields.values():
                if not field.Field.display_name in fields and field.default:
                    fields[field.Field.display_name] = field.default

            row = self.oac.insert_row(table, fields)
            self.name = row.name
            self.get_work_item_group()
        if time != timing.BEFORE or (time == timing.BEFORE and self.WorkItemGroup.before_action_complete == 0):
            actions = self.oac.get_step_actions(self.step.Step.id, time)
            for action in actions:
                if hasattr(self, action.function):
                    func = getattr(self, action.function)
                    params = {}
                    if action.params:
                        params = json.loads(action.params)
                    func(**params)
            if time == timing.BEFORE:
                self.oac.update_rows('work_item_group', {'before_action_complete': 1}, [self.WorkItemGroup.id])

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
            else:
                dynamic_params['row_names'] = json.dumps(['new','new','new'])
        return dynamic_params

    def get_dynamic_param_from_items(self):
        params = []
        if self.step.Field:
            field_table = self.oac.get_table_by_id(self.step.Field.table_object_id)
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
        if self.WorkItemGroup and self.WorkItemGroup.status == status.COMPLETE:
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
        if self.WorkItemGroup.status != status.COMPLETE:
            self.oac.update_rows('work_item_group', {'status': status.COMPLETE}, [self.WorkItemGroup.id])

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
                if tbl in self.work_items: # already saved, update
                    success = self.oac.set_work_items(self.WorkItemGroup.id, tbl_items, parent, self.work_items[tbl])
                else: # insert new
                    success = self.oac.set_work_items(self.WorkItemGroup.id, tbl_items, parent)
        return success

    def insert_row(self, tables, fields = {}):
        for table in tables:
            fc = FieldCollection(None, table)
            fc.set_fk_fields()
            fc.set_defaults()
            for field in fc.fields.values():
                if not field.Field.display_name in fields and field.default:
                    fields[field.Field.display_name] = field.default

            row = self.oac.insert_row(table, fields)
            if table in self.saved_rows:
                self.saved_rows[table].append({'table': table, 'name': row.name})
            else:
                self.saved_rows[table] = [{'table': table, 'name': row.name}]

    def check_item_field_value(self, item, field, name):
        if item in self.saved_rows:
            work_items = self.saved_rows[item]
            # get the price_item_id for sample
            table = field.replace('_id', '')
            sam = self.oac.get_row(table, {'name': name})
            if sam:
                skip_step = True
                # see if any items are samples
                for work_item in work_items:
                    res = self.oac.get_row(item, {'id': work_item['id']})
                    if res and getattr(res, field) == sam.id:
                        skip_step = False

                if skip_step: # if there are no samples
                    self.next_step = self.step_num
                    self.oac.update_rows('work_item_group', {'status': status.COMPLETE}, [self.WorkItemGroup.id])
                else:
                    none_list = []
                    if res.quantity:
                        for i in range(0, res.quantity):
                            new_sample = {'table': 'sample', 'id': None }
                            none_list.append(new_sample)
                        parent_item = {'table': item, 'id': res.id}
                        success = self.oac.set_work_items(self.WorkItemGroup.id, none_list, parent_item)

