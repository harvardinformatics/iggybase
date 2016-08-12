import sys
import os

# add iggybase root dir to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from illumina_iggy_script import IlluminaIggyScript

script = IlluminaIggyScript()
script.run()
