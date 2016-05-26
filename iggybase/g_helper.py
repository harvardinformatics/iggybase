from flask import g
from iggybase.core.role_access_control import RoleAccessControl
from iggybase.core.organization_access_control import OrganizationAccessControl
import logging

def get_role_access_control():
    if 'role_access' not in g:
        g.role_access = RoleAccessControl()
    return g.role_access

def get_org_access_control():
    if 'org_access' not in g:
        g.org_access = OrganizationAccessControl()
    return g.org_access

