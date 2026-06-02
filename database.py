from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Usuario(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), unique=True, nullable=False)
    contrasena = db.Column(db.String(200), nullable=False, default='')
    numero_whatsapp = db.Column(db.String(20), unique=True, nullable=True)
    activo = db.Column(db.Boolean, default=True)

    def set_password(self, contrasena):
        self.contrasena = generate_password_hash(str(contrasena))

    def check_password(self, contrasena):
        if not self.contrasena:
            return False
        return check_password_hash(self.contrasena, str(contrasena))


from datetime import datetime

class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=True)
    consulta = db.Column(db.Text, nullable=False)
    respuesta = db.Column(db.Text, nullable=False)
    tiempo_ms = db.Column(db.Integer)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    canal = db.Column(db.String(20), default='web')
    tipo_prospecto = db.Column(db.String(50), default='general')