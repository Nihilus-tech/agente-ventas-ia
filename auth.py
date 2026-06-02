from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required
from database import db, Usuario

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form.get('correo')
        contrasena = request.form.get('contrasena')
        usuario = Usuario.query.filter_by(correo=correo).first()
        if usuario and usuario.check_password(contrasena):
            login_user(usuario)
            return redirect(url_for('index'))
        flash('Correo o contraseña incorrectos')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))