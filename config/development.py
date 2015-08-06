import os

#_basedir = os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) )

DEBUG = True

ADMINS = frozenset( [ 'mbreneiser@g.harvard.edu' ] )
SECRET_KEY = 'n`}UyR_r+9w2]%xZ~H?FRz^'

THREADS_PER_PAGE = 8

WTF_CSRF_ENABLED = True
WTF_CSRF_SECRET_KEY = "aEsu'a}-j\>rJ4'8MFz{<yn"

MAIL_SERVER = 'smtp.fas.harvard.edu'
SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://iggybase:nK9[@=H3}Wf./)9K@db-internal.rc.fas.harvard.edu/iggybase'

