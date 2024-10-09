import os
import pandas as pd
import datetime
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.opt import SolverStatus, TerminationCondition
import logging
import math
import json
from pyomo.util.infeasible import log_infeasible_constraints
from models.AC_Module import Linear_AC, NonLinear_AC, AC_model
from models.DC_module import Linearised_DC, Transport_DC, NLP_DC, DC_model
from models.Link_Module import HVDC_links, VSC_links
from create_datfile import selecttestcase, printdata
    
    
class OPF:
    def __init__(self, opf_type_ac, opf_type_dc, link_type, tc_ac, tc_dc, solver, neos=True, out=0):
        self.opf_type_ac = opf_type_ac
        self.opf_type_dc = opf_type_dc
        self.link_type = link_type
        self.tc_ac = tc_ac
        self.tc_dc = tc_dc
        self.solver = solver
        self.neos = neos
        self.out = out
        self.model = None
        self.instance = None
        self.datfile = 'datafile.dat'
        
        self.create_datfile()
        self.initialise_models()
        self.solve_model()
        
        
    def create_datfile(self):
        ptc_ac = self.runcase(self.tc_ac, self.solver, self.neos, self.out, self.opf_type_ac, ac_mode=True)
        ptc_dc = self.runcase(self.tc_dc, self.solver, self.neos, self.out, self.opf_type_dc, ac_mode=False)
        self.connectACDC(ptc_ac, ptc_dc, self.datfile)
    
    def initialise_models(self):
        self.model = AbstractModel()
        
        # run AC initialise
        match(self.opf_type_ac):
            case "linear":
                ac_opf = Linear_AC.Linear_AC(self.solver, self.tc_ac, self.model)
            case "nonlinear":
                ac_opf = NonLinear_AC.NonLinear_AC(self.solver, self.tc_ac, self.model)
            case _:
                ac_opf = Linear_AC.Linear_AC(self.solver, self.tc_ac, self.model)
        
        ac_opf.create_ac_opf()
        
        # run DC initialise
        match(self.opf_type_dc):
            case "linear":
                dc_opf = Linearised_DC.Linear_DC(self.solver, self.tc_dc, self.model)
            case "transport":
                dc_opf = Transport_DC.Transport_DC(self.solver, self.tc_dc, self.model)
            case "nlp":
                dc_opf = NLP_DC.NLP_DC(self.solver, self.tc_dc, self.model)
            case _:
                dc_opf = Linearised_DC.Linear_DC(self.solver, self.tc_dc, self.model)
        
        dc_opf.create_dc_opf()
        
        # run links initialise
        match(self.link_type):
            case "VSC":
                links = VSC_links.VSC_Links(self.model)
            case _:
                links = HVDC_links.HVDC_Links(self.model)
        
        links.add_links()
        
        # Obj 
        self.model.OBJ = Objective(rule=objective, sense=minimize)
        
        self.instance = self.model.create_instance(self.datfile)
        
    def solve_model(self):
        solveroptions  = SolverFactory(self.solver)
        solver_manager = SolverManagerFactory('neos')
        with open("modelformulation.txt", "w") as outputfile:
            self.instance.pprint(outputfile)
            
        
            
        solver_manager.solve(self.instance, opt=solveroptions, tee=True)
            
        self.log_pyomo_infeasible_constraints(self.instance)

        results = {}

        for v in self.instance.component_data_objects(Var):
            split_key = str(v).split("[")
            try:
                results[split_key[0]][split_key[1][:-1]] =  value(v)
            except:
                results[split_key[0]] = {}
                # results[split_key[0]][split_key[1][:-1]] =  value(v)
                
        print("Results: ", results)
        
        print("======================")
    
        
                
                
        with open("modelformulation.txt", "w") as outputfile:
            self.instance.pprint(outputfile)
        
        with open("output_log.json", "w") as myfile:
            json_object = json.dumps(results, indent=4)
            myfile.write(json_object)
                
        # return results

    
    def runcase(self, testcase,solver, neos, out, opf_type, ac_results=None,ac_mode=True):
        testcase_ac = os.path.join(".", "data", testcase)
        ptc_ac = selecttestcase(testcase_ac, ac_mode) #read test case
        
        opt=({'neos':neos,\
        'solver':solver,'out':0})
        
        r = printdata(self.datfile,ptc_ac,opt, opf_type)
        r.reducedata()
        r.printheader() if ac_mode else None
        r.printkeysets(ac_mode)
        r.printnetwork(ac_mode)
        r.printOPF(ac_mode)
        if ac_mode:
            r.printACOPF()
        else:
            r.printDCOPF(opf_type)
            
        return ptc_ac
        
    def connectACDC(self, ac_data, dc_data, datfile):
        f = open(datfile, 'a')
        f.write('set ACDC_Links:=\n')
        for i in ac_data["hvdc"].index.tolist():
            if str(ac_data["hvdc"]["type"][i]) == "MTDC":
                f.write("(" + str(ac_data["hvdc"]["name"][i]) + "_gen,")
                f.write(str(ac_data["hvdc"]["name"][i]) + ") \n")
        f.write(';\n')
    
    def log_pyomo_infeasible_constraints(self, model_instance):          
            # Create a logger object with DEBUG level
            logging_logger = logging.getLogger()
            logging_logger.setLevel(logging.DEBUG)
            # Create a console handler
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            # add the handler to the logger
            logging_logger.addHandler(ch)
            # Log the infeasible constraints of pyomo object
            print("Displaying Infeasible Constraints")
            log_infeasible_constraints(model_instance, log_expression=True,
                                log_variables=True, logger=logging_logger)
            
    
def objective(model):
    # obj = sum(model.VOLL_AC[d]*(1-model.alpha_AC[d])*model.baseMVA_AC*model.PD_AC[d] for d in model.D_AC)
    # sum(model.c2_AC[g]*(model.baseMVA_AC*model.pG_AC[g])**2+model.c1_AC[g]*model.baseMVA_AC*model.pG_AC[g]+ model.c0_AC[g] for g in model.G_AC)+\
        
        # sum(model.c1_DC[g]*(model.baseMVA_DC*model.pG_DC[g])+model.c0_DC[g] for g in model.G_DC) +\
        # -(sum(model.pG_AC[g] for g in model.LOCAL_HVDC))
        # sum(model.VOLL_AC[d]*(1-model.alpha_AC[d])*model.baseMVA_AC*model.PD_AC[d] for d in model.D_AC) +\
    obj = sum(model.c1_AC[g]*(model.baseMVA_AC*model.pG_AC[g])+model.c0_AC[g] for g in model.G_AC) +\
    sum(model.VOLL_AC[d]*(1-model.alpha_AC[d])*model.baseMVA_AC*model.PD_AC[d] for d in model.D_AC)
    return obj

            
newOPF = OPF(opf_type_ac="nonlinear", opf_type_dc="nlp", link_type="vsc", \
    tc_ac="PYPSA_case9_combined.xlsx", tc_dc="case9_DC.xlsx", solver="ipopt", neos=False, out=0)