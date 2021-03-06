from flask.ext.security import login_required
from flask import request
from iggybase.web_files.decorators import templated
from iggybase import core
from iggybase import g_helper
from iggybase.web_files.page_template import PageTemplate
from collections import OrderedDict
from .forms import LipidAnalysisForm
from .lipid_analysis import LipidAnalysis
from . import smallmolecule
from config import Config

MODULE_NAME = 'smallmolecule'

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
        'Pass':'{"test_smms":{"status_id":' + str(getattr(test_status_pass,
            'id', None))
                + '},"sample_smms":{"status_id":' + str(getattr(sample_status_pass,'id', None))
                + ',"date_finished":"now"}}'})
    # on fail set test status to fail and sample status to in progress
    # must add fail second to maintain order in dict
    test_status_fail = oac.get_select_list_item('test_smms', 'status_id', 'FAILED')
    sample_status_pending = oac.get_select_list_item('sample_smms', 'status_id', 'IN PROGRESS')
    choose_action['Fail'] = ('{"test_smms":{"status_id":' + str(getattr(test_status_fail, 'id', None))
            + '},"sample_smms":{"status_id":' + str(getattr(sample_status_pending, 'id', None))
            + '}}')
    # TODO: would be better to get any field not just visible ones, cant get
    # test name
    hidden_fields = {'message_fields':'["sample_smms|name"]'}
    context = {'choose_action': choose_action, 'hidden_fields': hidden_fields}
    return core.routes.build_summary('qc', 'choose_action_summary', context)

@smallmolecule.route('/lipid_analysis/', methods=['GET', 'POST'])
@login_required
@templated()
def lipid_analysis(facility_name):
    form_data = request.form
    form = LipidAnalysisForm()
    zip_path = None
    debug = 'debug' in request.args
    if form.validate_on_submit():
        root_path = Config.UPLOAD_FOLDER + '/lipid_analysis/'
        file1 = request.files[form.file1.name]
        file1.save(root_path + 'file1.txt')
        file2 = request.files[form.file2.name]
        file2.save(root_path + 'file2.txt')
        file1_path = root_path + 'file1.txt'
        file2_path = root_path + 'file2.txt'

        la = LipidAnalysis([file1_path, file2_path])
        la.filter_rows(form.data['retention_time_filter'],
                form.data['group_pq_filter'],
                form.data['group_sn_filter'],
                form.data['group_area_filter'],
                form.data['group_height_filter']
        )
        la.subtract_blank(form.data['blank'], form.data['mult_factor'])
        la.remove_columns(form.data['remove_cols'])
        la.normalize(form.data)
        subclass_stats, class_stats = la.calc_class_stats(form.data['class_stats'])
        zip_path = la.write_results()

    context = {'params': {}}
    if debug:
        context['params'] = {'debug': True}
    pt = PageTemplate(MODULE_NAME, 'lipid_analysis', getattr(context, 'page_context', None))
    return pt.page_template_context(form=form, zip_path=zip_path, **context)
