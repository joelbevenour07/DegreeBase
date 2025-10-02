from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, FloatField, EmailField
from wtforms.validators import InputRequired, Length, ValidationError
from db import local_session
from db import User

class RegisterForm(FlaskForm):
    firstname = StringField("First Name", validators=[InputRequired(), Length(min=2, max=40)])
    lastname = StringField("Last Name", validators=[InputRequired(), Length(min=2, max=40)])
    email = EmailField("Email", validators=[InputRequired(), Length(min=4, max=50)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=4, max=20)])
    major_id = SelectField("Major")
    level_id = SelectField("Year")
    current_credits = FloatField("Credits Completed")
    submit = SubmitField("Register")
    
    def validate_email(self, email):
        existing_user_email =local_session.query(User).filter_by(email=email.data).first()
        
        if existing_user_email:
            raise ValidationError("Email already exists. Try again")
            
class LoginForm(FlaskForm):
    email = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Login")


class ClassForm(FlaskForm):
    CRN = IntegerField(validators=[InputRequired()], render_kw={"placeholder": 0})
    subject = StringField(validators=[InputRequired(), Length(min=1, max=10)], render_kw={"placeholder": ""})
    courseNum = StringField(validators=[InputRequired(), Length(min=1, max=100)], render_kw={"placeholder": ""})
    section = StringField(validators=[InputRequired(), Length(min=1, max=10)], render_kw={"placeholder": ""})
    credit_hours = IntegerField(validators=[InputRequired()], render_kw={"placeholder": 0})
    title = StringField(validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": ""})
    instructor = StringField(validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": ""})
    days = StringField(validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": ""})
    start_time = StringField(validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": ""})
    end_time = StringField(validators=[InputRequired(), Length(min=1, max=50)], render_kw={"placeholder": ""})
    location = StringField(validators=[InputRequired(), Length(min=1, max=20)], render_kw={"placeholder": ""})
    max_seats = IntegerField(validators=[InputRequired()], render_kw={"placeholder": 0})
    submit = SubmitField("Add Class")

class Delete_Class_Form(FlaskForm):
   class_id = SelectField("Class")  
   submit = SubmitField("Delete Class")
