from flask import g
from iggybase.core.role_access_control import RoleAccessControl
from iggybase.core.organization_access_control import OrganizationAccessControl
import logging


def get_role_access_control():
    if not hasattr(g, 'role_access'):
        g.role_access = RoleAccessControl()
    return g.role_access


def get_org_access_control():
    if not hasattr(g, 'org_access'):
        g.org_access = OrganizationAccessControl()
    return g.org_access

