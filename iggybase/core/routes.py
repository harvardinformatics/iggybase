from flask import request, jsonify, abort, g, render_template, url_for, current_app
from flask.ext.security import login_required
from flask.ext import excel
import json
import urllib
import time
from . import core
import iggybase.form_generator as form_generator
from iggybase import utilities as util
from iggybase.decorators import cached, templated
from iggybase import forms
import iggybase.templating as templating
from iggybase.core.organization_access_control import OrganizationAccessControl
from .table_query_collection import TableQueryCollection
from .work_item_group import WorkItemGroup
import logging

MODULE_NAME = 'core'

@core.route('/')
@login_required
def default(facility_name):
    return templating.page_template('index.html')


@core.route('/summary/<table_name>/')
@login_required
@templated('summary')
def summary(facility_name, table_name):
    page_form = template = 'summary'
    return build_summary(table_name, page_form, template)


@core.route('/summary/<table_name>/ajax')
@login_required
def summary_ajax(facility_name, table_name, page_form='summary', criteria={}):
    return build_summary_ajax(table_name, page_form, criteria)


@core.route('/action_summary/<table_name>/', methods=['GET', 'POST'])
@login_required
def action_summary(facility_name, table_name):
    page_form = 'summary'
    template = 'action_summary'
    return build_summary(table_name, page_form, template)


@core.route('/action_summary/<table_name>/ajax')
@login_required
def action_summary_ajax(facility_name, table_name, page_form='summary',
                        criteria={}):
    return build_summary_ajax(table_name, page_form, criteria)

@core.route('/detail/<table_name>/<row_name>')
@login_required
def detail(facility_name, table_name, row_name):
    page_form = template = 'detail'
    criteria = {(table_name, 'name'): row_name}
    tqc = TableQueryCollection(page_form,
                               table_name, criteria)
    tqc.get_results()
    add_row_id = False
    tqc.format_results(add_row_id)
    if not tqc.get_first().fc.fields:
        abort(404)
    if not tqc.get_first().table_dict:
        abort(403)
    hidden_fields = {'table': table_name, 'row_name': row_name}
    return templating.page_template(
        template,
        module_name=MODULE_NAME,
        table_name=table_name,
        row_name=row_name,
        table_queries=tqc,
        hidden_fields=hidden_fields
    )


@core.route('/summary/<table_name>/download/')
@login_required
def summary_download(facility_name, table_name):
    page_form = 'summary'
    add_row_id = False
    allow_links = False
    tqc = TableQueryCollection(page_form, table_name)
    tqc.get_results()
    tqc.format_results(add_row_id, allow_links)
    tq = tqc.get_first()
    csv = excel.make_response_from_array(tq.get_list_of_list(), 'csv')
    return csv


@core.route('/update_table_rows/<table_name>', methods=['GET', 'POST'])
@login_required
def update_table_rows(facility_name, table_name):
    #TODO: protect this by checking the rows ageninst org_ids
    updates = request.json['updates']
    message_fields = request.json['message_fields']
    ids = request.json['ids']

    tqc = TableQueryCollection('update', table_name,
                               {(table_name, 'id'): ids})
    tqc.get_results()
    tqc.format_results(True)
    tq = tqc.get_first()
    updated = tq.update_and_get_message(updates, ids, message_fields)
    return json.dumps({'updated': updated})


@core.route('/search', methods=['GET', 'POST'])
def search(facility_name):
    table_object = request.args.get('table_object')
    field_name = request.args.get('field_name')
    input_id = request.args.get('input_id')
    table_name = table_object.replace("_", " ").title()

    oac = OrganizationAccessControl()
    search_table, search_fields = oac.get_search_field_data(table_object, field_name)

    modal_html = '<div class="modal-header">'
    modal_html += '<button tobjectviewype="button" class="close_modal">&times;</button>'
    modal_html += '<h4 class="modal-title">' + table_name + ' Search</h4>'
    modal_html += '</div>'
    modal_html += '<div class="modal-body">'
    modal_html += '<input id="modal_input_id" value="' + input_id + '" type="hidden">'
    modal_html += '<input id="modal_table_object" value="' + table_object + '" type="hidden">'
    modal_html += '<input id="modal_search_table" value="' + search_table + '" type="hidden">'
    modal_html += '<input id="modal_field_name" value="' + field_name + '" type="hidden">'
    modal_html += '<p>All search inputs can use partial values</p>'
    modal_html += '<table>'
    if search_fields:
        for row in search_fields:
            modal_html += '<tr><td><label>' + row.FieldRole.display_name.replace("_", " ").title() + '</label></td>'
            modal_html += '<td><input id="search_' + row.Field.field_name + '"></input></td></tr>'
    else:
        modal_html += '<tr><td><label>' + field_name.replace("_", " ").title() + '</label></td>'
        modal_html += '<td><input id="search_name"></input></td></tr>'
    modal_html += '</table>'
    modal_html += '</div>'

    return modal_html


