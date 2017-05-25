from flask import g
from iggybase.core.role_access_control import RoleAccessControl
from iggybase.core.organization_access_control import OrganizationAccessControl
import logging


def get_role_access_control():
    if not hasattr(g, 'rac'):
        g.rac = RoleAccessControl()
    return g.rac


def get_org_access_control():
    if not hasattr(g, 'oac'):
        g.oac = OrganizationAccessControl()
    return g.oac

