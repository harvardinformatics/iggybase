import os
import sys
import site
import logging

# venv
venv_path = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'iggybase_env')

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir( os.path.join(venv_path, '/lib/python3.4/site-packages') )

# Activate your virtual env
activate_this = os.path.join( venv_path, 'bin', 'activate_this.py' )
exec( compile( open( activate_this, 'rb' ).read( ), activate_this, 'exec' ), dict( __file__ = activate_this ) )

sys.path.insert( 0, os.path.join(os.path.dirname( os.path.realpath( __file__ ) ), 'iggybase'))
sys.path.insert( 0, os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'iggybase.log' ) )

logging.basicConfig( filename=os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'iggybase.log' ),level=logging.DEBUG )

from iggybase.iggybase import create_app

application = create_app( )
