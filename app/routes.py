from flask import Flask, make_response, redirect, abort, render_template, session, url_for, flash
from flask.ext.bootstrap import Bootstrap
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.mail import Message
import os

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
bootstrap = Bootstrap(app)
app.config['SECRET_KEY'] = 'probando'

# configurar bd
app.config['SQLALCHEMY_DATABASE_URI'] =\
	'sqlite:///'+os.path.join(basedir,'data-sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True # asi no tengo que hacer commit todo el rato

db = SQLAlchemy(app)

#configurar email

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')

app.config['PRUEBAS_MAIL_SUBJECT_PREFIX'] = '[Pruebas]'
app.config['PRUEBAS_MAIL_SENDER'] = 'Pruebas Admin <xcstudiosonly@gmail.com>'
app.config['PRUEBAS_ADMIN'] = os.environ.get('PRUEBAS_ADMIN')

mail = Mail(app)

class Role(db.Model):
	__tablename__ = 'roles'
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(64), unique=True)
	# relacion con la tabla User
	usuarios = db.relationship('User', backref='role')

	def __repr__(self): 
	# hacemos el metodo repr que sirve para hacer un string leible de lo que devuelve para debuguear
	# por consola
		return '<Role %r>' % self.name

class User(db.Model):
	__tablename__ = 'usuarios'
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(64), unique=True, index=True)
	# clave foranea
	role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

	def __repr__(self):
	# hacemos el metodo repr que sirve para hacer un string leible de lo que devuelve para debuguear
	# por consola
		return '<Usuario %r>' % self.username

		

'''
@app.route('/')
def index():
	response = make_response('<h3>Esto va a llevar una cookie</h3>')
	response.set_cookie('answer','42')
	return response
'''
@app.route('/redirijo')
def redirijo():
	return redirect('http://www.google.es')
'''
@app.route('/user/<id>')
def get_usuario(id):
	user = load_user(id)
	if not user:
		abort(404)
	return '<h1>Hola, %s<h1>' % user.name
'''
# esto podria ponerlo en otro fichero e importarlo
class NameForm(Form):
	name = StringField('Cual es tu nombre?',validators=[Required()])
	submit = SubmitField('Submit')

'''
@app.route('/', methods=['GET','POST'])
def index():
	name = None
	form = NameForm()
	if form.validate_on_submit():
		name = form.name.data
		form.name.data = ''
	return render_template('index.html',form=form, name=name)
'''
def enviar_email(para,asunto,template, **kwargs): # kwargs - lista de argumentos
	msg = Message(app.config['PRUEBAS_MAIL_SUBJECT_PREFIX'] + asunto, 
				  sender= app.config['PRUEBAS_MAIL_SENDER'], recipients=[para])
	msg.body = render_template(template + '.txt', **kwargs)
	msg.html = render_template(template + '.html', **kwargs)
	mail.send(msg)


@app.route('/',methods=['GET','POST'])
def index():
	formulario = NameForm() #formulario coge los valores de la clase NameForm definida arriba
	if formulario.validate_on_submit(): # si valida al hacer submit
		nombre_viejo = session.get('nick') #comprobamos el nombre que tenia antes
		#if nombre_viejo !=  formulario.name.data: # si es distinto
			#flash('Parece que has cambiado tu nombre!') #muestro mensaje de que ha cambiado el nombre
		usuario = User.query.filter_by(username=formulario.name.data).first()
		if usuario is None:
			usuario = User(username=formulario.name.data)
			db.session.add(usuario)
			session['conocido'] = False
			if app.config['PRUEBAS_ADMIN']: #si existe (esta definida arriba)
				enviar_email(app.config['PRUEBAS_ADMIN'],'Nuevo usuario',
							 'mail/new_user', user=usuario) # usa el template de mail/new_user de
															# contenido del mensaje
		else:
			session['conocido'] = True
		session['nick'] = formulario.name.data #guardamos la nueva sesion
		formulario.name.data = ''
		return redirect(url_for('index')) #redireccionamos para evitar el refresco
	return render_template('index.html', form=formulario, name = session.get('nick'),
										 conocido=session.get('conocido',False)) 
	#renderizamos si no hizo nada en el form

@app.route('/usuario/<nick>')
def usuario(nick):
	return render_template('usuario.html', name=nick)



if __name__ == '__main__':
	app.run(debug=True)