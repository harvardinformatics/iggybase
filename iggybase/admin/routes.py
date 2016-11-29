from flask.ext.security import login_required
from . import admin

MODULE_NAME = 'admin'


@admin.route('/roles/', defaults={'page_context': 'base-context'})
@admin.route('/roles/<page_context>')
@login_required
def roles(facility_name, page_context):
    page_form = 'summary'
    context = {'page_context': page_context}
    return build_summary(table_name, page_form, context)

@admin.route('/fieldroles/', defaults={'page_context': 'base-context'})
@admin.route('/fieldroles/<page_context>')
@login_required
def fieldroles(facility_name, page_context):
    page_form = 'summary'
    context = {'page_context': page_context}
    return build_summary(table_name, page_form, context)