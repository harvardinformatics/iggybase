from flask import g, url_for
from collections import OrderedDict
from iggybase import g_helper
import logging

class Workflow:
    def __init__ (self, name):
        self.name = name
        self.display_name = name.replace('_', ' ')
        self.rac = g_helper.get_role_access_control()
        self.Workflow = self.rac.workflow(self.name)
        self.id = self.Workflow.id

        self.steps = OrderedDict()
        self.steps_by_id = {}
        # sets the above
        self.get_steps()

    def get_steps(self):
        res = self.rac.workflow_steps(self.Workflow.id)
        for row in res:
            self.steps[row.Step.order] = row
            self.steps_by_id[row.Step.id] = row

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
            if self.steps[step].Step.params:
                param_arr = self.steps[step].Step.params.split('=')
                if len(param_arr) == 2:
                    values[param_arr[0]] = param_arr[1]
        if work_item_group:
            values['work_item_group'] = work_item_group
        return url_for(endpoint, **values)

