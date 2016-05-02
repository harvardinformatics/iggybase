from flask import request, g
import json
from iggybase.core.organization_access_control import OrganizationAccessControl
from iggybase import utilities as util
import iggybase.templating as templating

# Retreives and formats data based on table_query
class WorkItemGroup:
    def __init__ (self, name):
        self.name = name
        self.rac = util.get_role_access_control()
        self.oac = None
        self.WorkItemGroup = None
        self.Step = None
        self.DynamicField = None
        self.Workflow = None
        self.TableObject = None
        self.Route = None
        self.Module = None
        self.buttons = []
        self.saved_rows = {}
        self.get_work_item_group()
        self.work_items = self.rac.work_items(self.WorkItemGroup.id)
        self.workflow_steps = self.rac.workflow_steps(self.Workflow.id)

    def get_work_item_group(self):
        wig = self.rac.work_item_group(self.name)
        if wig:
            self.WorkItemGroup = wig.WorkItemGroup
            self.Step = wig.Step
            self.Workflow = wig.Workflow
            self.TableObject = wig.TableObject
            self.Route = wig.Route
            self.Module = wig.Module
            if wig.Field:
                self.DynamicField = wig.Field

    def get_buttons(self, context_btns = None):
        submit_btn = False
        '''
        TODO have the template use a macro for building button from array
        for btn in context_btns:
            if btn['button_type'] == 'submit':
                submit_btn = True
                break'''
        workflow_button = {
            'button_type': 'submit',
            'button_value': 'Next Step',
            'button_id': 'next_step',
            'button_class': 'btn btn-default',
            'special_props': None,
            'submit_action_url': None
        }
        self.buttons = [templating.button_string(util.DictObject(workflow_button))]

    def set_saved(self, saved_rows):
        self.saved_rows = saved_rows
        print(self.saved_rows)

    def next_step(self):
        # first perform any actions on this step
        actions = self.get_oac().get_step_actions(self.Step.id)
        for action in actions:
            print(action)
            print(action.function)
            if hasattr(self, action.function):
                func = getattr(self, action.function)
                params = {}
                if action.params:
                    params = json.loads(action.params)
                func(**params)
        # increment the step
        next_step = self.Step.order + 1
        success = self.get_oac().update_step(self.WorkItemGroup.id, next_step, self.Workflow.id)
        if not success:
            logging.error('Workflow: next step failed.  Work Item Group: ' +
                    self.WorkItemGroup.name + ' Step: ' + self.Step.name)
        return next_step

    def get_oac(self):
        if not self.oac:
            self.oac = OrganizationAccessControl()
        return self.oac

    def set_dynamic_params(self):
        dynamic_params = {}
        dynamic_params['table_name'] = self.TableObject.name
        dynamic_params['facility_name'] = g.facility
        if self.DynamicField:
            item_tbl_ids = set()
            for item in self.work_items:
                if item.table_object_id == self.DynamicField.table_object_id:
                    name = self.get_oac().get_attr_from_id(item.table_object_id,
                            item.row_id, 'name')
                    if name:
                        dynamic_params['row_name'] = name
                        break
                item_tbl_ids.add(item.table_object_id)
        if not 'row_name' in dynamic_params:
            dynamic_params['row_name'] = 'new'
        return dynamic_params


    '''
    below are workflow action functions
    '''

    def insert_work_item(self, items):
        success = True
        for tbl in items:
            print(tbl)
            if tbl in self.saved_rows:
                tbl_items = self.saved_rows[tbl]
                success = self.get_oac().save_work_items(self.WorkItemGroup.id, tbl_items)
        return success

