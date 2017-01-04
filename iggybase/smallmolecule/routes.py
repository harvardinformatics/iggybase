from flask.ext.security import login_required
from iggybase.web_files.decorators import templated
from iggybase import g_helper
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
    return core.routes.build_summary_ajax('qc', {('sample_smms', 'status_id'):'pending'})


@smallmolecule.route( '/qc/' )
@login_required
@templated()
def qc(facility_name):
    choose_action = OrderedDict({'Pass':"[{'table':'test', 'field':'status_id', 'value':25}]", 'Fail':"{'status_id':25}"})
    oac = g_helper.get_org_access_control()
    analysis_arr = oac.get_row('analysis', {}, False, True)
    context = {'choose_action': choose_action}
    return core.routes.build_summary('qc', 'choose_action_summary', context)
