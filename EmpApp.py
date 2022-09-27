from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
import random
from time import gmtime, strftime
import datetime

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

#------------------------------------------guan tong------------------------------------------------
@app.route("/back", methods=['GET', 'POST'])
def back():
    return render_template('salary.html')

@app.route("/salary", methods=['GET', 'POST'])
def salary():
    return render_template('salary.html')

@app.route("/examine", methods=['GET', 'POST'])
def examine():
    return render_template('examine.html')
    
@app.route("/update", methods=['GET', 'POST'])
def update():
    return render_template('update.html')

@app.route("/view", methods=['GET', 'POST'])
def view():
    cursor = db_conn.cursor()
    string = "Select fname from employee"
    cursor.execute(string)
    result1 = cursor.fetchall()

    string2 = "Select lname from employee"
    cursor.execute(string2)
    result2 = cursor.fetchall()

    string3 = "Select salary from employee"
    cursor.execute(string3)
    result3 = cursor.fetchall()

    string4 = "Select Sum(salary) from employee"
    cursor.execute(string4)
    result4 = cursor.fetchone()


    db_conn.commit()
    cursor.close()

    return render_template('view.html', result1 = result1, result2 = result2, result3 = result3, result4 = result4[0])

@app.route("/search2", methods=['POST'])
def search2():
    emp_id = request.form['emp2_id']
    overtime = request.form['ot']
    penalty = request.form['penalty']
    epf = request.form['epf']
    cursor = db_conn.cursor()
    
    selectSql = "Select salary From employee Where emp_id = %s"
    id = (emp_id)
    cursor.execute(selectSql, id)
    result1 = cursor.fetchone()

    str(overtime)
    str(penalty)
    str(epf)
    
    total = int(result1[0]) + (int(overtime) * 10) - int(penalty)
    final = ((100 - float(epf)) * float(total)) / 100

    updateSql = "Update employee set salary = %s Where emp_id = %s"
    money = (final)
    id = (emp_id)
    cursor.execute(updateSql, (money, id))

    selectSql2 = "Select salary From employee Where emp_id = %s"
    id = (emp_id)
    cursor.execute(selectSql2, id)
    finalSalary = cursor.fetchone()
    db_conn.commit()
    cursor.close()

    return render_template('update.html', result = result1[0], finalSalary = finalSalary[0])

@app.route("/search", methods=['POST'])
def search():
    emp_id = request.form['emp1_id']
    
    cursor = db_conn.cursor()
    selectSql = "Select salary From employee Where emp_id = %s"
    id = (emp_id)
    cursor.execute(selectSql, id)
    result2 = cursor.fetchone()
    db_conn.commit()

    cursor.close()  
    return render_template('examine.html', result = result2[0])

#-----------------------------------------------------------------------------------------------------------------
#@app.route("/addemp", methods=['POST'])
#def AddEmp():
#    emp_id = request.form['emp_id']   
 #   first_name = request.form['first_name']
   #pri_skill = request.form['pri_skill']
  #  location = request.form['location']
   # position = request.form['position']
   # emp_image_file = request.files['emp_image_file']

    #insert_sql = "INSERT INTO employee (emp_id, first_name, last_name, pri_skill, location, position, salary) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    #cursor = db_conn.cursor()

   # if position == 'Senior':
    #    salary = 6000
    #else:
    #    salary = 3000
    #cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, position, salary))
    #db_conn.commit()   


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
    cursor = db_conn.cursor()
    name = ""

    if (request.method == 'GET') :
        emp_id = request.args['emp_id'] #request = page, args[''] = query string
        cursor.execute("SELECT CONCAT(fname, ' ', lname) AS name FROM employee WHERE id = (%s)", (emp_id)) #value of emp_id is from data field
        value = cursor.fetchall()
        for row in value:
            print(row[0])
            name = row[0]
            break
        db_conn.commit()
        cursor.close()
   
    return render_template('TakeAttendance.html', emp_id=emp_id, name=name) 

@app.route("/addcheckin", methods=['GET'])
def addCheckIn():
    cursor = db_conn.cursor()
    name = ""
    isExist = 0
    msg = ""

    emp_id = 0
    attd_id = ""
    in_time = ""
    out_time = ""
    attd_status = ""


    insert_sql = "INSERT INTO attendance(in_time, out_time, attd_status, emp_id) VALUES (%s, %s, %s, %s)"

    if (request.method == 'GET') :
        emp_id = request.args['emp_id'] #request = page, args[''] = query string
        cursor.execute("SELECT CONCAT(fname, ' ', lname) AS name, MAX(in_time), MAX(out_time) FROM employee INNER JOIN attendance ON employee.id = attendance.emp_id WHERE id = (%s)", (emp_id)) #value of emp_id is from data field
        value = cursor.fetchone()
        name = value[0]
        print(name)

        in_time = value[1]
        #in_time_arr = in_time.split(':')
        if(in_time != None):
            print(in_time)
            in_time = datetime.datetime.strptime(in_time, "%I:%M:%S %p")

        out_time = value[2]
        if(out_time != None):
            out_time = datetime.datetime.strptime(out_time, "%I:%M:%S %p")

        #check whether the emp id exists
        if(name != ""):
            #check whether the last time it is check in or checkout
            if(in_time == "" or in_time == None):
                in_time = datetime.datetime.now().strftime("%I:%M:%S %p")
                print(in_time)
                cursor.execute(insert_sql, (in_time, "", "Present", emp_id))
                db_conn.commit()
                isExist = 4
                #insert data
            elif(in_time != None):
                if(in_time < out_time): #if checkout then can check in
                    #insert data
                    in_time = datetime.datetime.now().strftime("%I:%M:%S %p")
                    cursor.execute(insert_sql, (in_time, "", "Present", emp_id))
                    db_conn.commit()
                    isExist = 4

                    return in_time
                elif(in_time > out_time):  #else tell them that they have checked in
                    #display message box
                    isExist = 1
                else:
                    #display message box
                    isExist = 2
                
        else:
            #display message box
            isExist = 3

        return render_template('TakeAttendance.html', emp_id=emp_id, name=name, isExist=isExist) 

#@@@@@@@@@@Payroll

#@@@@@@@@@@Performance Tracker


#DON'T TOUCH!
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
