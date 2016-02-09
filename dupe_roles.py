import sys
from run import make_app
from iggybase.database import db_session
from iggybase.mod_admin.models import *
from iggybase.mod_admin import models as adm_mods

app = make_app()        
sess = db_session        ## shorthand.


def input_role(where):
    """Get from or to role from the customer.
    """
    print()
    print('Which role to copy %s?' % where)
    for index, role in enumerate(roles):
        print(index+1, role.name)
    ans = input('1 - %d, which? ' % len(roles))
    try:
        role = roles[int(ans) - 1]
    except:
        print('Wrong answer. Frown....')
        sys.exit()
    return role

def do_you_want_message(from_role, to_role, role_models):
    print()
    msg = """Records for %s from the following tables will be duped 
to the role %s:""" \
        % (from_role.name, to_role.name)
    print(msg)
    print()
    for tab in role_mods:
        print(tab)
    print()
    do_you = "Do you want to continue? (y or n)? "
    ans = input(do_you)
    if ans != 'y':
        print('Bye...')
        sys.exit()



# All the models that associate roles in mod_admin excluding Role itself. 
role_mods = [am for am in dir(adm_mods) if am.endswith('Role') and len(am) > len('Role')]

roles = sess.query(Role).order_by('name').all()

from_role = input_role('FROM')

roles.remove(from_role) # Remove from_role from choices.
to_role = input_role('TO')

do_you_want_message(from_role, to_role, role_mods)

for rm in role_mods:
    xx = sess.query(eval(rm)).filter_by(role_id=from_role.id). \
        filter_by(active=True)
    for x in xx:
        print(x.name, x.id)
        initials = ''.join([c for c in rm if c.isupper()])
        indx = sess.query(func.max(eval(rm).id)).one()[0] + 1
    print()

    



