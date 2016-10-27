import os
import socket
from iggybase import create_app

def make_app():
    rootdir = os.path.basename( os.path.dirname( os.path.abspath( __file__ ) ) )
    hostname = socket.gethostname()
    return create_app()

iggybase = make_app()

if __name__ == '__main__':
    iggybase.run( )
