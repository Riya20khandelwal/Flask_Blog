from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from impdata import secret_key
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, date
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea


app = Flask(__name__)
db = SQLAlchemy()

# Add dataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:admin@localhost/users'
app.config['SECRET_KEY'] = secret_key

# Initialize Database
db.init_app(app)
migrate = Migrate(app, db)

# JSON Thing
@app.route('/date')
def get_current_date():
    fav_thing = {
        "color" : "Blue",
        "movie" : "HAHK"
    }
    # return {"DATE" : date.today()}
    return fav_thing

#Create Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    favorite_color = db.Column(db.String(50))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    password_hash = db.Column(db.String(250))

    @property
    def password(self):
        raise AttributeError("Password is not in readable format!")
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' %self.name

#  Create a Blog Post model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    author = db.Column(db.String(100))
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))

# Create a Form Class
    
class UserInfoForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired(), EqualTo('password_hash2', message="Password must match!")])
    password_hash2 =PasswordField("Confirm Password", validators=[DataRequired()])
    favorite_color = StringField("Favorite Color")
    submit = SubmitField("Submit")


class UserForm(FlaskForm):
    name = StringField("Full Name", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password_hash = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

# Create a Post Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")


#Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
def add_post():
    form = PostForm()

    if form.validate_on_submit():
        post = Posts(title=form.title.data, content=form.content.data, author=form.author.data, slug=form.slug.data)
        
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        
        db.session.add(post)
        db.session.commit()

        flash("Blog Post Submitted Successfully!")

    return render_template("add_post.html",
                           form=form)


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
            #Hash the password
            hashed_pw = generate_password_hash(form.password_hash.data)
            user = Users(name=form.name.data, email=form.email.data, favorite_color=form.favorite_color.data, password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        name=form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favorite_color.data = ''
        form.password_hash = ''
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
    
@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None

    form = PasswordForm()

    #Validate Form
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data

        form.email.data = ''
        form.password_hash.data = ''

        pw_to_check = Users.query.filter_by(email=email).first()
        # Check Hashed Password
        passed = check_password_hash(pw_to_check.password_hash, password)
        

        # flash("Form Submitted Successfully!!")

    return render_template('test_pw.html', email=email, 
           pw_to_check=pw_to_check ,password=password,
            passed = passed, form=form)



# Create Custom Error Pages

#Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

#Internal Server Error
@app.errorhandler(500)
def page_not_found(e):
    return render_template('500.html'), 500

