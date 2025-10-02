
from flask import Flask, render_template, url_for, redirect, request, jsonify
from sqlalchemy.sql import func
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from sqlalchemy import not_
from flask_bcrypt import Bcrypt
from forms.formsAuth import LoginForm, RegisterForm, ClassForm, Delete_Class_Form
from db import app, Base, local_session, engine, User, Major, Course, MajorHasCourse, Enrollments, Class, Note
from utility import can_enroll
from sqlalchemy import text
import json
import html
import mysql.connector
from mysql.connector import errorcode
import mysql.connector
from mysql.connector import errorcode
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

class MajorHasCourseAdmin(ModelView):
    form_columns = ('majors', 'course')
    column_list = ('majors', 'courses')
    
class EnrollmentsAdmin(ModelView):
    form_columns = ('students', 'courses', 'classes', "is_complete", "is_required")
    column_list = ('students', 'courses', 'classes', "is_complete", "is_required")
    

admin = Admin()
admin.init_app(app)
admin.add_views(ModelView(User, local_session),
                ModelView(Major, local_session),
                ModelView(Course, local_session), 
                ModelView(Class, local_session),
                ModelView(Note, local_session),
                EnrollmentsAdmin(Enrollments, local_session),
                MajorHasCourseAdmin(MajorHasCourse, local_session)
                )

bcrypt = Bcrypt(app)

# initialize Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return local_session.query(User).get(int(user_id))

# Create tables
Base.metadata.create_all(engine)

print(__name__)
# default route redirected to login
@app.route("/")
def index():
    return redirect(url_for('login'))

def convert_12_hour_to_24_hour(time_string):
    # Parse the time string into a datetime object
    time_object = datetime.strptime(time_string, "%I:%M %p")

    # Format the datetime object as a string in 24-hour format
    time_24_hour_string = time_object.strftime("%H:%M")

    return str(time_24_hour_string)


# redirect page to login if the user is not authenticated
@app.route("/dashboard", methods=["GET", "POST"])
@login_required

