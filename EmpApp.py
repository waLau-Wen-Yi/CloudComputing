from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
import random

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'

#@@@@@@@@@@General
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')

@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

#@@@@@@@@@@Employee Management
@app.route("/addemp", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    pri_skill = request.form['pri_skill']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:

        cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location))
        db_conn.commit()
        emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")
    return render_template('AddEmpOutput.html', name=emp_name)

#@@@@@@@@@@Attendance
@app.route("/attd", methods=['POST'])
def attd():
    return render_template('Attendance.html')

@app.route("/viewattd", methods=['POST'])
def ViewAttd():
    return render_template('ViewAttendanceLog.html')

@app.route("/takeattd", methods=['POST'])
def GoToTakeAttd():
    return render_template('TakeAttendance.html')

@app.route("/updateattd", methods=['POST'])
def GoToUpdateAttd():
    return render_template('UpdateAttdStatus.html')

@app.route("/gencode", methods=['GET'])
def TakeAttendance():
    emp = request.args['emp_id']
    attendance = 0
     
    #generate code
    code = random.randint(100000,999999)

    #update to database


    #display at UI 
    return render_template('TakeAttendance.html', emp_id=emp) 

@app.route("/getempname", methods=['GET'])
def GetEmpName():
    emp_id = 0
    if (request.method == 'GET') :
        emp_id = request.args['emp_id'] #request = page, args[''] = query string
        db_conn.cursor().execute("SELECT fname, lname FROM employee WHERE emp_id = (%s)", (emp_id)) #value of emp_id is from data field
        value = db_conn.fetchall()
    return render_template('TakeAttendance.html', id=emp_id) 

#@@@@@@@@@@Payroll

#@@@@@@@@@@Performance Tracker


#DON'T TOUCH!
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
