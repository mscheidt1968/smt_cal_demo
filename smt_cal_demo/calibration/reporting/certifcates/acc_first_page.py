# -*- coding: utf-8 -*-
"""
Created on Sun Jan 06 08:58:52 2013

@author: Scheidt
"""
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.platypus import Image, Paragraph, Table, Spacer
from reportlab.lib.styles import ParagraphStyle
import os

def to_html(s):
    return s.replace("&","&amp;")

def first_page(story, style_sheet, remarks, report_id, location_of_calibration, calibration, options):

    path = os.path.abspath(__file__)
    dir_path = os.path.dirname(path)

    img0 = Image(os.path.join(dir_path,'logo.png'))
    img0.drawWidth = 20*mm*img0.drawWidth / img0.drawHeight 
    img0.drawHeight = 20*mm
    
    
    p0 = Paragraph('''
                   Von der *** Akkreditierungsstelle akkreditierte Kalibrierstelle<br/>
                   Laboratoire d'étalonnage accrédité par le Service d'Accréditation Suisse<br/>
                   Calibration Laboratory accredited by the Swiss Accreditation Service<br/>
                   <br/>
                   <b>The *** is one of the signatories to the EA
                   Multilateral Agreement for the recognition of calibration certificates</b>''',
                   style_sheet["Info"])
    
    
    img1 = Image(os.path.join(dir_path,'logoACC.png'))
    img1.drawWidth = 35*mm*img1.drawWidth / img1.drawHeight 
    img1.drawHeight = 35*mm
    
    p1 = Paragraph('''
        Logo und Bezeichnung der Akkreditierungsstelle''',
        style_sheet["BodyText"])
    
    if options["acc"] == True:
        data= [[[img0,Spacer(50*mm,2*mm),p0], img1]]
         
        t0=Table(data,style=[('VALIGN',(1,0),(1,0),'TOP')],colWidths=[95*mm,75*mm])
        story.append(t0)
        story.append(Spacer(160*mm,5*mm))
    else:  
        img0.hAlign = "RIGHT"
        story.append(img0)
        story.append(Spacer(100*mm,10*mm))
    
    p20 = Paragraph('''<p align="left"><font size="6">Zertifikat Id <br/>ID du certifcat<br/>Certificate ID</font></p>''',
                   style_sheet["Info"])
    
    p21 = Paragraph('''Kunde Id <br/>Client<br/>Client''',
                   style_sheet["Info"])

    p22 = Paragraph('''Projekt Id <br/>ID de Project<br/>Project ID''',
                   style_sheet["Info"])
    
    p23 = Paragraph('''Kalibrierungs ID<br/>ID d' étalonnage<br/>Calibration ID''',
                   style_sheet["Info"])
    
    sample_id = report_id
    v20 = Paragraph(to_html(sample_id),
                   style_sheet["BodyText"])

    if calibration.instrument.customer.name is None:
        v21 = Paragraph('''Company''',
                       style_sheet["BodyText"])
    else:
        v21 = Paragraph(to_html(calibration.instrument.customer.name) +
                                "<br/>" + to_html(calibration.instrument.customer.addresses) ,style_sheet["BodyText"])

    if calibration.project_id_m is None:
        v22 = Paragraph('''no project''',
                       style_sheet["BodyText"])
    else:
        v22 = Paragraph(to_html(calibration.project_id_m) ,style_sheet["BodyText"])
    
    
    v23 = Paragraph(str(calibration.id),
                   style_sheet["BodyText"])
    
    t1=Table([[p20,v20,p22,v22],[p21,v21,p23,v23]],style=[('LEFTPADDING',(0,0),(3,1),0),
                                                    ('ALIGN',(0,0),(3,1),'LEFT'),
                                                 ('VALIGN',(1,0),(1,1),'MIDDLE'),
                                                ('VALIGN',(3,0),(3,1),'MIDDLE')],
                colWidths=[25*mm,90*mm,25*mm,30*mm],
                hAlign = 'LEFT'                              
                )
    
    story.append(t1)
    story.append(Spacer(160*mm,3*mm))
    
    lstyle = ParagraphStyle(style_sheet["Heading2"])
    lstyle.alignment=1
    if options["acc"] == True:
        p10 = Paragraph('''ACC''',lstyle)
    else:
        p10 = Paragraph('''''',lstyle)
    
    if options["safety"] == True:
        p11 = Paragraph('''SICHERHEITSPRÜFUNG NACH DIN VDE 0701-0702:2008-06<br/>
                           CONTROLE DE SECURITY SELON DIN VDE 0701-0702:2008-06<br/>
                           SAFETY CHECK ACCORDING DIN VDE 0701-0702:2008-06''',
                           lstyle)
    else:
        p11 = Paragraph('''KALIBRIERZERTIFIKAT<br/>
                           CERTIFICAT D´ETALONNAGE<br/>
                           CALIBRATION CERTIFICATE''',
                           lstyle)
    t2 = Table([[p10,p11,p10]],colWidths=[20*mm,130*mm,20*mm]
                                ,style=[('VALIGN',(0,0),(2,0),"MIDDLE"),
                                        ('BACKGROUND',(0,0),(-1,-1),colors.Color(0.9,1,0.9))])
    story.append(t2)
    story.append(Spacer(160*mm,3*mm))
    
    p30 = Paragraph('''Gegenstand<br/>
                        Objet<br/>
                        Object''',
                   style_sheet["Info"])
    
    p31 = Paragraph('''Hersteller<br/>
                        Fabricant<br/>
                        Manufacturer''',
                   style_sheet["Info"])
    
    p32 = Paragraph('''Typ<br/>
                        Type<br/>
                        Type''',
                   style_sheet["Info"])
    
    p33 = Paragraph('''Serien-Nr.<br/>
                        No de serie<br/>
                        Serial number''',
                   style_sheet["Info"])
    
    p34 = Paragraph('''Bemerkungen<br/>
                        Remarque<br/>
                        Remarks''',
                   style_sheet["Info"])
    
    p35 = Paragraph('''Datum / Ort der Kalibrierung<br/>
                        Date / locakité de l'étalonnage<br/>
                        Date / lcoation of calibration''',
                   style_sheet["Info"])
    
    v30 = Paragraph(to_html(calibration.instrument.object_description),style_sheet["BodyText"])
    
    v31 = Paragraph(to_html(calibration.instrument.manufacturer),style_sheet["BodyText"])
    
    v32 = Paragraph(to_html(calibration.instrument.model),style_sheet["BodyText"])
    
    v33 = Paragraph(to_html(calibration.instrument.serial_number),style_sheet["BodyText"])
    
    v34 = Paragraph(to_html(remarks),style_sheet["BodyText"])

    v35 = Paragraph(calibration.start_date.strftime("%d %b %Y") + " / " +
                    to_html(location_of_calibration),
                   style_sheet["BodyText"])
    
    t3 = Table([[p30,v30],[p31,v31],[p32,v32],[p33,v33],[p34,v34],[p35,v35]],
                colWidths = [35*mm, 135*mm],
                style=[('VALIGN',(1,0),(1,-1),"MIDDLE")])
    
    
    story.append(t3)
    story.append(Spacer(180*mm,3*mm))
    
    if options["safety"] == True:
        p41 = Paragraph('''Messresultate, Messunsicherheiten mit Vertrauensbereich und Messverfahren sind auf den folgenden Seiten aufgeführt und sind Teil des Zertifikates.<br/>
                        Les résultats, les incertitudes avec le niveau de confiance et les méthodes de mesure sont donnés aux pages suivantes et font partie du certificat.<br/>
                        The measurements, the uncertainties with confidence probability and calibration methods are given on the following pages and are part of the certificate
                        ''',
                       style_sheet["Info"])
    
        p42 = Paragraph('''Zertifikat darf ohne die schriftliche Zustimmung des Laboratoriums nicht auszugsweise vervielfältigt werden.<br/>
                        Ce certificat ne doit pas être reproduit, sinon en entier, sans l'autorisation écrite du laboratoire.<br/>
                        This certificate shall not be reproduced except in full, without written approval of the laboratory.
                        ''',
                       style_sheet["Info"])
    
        p43 = Paragraph('''Datenaufbewahrungsdauer: 5 Jahre<br/>
                        Le délai de conservation de données: 5 ans<br/>
                        Record retention period: 5 years
                        ''',
                       style_sheet["Info"])
        
        t4 = Table([[p41],[p42],[p43]], colWidths = [170*mm])
        
        story.append(t4)
        story.append(Spacer(160*mm,5*mm))
    else:
        p40 = Paragraph('''<b>
                        Dieses Kalibrierzertifikat dokumentiert die Rückverfolgbarkeit auf nationale Normale zur Darstellung der physikalischen Einheiten (SI).<br/>
                        Ce certificat d’étalonnage confirme le raccordement aux étalons nationaux qui matérialisent les grandeurs physiques (SI).<br/>
                        This calibration certificate documents the traceability to national standards, which realize the physical units of measurements (SI).
                        </b>''',
                       style_sheet["Info"])
        
        p41 = Paragraph('''Messresultate, Messunsicherheiten mit Vertrauensbereich und Messverfahren sind auf den folgenden Seiten aufgeführt und sind Teil des Zertifikates.<br/>
                        Les résultats, les incertitudes avec le niveau de confiance et les méthodes de mesure sont donnés aux pages suivantes et font partie du certificat.<br/>
                        The measurements, the uncertainties with confidence probability and calibration methods are given on the following pages and are part of the certificate
                        ''',
                       style_sheet["Info"])
    
        p42 = Paragraph('''Dieses Kalibrierzertifikat darf ohne die schriftliche Zustimmung des Laboratoriums nicht auszugsweise vervielfältigt werden.<br/>
                        Ce certificat d'étalonnage ne doit pas être reproduit, sinon en entier, sans l'autorisation écrite du laboratoire.<br/>
                        This calibration certificate shall not be reproduced except in full, without written approval of the laboratory.
                        ''',
                       style_sheet["Info"])
    
        p43 = Paragraph('''Datenaufbewahrungsdauer: 5 Jahre<br/>
                        Le délai de conservation de données: 5 ans<br/>
                        Record retention period: 5 years
                        ''',
                       style_sheet["Info"])
        
        t4 = Table([[p40],[p41],[p42],[p43]], colWidths = [170*mm])
        
        story.append(t4)
        story.append(Spacer(160*mm,5*mm))
    
    p50 = Paragraph('''Datum / Date/ Date</p>''',
                   style_sheet["Info"])
    
    
    p51 = Paragraph('''Leiter der Kalibrierstelle/ Chef du laboratoire d'étalonnage/ 
                        Head of the calibration laboratory''',
                   style_sheet["Info"])
    
    
    t5 = Table([[p50,p51],["","\n\nHead Laboratory"]],
               colWidths = [85*mm, 85*mm],
               style=[('ALIGN',(0,0),(0,-1),"RIGHT"),
                      ('ALIGN',(1,0),(1,-1),"LEFT"),
                      ('VALIGN',(0,0),(-1,0),"TOP"),
                      ('VALIGN',(0,1),(-1,1),"BOTTOM")  
               ])
    
    story.append(t5)
    story.append(Spacer(160*mm,2*mm))
    
    
    p70 = Paragraph('''
                        <b>E</b><br/>
                        The reported expanded uncertainty of measurement is stated as the standard uncertainty of measurement multiplied
                        by the coverage factor k = 2, which for a normal distribution corresponds to a coverage probability of approximately
                        95%.<br/>
                        <b>F</b><br/>
                        L'incertitude de mesure élargie donnée est l'incertitude-type sur le résultat de la mesure multipliée par le facteur
                        d'élargissement k = 2 ce qui, pour une distribution gaussienne, correspond à un niveau de confiance d'environ 95%.<br/>
                        <b>D</b><br/>
                        Die angegebene erweiterte Messunsicherheit ist die Standardunsicherheit der Messung multipliziert mit einem
                        Erweiterungsfaktor k = 2, was bei einer Normalverteilung einem Vertrauensniveau von etwa 95% entspricht.<br/>
                        <b>I</b><br/>
                        L'incertezza di misura riportata è la deviazione standard della misura moltiplicata con un fattore di copertura k = 2,
                        che, per una distribuzione gaussiana, corrisponde ad un fattore di confidenza di circa 95%.
                        ''',    style_sheet["Info"])
    
    story.append(p70)
    
    