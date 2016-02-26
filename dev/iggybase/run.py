import os
import socket
from iggybase import create_app

def make_app():
    rootdir = os.path.basename( os.path.dirname( os.path.abspath( __file__ ) ) )
    hostname = socket.gethostname()
    config_name = hostname + '.' + rootdir
    return create_app( config_name )

iggybase = make_app()

if __name__ == '__main__':
    iggybase.run( )
