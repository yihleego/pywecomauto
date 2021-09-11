# -*- coding: utf-8 -*-
import logging
import os

import yaml

DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(DIR, r'config.yaml')
file = open(CONFIG_PATH, 'r', encoding='utf-8')
config = yaml.load(file.read(), Loader=yaml.FullLoader)
logging_level = config['logging']['level']
server_port = config['server']['port']
logging.basicConfig(format="%(asctime)s %(levelname)5s %(module)s.%(funcName)s[%(lineno)d] : %(message)s", level=logging.getLevelName(logging_level))
