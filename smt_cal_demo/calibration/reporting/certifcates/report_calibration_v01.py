# -*- coding: utf-8 -*-
"""
Created on Mon Apr 01 12:48:40 2013

@author: Scheidt
"""

import smt_cal_demo.utilities.easygui as eg
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Table,KeepTogether,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import enums as rl_enums
from smt_cal_demo.calibration.database.support import session,Calibration,Instrument,Measurement,Certificate,db_id_offset
import smt_cal_demo.calibration.tokens.testpoint_keys as c_tst
import smt_cal_demo.calibration.tokens.device_functions as c_fct
import smt_cal_demo.calibration.tokens.reporting as c_rpt
import smt_cal_demo.calibration.tokens.physical_units as c_phy
from smt_cal_demo.calibration.models.support_v01 import Var
from smt_cal_demo.calibration.models.support_v01 import Var as oldVar

import math

def format_number_unc(x, ux, size=14, no_prefix=False):
    prefixes={-1:(1e-3,"m"),
            -2:(1e-6,"u"),
            -3:(1e-9,"n"),
            -4:(1e-12,"p"),
            -5:(1e-15,"f"),
            0:(1,""),
            1:(1e3,"k"),
            2:(1e6,"M"),
            3:(1e9,"G"),
            4:(1e12,"T"),
            5:(1e15,"P"),
            6:(1e18,"E"),
            }

    if x == 0:
        n_x = 1
    else:
        n_x = math.floor(math.log10(abs(x)))
    if ux == 0:
        n_ux = n_x-8
    else:
        n_ux = math.floor(math.log10(abs(ux)))
    potenz = 10**(n_ux-1)
    f_x = potenz*round(x/potenz)
    f_ux = potenz*math.ceil(ux/potenz)
    
    if abs(f_x)>abs(f_ux):
        pref_index = math.floor(n_x/3.0)
    else:
        pref_index = math.floor(n_ux/3.0)
    if no_prefix:
        pref_index = 0
    if abs(x) > 1e20:
        pref_index = 0
    
    pref_mul =  1/prefixes[pref_index][0]    
    pref_unit =  prefixes[pref_index][1]    
    
    kommastellen = 1- n_ux + pref_index * 3
    if kommastellen<0:
        kommastellen = 0
    format_str = "{" + ":.{:.0f}".format(kommastellen) + "f}"

    
    
    f2_x = format_str.format(f_x * pref_mul)
    if ux == 0:
        if f2_x.find(".")>=0:
            while f2_x[-1]=="0":
                f2_x = f2_x[0:-1]
            if f2_x[-1]==".":
                f2_x = f2_x[0:-1]

    if f2_x == "0":
        f2_x += pref_unit
    elif f2_x == "-0":
        f2_x = "0" + pref_unit
    else:    
        f2_x += pref_unit
    
    f2_ux = format_str.format(f_ux * pref_mul)
    if ux == 0:
        if f2_ux.find(".")>=0:
            while f2_ux[-1]=="0":
                f2_ux = f2_ux[0:-1]
            if f2_x[-1]==".":
                f2_ux = f2_ux[0:-1]

    if f2_ux == "0":
        pass
    elif f2_ux == "-0":
        f2_ux = "0"
    else:    
        f2_ux += pref_unit


    
    #return (f_x*pref_mul,f_ux*pref_mul,pref_unit,n_ux,1-n_ux+pref_index*3)
    if f2_x.lstrip().find("490.1499")>=0:
        pass
    return ( f2_x.lstrip(), f2_ux.lstrip())



def format_number(number, digits=6, no_prefix=False):
    f = float(number)
    if f==0:
        index = 0
    else:
        index = math.floor(math.log10(abs(f))//3)
    prefixes={-1:(1e-3,"m"),
            -2:(1e-6,"u"),
            -3:(1e-9,"n"),
            -4:(1e-12,"p"),
            -5:(1e-15,"f"),
            0:(1,""),
            1:(1e3,"k"),
            2:(1e6,"M"),
            3:(1e9,"G"),
            4:(1e12,"T")
    }
    if no_prefix:
        index = 0
        
    if index<-5:
        f = 0
        prefix = 0
        f1 = 0
        suffix = " "
    else:
        f1 = f/prefixes[index][0]
        suffix = prefixes[index][1]

    if f1==0:
        sf2 = "0"
    else:
        sf2="{:f}".format(f1)
        if sf2.find(".")>=0:
            while sf2[-1]=="0":
                sf2 = sf2[0:-1]
            if sf2[-1]==".":
                sf2 = sf2[0:-1]
    
    if sf2 == "0":
        pass
    elif sf2 == "-0":
        sf2 = "0"
    else:
        sf2 += suffix       
        
    return sf2

def compare(item1, item2):
    d1 = item1.strip("{").strip("}").split(",")
    d1 = [a.strip() for a in d1]
    
    d2 = item2.strip("{").strip("}").split(",")
    d2 = [a.strip() for a in d2]
    
    included = True
    for d in d1:
        if d not in d2:
            included = False

    return included

def is_in(item, item_list):
    
    for zw in item_list:
        if compare(item, zw):
            return zw
            
    return None

    
def create_report(story, style_sheet, calibration, sort_ids,cur_proc_instrs, specs, options):
    
    # create a list of all used instruments
    instruments = set()                        
    for item in calibration.measurements:
        try:
            prc = item.procedure
            if hasattr(item.procedure, "equipment_ids"):
                for item_id in item.procedure.equipment_ids:
                    try:
                        instruments.add(item_id)
                    except:
                        print(item_id)
        except:
            pass
            


    entry_style=ParagraphStyle("DataEntry",style_sheet["BodyText"])
    entry_style.fontSize = 7
    entry_style.spaceBefore = 0
    entry_style.spaceAfter = 0
    entry_style.leading = 9
    entry_style.alignment = 2
    
    proc_desc_style=ParagraphStyle("ProcDescription",style_sheet["BodyText"])
    proc_desc_style.fontSize = 8
    proc_desc_style.spaceBefore = 0
    proc_desc_style.spaceAfter = 0
    proc_desc_style.leading = 9
    proc_desc_style.alignment = 0
    proc_desc_style.keepWithNext  = True
    
    tab_header_style=ParagraphStyle("TabHeader",style_sheet["BodyText"])
    tab_header_style.fontName = "Helvetica-Bold"
    tab_header_style.fontSize = 8
    tab_header_style.spaceBefore = 0
    tab_header_style.spaceAfter = 0
    tab_header_style.leading = 9
    tab_header_style.alignment = 2
    
    tab_header_equipment_style=ParagraphStyle("TabHeaderEquipment",style_sheet["BodyText"])
    tab_header_equipment_style.fontName = "Helvetica-Bold"
    tab_header_equipment_style.fontSize = 8
    tab_header_equipment_style.spaceBefore = 0
    tab_header_equipment_style.spaceAfter = 0
    tab_header_equipment_style.leading = 9
    tab_header_equipment_style.alignment = 0


    tab_style = ParagraphStyle("Table",style_sheet["BodyText"])
    tab_style.alignement = rl_enums.TA_LEFT
    tab_style.fontSize = 8
    tab_style.leading = 8
    if len(instruments)>0:
        story.append(Paragraph("<b>Instruments used</b><br/><br/>",style_sheet["BodyText"]))                        

        tabledata = [[Paragraph("Instrument",tab_header_equipment_style),
                    Paragraph("Manufacturer and Model",tab_header_equipment_style),
                    Paragraph("Serial number",tab_header_equipment_style),
                    Paragraph("Last calibration",tab_header_equipment_style)]]

        for item in instruments:
            try:
                instrument = session.query(Instrument).filter(Instrument.marked_id == item).one()
                tabledata.append([Paragraph(instrument.object_description, tab_style),
                                  Paragraph(instrument.manufacturer + "<br/>" + instrument.model, tab_style),
                                  Paragraph(instrument.serial_number, tab_style),
                                  Paragraph(instrument.last_calibration.strftime("%d %b %Y"), tab_style)
                                  ])
            except Exception as exc:
                print(("Warning! " + item + " not in instrument database"))
                print("Fehler")
                print((exc.args[0]))
    
        list_style = TableStyle(
                                [('LINEABOVE', (0,0), (-1,0), 2, colors.green),
                                ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
                                ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
                                ('ALIGN', (0,0), (-1,-1), 'LEFT'),
                                ('BACKGROUND', (0,0), (-1,0), colors.Color(0.9,0.9,0.9)),
                                ('VALIGN', (0,0), (-1,-1), 'TOP')]     
                                )

        tx = Table(tabledata,
                    colWidths = [45*mm, 55*mm, 35*mm, 25*mm],
                    style=list_style)
        tx.hAlign = 'LEFT'
        story.append(tx)                        

    story.append(Paragraph("<br/><b>Laboratory Environment</b><br/><br/>Temperature: 23°C \u00B12K",proc_desc_style))                        

    c_pass_text = '<para alignment="right">P<font color="green">\u2714</font></para>'
    c_cond_conf_text = '<para alignment="right">P<super>C</super><font color="yellow">\u2714</font></para>'
    c_cond_failed_text = '<para alignment="right">F<super>C</super><font color="orange">-</font></para>'
    c_failed_text = '<para alignment="right">F<font color="red">-</font></para>'
    c_marginal_text = '<para alignment="right">M<font color="orange">\u2714</font></para>'

    # sometimes measurment are repeated. Try to take latest measurment and warn if there
    # are multiple valid measurmenst
    unique_measurments = dict()
    k1 = 0
    for item in calibration.measurements:
        if item.validity:
            # already available?
            if is_in(item.parameter, unique_measurments):
                print(("Warning! multiple measurements with parameter: " + item.parameter))
                other_measurement = calibration.measurements[unique_measurments[is_in(item.parameter, unique_measurments)]]
                if item.start_date > other_measurement.start_date:
                    # remove old key
                    unique_measurments.pop(is_in(item.parameter, unique_measurments))
                    unique_measurments[item.parameter] = k1
            else:
                unique_measurments[item.parameter] = k1
        else:
            print("not valid",item.parameter)
        k1 += 1
        

    # sorting can be changed by specificing sort_ids
    unique_measurments_indizes =list()
    if len(sort_ids) == 0:
        unique_measurments_indizes = list(unique_measurments.values())
        unique_measurments_indizes.sort()
        print(unique_measurments_indizes)
    else:
        for item in sort_ids:
            if is_in(item,unique_measurments) is not None:
                print(("found" + item))
                unique_measurments_indizes.append(unique_measurments[is_in(item,unique_measurments)])
            else:
                print(("missing" + item))

    
    unique_results = dict()    

    visual_inspection_done = False
    spec_available = False
    # verify measurment against specs    
    for key in unique_measurments_indizes:
        item = calibration.measurements[key]
        proc=item.procedure    
        if "test" in proc.testpoint:
            if proc.testpoint["test"].find("Visual inspection")>=0:
                visual_inspection_done = True

        spec = dict()
        test_result = None
        per_of_tol =None
        marginal_limit = 0.8

        spec_index = is_in(item.parameter, specs)
        if spec_index is not None:
# Caution: if you modify or add new parameters also cal_spec_reader must be adjusted            
            spec = specs[spec_index]
            if "testvar" in spec:
                test_var = spec["testvar"]
                if test_var == "delta":
                    proc.delta = proc.result_list()[-2]
                if "abs" in spec:
                    test_var_value = eval("proc." + test_var)
                    if type(test_var_value) is Var:
                        tol_max = spec["abs"]
                        if (abs(test_var_value.v)<tol_max - test_var_value.u*2 and
                            tol_max > test_var_value.u*2):
                            test_result = c_pass_text
                            per_of_tol = abs(test_var_value.v/tol_max)
                        elif abs(test_var_value.v)<tol_max + test_var_value.u*2:
                            if abs(test_var_value.v)<tol_max:
                                test_result = c_cond_conf_text
                                per_of_tol = abs(test_var_value.v/tol_max)
                            else:
                                test_result = c_cond_failed_text
                                per_of_tol = abs(test_var_value.v/tol_max)
                        else:
                            test_result = c_failed_text
                            per_of_tol = abs(test_var_value.v/tol_max)
                    else:
                        print("Achtung type surprize", key, test_var_value, type(test_var_value))
                        tol_max = spec["abs"]
                        if abs(test_var_value)<marginal_limit*tol_max:
                            test_result = c_pass_text
                        elif abs(test_var_value)<tol_max:
                            test_result = c_marginal_text
#                            raise Exception("Marginal not compatible to 17025:2018.")
                        else:
                            test_result = c_failed_text
                        per_of_tol = abs(test_var_value/tol_max)
                elif "rel" in spec:
                    test_var_value = eval("proc." + test_var)
                    if type(test_var_value) is Var:
                        tol_max = abs(spec["rel"] * proc.model.y.v)
                        if (abs(test_var_value.v)<tol_max - test_var_value.u*2 and
                            tol_max > test_var_value.u*2):
                            test_result = c_pass_text
                            per_of_tol = abs(test_var_value.v/tol_max)
                        elif abs(test_var_value.v)<tol_max + test_var_value.u*2:
                            if abs(test_var_value.v)<tol_max:
                                test_result = c_cond_conf_text
                                per_of_tol = abs(test_var_value.v/tol_max)
                            else:
                                test_result = c_cond_failed_text
                                per_of_tol = abs(test_var_value.v/tol_max)
                        else:
                            test_result = c_failed_text
                            per_of_tol = abs(test_var_value.v/tol_max)
                    else:
                        tol_max = abs(spec["rel"] * proc.model.y.v)
                        if abs(test_var_value)<marginal_limit*tol_max:
                            test_result = c_pass_text
                        elif abs(test_var_value)<tol_max:
                            test_result = c_marginal_text
    #                        raise Exception("Marginal not compatible to 17025:2018.")
                        else:
                            test_result = c_failed_text
                        per_of_tol = abs(test_var_value/tol_max)
# this is buggy and shoul not be used any more
#                if spec.has_key("abs_y_max"):
#                    test_var_value = eval("proc." + test_var)
#                    tol_max = spec["abs_y_max"]
#                    tol_min = 2 * proc.model.y.v - spec["abs_y_max"]
#                    if test_var_value>tol_max or test_var_value<tol_min:
#                        test_result = c_failed_text
#                    else:
#                        test_result = c_pass_text
#                    per_of_tol = abs(((tol_max+tol_min)/2-test_var_value)/(tol_max-tol_min))
                if "between" in spec:
                    test_var_value = eval("proc." + test_var)
                    tol_min = float( spec["between"].split(" ")[0])
                    tol_max = float( spec["between"].split(" ")[1])
                    if type(test_var_value) is Var:
                        per_of_tol = 2*abs(((tol_max+tol_min)/2-test_var_value.v)/(tol_max-tol_min))
                        if (test_var_value.v < tol_max - test_var_value.u) and (test_var_value.v > tol_min + test_var_value.u):
                            test_result = c_pass_text
                        elif (test_var_value.v < tol_max) and (test_var_value.v > tol_min):
                            test_result = c_cond_conf_text
                        elif (test_var_value.v < tol_max + test_var_value.u) and (test_var_value.v > tol_min - test_var_value.u):
                            test_result = c_cond_failed_text
                        else:
                            test_result = c_failed_text
                    else:
                        tol_min_marg = tol_min + (tol_max - tol_min) * (1-marginal_limit)/2
                        tol_max_marg = tol_max - (tol_max - tol_min) * (1-marginal_limit)/2
                        per_of_tol = 2*abs(((tol_max+tol_min)/2-test_var_value)/(tol_max-tol_min))
                        if test_var_value>tol_max or test_var_value<tol_min:
                            test_result = c_failed_text
                        elif test_var_value>tol_max_marg or test_var_value<tol_min_marg:
                            test_result = c_marginal_text
                            raise Exception("Marginal not compatible to 17025:2018.")
                        else:
                            test_result = c_pass_text
                if "between_no_marg" in spec:
                    test_var_value = eval("proc." + test_var)
                    tol_min = float( spec["between_no_marg"].split(" ")[0])
                    tol_max = float( spec["between_no_marg"].split(" ")[1])
                    per_of_tol = None
                    if hasattr(test_var_value,"v"):
                        if test_var_value.v>tol_max or test_var_value.v<tol_min:
                            test_result = c_failed_text
                        else:
                            test_result = c_pass_text
                    else:
                        if test_var_value>tol_max or test_var_value<tol_min:
                            test_result = c_failed_text
                        else:
                            test_result = c_pass_text
                        
            else:
                if "abs" in spec:
                    test_result = "multiline"
                    
        unique_results[key] = (test_result,per_of_tol)

    if visual_inspection_done == False:
        if eg.ynbox("No visual inspection! Proceed (Yes)"):
            pass
        else:
            raise Exception("no visual inspection")
    
    # now process measurments as they come in.
    # a new section will be started if the test name, the procedure, the function or the sub function changes

    lastproc = ""
    last_function_test = ""
    last_sub_function_test = ""
    last_test_name = ""
    tabledata=list()
    has_units = False

    for key in unique_measurments_indizes:
        item = calibration.measurements[key]
        proc=item.procedure    
        test_result = unique_results[key][0]
        per_of_tol = unique_results[key][1]            
        curr_function_test = proc.testpoint["Function"] if "Function" in proc.testpoint else ""
        if "test" in proc.testpoint:
            curr_test_name = proc.testpoint["test"]
        else:
            curr_test_name = ""

        if c_tst.sub_function in proc.testpoint:
            curr_sub_function_test = proc.testpoint[c_tst.sub_function]
        else:
            curr_sub_function_test = ""

        if ((str(proc.__class__ ) != lastproc) or
            (curr_function_test != last_function_test) or
            (curr_test_name != last_test_name) or
            (curr_sub_function_test != last_sub_function_test)):

            if tabledata:
                process_table(tabledata, has_units, newtype, story)
            tabledata = list()
            

            lastproc=str(proc.__class__)
            last_function_test = curr_function_test
            last_test_name = curr_test_name
            last_sub_function_test = curr_sub_function_test
            
            info="<br/>"
            if "explanation" in proc.testpoint:
                raise Exception()

            if "test" in proc.testpoint:
                if is_in(item.parameter,cur_proc_instrs):
                    if "test" in cur_proc_instrs[is_in(item.parameter,cur_proc_instrs)]:
                        test_info = cur_proc_instrs[is_in(item.parameter,cur_proc_instrs)]["test"]
                    else:
                        test_info = proc.testpoint["test"]
                else:
                    test_info = proc.testpoint["test"]
                    
                info += "<b>Test: " + correct_text(test_info) + "</b><br/>"
                if curr_sub_function_test!="":
                    info += "<b>Sub Function: " + correct_text(curr_sub_function_test) + "</b><br/>"
                    
            elif curr_function_test != "":
                info += "<b>Tested functionality: " + curr_function_test + "</b><br/>"
            if not proc.method_info() == "":
                info += "<br/><b>Measuring principle:</b><br/>"
                info += proc.method_info()
            
            info += "<br/><b>Used procedure:</b><br/>" + str(proc.__class__).split("'")[1]


            if is_in(item.parameter,cur_proc_instrs):
                if "explanation" in cur_proc_instrs[is_in(item.parameter,cur_proc_instrs)]:
                    info += "<br/><b>Detailed Explanation:</b><br/>"
                    info += cur_proc_instrs[is_in(item.parameter,cur_proc_instrs)]["explanation"]

            if hasattr(proc,"env_info"):
                if proc.env_info:
                    info += "<br/>Test environment:<br/>"
                    #info += proc.env_info.replace("\n","<br/>")
                    # fix wrong cable 
                    info += proc.env_info.replace("\n","<br/>").replace(
                    "Unused, no component",
                    "None").replace(
                    "RG58 cable 0.6m Emerson Network Power 415-0058-024#1",
                    "Huber Sugner Sucoflex 104P 400mm #SN 501989").replace(
                    "Huber Sugner", "Huber Suhner")
            if hasattr(proc,"dut_info"):
                if proc.dut_info:
                    info += "<br/>DUT:<br/>"
                    info += proc.dut_info.replace("\n","<br/>")
                
            
            info += "<br/><br/>"


            story.append(Paragraph(info,proc_desc_style))

                    
            units = list()
            has_units = False
            org_headers = proc.header_list()
            newtype = False
            if type(org_headers[0]) is tuple:
                newtype = True
                    
                    
                    
            if newtype:
                headers = list()
                grouping_layer = False
                for item in org_headers:
                    if item[2]!=c_rpt.not_grouped:
                        grouping_layer = True
                
                has_units = False
                for item in org_headers:
                    if item[1]!=c_phy.none:
                        has_units = True

                units = list()
                format_rules = list()
                for item in org_headers:
                    headers.append(item[0])
                    if item[1] == c_phy.Ohm:
                        units.append("\u03A9")
                        format_rules.append("")
                    elif item[1] == c_phy.Ohm_per_Ohm:
                        units.append("\u03A9/\u03A9")
                        format_rules.append("")
                    elif item[1] == c_phy.GradC:
                        units.append("°C")
                        format_rules.append("Temp")
                    elif item[1] == c_phy.scalar_per_cent:
                        units.append("%")
                        format_rules.append("per_cent")
                    elif item[1] == c_phy.scalar_ppm:
                        units.append("ppm")
                        format_rules.append("ppm")
                    elif item[1] == c_phy.V_per_div:
                        units.append("V/div")
                        format_rules.append("")
                    elif item[1] == c_phy.none:
                        units.append("")
                        format_rules.append("")
                    elif item[1] == c_phy.scalar_ratio_one_over:
                        units.append("")
                        format_rules.append("scalar_ratio_one_over")
                    elif item[1] == c_phy.scalar_one_to_one:
                        units.append("")
                        format_rules.append("scalar_one_to_one")
                    else:
                        units.append(str(item[1]))
                        format_rules.append("")
                    # test if an uncertainty spec exists
                    if len(item) > 3:
                        headers.append(c_rpt.exp_unc)
                        if item[1] == c_phy.Ohm:
                            units.append("\u03A9")
                            format_rules.append("")
                        elif item[1] == c_phy.Ohm_per_Ohm:
                            units.append("\u03A9/\u03A9")
                            format_rules.append("")
                        elif item[1] == c_phy.GradC:
                            units.append("°C")
                            format_rules.append("Temp")
                        elif item[1] == c_phy.scalar_per_cent:
                            units.append("%")
                            format_rules.append("per_cent")
                        elif item[1] == c_phy.scalar_ppm:
                            units.append("ppm")
                            format_rules.append("ppm")
                        elif item[1] == c_phy.V_per_div:
                            units.append("V/div")
                            format_rules.append("")
                        elif item[1] == c_phy.none:
                            units.append("")
                            format_rules.append("")
                        elif item[1] == c_phy.scalar_ratio_one_over:
                            units.append("ppm")
                            format_rules.append("scalar_ratio_one_over")
                        elif item[1] == c_phy.scalar_one_to_one:
                            units.append("")
                            format_rules.append("scalar_one_to_one")
                        else:
                            units.append(str(item[1]))
                            format_rules.append("")
                
                if not test_result is None:
                    headers.append("Tol. used")
                    units.append("%")
                    format_rules.append("")
                    headers.append("Test result")
                    units.append("P/M/F")
                    format_rules.append("")
    
                headers = [x.replace(" ","\n") for x in headers]
                row=list()
                for item2 in headers:
                    row.append(Paragraph(item2,tab_header_style))
    
                tabledata.append(row)
            else:
                headers = org_headers
                k1 = 0
                for k1 in range(0,len(headers)):
                    header = headers[k1]
                    header_split = header.split("(")
                    if len(header_split) == 2:
                        has_units = True
                        units.append(Paragraph(header_split[1][0:-1],tab_header_style))
                        headers[k1] = header_split[0]
                    else:
                        units.append(Paragraph("",tab_header_style))

                if not test_result is None:
                    headers.append("Tol. used (%)")
                    headers.append("Test result (P/M/F)")
    
                headers = [x.replace(" ","\n") for x in headers]
                row=list()
                for item2 in headers:
                    row.append(Paragraph(item2,tab_header_style))
    
                tabledata.append(row)
                if has_units:
                    tabledata.append(units)
            
        if newtype:
            if options["acc_spec"]:
                if hasattr(proc,"acc_result_list"):
                    raw_data = proc.acc_result_list()
                else:
                    raw_data = proc.result_list()
                    #raise Exception("accredited result list is missing")
            else:
                raw_data = proc.result_list()

            multirow_data = False
            if type(raw_data) is list:
                if type(raw_data[0]) is list:
                    multirow_data = True
                else:
                    raw_data = [raw_data]

            abs_errors = None
            if multirow_data:
                if is_in(calibration.measurements[key].parameter, specs):
                    spec = specs[is_in(calibration.measurements[key].parameter, specs)]
                    if "abs" in spec:
                        abs_errors = spec["abs"].split(" ")
                        
    
            print((proc.result_string()))
    
            for k_data in range(len(raw_data)):
                data = raw_data[k_data]
                    
                row=list()
                    
                if (not (test_result is None)) and (test_result!="multiline"):
                    data.append(per_of_tol)
                    data.append(test_result)
                elif not (abs_errors is None):
                    if abs_errors[k_data].strip() == "-":
                        data.append("-")
                        data.append("-")
                        pass
                    else:
                        tol_max = float(abs_errors[k_data])
                        test_var_value = data[-1].v
                        if abs(test_var_value)<marginal_limit*tol_max:
                            test_result_ml = c_pass_text
                        elif abs(test_var_value)<tol_max:
                            test_result_ml = c_marginal_text
                            raise Exception("Marginal not compatible to 17025:2018.")
                        else:
                            test_result_ml = c_failed_text
                        per_of_tol = abs(test_var_value/tol_max)
                        data.append(per_of_tol)
                        data.append(test_result_ml)
                    
                    
                
                k2 = 0
                for k1 in range(data.__len__()):
                    item = data[k1]
                    limited_value = None
                    if type(item) is tuple:
                        print("hier", item)
                        limited_value = item
                        item = item[0]

                    format_rule = format_rules[k2]
                    if type(item) is oldVar:
                        print("Warning: Pyhon 3 conversion wrong for: ", type(proc))
                    if (type(item) is str or
                        type(item) is str):
                        row.append(Paragraph(item,entry_style))
                        k2+=1
                    elif (type(item) is Var) or (type(item) is oldVar):
                        if format_rule == "Temp":
                            if abs(item.u)<1e-2:
                                zw = format_number_unc(item.v,1e-2*2,14,no_prefix=True)
                            else:
                                zw = format_number_unc(item.v,item.u*2,14,no_prefix=True)
                        elif format_rule == "per_cent":
                            zw = format_number_unc(item.v*100,item.u*2*100,14,no_prefix=True)
                        elif format_rule == "ppm":
                            zw = format_number_unc(item.v*1e6,item.u*2*1e6,14,no_prefix=True)
                        elif format_rule == "scalar_ratio_one_over":
                            if item.v > 1:
                                zw1 = format_number_unc(item.v,item.u,14,no_prefix=True)
                                zw = list()
                                zw.append(zw1[0] + ":1")              
                                zw.append(format_number_unc(item.u*2/item.v*1e6,item.u*2/item.v*1e6,14,no_prefix=True)[0])
                            else:
                                zw1 = format_number_unc(1/item.v,2*item.u/(item.v**2),14,no_prefix=True)
                                zw = list()
                                zw.append("1:" + zw1[0])              
                                zw.append(format_number_unc(item.u*2/item.v*1e6,item.u*2/item.v*1e6,14,no_prefix=True)[0])
                        elif format_rule == "scalar_one_to_one":
                            zw1 = format_number_unc(item.v,item.u,14,no_prefix=False)
                            zw = list()
                            zw.append("{:.3f}".format(item.v))              
                            zw.append(zw1[1])
                        else:
                            if limited_value is None:
                                zw = format_number_unc(item.v,item.u*2,14)
                            else:
                                if item.v < limited_value[1][0]:
                                    zw = (limited_value[1][1],"-")
                                elif item.v > limited_value[2][0]:
                                    zw = (limited_value[2][1],"-")
                                else:
                                    zw = format_number_unc(item.v,item.u*2,14)
                            
                        row.append(Paragraph(zw[0]+units[k2],entry_style))
                        k2+=1
                        if len(org_headers[k1])>3:
                            if org_headers[k1][3] == c_rpt.exp_unc:
                                row.append(Paragraph(zw[1]+units[k2],entry_style))
                                k2+=1
                            elif org_headers[k1][3] == c_rpt.exp_unc_limited:
                                row.append(Paragraph(zw[1]+units[k2],entry_style))
                                k2+=1
                    elif headers[k2].find("Tol.\nused") >= 0:
                        if item is None:
                            row.append(Paragraph("n.a.",entry_style))
                        else:
                            row.append(Paragraph("{:.0f}%".format(item*100),entry_style))
                        k2+=1
                    elif item is None:
                        row.append(Paragraph("-",entry_style))
                    else:
                        if format_rule == "Temp":
                            row.append(Paragraph(format_number(item, no_prefix=True)+units[k2],entry_style))
                        elif format_rule == "per_cent":
                            row.append(Paragraph(format_number(item*100, no_prefix=True)+units[k2],entry_style))
                        elif format_rule == "ppm":
                            row.append(Paragraph(format_number(item*1e6, no_prefix=True)+units[k2],entry_style))
                        elif format_rule == "scalar_ratio_one_over":
                            if item>1:
                                row.append(Paragraph(format_number(item, no_prefix=True) + ":1" +units[k2],entry_style) )
                            else:
                                row.append(Paragraph("1:" + format_number(1/item, no_prefix=True)+units[k2],entry_style))
                        elif format_rule == "scalar_one_to_one":
                            row.append(Paragraph("{:.3f}".format(item),entry_style) )
                        else:
                            row.append(Paragraph(format_number(item)+units[k2],entry_style))
                        k2+=1
                        
                tabledata.append(row)

        else:
            if options["acc_spec"]:
                if hasattr(proc,"acc_result_list"):
                    datas_raw = proc.acc_result_list()
                else:
                    datas_raw = proc.result_list()
                    #raise Exception("accredited result list is missing")
            else:
                datas_raw = proc.result_list()

            multirow_data = False
            if type(datas_raw) is list:
                if type(datas_raw[0]) is list:
                    multirow_data = True
                else:
                    datas_raw = [datas_raw]
    
            print((proc.result_string()))
    
            for datas in datas_raw:
                row=list()
        
                    
                if not test_result is None:
                    datas.append(per_of_tol)
                    datas.append(test_result)
                
                for k1 in range(len(datas)):
                    item = datas[k1]
                    if type(item) == str:
                        row.append(Paragraph(item,entry_style))
                    elif type(item) == str:
                        row.append(Paragraph(item,entry_style))
                    else:
                        processed_exp_unc = False
                        if len(headers) > k1+1:
                            if headers[k1+1].find("Exp.\nUnc.")>=0:
                                zw = format_number_unc(item,datas[k1+1],14)
                                row.append(Paragraph(zw[0],entry_style))
                                row.append(Paragraph(zw[1],entry_style))
                                processed_exp_unc = True
                        if processed_exp_unc == False:
                            if headers[k1].find("Delta")==0:
                                if units[k1]=="dB":
                                    row.append(Paragraph("{:7.3f}".format(item),entry_style))
                                else:
                                    row.append(Paragraph(format_number(item,digits=2),entry_style))
                            elif headers[k1].find("Exp.\nUnc.")>=0:
                                if units[k1]=="dB":
                                    pass#row.append("{:7.3f}".format(item))
                                else:
                                    pass#row.append(format_number(item,digits=2))
                            elif headers[k1] == "Range":
                                row.append(Paragraph(format_number(item,digits=2),entry_style))
                            elif headers[k1].find("Tol.\nused") >= 0:
                                if item is None:
                                    row.append(Paragraph("n.a.",entry_style))
                                else:
                                    row.append(Paragraph("{:.0f}%".format(item*100),entry_style))
                            elif units[k1]=="dB" or units[k1]=="dBm":
                                row.append(Paragraph("{:7.3f}".format(item),entry_style))
                            else:
                                if type(item) is Var:
                                    row.append(Paragraph(format_number(item.v),entry_style))
                                else:
                                    row.append(Paragraph(format_number(item),entry_style))
                        
                tabledata.append(row)
    
    if tabledata:
        process_table(tabledata, has_units, newtype ,story)



                            
def process_section_start():
    pass

def process_table(tabledata, has_units, new_type, story):
    redlines = list()
    k1 = 0
    if tabledata[0][0].text.find("Range") == 0:
        delete_range_row = True
        for k1 in range((2 if has_units else 1),len(tabledata)):
            row = tabledata[k1]
            if row[0] != c_rpt.no_range_specified:
                delete_range_row = False

        if delete_range_row:
            new_tabledata = list()
            for row in tabledata:
                row = row[1:]
                new_tabledata.append(row)
            tabledata = new_tabledata
            
                
    k1 = 0            
    for row in tabledata:
        if row[-1] == "F" and k1 > 1:
            #redlines.append(('LINEBELOW', (0,k1), (-1,k1), 1, colors.red))
            redlines.append(('BACKGROUND', (0,k1), (-1,k1), colors.Color(1,0.95,0.95)))
        k1 += 1

    base_style = [('LINEABOVE', (0,0), (-1,0), 2, colors.green),
                    ('LINEABOVE', (0,1), (-1,-1), 0.25, colors.black),
                    ('LINEBELOW', (0,-1), (-1,-1), 2, colors.green),
                    ('ALIGN', (0,0), (-1,-1), 'RIGHT'),
                    ('BACKGROUND', (0,0), (-1,(1 if has_units and not new_type else 0)), colors.Color(0.9,0.9,0.9)),
                    ('VALIGN', (0,0), (-1,0), 'MIDDLE')]     
    
    list_style = TableStyle(base_style + redlines)
    col_count = len(tabledata[0])
    col_widths = list()
    for k1 in range(col_count):
        col_widths.append(170/float(col_count)*mm)
    tx = Table(tabledata, colWidths=col_widths, repeatRows=(2 if has_units and not new_type else 1),style = list_style)    
    tx.hAlign = 'LEFT'
       
    story.append(tx)
    
def correct_text(uncorrected_text):
    if uncorrected_text.strip() == (
"AC Volts Frequency Counter Sensitivity amd Trigger Level"    
    ):
        return (
"AC Volts Frequency Counter Sensitivity and Trigger Level"    
        )
    elif uncorrected_text.strip() == (
"DC Volts Frequency Counter Sensitivity amd Trigger Level"    
    ):
        return (
"DC Volts Frequency Counter Sensitivity and Trigger Level"    
        )
    else:
        return uncorrected_text
    