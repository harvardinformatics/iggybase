import iggybase.templating as templating

def index():
    return templating.render_template( 'index.html' )

def default():
    return templating.page_template('index.html')

def message(page_temp, page_msg):
    return templating.page_template(page_temp, page_msg=page_msg)

def forbidden():
    return templating.page_template('forbidden')

def page_not_found():
    return templating.page_template('not_authorized')
