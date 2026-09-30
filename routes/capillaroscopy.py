import os
import json
import random
from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file, current_app
from flask_login import login_required, current_user
from models import db, User, Patient, Capillaroscopy, CapillaryImage
from utils.security import allowed_file, validate_image_header, sanitize_user_filename
from utils.mock_analyzer import get_mock_report
from utils.pdf_generator import generate_capillaroscopy_pdf

capillaroscopy_bp = Blueprint('capillaroscopy', __name__)

FINGERS = ['L2', 'L3', 'L4', 'L5', 'R2', 'R3', 'R4', 'R5']
SLOTS = ['A', 'B', 'C']

def generate_unique_7digit_patient_code():
    while True:
        num = random.randint(1000000, 9999999)
        code = f"P-{num}"
        existing = Patient.query.filter_by(patient_code=code).first()
        if not existing:
            return code

@capillaroscopy_bp.route('/')
@capillaroscopy_bp.route('/dashboard')
@login_required
def dashboard():
    patient_id = request.args.get('patient_id', type=str)
    
    if current_user.is_admin:
        query = Capillaroscopy.query
        patients = Patient.query.order_by(Patient.name.asc()).all()
    else:
        query = Capillaroscopy.query.filter_by(user_id=current_user.id)
        patients = Patient.query.filter_by(user_id=current_user.id).order_by(Patient.name.asc()).all()
        
    if patient_id:
        query = query.filter_by(patient_id=patient_id)
        
    sessions = query.order_by(Capillaroscopy.created_at.desc()).all()
    
    return render_template(
        'capillaroscopy/list.html',
        sessions=sessions,
        patients=patients,
        selected_patient_id=patient_id
    )


@capillaroscopy_bp.route('/patients', methods=['GET', 'POST'])
@login_required
def patients_list():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        patient_code = request.form.get('patient_code', '').strip()
        notes = request.form.get('notes', '').strip()
        
        if not name:
            flash('Patient Name is required.', 'warning')
        else:
            if not patient_code:
                patient_code = generate_unique_7digit_patient_code()
            else:
                if not patient_code.startswith('P-'):
                    patient_code = f"P-{patient_code}"
                existing = Patient.query.filter_by(patient_code=patient_code).first()
                if existing:
                    flash(f'Patient code "{patient_code}" is already in use in the system. Generated a new unique code.', 'info')
                    patient_code = generate_unique_7digit_patient_code()
                    
            new_p = Patient(
                user_id=current_user.id,
                name=name,
                patient_code=patient_code,
                notes=notes
            )
            db.session.add(new_p)
            db.session.commit()
            flash(f'Patient "{name}" ({patient_code}) created successfully.', 'success')
            return redirect(url_for('capillaroscopy.patients_list'))
                
    if current_user.is_admin:
        patients = Patient.query.order_by(Patient.created_at.desc()).all()
    else:
        patients = Patient.query.filter_by(user_id=current_user.id).order_by(Patient.created_at.desc()).all()
        
    return render_template('patients/list.html', patients=patients)


@capillaroscopy_bp.route('/patients/<string:patient_id>/edit_notes', methods=['POST'])
@login_required
def edit_patient_notes(patient_id):
    if current_user.is_admin:
        patient = Patient.query.get_or_404(patient_id)
    else:
        patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first_or_404()
        
    new_notes = request.form.get('notes', '').strip()
    patient.notes = new_notes
    db.session.commit()
    
    flash(f'Clinical notes for patient "{patient.name}" updated successfully.', 'success')
    return redirect(url_for('capillaroscopy.patients_list'))


@capillaroscopy_bp.route('/capillaroscopy/create')
@login_required
def create():
    if current_user.is_admin:
        patients = Patient.query.order_by(Patient.name.asc()).all()
    else:
        patients = Patient.query.filter_by(user_id=current_user.id).order_by(Patient.name.asc()).all()
        
    return render_template('capillaroscopy/upload.html', patients=patients, fingers=FINGERS)


