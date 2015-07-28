import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/var/www/html/iggybase/iggybase_env/lib/python3.4/site-packages')



# Activate your virtual env
activate_this = '/var/www/html/iggybase/iggybase_env/bin/activate_this.py'
exec( compile( open( activate_this, 'rb' ).read( ), activate_this, 'exec' ), dict( __file__ = activate_this ) )

sys.path.insert( 0, '/var/www/html/iggybase' )
sys.path.insert( 0, '/var/www/html/iggybase/iggybase' )

from iggybase import app as application
