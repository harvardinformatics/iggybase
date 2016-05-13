from flask import request, g, url_for, session
import json
from collections import OrderedDict
from iggybase.core.organization_access_control import OrganizationAccessControl
from iggybase import utilities as util
from .workflow import Workflow

# Retreives work_item_group info and processes steps and actions
class WorkItemGroup:
    def __init__ (self, work_item_group_name, workflow_name, step = None):
        self.name = work_item_group_name  # can be new
        self.rac = util.get_role_access_control()
        self.oac = OrganizationAccessControl()
        self.workflow = Workflow(workflow_name)

        # sql alchemy results will populate these capitalized vars
        self.WorkItemGroup = None
        self.work_items = []
        self.get_work_item_group()

        # which step is the wig currently on
        self.step = self.get_step()
        self.step_num = self.step.Step.order

        # set the url for current step
        self.endpoint = self.step.Module.name + '.' + self.step.Route.url_path
        self.dynamic_params = self.set_dynamic_params()
        self.url = url_for(self.endpoint, **self.dynamic_params)

        # which step is requested for show
        if step:
            self.show_step_num = int(step)
        else:
            self.show_step_num = self.step

        # default set on init, actions can change this
        self.next_step = self.step_num + 1

        # not all steps are necessary depending on items
        self.active_steps = self.get_active_steps(self.workflow.steps)
        self.buttons = []
        self.saved_rows = {}

    def get_work_item_group(self):
        if self.name != 'new':
            wig = self.oac.work_item_group(self.name)
            if wig:
                self.WorkItemGroup = wig
                self.work_items = self.oac.work_items(self.WorkItemGroup.id)

    def get_step(self):
        # which step is the wig currently on
        if self.WorkItemGroup:
            step = self.workflow.get_step_by_id(self.WorkItemGroup.step_id)
        else:
            step = self.workflow.steps[1]
        return step

    def get_buttons(self, context_btns = None):
        submit_btn = False
        for btn in context_btns:
            if btn.button_type == 'submit':
                submit_btn = True
                break
        if not submit_btn:
            workflow_button = {
                'button_type': 'submit',
                'button_value': 'Next Step',
                'button_id': 'next_step',
                'button_class': 'btn btn-default',
                'special_props': None,
                'submit_action_url': None
            }
            if len(self.active_steps) == self.show_step_num: # last step
                workflow_button['button_value'] = 'Complete'
                workflow_button['button_id'] = 'complete'

            self.buttons.append(util.DictObject(workflow_button))

    def set_saved(self, saved_rows):
        self.saved_rows = saved_rows

    def update_step(self):
        # next_step can be altered by actions, by default it is incremented by one
        if not self.is_complete() and self.next_step != self.step_num:
            success = self.oac.update_step(self.WorkItemGroup.id, self.next_step, self.workflow.id)
            if not success:
                logging.error('Workflow: next step failed.  Work Item Group: ' +
                        self.name + ' Step: ' + self.step.Step.name)
        if self.is_complete() and self.step_num == self.show_step_num:
            url = self.workflow.get_complete_url(self.name)
        else:
            url = self.workflow.get_step_url(self.next_step, self.name)
        return url

    def do_step_actions(self):
        # first perform any actions on this step
        if not self.is_complete():
            # if new then insert work_item_group
            if self.step_num == 1 and self.name == 'new':
                self.name = self.oac.insert_work_item_group(self.workflow.id,
                        self.step_num, status.IN_PROGRESS)
                self.get_work_item_group()
            actions = self.oac.get_step_actions(self.step.Step.id)
            for action in actions:
                if hasattr(self, action.function):
                    func = getattr(self, action.function)
                    params = {}
                    if action.params:
                        params = json.loads(action.params)
                    func(**params)

    def set_dynamic_params(self):
        args = []
        if self.endpoint in session['routes']:
            args = session['routes'][self.endpoint]
        dynamic_params = {}
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
            dynamic_params['row_names'] = json.dumps(self.get_dynamic_param_from_items())
        return dynamic_params

    def get_dynamic_param_from_items(self):
        params = []
        if self.step.Field:
            for item in self.work_items:
                if item.table_object_id == self.step.Field.table_object_id:
                    name = self.oac.get_attr_from_id(item.table_object_id,
                            item.row_id, 'name')
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
                success = self.oac.insert_work_items(self.WorkItemGroup.id, tbl_items, parent)
        return success

    def check_item_type(self, item, type):
        if item in self.saved_rows:
            work_item = self.saved_rows[item][0]
            res = self.oac.get_row(item, {'id': work_item['id']})
            if res:
                if res.quantity == 2: # TODO: replace with type check
                    self.next_step = self.step_num
                    self.oac.update_work_item_group(self.WorkItemGroup.id, 'status', status.COMPLETE)

class status:
    IN_PROGRESS = 2
    COMPLETE = 3
    FINAL = 4
