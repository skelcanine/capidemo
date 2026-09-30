from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User, Patient, Capillaroscopy, CapillaryImage
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('capillaroscopy.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('')
@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    users = User.query.order_by(User.created_at.desc()).all()
    
    user_stats = []
    total_images_system = 0
    total_patients_system = Patient.query.count()
    total_sessions_system = Capillaroscopy.query.count()
    
    for u in users:
        patient_count = u.patients.count()
        session_count = u.capillaroscopies.count()
        
        image_count = db.session.query(CapillaryImage)\
            .join(Capillaroscopy, CapillaryImage.capillaroscopy_id == Capillaroscopy.id)\
            .filter(Capillaroscopy.user_id == u.id).count()
            
        total_images_system += image_count
        
        user_stats.append({
            'user': u,
            'patient_count': patient_count,
            'session_count': session_count,
            'image_count': image_count,
            'credits': u.credits
        })
        
    return render_template(
        'admin/dashboard.html',
        user_stats=user_stats,
        total_users=len(users),
        total_patients=total_patients_system,
        total_sessions=total_sessions_system,
        total_images=total_images_system
    )

@admin_bp.route('/give_credit', methods=['POST'])
@login_required
@admin_required
def give_credit():
    user_id = request.form.get('user_id', type=str)
    credit_amount = request.form.get('credit_amount', type=int)
    
    if not user_id or credit_amount is None or credit_amount <= 0:
        flash('Invalid user or credit amount.', 'warning')
        return redirect(url_for('admin.dashboard'))
        
    target_user = User.query.get(user_id)
    if not target_user:
        flash('User not found.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    target_user.credits += credit_amount
    db.session.commit()
    
    flash(f'Successfully added {credit_amount} credits to {target_user.full_name} ({target_user.email}). New balance: {target_user.credits} credits.', 'success')
    return redirect(url_for('admin.dashboard'))