@core.route('/search_results', methods=['GET', 'POST'])
def search_results(facility_name):
    search_vals = json.loads(request.args.get('search_vals'))

    oac = OrganizationAccessControl()

    input_id = search_vals['modal_input_id']
    table_object = search_vals['modal_table_object']
    field_name = search_vals['modal_field_name']
    search_table = search_vals['modal_search_table']

    search_params = {}
    fields = []
    for key, value in search_vals.items():
        if key[:7] == 'search_':
            fields.append(key[7:])
            if value != '':
                search_params[key[7:]] = value

    if search_table == '':
        search_table, search_fields = oac.get_search_field_data(table_object, field_name)

        for row in search_fields:
            if row.Field.field_name not in fields:
                fields.append(row.Field.field_name)

    search_results = oac.get_search_results(search_table, search_params)

    modal_html = '<div class="modal-header">'
    modal_html += '<button type="button" class="close_modal">&times;</button>'
    modal_html += '<h4 class="modal-title">Search Results</h4>'
    modal_html += '</div>'
    modal_html += '<div class="modal-body">'
    modal_html += '<input id="modal_input_id" value="' + input_id + '" type="hidden">'
    modal_html += '<input id="modal_table_object" value="' + table_object + '" type="hidden">'
    modal_html += '<input id="modal_field_name" value="' + field_name + '" type="hidden">'
    modal_html += '<input id="modal_search_table" value="' + search_table + '" type="hidden">'
    modal_html += '<table class="table-sm table-striped"><tr><td>Name</td>'

    for field in fields:
        if field != 'name':
            modal_html += '<td>' + field.replace("_", " ").title() + '</td>'

    modal_html += '</tr>'

    if search_results is not None and len(search_params) != 0:
        for row in search_results:
            modal_html += '<tr><td><input luid="' + input_id + '"class="search-results" type="button" value="' + row.name + '"></input></td>'
            for field in fields:
                if field != 'name':
                    res = getattr(row, field)
                    if res is not None:
                        modal_html += '<td><label>' + format(res) + '</label></td>'
                    else:
                        modal_html += '<td></td>'

            modal_html += '</tr>'
    else:
        modal_html += '<tr><td><label>No Results Found</label></td></tr>'

    modal_html += '</table>'
    modal_html += '</div>'

    return modal_html


@core.route('/change_role', methods=['POST'])
@login_required
def change_role(facility_name):
    role_id = request.json['role_id']
    rac = util.get_role_access_control()
    success = rac.change_role(role_id)
    return json.dumps({'success': success})


@core.route('/data_entry/<table_name>/<row_name>/', methods=['GET', 'POST'])
@login_required
@templated('single_data_entry')
def data_entry(facility_name, table_name, row_name):
    module_name = MODULE_NAME
    rac = util.get_role_access_control()
    table_data = rac.has_access('TableObject', {'name': table_name})

    if not table_data:
        print(test)
        abort(403)

    fg = form_generator.FormGenerator(table_name)
    form = fg.default_data_entry_form(table_data, row_name)

    if form.validate_on_submit() and len(form.errors) == 0:
        print(test2)
        oac = OrganizationAccessControl()
        row_names = oac.save_form()

        return saved_data(facility_name, module_name, table_name, row_names)

    return templating.page_template_context('single_data_entry',
                                    module_name=module_name, form=form, table_name=table_name)


@core.route('/multiple_entry/<table_name>/', methods=['GET','POST'])
@login_required
def multiple_entry(facility_name, table_name):
    module_name = MODULE_NAME
    rac = util.get_role_access_control()
    table_data = rac.has_access('TableObject', {'name': table_name})

    if not table_data:
        abort(403)
    row_names = json.loads(request.args.get('row_names'))

    fg = form_generator.FormGenerator(table_name)
    form = fg.default_multiple_entry_form(row_names)

    if form.validate_on_submit() and len(form.errors) == 0 and len(row_names) == 0:
        oac = OrganizationAccessControl()
        row_names = oac.save_form()

        return saved_data(facility_name, module_name, table_name, row_names)

    return templating.page_template('multiple_data_entry', module_name=module_name, form=form, table_name=table_name)