def dashboard():
    
    enrolled_course_ids = local_session.query(Enrollments.course_id).distinct().subquery()
    my_enrollments = local_session.query(Enrollments).filter_by(student_id = current_user.id).all()
    major_courses = local_session.query(MajorHasCourse).filter(not_(MajorHasCourse.course_id.in_(enrolled_course_ids))).filter_by(majors = current_user.majors).all()
    #my_classes = local_session.query(Enrollments).filter_by(student_id=current_user.id).all()
    
    class_ids = [enrollment.class_id for enrollment in my_enrollments]
    #print(my_enrollments[1].is_required)
    current_classes = local_session.query(Class).filter(Class.id.in_(class_ids)).all()
    
    major_class_list = local_session.query(Class).all()
    #.\
     #   join(Course, (Course.subject == Class.subject) & (Course.courseNum == Class.courseNum)).\
      #  join(MajorHasCourse, MajorHasCourse.course_id == Course.id).all()

    major_required_list = local_session.query(Class).\
        join(MajorHasCourse, (MajorHasCourse.course_id == Class.course_id))
    
    for classes in major_required_list:
        print(classes.title)
    
    #json_class_list = jsonify(major_class_list)
    #List comprehension to extract details

    class_details = [{
        'days': my_class.days,
        'start_time': convert_12_hour_to_24_hour(my_class.start_time),
        'end_time': convert_12_hour_to_24_hour(my_class.end_time),
        # 'start_time': ''.join(filter(str.isdigit, my_class.courses.classes.start_time)),
        # 'end_time': ''.join(filter(str.isdigit, my_class.courses.classes.end_time)),
        'Coursenum': my_class.courseNum,
        'Title': my_class.title,
        'Section': my_class.section,
        'num_seats': my_class.max_seats
    } for my_class in current_classes]
    class_data = json.dumps(class_details, allow_nan=True)
    class_data_unes = html.unescape(class_data)
        #degree_id = local_session.query(User.major_id).filter_by( )
    #degree = local_session.query(Major.major_name).filter_by(Major.id == degree_id)
    if local_session.query(User.is_admin).filter_by(id = current_user.id).first() == (1,):
        database_url = url_for('check')
        dashboard_url = url_for('dashboard')

        student_list = local_session.query(User).all()
        Notes_list = local_session.query(Note).all()
        Note_dict = []
        students_dict = []
        for student in student_list:
            students_dict.append({"id": student.id, "firstname": student.firstname, "lastname": student.lastname, "credits_needed": student.credits_needed, "credits_completed" : student.credits_completed, "GPA" : student.GPA, "year" : student.year, "grad_year": student.grad_year, "email" : student.email, "major_id" : student.major_id})


        for note in Notes_list:
            date_created_str = note.date_created.isoformat()
            Note_dict.append({"id": note.fk_student_id, "Note": note.note_text, "Date_created": date_created_str})
    
        note_data = json.dumps(Note_dict, allow_nan= True)
        note_data_unes = html.unescape(note_data)

        student_data = json.dumps(students_dict, allow_nan=True)
        student_data_unes = html.unescape(student_data)
        return render_template('admin_page.html',dashboard_url=dashboard_url, database_url=database_url, student_list = student_data_unes, note_list = note_data_unes)
    else:
        major_courses_list = []
        major_courses_all = []
        major_courses_all = local_session.query(MajorHasCourse).filter_by(majors = current_user.majors).all()
        major_courses_full = []
        for major_course in local_session.query(MajorHasCourse):
            if(current_user.major_id == major_course.major_id):
                major_courses_list.append(local_session.query(Course.coursename).filter_by(id = major_course.course_id).first())
                major_courses_full.append(local_session.query(Course.full_title).filter_by(id = major_course.course_id).first())
        major = local_session.query(Major).get(int(current_user.major_id))
        
        return render_template("dashboard.html", current_user= current_user, current_major = major, courses = major_courses, current_classes=current_classes, class_details=class_data_unes, courses_full = major_courses_full, major_courses = major_courses_all, json_class_list=major_class_list, major_required_list = major_required_list)



# @app.route("/admin_page", methods=["GET", "POST"])
# @login_required

# def admin_page():
#     return render_template("admin_page.html")


