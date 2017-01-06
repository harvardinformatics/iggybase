from flask.ext.security import login_required
from iggybase.web_files.decorators import templated
from iggybase import core
from iggybase.web_files.page_template import PageTemplate
from collections import OrderedDict
from . import smallmolecule

@smallmolecule.route('/')
@templated()
def default():
    pt = PageTemplate('smallmolecule', 'index')
    return pt.page_template_context()


@smallmolecule.route( '/qc/ajax' )
@login_required
def qc_ajax(facility_name):
    return core.routes.build_summary_ajax('qc', {('test_smms', 'status_id'):'pending'})


@smallmolecule.route( '/qc/' )
@login_required
@templated()
def qc(facility_name):
    oac = g_helper.get_org_access_control()
    test_status_pass = oac.get_select_list_item('test_smms', 'status_id', 'PASSED')
    sample_status_pass = oac.get_select_list_item('sample_smms', 'status_id', 'PASSED')
    # on pass update status and date_finished
    choose_action = OrderedDict({
        'Pass':'{"test_smms":{"status_id":' + str(test_status_pass.id)
                + '},"sample_smms":{"status_id":' + str(sample_status_pass.id)
                + ',"date_finished":"now"}}'})
    # on fail set test status to fail and sample status to in progress
    # must add fail second to maintain order in dict
    test_status_fail = oac.get_select_list_item('test_smms', 'status_id', 'FAILED')
    sample_status_pending = oac.get_select_list_item('sample_smms', 'status_id', 'PENDING')
    choose_action['Fail'] = ('{"test_smms":{"status_id":' + str(test_status_fail.id)
            + '},"sample_smms":{"status_id":' + str(sample_status_pending.id)
            + '}}')
    # TODO: would be better to get any field not just visible ones, cant get
    # test name
    hidden_fields = {'message_fields':'["sample_smms|name"]'}
    context = {'choose_action': choose_action, 'hidden_fields': hidden_fields}
    return core.routes.build_summary('qc', 'choose_action_summary', context)
