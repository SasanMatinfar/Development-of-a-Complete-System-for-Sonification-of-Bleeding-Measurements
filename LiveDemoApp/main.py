import sys
import logging
from sonification import *


logger = logging.getLogger()
file_handler = logging.FileHandler(filename='mylog.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    start_algomus()
    sys.exit(app.exec_())




