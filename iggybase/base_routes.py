from flask import request
from flask.ext import excel
import iggybase.templating as templating
import iggybase.form_generator as form_generator
import iggybase.mod_auth.organization_access_control as oac
import logging


def default():
    return templating.page_template('index.html')


def message(page_temp, page_msg):
    return templating.page_template(page_temp, page_msg=page_msg)


def summary(module_name, table_name):
    organization_access_control = oac.OrganizationAccessControl('mod_' + module_name)
    results = organization_access_control.get_summary_data(table_name)
    table_rows = organization_access_control.format_data(results)
    return templating.page_template('summary', table_name=table_name, table_rows=
    table_rows)


def summary_download(module_name, table_name):
    # TODO: the page_form for this now doesn't equal summary - fix somehow
    organization_access_control = oac.OrganizationAccessControl('mod_' + module_name)
    for_download = True;
    results = organization_access_control.get_summary_data(table_name)
    table_rows = organization_access_control.format_data(results, for_download)
    csv = excel.make_response_from_records(table_rows, 'csv')
    return csv


def action_summary(module_name, table_name=None):
    # TODO: convert to using fields
    organization_access_control = oac.OrganizationAccessControl('mod_' + module_name)
    results = organization_access_control.get_summary_data(table_name)
    table_rows = organization_access_control.format_data(results)
    return templating.page_template('action_summary', table_name=table_name, table_rows=
    table_rows)


def detail(module_name, table_name, row_name):
    organization_access_control = oac.OrganizationAccessControl('mod_' + module_name)
    results = organization_access_control.get_summary_data(table_name, row_name)
    table_rows = organization_access_control.format_data(results)
    mod = request.path.split('/')[1]
    hidden_fields = {'mod': mod, 'table': table_name, 'row_name': row_name}
    # get any addional_tables
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
