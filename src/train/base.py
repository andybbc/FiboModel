# -*- coding: utf-8 -*-
import sys
sys.path.append("..")
from core.base import RecoBase


class Base(RecoBase):

    def __init__(self, dic_config={}):
        RecoBase.__init__(self, dic_config)
