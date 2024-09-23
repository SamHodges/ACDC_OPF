from __future__ import division
from pyomo.environ import *
from models.DC_module.DC_model import DC_model

class NLP_DC(DC_model):
    def __init__(self, solver, testcase, model):
         super().__init__(solver, testcase, model)
         