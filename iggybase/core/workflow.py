from flask import g, url_for
from iggybase.core.organization_access_control import OrganizationAccessControl
from collections import OrderedDict
from iggybase import utilities as util

class Workflow:
    def __init__ (self, name):
        print('workflow')
        self.name = name
        self.rac = util.get_role_access_control()
        self.oac = None
        self.Workflow = self.rac.workflow(self.name)
        self.id = self.Workflow.id
        self.steps, self.steps_by_id = self.get_steps()


    def get_steps(self):
        res = self.rac.workflow_steps(self.Workflow.id)
        steps = OrderedDict()
        steps_by_id = {}
        for row in res:
            steps[row.Step.order] = row
            steps_by_id[row.Step.id] = row
        return steps, steps_by_id

    def get_step_by_id(self, step_id):
        return self.steps_by_id[step_id]

    def get_complete_url(self, work_item_group_name):
        return self.get_url('workflow_complete', self.name, None, work_item_group_name)

    def get_summary_url(self):
        return self.get_url('workflow', self.name)

    def get_step_url(self, step_num, work_item_group_name = None):
        step = self.steps[step_num]
        return self.get_url('work_item_group', self.name, step_num, work_item_group_name)

    def get_url(self, table, workflow, step = None, work_item_group = None):
        endpoint = g.module + '.' + table
        values = {
                'facility_name': g.facility,
                'workflow_name': workflow
                }
        if step:
            values['step'] = step
        if work_item_group:
            values['work_item_group'] = work_item_group
        return url_for(endpoint, **values)