# redirect user to login page after logging out 

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
   
    # redirect to dashboard if the user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    # check if the form is valid when the user clicks on login
    if form.validate_on_submit():
        user = local_session.query(User).filter_by(email= form.email.data).first()
        # proceed to check the credentials if the user exist under the specified email
        if user:
            # If the entered password matches, login the user and return the dashboard
            if (user.password == form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            # return to login if the password doesn't match the stored credentials in database
            else: 
                return render_template("login.html", form=form, title="Login", error="Your credentials doesn't match.")
        # return to login if the email doesn't exist
        else:
            return render_template("login.html", form=form, title="Login", error="Email Doesn't Exist")
    # return the login form view
    return render_template("login.html", form=form, title="Login")



@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/class_deletion_form', methods=['GET', 'POST'])
def class_delete():
   class_list = local_session.query(Class).all()
   class_choices = []
   for item in class_list:
      mylist=[]
      mylist.append(str(item.id))
      mylist.append("{}, Section {}".format(item.title, item.section) )
      my_tuple = tuple(mylist)
      class_choices.append(my_tuple)
   
   form = Delete_Class_Form()
   form.class_id.choices=class_choices  
   '''
   added check_same_thread=False in  app_planet_define.py 
   engine = create_engine('sqlite:///planet.db?check_same_thread=False')
   otherwise was getting thread issues
   '''

   # KEPT COMING BACK AS INVALID
   if form.validate_on_submit():
   #if form.is_submitted():
      result = request.form
      
      class_to_delete = local_session.query(Class).get(int(result["class_id"]))
      deletion_string = "Successfully deleted " + class_to_delete.title + " Section " + class_to_delete.section
      local_session.delete(class_to_delete)
      local_session.flush()
      local_session.commit() 

      return render_template('class_deletion_form.html', title="Delete Class", header="Delete Class", form=form, deleted=deletion_string)

   return render_template('class_deletion_form.html', title="Delete Class", header="Delete Class", form=form)


# redirect to dashboard if the user is already logged in,
# attempt to login using password and email input
# def dashboard():
    
#     #degree_id = local_session.query(User.major_id).filter_by( )
#     #degree = local_session.query(Major.major_name).filter_by(Major.id == degree_id)
#     if local_session.query(User.is_admin).filter_by(id = current_user.id).first() == (1,):
#         database_url = url_for('check')
#         dashboard_url = url_for('dashboard')

#         student_list = local_session.query(User).all()
#         students_dict = []
#         for student in student_list:
#             student_dict = {"id": student.id, "firstname": student.firstname, "lastname": student.lastname, "credits_needed": student.credits_needed, "credits_completed" : student.credits_completed, "GPA" : student.GPA, "year" : student.year, "grad_year": student.grad_year, "email" : student.email, "major_id" : student.major_id}
#             students_dict.append(student_dict)

#         student_data = json.dumps(students_dict, allow_nan=True)
#         student_data_unes = html.unescape(student_data)
#         return render_template('admin_page.html',dashboard_url=dashboard_url, database_url=database_url, student_list = student_data_unes)
#     else:
#         major_courses = []
#         major_courses_all = []
#         major_courses_all = local_session.query(MajorHasCourse).filter_by(majors = current_user.majors).all()
#         major_courses_full = []
#         for major_course in local_session.query(MajorHasCourse):
#             if(current_user.major_id == major_course.major_id):
#                 major_courses.append(local_session.query(Course.coursename).filter_by(id = major_course.course_id).first())
#                 major_courses_full.append(local_session.query(Course.full_title).filter_by(id = major_course.course_id).first())
#         major = local_session.query(Major).get(int(current_user.major_id))
        
#         return render_template("dashboard.html", current_user= current_user, current_major = major, courses = major_courses, courses_full = major_courses_full, major_courses = major_courses_all)

# @app.route("/admin_page", methods=["GET", "POST"])
# @login_required

# def admin_page():
#     return render_template("admin_page.html")


# redirect user to login page after logging out 

    

@app.route('/class_form', methods=['GET', 'POST'])
def class_form():
   form = ClassForm()
   print(form.validate_on_submit())
   if form.validate_on_submit():

      result = request.form
      
      newClass = Class(CRN = result.get('CRN'), subject = result.get('subject'), courseNum = result.get('courseNum'), section = result.get('section'), credit_hours = result.get('credit_hours'), camp_code = "D", pt = "1",  title = result.get('title'), instructor = result.get('instructor'), days = result.get('days'), start_time = result.get('start_time'), end_time = result.get('end_time'), location = result.get('location'), max_seats = result.get('max_seats'), seats_occ = 0, seats_rem = result.get('max_seats'))
      newCourse = Course(coursename = result.get('subject') + " " + result.get('courseNum'), full_title = result.get('title'))
      local_session.add(newClass)
      local_session.add(newCourse)
      local_session.commit()
      return render_template('class_form_handler.html', 
                             title="Class Added", 
                             header="New Class", 
                             result=result
                             )
   # if not from a submit, go to form 
   return render_template('class_form.html', 
                          title="Enter New Class Data", 
                          header="New Class", 
                          form=form)


# register the user using the entered information
@app.route("/register", methods=["GET","POST"])
def register():

    major_list = local_session.query(Major).all()
    major_choices = []
    level_ids = ["Freshman", "Sophomore", "Junior", "Senior", "Graduate"]
    for item in major_list:
        mylist=[]
        mylist.append(str(item.id))
        mylist.append("{}".format(item.major_name) )
        my_tuple = tuple(mylist)
        major_choices.append(my_tuple)
    form = RegisterForm()
    form.major_id.choices=major_choices 
    #print(form.major_id.id)
    #form.minor_id.choices = major_choices
    form.level_id.choices = level_ids
    # check if the entered information is validated, then redirect to login page
    if form.validate_on_submit():
        # use bcrypt to hash the password when storing to db
        #hashed_password = bcrypt.generate_password_hash(form.password.data)
        if form.level_id.data == "Graduate" :
            credits_needed = 60
        else:
            credits_needed = 120
        #major_to_add = local_session.query(Major.id).filter_by(form.major_id.data)
        new_user = User(firstname=form.firstname.data,lastname=form.lastname.data,email=form.email.data, password=form.password.data, major_id=form.major_id.data,is_admin=0, year = form.level_id.data, credits_needed = credits_needed, credits_completed = form.current_credits.data )
        local_session.add(new_user)
        local_session.commit()
        return redirect(url_for('login'))
    # return the register form view
    return render_template("register.html", form=form, title="Register")


#extend the database when clicked
@app.route('/check', methods=["Get","POST"])
def check():
    users = local_session.query(User).all()

            # Fetch all courses from the Course table
    courses = local_session.query(Course).all()

            # Fetch all classes from the Class table
    classes = local_session.query(Class).all()

            # Fetch all majors from the Major table
    majors = local_session.query(Major).all()

            # Fetch all enrollments from the Enrollments table
    enrollments = local_session.query(Enrollments).all()

            # Fetch all major-has-course relationships from the major_has_course table
    major_course_relationships = local_session.query(MajorHasCourse).all()
    dashboard_url = url_for('dashboard')
    database_url = url_for('check')
    return render_template('check.html', users=users, courses=courses, classes=classes, majors=majors, enrollments=enrollments, major_course_relationships=major_course_relationships, dashboard_url=dashboard_url, database_url=database_url)

@app.route("/enrollClass", methods=["POST"])
def enrollClass():
    data = request.json
    print(data)
    new_enrollment = Enrollments(student_id=data['student_id'], course_id=data['course_id'],class_id=data['class_id'], is_complete=0, is_required=1)
    
    existing_enrollments = local_session.query(Enrollments).filter_by(student_id=current_user.id).all()

    class_ids = [enrollment.class_id for enrollment in existing_enrollments]
    #print(class_ids)
    existing_classes = local_session.query(Class).where(Class.id.in_(class_ids)).all()

    #existing_enrollments = local_session.query(Enrollments).filter_by(student_id=current_user.id).all()
    #existing_classes = local_session.query(Class).filter_by()
    new_class = local_session.query(Class).filter_by(id=data['class_id']).first()
    # Assume `new_class` is the class the student wants to enroll in
    # `existing_classes` is a list of classes the student is already enrolled in
    if can_enroll(new_enrollment, existing_classes, new_class):
        # Code to enroll the student
        local_session.add(new_enrollment)
        local_session.commit()
        print("Enrolled successfully.")
        return jsonify({'response': new_class.title}),200
    else:
        print("Cannot enroll, schedule conflict.")
        return jsonify({'response': "Cannot enroll, schedule conflict."}),400
        
    
@app.route("/add_note", methods=["POST"])
def add_note():

    data = request.json
    student_id = data.get('student_id')
    note_text = data.get('noteText')
    print("Received data:", data)
    print("Student ID:", student_id)
    print("Note Text:", note_text)
    # Check if the student ID exists in the database
    student = local_session.query(User).filter_by(id=student_id).first()
    if student:
        # Create a new note object
        new_note = Note(
            note_text=note_text,
            fk_student_id=student_id
        )
        local_session.add(new_note)
        local_session.commit()
        return jsonify({'message': 'Note added successfully.'}), 200
    else:
        return jsonify({'error': 'Student not found.'}), 404

if __name__ == "__main__":
   print("x")
   app.run(debug=True)

