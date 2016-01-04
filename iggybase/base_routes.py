import json
from flask import request, jsonify
from flask.ext import excel
import iggybase.templating as templating
import iggybase.form_generator as form_generator
import iggybase.mod_auth.organization_access_control as oac
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
    return templating.page_template('summary',
            module_name = module_name,
            table_name = table_name,
            table_query = table_queries.get_first())

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
    table_queries = tqc.TableQueryCollection(module_name, page_form, table_name)
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


def data_entry(module_name, table_name, row_name):
    fg = form_generator.FormGenerator('mod_' + module_name, table_name)
    form = fg.default_single_entry_form(row_name)

    if form.validate_on_submit():
        organization_access_control = oac.OrganizationAccessControl('mod_' + module_name)
        organization_access_control.save_form(form)

    return templating.page_template('single_data_entry',
            module_name=module_name, form=form)


def multiple_data_entry(module_name, table_name):
    row_names =  json.loads(request.args.get('row_names'))
    fg = form_generator.FormGenerator('mod_' + module_name, table_name)
    form = fg.default_multiple_entry_form(row_names)

    if form.validate_on_submit():
        organization_access_control = oac.OrganizationAccessControl('mod_' + module_name)
        organization_access_control.save_form(form)

    return templating.page_template('single_data_entry',
            module_name=module_name, form=form)
