from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SelectField, ValidationError
from wtforms.validators import DataRequired, Length, email
from iggybase.mod_admin.models import TableObject, TableObjectFacilityRole, Field, FieldFacilityRole
from iggybase.mod_auth.facility_role_access_control import FacilityRoleAccessControl


class DefaultSingleEntryForm( Form ):
    pass


class DefaultSummaryForm( Form ):
    pass


class DefaultMultupleEntryForm( Form ):
    pass


class DefaultMultupleEntryForm( Form ):
    pass