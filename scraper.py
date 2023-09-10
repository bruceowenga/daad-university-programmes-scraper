import requests
import sqlite3

from requests import Session


class Course:
    def __init__(self, course_name, institution, subject, location, duration, tuition, course_url):
        self.course_name = course_name
        self.institution = institution
        self.subject = subject
        self.location = location
        self.duration = duration
        self.tuition = tuition
        self.course_url = course_url


# Create a SQLite database (or connect to an existing one)
conn = sqlite3.connect("courses.db")
cursor = conn.cursor()

# Create a 'courses' table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT,
        institution TEXT,
        subject TEXT,
        location TEXT,
        duration INTEGER,
        tuition TEXT,
        course_url TEXT
    )
''')

# Commit the table creation
conn.commit()

s = requests.Session()

url = "https://www2.daad.de/deutschland/studienangebote/international-programmes/api/solr/en/search.json?q=&degree%5B%5D=1&lang%5B%5D=2&sort=4&limit=1000&display=list"

response = s.get(url).json()

courses_data = response['courses']

# Create courses list
courses = []

for course_data in courses_data:
    course_name = course_data['courseName']
    institution = course_data['academy']
    subject = course_data['subject']
    location = course_data['city']
    duration_text = course_data['programmeDuration']
    duration = duration_text.split(' semesters')[0]
    tuition = course_data['tuitionFees']
    if tuition == 'none':
        tuition = None
    course_url_slug = course_data['link']
    course_url = f"https://www2.daad.de{course_url_slug}"

    # Create a Course instance and append it to the list
    course = Course(course_name, institution, subject, location, duration, tuition, course_url)
    courses.append(course)

# Insert course data into the SQLite database
for course in courses:
    cursor.execute('''
        INSERT INTO courses (course_name, institution, subject, location, duration, tuition, course_url)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (course.course_name, course.institution, course.subject, course.location, course.duration, course.tuition, course.course_url)
    )

# Commit the changes and close the database connection
conn.commit()
conn.close()

