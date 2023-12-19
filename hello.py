from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from impdata import secret_key

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key

# Create a Form Class
class UserForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route('/')
def index():
    # return "<h1>This is Flask Blog Website</h1>"
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    # return "<h1>Hello {}!</h1>".format(name)
    return render_template("user.html",user_name=name)

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = UserForm()

    #Validate Form
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form Submitted Successfully!!")

    return render_template('name.html', name=name, form=form)

# Create Custom Error Pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

