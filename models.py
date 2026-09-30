import uuid
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def generate_uuid():
    return str(uuid.uuid4())

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user') # 'admin' or 'user'
    credits = db.Column(db.Integer, nullable=False, default=5) # Newly registered users start with 5 credits
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    patients = db.relationship('Patient', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    capillaroscopies = db.relationship('Capillaroscopy', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.email} ({self.full_name}) - Credits: {self.credits}>'


class Patient(db.Model):
    __tablename__ = 'patients'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    patient_code = db.Column(db.String(50), unique=True, nullable=False, index=True) # Globally unique 7-digit code
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    capillaroscopies = db.relationship('Capillaroscopy', backref='patient', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Patient {self.name} ({self.patient_code})>'


class Capillaroscopy(db.Model):
    __tablename__ = 'capillaroscopies'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    patient_id = db.Column(db.String(36), db.ForeignKey('patients.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    capillaroscopy_date = db.Column(db.DateTime, default=datetime.utcnow)
    pattern = db.Column(db.String(50), default='N/A')
    ssc_classification = db.Column(db.String(50), default='non-SSc')
    quality_score = db.Column(db.Float, default=99.0)
    status = db.Column(db.String(20), default='completed')
    report_data_json = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    images = db.relationship('CapillaryImage', backref='session', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Capillaroscopy {self.title} - {self.status}>'


class CapillaryImage(db.Model):
    __tablename__ = 'capillary_images'
    
    id = db.Column(db.String(36), primary_key=True, default=generate_uuid)
    capillaroscopy_id = db.Column(db.String(36), db.ForeignKey('capillaroscopies.id'), nullable=False)
    finger = db.Column(db.String(10), nullable=False) # L2, L3, L4, L5, R2, R3, R4, R5
    slot = db.Column(db.String(10), nullable=True) # A, B, C
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CapillaryImage {self.finger} ({self.filename})>'
