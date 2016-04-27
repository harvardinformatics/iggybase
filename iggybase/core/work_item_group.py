from flask import request, g
from iggybase.core.organization_access_control import OrganizationAccessControl
from iggybase import utilities as util
import iggybase.templating as templating

# Retreives and formats data based on table_query
class WorkItemGroup:
    def __init__ (self, name):
        self.name = name
        self.rac = util.get_role_access_control()
        self.Step = None
        self.Workflow = None
        self.TableObject = None
        self.Route = None
        self.Module = None
        self.buttons = []
        self.saved_rows = {}
        self.get_work_item_group()

    def get_work_item_group(self):
        wig = self.rac.work_item_group(self.name)
        if wig:
            self.Step = wig.Step
            self.Workflow = wig.Workflow
            self.TableObject = wig.TableObject
            self.Module = wig.Module
            self.Route = wig.Route
            self.WorkItemGroup = wig.WorkItemGroup

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

    def next_step(self):
        next_step = self.Step.order + 1
        oac = OrganizationAccessControl()
        success = oac.update_step(self.Workflow.id, self.WorkItemGroup.name, next_step)
        if not success:
            logging.error('Workflow: next step failed.  Work Item Group: ' +
                    self.WorkItemGroup.name + ' Step: ' + self.Step.name)
        return next_step
