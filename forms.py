from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_ckeditor import CKEditorField
from flask_wtf.file import FileField


# create search form 
class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("Potvrdit")

# create post form 
class PostForm(FlaskForm):
    title = StringField("Titulek", validators=[DataRequired()])
    #content = StringField("Content", validators=[DataRequired()], widget=TextArea())
    content = CKEditorField("Content", validators=[DataRequired()])
    author = StringField("Autor")
    slug = StringField("SlugField", validators=[DataRequired()])
    submit = SubmitField("Submit")
    
    
#create logiin form
class LoginForm(FlaskForm):
    nick_name = StringField("Nick name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Potvrdit")
    

# Create form class 
class NamerForm(FlaskForm):
    name = StringField('What is your name', validators=[DataRequired()])
    submit = SubmitField('submit')


# Create form class password
class PasswordForm(FlaskForm):
    email = StringField('Your email', validators=[DataRequired()])
    password_hash  = PasswordField('Your password ', validators=[DataRequired()])
    submit = SubmitField('submit')


# create user form class 
class UserForm(FlaskForm):
    nick_name = StringField("Nick name", validators=[DataRequired()])
    first_name = StringField("First name", validators=[DataRequired()])
    last_name = StringField("Last name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    age = StringField("Věk", validators=[DataRequired()])
    color = StringField("barva", validators=[DataRequired()])
    about_profile = TextAreaField("Něco o uživateli")
    password_hash = PasswordField("Heslo", validators=[DataRequired(), EqualTo('password_hash2', message="Passwords Must Match!")])
    password_hash2 = PasswordField("Potvrdit heslo", validators=[DataRequired()])
    profile_pic = FileField("Profile pic")
    submit = SubmitField("Submit")

