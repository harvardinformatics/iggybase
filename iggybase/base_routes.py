import json
from flask import request, jsonify, abort
import iggybase.templating as templating
import iggybase.form_generator as form_generator
import iggybase.mod_auth.organization_access_control as oac
import iggybase.mod_auth.role_access_control as rac
import iggybase.table_query_collection as tqc
import json
import logging
import urllib


def index():
    return templating.render_template( 'index.html' )

def default():
    return templating.page_template('index.html')

def message(page_temp, page_msg):
    return templating.page_template(page_temp, page_msg=page_msg)

def saved_data(module_name, table_name, row_names):
    msg = 'Saved: '
    error = False
    for row_name in row_names:
        if row_name[0] == 'error':

            msg = 'Error: %s,' % str(row_name[1]).replace('<','').replace('>','')
            error = True
        else:
            table = urllib.parse.quote(row_name[1])
            name = urllib.parse.quote(row_name[0])
            msg += ' <a href='+request.url_root+module_name+'/detail/'+table+'/'+name+'>'+row_name[0]+'</a>,'

    msg = msg[:-1]
    if error:
        return templating.page_template('error_message', module_name=module_name, table_name=table_name, page_msg=msg)
    else:
        return templating.page_template('save_message', module_name=module_name, table_name=table_name, page_msg=msg)


def data_entry(module_name, table_name, row_name):
    role_access = rac.RoleAccessControl()
    table_data = role_access.has_access('TableObject', {'name': table_name})

    link_data, child_tables = role_access.get_child_tables(table_data.id)

    fg = form_generator.FormGenerator('mod_' + module_name, table_name)
    if row_name == 'new' or not child_tables:
        form = fg.default_single_entry_form(table_data, row_name)
    else:
        form = fg.default_parent_child_form(table_data, child_tables, link_data, row_name)

    if form.validate_on_submit() and len(form.errors) == 0:
        organization_access_control = oac.OrganizationAccessControl()
        row_names = organization_access_control.save_form()

        return saved_data(module_name, table_name, row_names)

    return templating.page_template('single_data_entry',
            module_name=module_name, form=form, table_name=table_name)


def multiple_entry(module_name, table_name):
    row_names =  json.loads(request.args.get('row_names'))
    fg = form_generator.FormGenerator('mod_' + module_name, table_name)
    form = fg.default_multiple_entry_form(row_names)

    if form.validate_on_submit() and len(form.errors) == 0:
        organization_access_control = oac.OrganizationAccessControl()
        row_names = organization_access_control.save_form()

        form = fg.default_multiple_entry_form(row_names)

        return saved_data(module_name, table_name, row_names)

    return templating.page_template('multiple_data_entry', module_name=module_name, form=form, table_name=table_name)

def change_role():
    role_id = request.json['role_id']
    role_access_control = rac.RoleAccessControl()
    success = role_access_control.change_role(role_id)
    return json.dumps({'success':success})

def forbidden():
    return templating.page_template('forbidden')
