from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db, User
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('capillaroscopy.dashboard'))
        
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        remember = True if request.form.get('remember') else False
        
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            flash('Invalid email address or password.', 'danger')
            return render_template('auth/login.html')
            
        login_user(user, remember=remember)
        next_page = request.args.get('next')
        
        if user.is_admin:
            return redirect(next_page or url_for('admin.dashboard'))
        return redirect(next_page or url_for('capillaroscopy.dashboard'))
        
    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('capillaroscopy.dashboard'))
        
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not full_name or not email or not password:
            flash('Full Name, Email Address, and Password are required.', 'danger')
            return render_template('auth/register.html')
            
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('auth/register.html')
            
        if User.query.filter_by(email=email).first():
            flash('This email address is already registered.', 'danger')
            return render_template('auth/register.html')
            
        new_user = User(
            full_name=full_name,
            email=email,
            role='user', # Role is user
            credits=Config.NEW_USER_CREDITS
        )
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash(f'Registration successful! You have received {Config.NEW_USER_CREDITS} initial credits. Please log in with your email.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))
