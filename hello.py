from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
from impdata import secret_key
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime

app = Flask(__name__)
db = SQLAlchemy()

# Add dataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/users'
app.config['SECRET_KEY'] = secret_key

# Initialize Database
db.init_app(app)
migrate = Migrate(app, db)

#Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<Name %r>' %self.name

# Create a Form Class
    
class UserInfoForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")


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

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None
    form = UserInfoForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()
        name=form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        flash("User Added Successfully!")
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html',
                           form=form,
                           name=name,
                           our_users=our_users)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserInfoForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == "POST":
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        except:
            flash("Error! Looks like there was a problem. Please try again!!")
            return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
        
    else:
        return render_template("update.html", form=form, name_to_update=name_to_update, id=id)
    
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None
    form = UserInfoForm()
    
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!!")

        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html',
                            form=form,
                            name=name,
                            our_users=our_users)
    except:
        flash("Something Went Wrong!!")
        return render_template('add_user.html',
                            form=form,
                            name=name,
                            our_users=our_users)



# Create Custom Error Pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

