from iggybase.web_files.form_generator import FormGenerator
from iggybase.web_files.iggybase_form_fields import IggybaseBooleanField, IggybaseSelectField
from wtforms.validators import DataRequired
from iggybase import g_helper

class RoleForm(FormGenerator):
    def __init__(self, page_form_name, form_type, page_context, module_name):
        super(RoleForm, self).__init__(module_name, page_form_name, page_context)

        self.role_tables = ['menu', 'page_form_button', 'route', 'table_object', 'workflow']
        self.table_name = 'Role'
        self.form_type = form_type
        self.classattr = {}


    role = IggybaseSelectField('Role', validators=[DataRequired()])
    remember_me = IggybaseBooleanField('remember_me', default=False)