@core.route('/cache/', methods=['GET','POST'])
@login_required
def cache(facility_name):
    module_name = MODULE_NAME
    form = forms.CacheForm()
    value = None
    if form.validate_on_submit() and len(form.errors) == 0:
        if 'get_value' in request.form and request.form['get_value']:
            if form.data['key']:
                value = current_app.cache.get(form.data['key'])
                if hasattr(value, 'data'):
                    value = value.data
        elif 'set_key' in request.form and request.form['set_key']:
            if form.data['key'] and form.data['value']:
                current_app.cache.set(form.data['key'], form.data['value'],
                        None, None, False)
                value = ('successfully set key ' + form.data['key'] + ' = ' +
                    form.data['value'])
        elif 'get_version' in request.form and request.form['get_version']:
            if form.data['refresh_obj']:
                value = str(current_app.cache.get_version(form.data['refresh_obj']))
            elif form.data['key']:
                value = str(current_app.cache.get_key_version(form.data['key']))
        elif 'set_version' in request.form and request.form['set_version']:
            if form.data['refresh_obj'] and form.data['version']:
                success = current_app.cache.set_version(form.data['refresh_obj'], form.data['version'])
                if success:
                    value = 'successfully '
                else:
                    value = 'failed to '
                value += ('set version ' + form.data['refresh_obj'] + ' = ' +
                    form.data['version'])

    return templating.page_template('cache', module_name=module_name,
            form=form,
            value=value)
@core.route('/workflow/<table_name>/')
@login_required
def workflow(facility_name, table_name):
    table_name = 'work_item_group'
    page_form = 'summary'
    template = 'workflow_summary'
    return build_summary(table_name, page_form, template)

@core.route('/workflow/<table_name>/ajax')
@login_required
def workflow_summary_ajax(facility_name, table_name, page_form='summary',
                        criteria={}):
    criteria = {'work_item_group.workflow':table_name}
    table_name = 'work_item_group'
    return action_summary_ajax(facility_name, table_name, page_form, criteria)

@core.route('/workflow/<workflow_name>/<work_item_group>', methods=['GET', 'POST'])
@login_required
def workflow_item_group(facility_name, workflow_name, work_item_group):
    page_form = 'summary'
    template = 'workflow_summary'
    template = 'single_data_entry'
    wig = WorkItemGroup(work_item_group)
    dynamic_vars = {}
    table_name = ''
    if wig.TableObject:
        table_name = wig.TableObject.name
        dynamic_vars['table_name'] = table_name
        dynamic_vars['row_name'] = 'new'
        dynamic_vars['facility_name'] = g.facility
    #url = url_for('core.data_entry', facility_name = g.facility, table_name = 'order', row_name = 'new')
    #url = url_for('core.detail', facility_name = 'murray', table_name = 'user', row_name = g.user.name)
    #url = url_for((module + '.' + route), **dynamic_vars)
    func = globals()[wig.Route.url_path]
    context = func(**dynamic_vars)
    wig.get_buttons(context['bottom_buttons'])
    context['wig'] = wig
    return render_template('work_item_group.html', **context)

""" helper functions start """


def build_summary(table_name, page_form, template, form=None):
    tqc = TableQueryCollection(page_form, table_name)
    tq = tqc.get_first()
    # if nothing to display then page not found
    if not tq.fc.fields:
        abort(404)
    return templating.page_template_context(template,
                                    module_name=MODULE_NAME,
                                    form=form,
                                    table_name=table_name,
                                    table_query=tq)


def build_summary_ajax(table_name, page_form, criteria):
    start = time.time()
    route = util.get_path(util.ROUTE)
    key = current_app.cache.make_key(
            route,
            g.rac.role.id,
            table_name
    )
    ret = current_app.cache.get(key)
    if not ret:
        print('NOT')
        tqc = TableQueryCollection(page_form, table_name, criteria)
        current = time.time()
        print(str(current - start))
        tqc.get_results()
        current = time.time()
        print(str(current - start))
        tqc.format_results()
        current = time.time()
        print(str(current - start))
        table_query = tqc.get_first()
        current = time.time()
        print(str(current - start))
        json_rows = table_query.get_row_list()
        current = time.time()
        print(str(current - start))
        ret = jsonify({'data': json_rows})
        current_app.cache.set(key, ret, (24 * 60 * 60), [table_name])
    return ret


def saved_data(facility_name, module_name, table_name, row_names):
    msg = 'Saved: '
    error = False
    for row_name in row_names:
        if row_name[0] == 'error':

            msg = 'Error: %s,' % str(row_name[1]).replace('<', '').replace('>', '')
            error = True
        else:
            table = urllib.parse.quote(row_name[1])
            name = urllib.parse.quote(row_name[0])
            msg += ' <a href=' + request.url_root + facility_name + '/' + module_name + '/detail/' + table + '/' + name + '>' + \
                   row_name[0] + '</a>,'

    msg = msg[:-1]
    if error:
        return templating.page_template('error_message', module_name=module_name, table_name=table_name, page_msg=msg)
    else:
        return templating.page_template('save_message', module_name=module_name, table_name=table_name, page_msg=msg)
