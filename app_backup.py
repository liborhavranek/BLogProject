from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
# create flask instance 

app = Flask(__name__) 
app.config['SECRET_KEY']= 'key'
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"

db = SQLAlchemy(app)
migrate = Migrate(app,db)

# add json think 
@app.route('/date')
def get_curent_date():
    return {"Date": date.today()}

# create blog post model 

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(55))
    content = db.Column(db.Text)
    author = db.Column(db.String(30))
    date_post = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(40))
    
    
# create post form 

class PostForm(FlaskForm):
    title = StringField("Titulek", validators=[DataRequired()])
    content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    author = StringField("Autor", validators=[DataRequired()])
    slug = StringField("SlugField", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    
# add post page 

@app.route('/add-post', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    
    if form.validate_on_submit():
        post = Post(title = form.title.data,
                    content = form.content.data,
                    author = form.author.data,
                    slug = form.slug.data)
        # clear the form
        form.title.data = ''
        form.content.data = ''
        form.author.data = ''
        form.slug.data = ''
        # add post to database
        db.session.add(post)
        db.session.commit()
        flash('post was postet successfully')
    return render_template("add_post.html", form=form)


@app.route('/post<int:id>')
def post(id):
    post = Post.query.get_or_404(id)
    return render_template('post.html', post=post)

@app.route('/posts/edit<int:id>', methods=['GET', 'POST'])
@login_required
def edit_post(id):
    post = Post.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.author = form.author.data
        post.slug = form.slug.data
        db.session.add(post)
        db.session.commit()
        flash("Post updatet successfully")
        return redirect(url_for('post', id=post.id))
    form.title.data = post.title
    form.author.data = post.author 
    form.slug.data = post.slug 
    form.content.data = post.content 
    return render_template('edit_post.html', form=form)

@app.route('/post/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id)
    form = PostForm()
    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash('post deletet successfully')
        posts = Post.query.order_by(Post.date_post)
        return render_template('posts.html', posts=posts)
    except:
        flash('Oups something wrong ...')
        posts = Post.query.order_by(Post.date_post)
        return render_template('posts.html', posts=posts)

@app.route('/posts')
def posts():
    posts = Post.query.order_by(Post.date_post)
    return render_template('posts.html', posts=posts)


class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nick_name = db.Column(db.String(30), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(30), nullable=False, unique=True)
    age = db.Column(db.Integer)
    color = db.Column(db.String(30))
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    # do some password stuff
    password_hash = db.Column(db.String(128))
    @property
    def password(self):
        raise AttributeError('Password is not readable')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.name

#create logiin form
class LoginForm(FlaskForm):
    nick_name = StringField("Nick name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Potvrdit")

#create logiin page 
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(nick_name=form.nick_name.data).first()
        if user:
            #check the hash password
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash('login successfull')
                return redirect(url_for('dashboard'))
            else:
                flash('Wrong password try again')
        else:
            flash('That user does not exist')
    return render_template('login.html', form=form)

# flask login stuff 
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


#create dashboard
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = UserForm()
    id = current_user.id
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.nick_name = request.form['nick_name']
        name_to_update.first_name = request.form['first_name']
        name_to_update.last_name = request.form['last_name']
        name_to_update.email = request.form['email']
        name_to_update.age = request.form['age']
        name_to_update.color = request.form['color']
        try:
            db.session.commit()
            flash("User updatet successfully")
            return render_template('dashboard.html', form=form, name_to_update=name_to_update)

        except:
             flash("There is some prblem ")
             return render_template('dashboard.html', form=form, name_to_update=name_to_update)
    else:
        return render_template('dashboard.html', form=form, name_to_update=name_to_update, id=id)


# create logout
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash('User is logout successfully')
    return redirect(url_for('login'))

@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    nick_name=None
    form = UserForm()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash('user deletet successfully')
        our_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, nick_name=nick_name, our_users=our_users)
    except:
        flash('Oups something wrong ...')
        return render_template('add_user.html', form=form, nick_name=nick_name, our_users=our_users, id=id)


@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.nick_name = request.form['nick_name']
        name_to_update.first_name = request.form['first_name']
        name_to_update.last_name = request.form['last_name']
        name_to_update.email = request.form['email']
        name_to_update.age = request.form['age']
        name_to_update.color = request.form['color']
        try:
            db.session.commit()
            flash("User updatet successfully")
            return render_template('dashboard.html', 
            form=form, name_to_update=name_to_update)

        except:
             flash("There is some prblem ")
             return render_template('update.html', 
            form=form, name_to_update=name_to_update)
    else:
        return render_template('update.html', 
            form=form, name_to_update=name_to_update, id=id)



@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    nick_name=None
    form = UserForm()
    if form.validate_on_submit():
        hashed_pw = generate_password_hash(form.password_hash.data, "sha256")
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user=Users(nick_name = form.nick_name.data,
            first_name = form.first_name.data,
            last_name = form.last_name.data,
            email = form.email.data,
            age = form.age.data,
            color = form.color.data,
            password_hash=hashed_pw)
            db.session.add(user)
            db.session.commit()
        nick_name = form.nick_name.data
        # clear the form
        form.nick_name.data = ''
        form.first_name.data = ''
        form.last_name.data = ''
        form.email.data = ''
        form.age.data = ''
        form.color.data= ''
        form.password_hash.data = ''
        flash('usser add succesfully')
    our_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, nick_name=nick_name, our_users=our_users)



# create route decorator 

@app.route('/user/<name>')
def user(name):
    return render_template('user.html', user_name=name)



@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')

@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NamerForm()
    # validate form 
    if form.validate_on_submit():
        name=form.name.data
        form.name.data = ''
        flash('form is submittet successfully')
    return render_template('name.html', name=name, form=form)


@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()
    # validate form 
    if form.validate_on_submit():
        email=form.email.data
        password = form.password_hash.data
        form.email.data = ''
        form.password_hash.data=''
        pw_to_check = Users.query.filter_by(email=email).first()
        passed = check_password_hash(pw_to_check.password_hash, password)
    return render_template('test_pw.html', email=email, form=form, password=password, pw_to_check=pw_to_check, passed=passed)

# Create form class 
class NamerForm(FlaskForm):
    name = StringField('What is your name', validators=[DataRequired()])
    submit = SubmitField('submit')


# Create form class password
class PasswordForm(FlaskForm):
    email = StringField('Your email', validators=[DataRequired()])
    password_hash  = PasswordField('Your password ', validators=[DataRequired()])
    submit = SubmitField('submit')


# create form class 
class UserForm(FlaskForm):
    nick_name = StringField("Nick name", validators=[DataRequired()])
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    age = StringField("Věk", validators=[DataRequired()])
    color = StringField("barva", validators=[DataRequired()])
    password_hash = PasswordField("Heslo", validators=[DataRequired(), EqualTo('password_hash2', message="Passwords Must Match!")])
    password_hash2 = PasswordField("Potvrdit heslo", validators=[DataRequired()])
    submit = SubmitField("Submit")


if __name__ == "__main__":
    app.run(debug=True)