from flask import request
from flask.ext import excel
import iggybase.templating as templating
import iggybase.form_generator as form_generator
import iggybase.mod_auth.organization_access_control as oac
import iggybase.table_query as tq
import logging


def default():
    return templating.page_template('index.html')


def message(page_temp, page_msg):
    return templating.page_template(page_temp, page_msg=page_msg)

def summary(module_name, table_name):
    page_form = 'summary'
    table_query = tq.TableQuery(module_name, table_name, page_form)
    results = table_query.get_results()
    table_rows = table_query.format_data(results)
    return templating.page_template('summary', table_name = table_name, table_rows =
            table_rows)

def summary_download(module_name, table_name):
    page_form = 'summary'
    for_download = True;
    table_query = tq.TableQuery(module_name, table_name, page_form)
    results = table_query.get_results()
    table_rows = table_query.format_data(results, for_download)
    csv = excel.make_response_from_records(table_rows, 'csv')
    return csv

def action_summary(module_name, table_name = None):
    page_form = 'summary'
    table_query = tq.TableQuery(module_name, table_name, page_form)
    results = table_query.get_results()
    table_rows = table_query.format_data(results)
    return templating.page_template('action_summary', table_name = table_name, table_rows =
            table_rows)

def detail(module_name, table_name, row_name):
    page_form = 'detail'
    table_query = tq.TableQuery(module_name, table_name, page_form)
    results = table_query.get_results()
    table_rows = table_query.format_data(results)
    mod = request.path.split('/')[1]
    hidden_fields = {'mod': mod, 'table': table_name, 'row_name': row_name}
    # get any addional_tables
    # TODO: this is broken with the table query class, need to fix
    additional_table_rows = {}
    additional_tables = organization_access_control.get_additional_tables(table_name)
    for table in additional_tables:
        additional_table_name = table[0][0].__tablename__
        additional_table_rows[additional_table_name] = organization_access_control.format_data(table)
    return templating.page_template(
        'detail',
        table_name=table_name,
        row_name=row_name,
        table_rows=table_rows,
        hidden_fields=hidden_fields,
        additional_tables=additional_table_rows
    )


def data_entry(module_name, table_name, row_name):
    fg = form_generator.FormGenerator('mod_' + module_name, table_name)
    form = fg.default_single_entry_form(row_name)

    if form.validate_on_submit():
        organization_access_control = oac.OrganizationAccessControl('mod_' + module_name)
        organization_access_control.save_form(form)

    return templating.page_template('single_data_entry', form=form)


def multiple_data_entry(module_name, table_name, row_names):
    row_names =  request.json[ 'row_names' ]
    fg = form_generator.FormGenerator('mod_' + module_name, table_name)
    form = fg.default_multiple_entry_form(row_names)

    if form.validate_on_submit():
        organization_access_control = oac.OrganizationAccessControl('mod_' + module_name)
        organization_access_control.save_form(form)

    return templating.page_template('single_data_entry', form=form)
