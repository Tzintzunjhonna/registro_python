from flask import Flask, render_template, request, redirect, url_for, flash, g 
from flask_mysqldb import MySQL
from flask import session
import time 
from datetime import date, datetime
 

app = Flask(__name__)

#--- ---- ------ ------ ------- ------- -------- --------- -------- -------- -------

#Conexion MySQL
mysql = MySQL(app)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'python'

#--- ---- ------ ------ ------- ------- -------- --------- -------- -------- -------

#Encriptaci'on de datos


app.secret_key ='mysecretkey'


#--- ---- ------ ------ ------- ------- -------- --------- -------- -------- -------
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.route('/')
def inicio():
    return render_template('inicio.html')

@app.route('/registro')
def registro():
    if g.user:
        flash('¡Cierra sesión para registar otro usuario!')
        return render_template('sesionbloqueada.html')
    else:
        return render_template('registro.html')

@app.route('/administrador')
def administrador():
    if not g.user:
        return render_template('peligro.html')
    elif session['user'] == 'administrador':
        return render_template('administrador.html')
    else:
        return render_template('sesionbloqueada.html')

@app.route('/salidas')
def salidas():
    if not g.user:
        return render_template('peligro.html')
    elif session['user'] == 'administrador':
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM salidas')
        data = cur.fetchall()
        return render_template('salidas.html', contacts = data)
    else:
        return render_template('sesionbloqueada.html')

@app.route('/entradas')
def entradas():
    if not g.user:
        return render_template('peligro.html')
    elif session['user'] == 'administrador':
        cur = mysql.connection.cursor()
        cur.execute('SELECT * FROM entrada')
        data = cur.fetchall()
        return render_template('entradas.html', contacts = data)
    else:
        return render_template('sesionbloqueada.html')

@app.route('/iniciousuario')
def iniciousuario():
    if not g.user:
        return render_template('peligro.html')
    elif session['user'] == 'usuario':
        return render_template('usuario.html')
    else:
        return render_template('sesionbloqueada.html')
    

#--- ---- ------ ------ ------- ------- -------- --------- -------- -------- -------

#Registro de usuario


@app.route('/registro_usuario', methods = ['POST'])
def registro_usuario():

    if request.method == 'POST':
        
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        correo = request.form['correo']
        contraseña = request.form['contraseña']
        if (nombre == '' or apellido == '' or correo == '' or contraseña == ''):
                flash('¡ Campos vacios !')
                return render_template('registro.html')
        print("hola")
        cur = mysql.connection.cursor()
        cur.execute('INSERT INTO registro (nombre, apellido, correo, contraseña) VALUES (%s, %s, %s, %s)', (nombre, apellido, correo, contraseña))
        mysql.connection.commit()
        flash('Usuario registrado, inicie sesión')
        return render_template('inicio.html')




#--- ---- ------ ------ ------- ------- -------- --------- -------- -------- -------

# Ingresar administrador y usuario

@app.route('/iniciosesion', methods = ['GET' , 'POST'])
def iniciosesion():
    error = None

    if request.method == 'POST':
        session.pop('user', None)
        session['user'] = request.form['correo']
        contraseña = request.form['contraseña']
        if (session['user'] == 'administrador@correo.urg' and contraseña == '1234567890'):
            session['user'] = 'administrador'
            return redirect(url_for('administrador'))
        else:
            if (session['user'] == 'administrador@correo.urg' and contraseña != '1234567890' ):
                flash('Hola Administrador, tu contraseña es incorrecta')
                return render_template('inicio.html')

        cur = mysql.connection.cursor()
        user = session['user']  

        hora = time.strftime("%I:%M:%S")
        fecha = date.today()
        cur.execute('INSERT INTO entrada (correo, hora , fecha) VALUES (%s, %s, %s)', (user, hora, fecha))
        filas = cur.execute(f'SELECT * FROM registro where correo = "{user}" and contraseña = "{contraseña}"')
        session['user'] = user
        mysql.connection.commit()

        if filas == 0 :
            error = 'Datos invalido'
            flash('Correo o contraseña invalida')
        else:
            return redirect(url_for('protegidousuario'))
            
    return render_template('inicio.html', error=error)


#--- ---- ------ ------ ------- ------- -------- --------- -------- -------- -------

# Iniciar session     
        
@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']


#--- ---- ------ ------ ------- ------- -------- --------- -------- -------- -------

# Proteger sitio 

@app.route('/protegido')
def protegido():
    if g.user:
        flash('Administrador')
        session['user'] == 'administrador'
        return render_template('administrador.html')

    return redirect(url_for('inicio'))

@app.route('/protegidousuario')
def protegidousuario():
    if g.user:
        flash(g.user)
        session['user'] == 'usuario'
        return render_template('usuario.html')
    return redirect(url_for('inicio'))

@app.route('/inicio_otra_sesion')
def inicio_otra_sesion():
   return render_template('sesionbloqueada.html')


#--- ---- ------ ------ ------- ------- -------- --------- -------- -------- -------

# Cerrar session 

@app.route('/salir')
def salir(): 

    if session['user'] == 'administrador':
        session['administrador']=''
    hora = time.strftime("%I:%M:%S")
    fecha = date.today()
    cur = mysql.connection.cursor()
    cur.execute('INSERT INTO salidas (correo, hora , fecha) VALUES (%s, %s, %s)', (session['user'], hora, fecha))
    mysql.connection.commit()
    session.pop('user', None)
    flash('Cerro sesión')
    return redirect(url_for('inicio'))


   

if __name__ == "__main__":
    app.run(debug=True)