import json
from flask import request, jsonify, abort
from flask.ext import excel
import iggybase.templating as templating
import iggybase.form_generator as form_generator
import iggybase.mod_auth.organization_access_control as oac
import iggybase.mod_auth.role_access_control as frac
import iggybase.table_query_collection as tqc
import json
import logging


def index():
    return templating.render_template( 'index.html' )

def default():
    return templating.page_template('index.html')

def message(page_temp, page_msg):
    return templating.page_template(page_temp, page_msg=page_msg)

def summary(module_name, table_name):
    page_form = 'summary'
    table_queries = tqc.TableQueryCollection(module_name, page_form, table_name)
    table_queries.get_fields()
    first_table_query = table_queries.get_first()
    # if nothing to display then page not found
    if not first_table_query.table_fields:
        abort(404)
    return templating.page_template('summary',
            module_name = module_name,
            table_name = table_name,
            table_query = first_table_query)

def summary_ajax(module_name, table_name):
    page_form = 'summary'
    table_queries = tqc.TableQueryCollection(module_name, page_form, table_name)
    table_queries.get_fields()
    table_queries.get_results()
    table_queries.format_results()
    table_query = table_queries.get_first()
    json_rows = table_query.get_json()
    return jsonify({'data':json_rows})

def summary_download(module_name, table_name):
    page_form = 'summary'
    for_download = True
    table_queries = tqc.TableQueryCollection(module_name, page_form, table_name)
    table_queries.get_fields()
    table_queries.get_results()
    table_queries.format_results(for_download)
    table_rows = table_queries.get_first().table_rows
    csv = excel.make_response_from_records(table_rows, 'csv')
    return csv

def action_summary(module_name, table_name = None):
    page_form = 'summary'
    table_queries = tqc.TableQueryCollection(module_name, page_form, table_name)
    table_queries.get_fields()
    hidden_fields = {'table': table_name}
    return templating.page_template('action_summary',
            module_name = module_name,
            table_name = table_name,
            table_query = table_queries.get_first(), hidden_fields = hidden_fields)

def action_summary_ajax(module_name, table_name = None):
    page_form = 'summary'
    table_queries = tqc.TableQueryCollection(module_name, page_form, table_name)
    table_queries.get_fields()
    table_queries.get_results()
    table_queries.format_results()
    table_query = table_queries.get_first()
    json_rows = table_query.get_json()
    return jsonify({'data':json_rows})

def detail(module_name, table_name, row_name):
    page_form = 'detail'
    criteria = {(table_name, 'name'): row_name}
    table_queries = tqc.TableQueryCollection(module_name, page_form,
            table_name, criteria)
    table_queries.get_fields()
    table_queries.get_results()
    table_queries.format_results()
    hidden_fields = {'table': table_name, 'row_name': row_name}
    return templating.page_template(
        'detail',
        module_name=module_name,
        table_name=table_name,
        row_name=row_name,
        table_queries=table_queries,
        hidden_fields=hidden_fields
    )


def saved_data(module_name, table_name, row_names):
    msg = 'Saved: '
    for row_name in row_names:
        msg += ' <a href='+request.url_root+module_name+'/detail/'+table_name+'/'+row_name+'>'+row_name+'</a>,'

    msg = msg[:-1]
    return templating.page_template('save_message', module_name=module_name, table_name=table_name, page_msg=msg)


def data_entry(module_name, table_name, row_name):
    fg = form_generator.FormGenerator('mod_' + module_name, table_name)
    form = fg.default_single_entry_form(row_name)

    if form.validate_on_submit():
        organization_access_control = oac.OrganizationAccessControl()
        row_names = organization_access_control.save_form(form)

        return saved_data(module_name, table_name, row_names)

    return templating.page_template('single_data_entry',
            module_name=module_name, form=form, table_name=table_name)


def multiple_data_entry(module_name, table_name):
    row_names =  json.loads(request.args.get('row_names'))
    fg = form_generator.FormGenerator('mod_' + module_name, table_name)
    form = fg.default_multiple_entry_form(row_names)

    if form.validate_on_submit():
        organization_access_control = oac.OrganizationAccessControl()
        row_names = organization_access_control.save_form(form)

        form = fg.default_multiple_entry_form(row_names)

        return saved_data(module_name, table_name, row_names)

    return templating.page_template('multiple_data_entry', module_name=module_name, form=form, table_name=table_name)

def change_facility_role():
    facility_role_id = request.json['facility_role_id']
    facility_role_access_control = frac.RoleAccessControl()
    success = facility_role_access_control.change_facility_role(facility_role_id)
    return json.dumps({'success':success})

def forbidden():
    return templating.page_template('forbidden')
