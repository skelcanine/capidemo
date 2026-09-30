import io
import json
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def generate_capillaroscopy_pdf(capillaroscopy, patient, doctor, images):
    """
    Generates a professional PDF report for a capillaroscopy analysis session using ReportLab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#DC2626')
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#475569')
    )
    
    heading2_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    bold_body_style = ParagraphStyle(
        'BoldBodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E293B')
    )

    elements = []
    
    elements.append(Paragraph("Capillary Detection & Analysis Report", title_style))
    elements.append(Paragraph(f"Capillaroscopy Session: {capillaroscopy.title}", subtitle_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#DC2626'), spaceAfter=15))
    
    patient_name = patient.name if patient else "N/A"
    patient_code = patient.patient_code if patient else "N/A"
    date_str = capillaroscopy.capillaroscopy_date.strftime("%d %b %Y %H:%M UTC") if capillaroscopy.capillaroscopy_date else "N/A"
    doctor_info = f"{doctor.full_name} ({doctor.email})" if doctor else "N/A"
    
    meta_data = [
        [Paragraph("<b>Patient Name:</b>", body_style), Paragraph(patient_name, body_style),
         Paragraph("<b>Evaluator:</b>", body_style), Paragraph(doctor_info, body_style)],
        [Paragraph("<b>Patient Code:</b>", body_style), Paragraph(patient_code, body_style),
         Paragraph("<b>Date (UTC):</b>", body_style), Paragraph(date_str, body_style)],
        [Paragraph("<b>SSc Status:</b>", body_style), Paragraph(capillaroscopy.ssc_classification, bold_body_style),
         Paragraph("<b>Pattern:</b>", body_style), Paragraph(capillaroscopy.pattern, bold_body_style)]
    ]
    
    meta_table = Table(meta_data, colWidths=[1.3*inch, 2.2*inch, 1.3*inch, 2.2*inch])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#F1F5F9')),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    
    elements.append(meta_table)
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("Quantitative Capillary Metrics", heading2_style))
    
    report_json = {}
    if capillaroscopy.report_data_json:
        try:
            report_json = json.loads(capillaroscopy.report_data_json)
        except Exception:
            pass
            
    table_rows = report_json.get('table_data', [])
    
    summary_table_data = [
        [
            Paragraph("<b>Type</b>", bold_body_style),
            Paragraph("<b>Total</b>", bold_body_style),
            Paragraph("<b>%</b>", bold_body_style),
            Paragraph("<b>Density</b>", bold_body_style),
            Paragraph("<b>Apical Dia. (µm)</b>", bold_body_style),
            Paragraph("<b>Arterial Width</b>", bold_body_style),
            Paragraph("<b>Venous Width</b>", bold_body_style),
        ]
    ]
    
    for row in table_rows:
        apical = str(row.get('apical_diameter')) if row.get('apical_diameter') is not None else "—"
        arterial = str(row.get('arterial_limb_width')) if row.get('arterial_limb_width') is not None else "—"
        venous = str(row.get('venous_limb_width')) if row.get('venous_limb_width') is not None else "—"
        
        summary_table_data.append([
            Paragraph(str(row.get('type', '')), body_style),
            Paragraph(str(row.get('total', 0)), body_style),
            Paragraph(f"{row.get('percentage', 0)}%", body_style),
            Paragraph(str(row.get('density', 0)), body_style),
            Paragraph(apical, body_style),
            Paragraph(arterial, body_style),
            Paragraph(venous, body_style),
        ])
        
    sum_table = Table(summary_table_data, colWidths=[1.8*inch, 0.7*inch, 0.7*inch, 0.9*inch, 1.1*inch, 1.0*inch, 1.0*inch])
    sum_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F1F5F9')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (1,0), (-1,-1), 'CENTER'),
    ]))
    
    elements.append(sum_table)
    elements.append(Spacer(1, 15))
    
    narratives = report_json.get('narratives', {})
    elements.append(Paragraph("Clinical Narrative Summary", heading2_style))
    elements.append(Paragraph(f"<b>Capillary Density:</b> {narratives.get('capillary_density', 'N/A')}", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<b>Capillary Enlargement:</b> {narratives.get('capillary_enlargement', 'N/A')}", body_style))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph(f"<b>Capillary Deformities:</b> {narratives.get('capillary_deformities', 'N/A')}", body_style))
    elements.append(Spacer(1, 15))
    
    if images:
        elements.append(Paragraph("Analyzed Finger Images", heading2_style))
        img_table_data = []
        row_imgs = []
        for idx, img_obj in enumerate(images):
            abs_path = img_obj.file_path
            if os.path.exists(abs_path):
                try:
                    rl_img = RLImage(abs_path, width=2.0*inch, height=1.5*inch)
                    cell = [Paragraph(f"<b>Finger {img_obj.finger}</b> ({img_obj.filename})", body_style), rl_img]
                    row_imgs.append(cell)
                    if len(row_imgs) == 3 or idx == len(images) - 1:
                        img_table_data.append(row_imgs)
                        row_imgs = []
                except Exception:
                    pass
        if img_table_data:
            for r in img_table_data:
                cell_flowables = []
                for cell in r:
                    cell_flowables.append(cell[0])
                    cell_flowables.append(cell[1])
                    cell_flowables.append(Spacer(1, 8))
                elements.extend(cell_flowables)
    
    elements.append(Spacer(1, 20))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#CBD5E1'), spaceAfter=10))
    elements.append(Paragraph("Automated Capillaroscopy Classification System — Verified Medical Report", ParagraphStyle('Footer', parent=styles['Normal'], fontName='Helvetica-Oblique', fontSize=8, textColor=colors.HexColor('#64748B'), alignment=1)))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer
