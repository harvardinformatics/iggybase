import logging

from flask import g, redirect, url_for
from iggybase.web_files.decorators import templated
from iggybase.web_files.page_template import PageTemplate


def index():
    pt = PageTemplate(None, 'index')
    return pt.page_template_context()

@templated()
def default():
    pt = PageTemplate(None, 'index')
    return pt.page_template_context()

@templated()
def message(page_temp, page_msg):
    pt = PageTemplate(None, page_temp, page_msg=page_msg)
    return pt.page_template_context()

@templated()
def forbidden():
    pt = PageTemplate(None, 'forbidden')
    return pt.page_template_context()

@templated()
def page_not_found():
    logging.info('page_not_found')
    pt = PageTemplate(None, 'not_authorized')
    return pt.page_template_context()

def home():
    """redirects to user home page
    """
    if not g.user:
        abort( 403 )
    if g.user.home_page:
        home_page = g.user.home_page
    else:
        # TODO: we need to dynamically come up with facility
        home_page = url_for('core.detail', facility_name = 'murray', table_name =
        'user', row_name = g.user.name)
    return redirect( home_page )
