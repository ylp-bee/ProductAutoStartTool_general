# -*- coding: UTF-8 -*-
import logging
import logging.config
from ConfigManager import configs
import os
import sys

class Logger():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(level=logging.INFO)
        handler = logging.FileHandler(configs.logger_name)
        handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s-%(funcName)s:%(lineno)d-%(levelname)s %(message)s')
        handler.setFormatter(formatter)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        self.logger.addHandler(handler)
        self.logger.addHandler(console)

    def get_logger(self):
        return self.logger

logger=Logger().get_logger()
