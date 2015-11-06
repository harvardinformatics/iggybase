import os
import socket
import logging

class Config:
    _basedir = os.path.abspath( os.path.dirname( __file__ ) )

    ADMINS = frozenset( [ 'mbreneiser@g.harvard.edu' ] )

    THREADS_PER_PAGE = 8

    WTF_CSRF_ENABLED = True

    MAIL_SERVER = 'smtp.fas.harvard.edu'

    ADMIN_DB_NAME = 'iggybase_admin'
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://iggybase:nK9[@=H3}Wf./)9K@db-internal.rc.fas.harvard.edu/'

class RC_Development( Config ):
    PROJECT = "iggybase"

    DEBUG = True
    SECRET_KEY = 'n`}UyR_r+9w2]%xZ~H?FRz^'

    WTF_CSRF_SECRET_KEY = "aEsu'a}-j\>rJ4'8MFz{<yn"

    DATA_DB_NAME = 'iggybase'

    GROUP = 'RC'

class MB_Development( Config ):
    PROJECT = "iggybase"

    DEBUG = True
    SECRET_KEY = 'n`}UyR_r+9w2]%xZ~H?FRz^'

    WTF_CSRF_SECRET_KEY = "aEsu'a}-j\>rJ4'8MFz{<yn"

    DATA_DB_NAME = 'iggybase_mb'

    GROUP = 'RC'

class RK_Development( Config ):
    PROJECT = "iggybase"
    ADMIN_DB_NAME = 'iggybase_rk_admin'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://reuven:shekels@localhost/'
    DATA_DB_NAME = 'iggybase_rk_data'
    DEBUG = True
    SECRET_KEY = 'n`}UyR_r+9w2]%xZ~H?FRz^'
    WTF_CSRF_SECRET_KEY = "aEsu'a}-j\>rJ4'8MFz{<yn"
    FACILITY= 'RC'
    GROUP = 'RC'
    
config = {
    'timbran.rc.fas.harvard.edu.iggybase': RC_Development,
    'mbreneiser.iggybase': MB_Development,
    'Reuvens-iMac.local.iggybase': RK_Development,
}

def get_config( ):
        rootdir = os.path.basename( os.path.dirname( os.path.abspath( __file__ ) ) )
        hostname = socket.gethostname()
        config_name = hostname + '.' + rootdir
        conf = config[ config_name ]( )
        logging.debug( config_name )
        #logging.debug( conf.LAB )

        return conf

