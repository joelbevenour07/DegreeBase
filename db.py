
import os
from flask import Flask
from flask_login import UserMixin
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
from sqlalchemy import MetaData, create_engine, Table, ForeignKey, Date
from sqlalchemy import create_engine, Column, Integer, String, Float
#from db import app, Base, session, engine
import mysql.connector
#from models.user import User

from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# DB configuration
database_url = os.environ.get('DATABASE_URI')
app.config["SQLALCHEMY_DATABASE_URI"]= database_url
app.config["SECRET_KEY"]= os.environ.get('SECRET_KEY')

# SQLAlchemy setup
engine = create_engine(database_url)
Base = declarative_base()
Base.metadata.bind = engine 
metadata = MetaData()
 # Associate the Base with the engine
Session = sessionmaker(bind=engine)
local_session = Session()

# Define your models (replace with your actual models)
class Class(Base):
    __tablename__ = 'Class'
    id = Column(Integer, primary_key=True)
    CRN = Column(Integer, nullable=True)
    subject = Column(String(10), nullable=False)
    courseNum = Column(String(100), nullable=False)
    section = Column(String(10), nullable=True)
    credit_hours = Column(Integer, nullable=True)
    camp_code = Column(String(10), nullable=True)
    pt = Column(String(10), nullable=True)
    title = Column(String(50), nullable=True)
    instructor = Column(String(50), nullable=True)
    days = Column(String(50), nullable=True)
    start_time = Column(String(20), nullable=True)
    end_time = Column(String(20), nullable=True)
    location = Column(String(20), nullable=True)
    max_seats = Column(Integer, nullable=True)
    seats_occ = Column(Integer, nullable=True)
    seats_rem = Column(Integer, nullable=True)
    course_id = Column('course_id', Integer, ForeignKey('Courses.id'),primary_key=True)
    # Define your columns here


class Major(Base):
    __tablename__ = 'Major'
    id = Column(Integer, primary_key=True)
    major_name = Column(String(50), nullable=False)
    major_desc = Column(String(255), nullable=True)
    major_dept = Column(String(60), nullable=True)
    
    def __str__(self):
        return self.major_name

class Course(Base):
    __tablename__ = 'Courses'
    id = Column(Integer, primary_key=True)
    coursename = Column(String(50), nullable=False)
    full_title = Column(String(50), nullable=False)
    subject = Column(String(10), ForeignKey('Class.subject'), primary_key=True )
    courseNum = Column(Integer, ForeignKey('Class.courseNum'), primary_key=True )
    classes = relationship("Class", primaryjoin="and_(Class.subject == Course.subject, Class.courseNum == Course.courseNum)",backref='courses')
    def __str__(self):
        return self.coursename
class Note(Base):
    __tablename__ = 'Notes'
    note_id = Column(Integer, primary_key=True, autoincrement=True)
    note_text = Column(String(255))
    date_created = Column(Date)
    fk_student_id = Column(Integer, ForeignKey('users.id'), nullable = False)

    # Define relationship with Student table
    students = relationship("User", foreign_keys=[fk_student_id], backref='Student')
    user = relationship("User", back_populates="notes", overlaps="Student,students")

class User(Base, UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    firstname = Column(String(99), nullable=False)
    lastname = Column(String(99), nullable=False)
    credits_needed = Column(Float, nullable=True)
    credits_completed = Column(Float, nullable=True)
    GPA = Column(Float, nullable=True)
    year = Column(String(15), nullable=True)
    grad_year = Column(Integer, nullable=True)
    email = Column(String(50), nullable=True, unique=False)
    password = Column(String(80), nullable=True)
    major_id = Column(Integer, ForeignKey('Major.id') )
    is_admin = Column(Integer, nullable=False)
    
    majors = relationship("Major", foreign_keys=[major_id], backref='students')
    notes = relationship("Note", back_populates="user", overlaps="Student,students")
    def __str__(self):
        return self.firstname+ " " + self.lastname

class Enrollments(Base):
    __tablename__ = 'Enrollments'
    student_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    course_id = Column(Integer, ForeignKey('Courses.id'), primary_key=True)
    is_complete = Column(Integer, nullable=False)
    is_required = Column(Integer, nullable=False)
    class_id = Column(Integer, ForeignKey('Class.id'), primary_key=True)
    #grade = Column(String(2), nullable=True)
    students = relationship("User", foreign_keys=[student_id], backref='students')
    courses = relationship("Course", foreign_keys=[course_id], backref='courses')
    classes = relationship("Class", foreign_keys=[class_id], backref='class')

class MajorHasCourse(Base):
    __tablename__ = 'major_has_course'
    major_id = Column('major_id', Integer, ForeignKey('Major.id'),primary_key=True)
    course_id = Column('course_id', Integer, ForeignKey('Courses.id'),primary_key=True)
    # ReqType = Column(String(255), nullable=True)
    
    majors = relationship("Major", foreign_keys=[major_id], backref='majorcourse')
    course = relationship("Course", foreign_keys=[course_id], backref='majorcourse')
    def __str__(self):
        return self.course
    


# Create tables in the local database
def create_local_tables():
    Base.metadata.create_all(bind=engine)

# Fetch data from the remote database and insert into the local database
def fetch_data_and_insert():
    # Create a session to interact with the local database
    

    # Use the remote connection code to fetch data
    remote_conn = mysql.connector.connect(
        host="198.71.61.167",
        user="python-user",
        password="Password1$",
        database="degreebase",
        port=3306
    )

    # Fetch data from the remote database (replace with your own logic)
    remote_cursor = remote_conn.cursor()
    remote_cursor.execute("SELECT * FROM Class")
    remote_data = remote_cursor.fetchall()

    # Insert data into the local database
    for row in remote_data:
        local_session.execute(Class.__table__.insert().values(row))

    # Commit the changes
    local_session.commit()

    remote_cursor.execute("SELECT * FROM Student")
    remote_data = remote_cursor.fetchall()

    # Insert data into the local database
    
    for row in remote_data:
        local_session.execute(User.__table__.insert().values(row))

    # Commit the changes
    local_session.commit()

    remote_cursor.execute("SELECT * FROM Major")
    remote_data = remote_cursor.fetchall()

    # Insert data into the local database
    for row in remote_data:
        local_session.execute(Major.__table__.insert().values(row))

    # Commit the changes
    local_session.commit()

    remote_cursor.execute("SELECT * FROM Courses")
    remote_data = remote_cursor.fetchall()

    # Insert data into the local database
    for row in remote_data:
        local_session.execute(Course.__table__.insert().values(row))

    

    remote_cursor.execute("SELECT * FROM Enrollments")
    remote_data = remote_cursor.fetchall()

    # Insert data into the local database
    for row in remote_data:
        local_session.execute(Enrollments.__table__.insert().values(row))

    # Commit the changes
    local_session.commit()

    remote_cursor.execute("SELECT * FROM major_has_course")
    remote_data = remote_cursor.fetchall()

    # Insert data into the local database
    for row in remote_data:
        local_session.execute(MajorHasCourse.__table__.insert().values(row))

    # Commit the changes
    local_session.commit()

    remote_cursor.execute("SELECT * FROM Notes")
    remote_data = remote_cursor.fetchall()

    # Insert data into the local database
    for row in remote_data:
        local_session.execute(Note.__table__.insert().values(row))

    # Commit the changes
    local_session.commit()

if not os.path.exists("degreebase.db"):
    with app.app_context():
        create_local_tables()
        fetch_data_and_insert()

