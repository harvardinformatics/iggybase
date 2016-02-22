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



def forbidden():
    return templating.page_template('forbidden')