@capillaroscopy_bp.route('/capillaroscopy/analyze', methods=['POST'])
@login_required
def analyze():
    db.session.refresh(current_user)
    if current_user.credits < 1:
        flash('Insufficient credits! You need at least 1 credit to run an analysis. Please contact your administrator.', 'danger')
        return redirect(url_for('capillaroscopy.dashboard'))
        
    patient_id = request.form.get('patient_id', type=str)
    new_patient_name = request.form.get('new_patient_name', '').strip()
    
    if not patient_id and not new_patient_name:
        flash('Patient selection or new patient name is strictly required to perform an analysis.', 'warning')
        return redirect(url_for('capillaroscopy.create'))
        
    patient = None
    if patient_id:
        if current_user.is_admin:
            patient = Patient.query.get(patient_id)
        else:
            patient = Patient.query.filter_by(id=patient_id, user_id=current_user.id).first()
            
    if not patient and new_patient_name:
        code = generate_unique_7digit_patient_code()
        patient = Patient(user_id=current_user.id, name=new_patient_name, patient_code=code)
        db.session.add(patient)
        db.session.flush()
        
    if not patient:
        flash('Invalid patient selection.', 'danger')
        return redirect(url_for('capillaroscopy.create'))
        
    session_title = f"{patient.name} - Capillaroscopy ({datetime.utcnow().strftime('%d %b %Y %H:%M UTC')})"
    
    timestamp_folder = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    user_sanitized = sanitize_user_filename(current_user.id)
    patient_sanitized = sanitize_user_filename(patient.patient_code)
    
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], user_sanitized, patient_sanitized, timestamp_folder)
    os.makedirs(upload_dir, exist_ok=True)
    
    mock_data = get_mock_report()
    cap_session = Capillaroscopy(
        user_id=current_user.id,
        patient_id=patient.id,
        title=session_title,
        pattern=mock_data.get('suggested_pattern', 'Normal'),
        ssc_classification=mock_data.get('ssc_classification', 'non-SSc'),
        quality_score=mock_data.get('quality_score', 99.0),
        status='completed',
        report_data_json=json.dumps(mock_data)
    )
    db.session.add(cap_session)
    db.session.flush()
    
    saved_images_count = 0
    
    for finger in FINGERS:
        # Check files per slot (A, B, C) or general upload
        finger_files_to_save = {} # slot -> FileStorage
        
        for slot in SLOTS:
            files_slot = request.files.getlist(f'images_{finger}_{slot}')
            if files_slot and files_slot[0] and files_slot[0].filename:
                finger_files_to_save[slot] = files_slot[0]
                
        # Check general PLUS input or legacy images input
        files_plus = request.files.getlist(f'images_{finger}_PLUS') + request.files.getlist(f'images_{finger}')
        for file in files_plus:
            if file and file.filename:
                # Find first unoccupied slot A, B, or C
                for s in SLOTS:
                    if s not in finger_files_to_save:
                        finger_files_to_save[s] = file
                        break
                        
        # Save up to 3 slot files (A, B, C) to disk & DB
        for slot_name in SLOTS:
            if slot_name in finger_files_to_save:
                file = finger_files_to_save[slot_name]
                filename = sanitize_user_filename(file.filename)
                
                if not allowed_file(filename):
                    flash(f'File "{filename}" rejected: Only .jpg, .jpeg, and .png images are allowed.', 'danger')
                    continue
                    
                if not validate_image_header(file.stream):
                    flash(f'File "{filename}" rejected: File content header is not a valid image.', 'danger')
                    continue
                    
                save_filename = f"{finger}_{slot_name}_{filename}"
                save_path = os.path.join(upload_dir, save_filename)
                
                file.save(save_path)
                
                img_record = CapillaryImage(
                    capillaroscopy_id=cap_session.id,
                    finger=finger,
                    slot=slot_name,
                    filename=filename,
                    file_path=save_path
                )
                db.session.add(img_record)
                saved_images_count += 1
                
    if saved_images_count == 0:
        flash('Warning: No valid finger images were uploaded for analysis.', 'warning')

    current_user.credits -= 1
    db.session.commit()
    
    flash(f'Analysis for patient "{patient.name}" completed successfully! 1 credit deducted. Remaining credits: {current_user.credits}.', 'success')
    return redirect(url_for('capillaroscopy.detail', session_id=cap_session.id))


@capillaroscopy_bp.route('/capillaroscopy/<string:session_id>')
@login_required
def detail(session_id):
    if current_user.is_admin:
        cap_session = Capillaroscopy.query.get_or_404(session_id)
    else:
        cap_session = Capillaroscopy.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
        
    images = CapillaryImage.query.filter_by(capillaroscopy_id=cap_session.id).all()
    
    finger_images = {f: [] for f in FINGERS}
    finger_slots_uploaded = {f: set() for f in FINGERS}
    
    for img in images:
        if img.finger in finger_images:
            finger_images[img.finger].append(img)
            finger_slots_uploaded[img.finger].add(img.slot)
            
    report_data = {}
    if cap_session.report_data_json:
        try:
            report_data = json.loads(cap_session.report_data_json)
        except Exception:
            pass
            
    return render_template(
        'capillaroscopy/detail.html',
        session=cap_session,
        finger_images=finger_images,
        finger_slots_uploaded=finger_slots_uploaded,
        report_data=report_data,
        fingers=FINGERS
    )


@capillaroscopy_bp.route('/capillaroscopy/<string:session_id>/download_report')
@login_required
def download_report(session_id):
    if current_user.is_admin:
        cap_session = Capillaroscopy.query.get_or_404(session_id)
    else:
        cap_session = Capillaroscopy.query.filter_by(id=session_id, user_id=current_user.id).first_or_404()
        
    images = CapillaryImage.query.filter_by(capillaroscopy_id=cap_session.id).all()
    patient = cap_session.patient
    evaluator_user = cap_session.user
    
    pdf_buffer = generate_capillaroscopy_pdf(cap_session, patient, evaluator_user, images)
    
    filename = f"Capillaroscopy_Report_{patient.patient_code if patient else 'Patient'}_{cap_session.id[:8]}.pdf"
    return send_file(
        pdf_buffer,
        as_attachment=True,
        download_name=filename,
        mimetype='application/pdf'
    )


@capillaroscopy_bp.route('/uploads/<string:image_id>')
@login_required
def serve_upload(image_id):
    img = CapillaryImage.query.get_or_404(image_id)
    session = Capillaroscopy.query.get_or_404(img.capillaroscopy_id)
    
    if session.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access to image file.', 'danger')
        return redirect(url_for('capillaroscopy.dashboard'))
        
    return send_file(img.file_path)
