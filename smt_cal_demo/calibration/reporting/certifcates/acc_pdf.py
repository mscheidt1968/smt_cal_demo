# -*- coding: utf-8 -*-
"""
Created on Thu Nov 08 12:37:05 2012

@author: Scheidt

"""
import datetime as dat

import os

from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, PageBreak, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

import smt_cal_demo.utilities.easygui as eg
import smt_cal_demo.utilities.files as n_files
from smt_cal_demo.calibration.database.support import session, Calibration, Certificate, db_id_offset
import smt_cal_demo.calibration.reporting.certifcates.acc_first_page as n_acc_first_page
import smt_cal_demo.calibration.reporting.certifcates.report_calibration_v01 as n_report_calibration_v01
import smt_cal_demo.calibration.reporting.certifcates.make_label as n_make_label


c_ui_title = "Certicate creation"

class NumberedCanvas(canvas.Canvas):
    
    report_id = ""    
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.date_created = dat.datetime.now()

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        """add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_number(self, page_count):
        self.setFont("Helvetica", 8)
        footer = ("Page {:d} of {:d}".format(self._pageNumber, page_count) + 
        " Report: " + self.report_id + 
        " Created: " + self.date_created.strftime("%d.%m.%Y %H:%M"))
        
        self.drawCentredString(100*mm, 15*mm,footer)           
        footer = "Company Name, Street, Location, Web Site, Phone"
        self.drawCentredString(100*mm, 10*mm,footer)           

def create_certificate(calibration,sort_ids=list(),cur_proc_instrs= dict(), specs = dict(),options = dict(acc = False)):
    # initialize data structure and define file name

    #print "create certificate started"
    target_file = ""
    date_today = dat.datetime.now()
    day_id = 0
    report_id = ""
    filename_fixed = False
    while filename_fixed == False:
        report_id = date_today.strftime("%y%m%d") + "_C{:02d}_{:03d}".format(int(db_id_offset.value), day_id)
        target_file = os.path.join(n_files.firma_path,"Reports",report_id + " Report.pdf")
        if os.path.isfile(target_file):
            day_id += 1
        else:
            filename_fixed = True
            
        if day_id > 999:
            raise SystemError("More than 1000 reports created?")

    
    remarks = ""
    if options["database"] ==True:
        # check if certificate was already published
        ids_of_valid_certificates = list()            
        if len(calibration.certificates)>0:
            # there exists a certificate already ask for reason
            for item in calibration.certificates:
                if item.validity == True:
                    if remarks == "":
                        remarks = "Replaces certifcate(s) with ID: "
                    else:
                        remarks += " , "
                    remarks += item.id_m
                    ids_of_valid_certificates.append(item.id)
            msg = "Please enter reason for new certificate."
            msg += "This comment will be stored with last certifcate dataset"
            unvalidity_reason = eg.enterbox(msg,c_ui_title)            
            if unvalidity_reason == "" or unvalidity_reason is None:
                return
    #print "trying to open enterbox"

    values = eg.multenterbox("Please add following information",c_ui_title,("Remarks","Location"),("none","Company Name, Location"))
    if remarks != "" and values[0] != "":    
        remarks += "," + values[0]
    elif values[0] != "":
        remarks = values[0] 
        
    location_of_calibration = values[1]
    
    NumberedCanvas.report_id = report_id
    
    doc = SimpleDocTemplate(target_file, pagesize=A4,
                            leftMargin = 20*mm,
                            rightMargin = 20*mm,
                            topMargin = 10*mm,
                            bottomMargin = 20*mm
                            )
    
    style_sheet = getSampleStyleSheet()
    
    story = list()
    infostyle=ParagraphStyle("Info",style_sheet["BodyText"])
    infostyle.fontSize = 6
    infostyle.spaceBefore = 0
    infostyle.spaceAfter = 0
    infostyle.leading = 8
    style_sheet.add(infostyle)

    n_acc_first_page.first_page(story, style_sheet, remarks, report_id, location_of_calibration, calibration, options)
    
    story.append(PageBreak())

    n_report_calibration_v01.create_report(story, style_sheet, calibration, sort_ids,cur_proc_instrs, specs, options)

    story.append(Paragraph(
        "<br/><b>Measurements accomplished by:</b><br/>{:s}".format(calibration.operator),style_sheet["BodyText"]))                        

    story.append(Paragraph(
        "<br/><b>Measurements beyond current accreditation are marked with (*)</b><br/>",style_sheet["BodyText"]))                        
    
    zw=list(cur_proc_instrs.items())[0][1]             
    if "spec" in zw:
        story.append(Paragraph(
            "<br/><b>Specification used:</b><br/>{:s}".format(zw["spec"]),style_sheet["BodyText"]))                        
    elif "spec_ref" in zw:
        story.append(Paragraph(
            "<br/><b>Specification used:</b><br/>{:s}".format(zw["spec_ref"]),style_sheet["BodyText"]))                        
        
    story.append(Paragraph(
        "<br/><b>Abreviations:</b><br/>",style_sheet["BodyText"]))                        
    story.append(Paragraph(
        "<b>Exp. Unc.:  </b>Expanded uncertainty",style_sheet["BodyText"]))                        
    story.append(Paragraph(
        "<b>P    :  </b>Passed. Specification is met for this test.",style_sheet["BodyText"]))                        
    story.append(Paragraph(
        "<b>P<super>C</super>:  </b>It is not possible to state compliance using a 95 % coverage probability for the expanded uncertainty although the measurement result is below the limit. (see ILAC G8:03/2009)",style_sheet["BodyText"]))                        
    story.append(Paragraph(
        "<b>F<super>C</super>:  </b>It is not possible to state non compliance using a 95 % coverage probability for the expanded uncertainty although the measurement result is above the limit. (see ILAC G8:03/2009)",style_sheet["BodyText"]))                        
#    story.append(Paragraph(
#        "<b>M    :  </b>Marginal. Specification is met for this test. More than 80% of tolerance is used.",style_sheet["BodyText"]))                        
    story.append(Paragraph(
        "<b>F    :  </b>Failed. Specification is not met for this test.",style_sheet["BodyText"]))                        

                    

    # create doc now
    doc.build(story, canvasmaker=NumberedCanvas)

    if options["database"] ==True:
        curr_cert = Certificate()
        curr_cert.print_date = dat.datetime.now()
        curr_cert.id_m = report_id
        comment = ""
        answer = eg.enterbox("Would you add a comment to the certificate dataset")
        if not answer is None:
            comment = answer

        if len(ids_of_valid_certificates) > 0:
            for item in calibration.certificates:
                if item.validity == True:
                    item.validity = False
                    item.unvalidity_comment = unvalidity_reason
                    session.add(item)
                    comment += "\nReplaces certificate filename: " + item.id_m
        curr_cert.validity =True
        curr_cert.unvalidity_comment = ""
        curr_cert.calibration = calibration
        session.add(curr_cert)
        session.commit()

        if options["safety"]:
            n_make_label.make_label(calibration.instrument.id, calibration.instrument.serial_number, report_id, calibration.start_date, acc_logo=False, safety=True)
        else:
            n_make_label.make_label(calibration.instrument.id, calibration.instrument.serial_number, report_id, calibration.start_date, acc_logo=True, safety=False)


    os.startfile(target_file)    
    
    
if __name__== "__main__":
    cal = session.query(Calibration).filter(Calibration.id==4295103969).one()
    #cal = session.query(Calibration).filter(Calibration.id==4294981793L).one()

    create_certificate(cal,options=dict(database=False, acc=True))
    