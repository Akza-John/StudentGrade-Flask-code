from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)


# Function to fetch students' data based on filter criteria
def fetch_students(filter_option=None, search_query=None):
    conn = sqlite3.connect('grades.db')
    c = conn.cursor()

    query = '''SELECT mst_student.student_name, mst_subject.subject_name, mst_student.grade
               FROM mst_student
               INNER JOIN mst_subject ON mst_student.subject_key = mst_subject.subject_key'''

    if filter_option:
        if filter_option == 'PASS':
            query += ' WHERE mst_student.grade >= 75'
        elif filter_option == 'FAIL':
            query += ' WHERE mst_student.grade < 75'

    if search_query:
        query += f" WHERE mst_student.student_name LIKE '%{search_query}%'"

    c.execute(query)
    students = c.fetchall()
    conn.close()
    return students


# Routes
@app.route('/')
def index():
    students = fetch_students()
    return render_template('index.html', students=students)


@app.route('/add_student', methods=['POST'])
def add_student():
    student_name = request.form['student-name']
    subject_name = request.form['subject-name']
    grade = int(request.form['grade'])

    conn = sqlite3.connect('grades.db')
    c = conn.cursor()

    c.execute("SELECT subject_key FROM mst_subject WHERE subject_name=?", (subject_name,))
    result = c.fetchone()
    if result:
        subject_key = result[0]
    else:
        c.execute("INSERT INTO mst_subject (subject_name) VALUES (?)", (subject_name,))
        subject_key = c.lastrowid

    remarks = "PASS" if grade >= 75 else "FAIL"

    c.execute("INSERT INTO mst_student (student_name, subject_key, grade) VALUES (?, ?, ?)",
              (student_name, subject_key, grade))

    conn.commit()
    conn.close()

    return redirect(url_for('index'))


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        search_query = request.form['search']
        students = fetch_students(search_query=search_query)
    else:
        students = fetch_students()
    return render_template('index.html', students=students)


@app.route('/filter', methods=['GET', 'POST'])
def filter():
    filter_option = request.form['filter']
    students = fetch_students(filter_option=filter_option)
    return render_template('index.html', students=students)


if __name__ == "__main__":
    app.run(debug=True)
