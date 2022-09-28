from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *
import random
from time import gmtime, strftime, time
from datetime import datetime
from datetime import date
import datetime
import re


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

# ------------------------------------------guan tong------------------------------------------------


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
    string = "Select fname, lname, salary from employee"
    cursor.execute(string)
    result1 = cursor.fetchall()
    
    arr = []
    for col in range(len(result1)):
        arr.append([])
        arr[col].append(col + 1)
        arr[col].append(result[col][0] + "" + result[col][1])
        arr[col].append(result[col][2])

    string4 = "Select Sum(salary) from employee"
    cursor.execute(string4)
    result4 = cursor.fetchone()

    db_conn.commit()
    cursor.close()

    return render_template('view.html', result4=result4[0], content=arr)


@app.route("/search2", methods=['POST'])
def search2():
    id = request.form['emp2_id']
    overtime = request.form['ot']
    penalty = request.form['penalty']
    epf = request.form['epf']
    cursor = db_conn.cursor()

    selectSql = "Select salary From employee Where id = %s"
    id = (id)
    cursor.execute(selectSql, id)
    result1 = cursor.fetchone()

    str(overtime)
    str(penalty)
    str(epf)

    total = int(result1[0]) + (int(overtime) * 10) - int(penalty)
    final = ((100 - float(epf)) * float(total)) / 100

    updateSql = "Update employee set salary = %s Where id = %s"
    money = (final)
    id = (id)
    cursor.execute(updateSql, (money, id))

    selectSql2 = "Select salary From employee Where id = %s"
    id = (id)
    cursor.execute(selectSql2, id)
    finalSalary = cursor.fetchone()
    db_conn.commit()
    cursor.close()

    return render_template('update.html', result=result1[0], finalSalary=finalSalary[0])


@app.route("/search", methods=['POST'])
def search():
    id = request.form['emp1_id']

    cursor = db_conn.cursor()
    selectSql = "Select salary From employee Where id = %s"
    id = (id)
    cursor.execute(selectSql, id)
    result2 = cursor.fetchone()
    db_conn.commit()

    cursor.close()
    return render_template('examine.html', result=result2[0])

# -----------------------------------------------------------------------------------------------------------------
# @app.route("/addemp", methods=['POST'])
# def AddEmp():
#    emp_id = request.form['emp_id']
 #   first_name = request.form['first_name']
   # pri_skill = request.form['pri_skill']
  #  location = request.form['location']
   # position = request.form['position']
   # emp_image_file = request.files['emp_image_file']

    # insert_sql = "INSERT INTO employee (emp_id, first_name, last_name, pri_skill, location, position, salary) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    # cursor = db_conn.cursor()

   # if position == 'Senior':
    #    salary = 6000
    # else:
    #    salary = 3000
    # cursor.execute(insert_sql, (emp_id, first_name, last_name, pri_skill, location, position, salary))
    # db_conn.commit()


# @@@@@@@@@@General
@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('Home.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')

# ------------------------------------------wen yi------------------------------------------------

#@@@@@@@@@@Employee Management
@app.route("/empmng", methods=['GET', 'POST'])
def EmpMng():
    return render_template('/EmpMng/EmpMngHome.html')


@app.route("/rgsemp", methods=['GET', 'POST'])
def RgsEmp():
    return render_template('/EmpMng/RegisEmp.html')

@app.route("/addemp", methods=['POST'])
def AddEmp():
        emp_fname = request.form['emp_fname']
        emp_lname = request.form['emp_lname']
        emp_position = request.form['emp_position']
        emp_id = request.form['emp_id']
        emp_phone = request.form['emp_phone']
        emp_email = request.form['emp_email']
        emp_jdate = datetime.date.today()
        emp_salary = request.form['emp_salary']
        emp_location = request.form['emp_location']
        emp_interest = request.form['emp_interest']
        emp_dob = request.form['emp_dob']
        emp_skills = request.form['emp_skills']
        emp_image_file = request.files['image_file']

        insert_sql = "INSERT INTO employee (id, fname, lname, position, phone, email, jdate, salary, location, interest, dob, skills) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        cursor = db_conn.cursor()

        if emp_image_file.filename == "":
            return "Please select a file"

        try:
            cursor.execute(insert_sql, 
                (emp_id, emp_fname, emp_lname,
                emp_position, emp_phone, emp_email, emp_jdate,
                emp_salary, emp_location, emp_interest, emp_dob,
                emp_skills))
            db_conn.commit()
            # Uplaod image file in S3 #
            emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_profile_pic"
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

                cursor.execute("UPDATE employee SET imgurl = (%s) WHERE id = (%s)", object_url, emp_id)
                db_conn.commit()

            except Exception as e:
                return str(e)

        finally:
            cursor.close()

        print("all modification done...")
        return render_template('/EmpMng/ShowEmpDetails.html', 
             id = emp_id, 
             imgurl = object_url,
             fname = emp_fname,
             lname = emp_lname,
             position = emp_position,
             phone = emp_phone,
             email = emp_email,
             jdate = emp_jdate,
             salary = emp_salary,
             location = emp_location,
             interest = emp_interest,
             dob = emp_dob,
             skills = emp_skills
             )

@app.route("/shwempdtl", methods=['GET', 'POST'])
def ShwEmpDtl():
    routePage = "/EmpMng/ShowEmpDetails.html"
    emp_id = 0
    empData = []
    cursor = db_conn.cursor()
    if (request.method == 'GET'):
        emp_id = request.args['emp_id']
        qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
        if qryRslt == 0:
            return render_template(routePage, id = "DOES NOT EXISTED, PLEASE SEARCH ANOTHER ID")
        else:
            empData = cursor.fetchall()
            return render_template(routePage,
             id = empData[0][0], 
             fname = empData[0][2],
             lname = empData[0][3],
             position = empData[0][4],
             phone = empData[0][5],
             email = empData[0][6],
             jdate = empData[0][7],
             salary = empData[0][8],
             location = empData[0][9],
             interest = empData[0][10],
             dob = empData[0][11],
             skills = empData[0][12]
             )
    return render_template(routePage, id = "")

@app.route("/edtempdtl", methods=['GET', 'POST'])
def EdtEmpDtl():
    routePage = "/EmpMng/EditEmpDetails.html"
    cursor = db_conn.cursor()
    if (request.method == 'GET'):
        emp_id = request.args['emp_id']
        qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
        if qryRslt == 0:
            return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
        else:
            empData = cursor.fetchall()
            return render_template(routePage,
             id = empData[0][0], 
             fname = empData[0][2],
             lname = empData[0][3],
             position = empData[0][4],
             phone = empData[0][5],
             email = empData[0][6],
             jdate = empData[0][7],
             salary = empData[0][8],
             location = empData[0][9],
             interest = empData[0][10],
             dob = empData[0][11],
             skills = empData[0][12]
             )
    return render_template(routePage)

@app.route('/edtemp', methods=['POST'])
def EdtEmp():
    emp_fname = request.form['emp_fname']
    emp_lname = request.form['emp_lname']
    emp_position = request.form['emp_position']
    emp_id = request.form['emp_id']
    emp_phone = request.form['emp_phone']
    emp_email = request.form['emp_email']
    emp_jdate = request.form['emp_jdate']
    emp_salary = request.form['emp_salary']
    emp_location = request.form['emp_location']
    emp_interest = request.form['emp_interest']
    emp_dob = request.form['emp_dob']
    emp_skills = request.form['emp_skills']

    cursor = db_conn.cursor()
    cursor.execute(
        "UPDATE employee SET fname = (%s), lname = (%s), position = (%s), phone = (%s), email = (%s), jdate = (%s), salary = (%s), location = (%s), interest = (%s), dob = (%s), skills = (%s) WHERE id = (%s)",
        (emp_fname, emp_lname, emp_position, emp_phone, emp_email, emp_jdate, emp_salary, emp_location, emp_interest, emp_dob, emp_skills, emp_id))
    db_conn.commit()

    routePage = "/EmpMng/EditEmpDetails.html"
    qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
    empData = cursor.fetchall()
    return render_template(routePage,
        id = empData[0][0], 
        fname = empData[0][2],
        lname = empData[0][3],
        position = empData[0][4],
        phone = empData[0][5],
        email = empData[0][6],
        jdate = empData[0][7],
        salary = empData[0][8],
        location = empData[0][9],
        interest = empData[0][10],
        dob = empData[0][11],
        skills = empData[0][12]
        )

@app.route('/rmvemp', methods=['GET', 'POST'])
def RmvEmp():
    routePage = "/EmpMng/RemoveEmp.html"
    cursor = db_conn.cursor()
    if (request.method == 'GET'):
        emp_id = request.args['emp_id']
        qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
        if qryRslt == 0:
            return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
        else:
            empData = cursor.fetchall()
            return render_template(routePage,
             id = empData[0][0],
             fname = empData[0][2],
             lname = empData[0][3],
             position = empData[0][4],
             jdate = empData[0][7]
             )
    return render_template(routePage)

@app.route('/rmvempcmfrm', methods=['GET'])
def RmvEmpCmfrm():
    routePage = "/EmpMng/RemoveEmp.html"
    cursor = db_conn.cursor()
    emp_id = request.args['emp_id']
    qryRslt = cursor.execute("DELETE FROM employee WHERE id = %s", (emp_id))
    if qryRslt == 1:
        return render_template(routePage, id = "ID ({}) HAS BEEN DELETED".format(emp_id))
    else:
        return render_template(routePage, id = "SOMETHING IS WRONG")

#@@@@@@@@@@Performance Tracker
@app.route('/prftrk', methods=['GET', 'POST'])
def PrfTrk():
    routePage = "/PrfTrk/PrfTrk.html"
    cursor = db_conn.cursor()
    if (request.method == 'GET'):
        emp_id = request.args['emp_id']
        qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
        if qryRslt == 0:
            return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
        else:
            empData = cursor.fetchall()
            goal_id = 'prf{}'.format(emp_id)
            qryRslt = cursor.execute("SELECT * FROM performance WHERE prf_id = %s", (goal_id))
            if (qryRslt == 1):
                prfData = cursor.fetchall()
                return render_template(routePage,
                id = empData[0][0],
                fname = empData[0][2],
                lname = empData[0][3],
                position = empData[0][4],
                jdate = empData[0][7],
                goal = prfData[0][1],
                objective = prfData[0][2],
                grade = prfData[0][3],
                pros = prfData[0][4],
                cons = prfData[0][5]
                )
            else:
                return render_template(routePage,
                id = empData[0][0],
                fname = empData[0][2],
                lname = empData[0][3],
                position = empData[0][4],
                jdate = empData[0][7],
                goal = "DATA NOT FOUNDED"
                )
    return render_template(routePage)

@app.route('/prftrkedt', methods=['GET'])
def PrfTrkEdt():
    routePage = "/PrfTrk/PrfTrkEdt.html"
    cursor = db_conn.cursor()
    emp_id = request.args['emp_id']
    qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
    if qryRslt == 0:
        return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
    else:
        empData = cursor.fetchall()
        goal_id = 'prf{}'.format(emp_id)
        qryRslt = cursor.execute("SELECT * FROM performance WHERE prf_id = %s", (goal_id))
        if (qryRslt == 1):
            prfData = cursor.fetchall()
            return render_template(routePage,
            id = empData[0][0],
            fname = empData[0][2],
            lname = empData[0][3],
            position = empData[0][4],
            jdate = empData[0][7],
            goal = prfData[0][1],
            objective = prfData[0][2],
            grade = prfData[0][3],
            pros = prfData[0][4],
            cons = prfData[0][5]
            )
        else:
            return render_template(routePage,
            id = empData[0][0],
            fname = empData[0][2],
            lname = empData[0][3],
            position = empData[0][4],
            jdate = empData[0][7],
            goal = "DATA NOT FOUNDED"
            )

@app.route('/prfedtact', methods=['POST'])
def PrfEdtAct():
    routePage = "/PrfTrk/PrfTrk.html"
    cursor = db_conn.cursor()
    emp_id = request.form['emp_id']
    goal_id = request.form['prf_id']
    goal = request.form['prf_goal']
    objective = request.form['prf_obj']
    grade = request.form['prf_grade']
    pros = request.form['prf_pros']
    cons = request.form['prf_cons']
    cursor.execute(
        "UPDATE performance SET prf_goal = (%s), prf_obj = (%s), prf_grade = (%s), prf_pros = (%s), prf_cons = (%s) WHERE prf_id = (%s)",
        (goal, objective, grade, pros, cons, goal_id))
    db_conn.commit()

    qryRslt = cursor.execute("SELECT * FROM employee WHERE id = (%s)", (emp_id))
    if qryRslt == 0:
        return render_template(routePage, id = "DATA NOT FOUNDED, PLEASE SEARCH ANOTHER ID")
    else:
        empData = cursor.fetchall()
        goal_id = 'prf{}'.format(emp_id)
        qryRslt = cursor.execute("SELECT * FROM performance WHERE prf_id = %s", (goal_id))
        if (qryRslt == 1):
            prfData = cursor.fetchall()
            return render_template(routePage,
            id = empData[0][0],
            fname = empData[0][2],
            lname = empData[0][3],
            position = empData[0][4],
            jdate = empData[0][7],
            goal = prfData[0][1],
            objective = prfData[0][2],
            grade = prfData[0][3],
            pros = prfData[0][4],
            cons = prfData[0][5]
            )
        else:
            return render_template(routePage,
            id = empData[0][0],
            fname = empData[0][2],
            lname = empData[0][3],
            position = empData[0][4],
            jdate = empData[0][7],
            goal = "DATA NOT FOUNDED"
            )

# -----------------------------------------------------------------------------------------------------------------

# @@@@@@@@@@Attendance


@app.route("/attd", methods=['GET', 'POST'])
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

    # generate code
    code = random.randint(100000, 999999)

    # update to database

    # display at UI
    return render_template('TakeAttendance.html', emp_id=emp)


@app.route("/getempname", methods=['GET'])
def GetEmpName():
    emp_id = 0
    cursor = db_conn.cursor()
    name = ""

    if (request.method == 'GET'):
        # request = page, args[''] = query string
        emp_id = request.args['emp_id']
        # value of emp_id is from data field
        cursor.execute(
            "SELECT CONCAT(fname, ' ', lname) AS name FROM employee WHERE id = (%s)", (emp_id))
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
    dates = ""
    attd_status = ""

    insert_sql = "INSERT INTO attendance(in_time, out_time, date, attd_status, emp_id) VALUES (%s, %s, %s, %s, %s)"

    if (request.method == 'GET'):
        # request = page, args[''] = query string
        emp_id = request.args['emp_id']
        # value of emp_id is from data field
        cursor.execute("SELECT CONCAT(fname, ' ', lname) AS name, MAX(in_time), MAX(out_time), date FROM employee LEFT JOIN attendance ON employee.id = attendance.emp_id WHERE id = (%s) GROUP BY fname, lname, date", (emp_id))
        value = cursor.fetchone()
        if (value != None and len(value) > 0):
            name = value[0]
            print(name)

            in_time = value[1]
            # in_time_arr = in_time.split(':')
            if (in_time != None and in_time != ""):
                print("in:", in_time)
                in_time = datetime.datetime.strptime(in_time, "%I:%M:%S %p")

            out_time = value[2]
            if (out_time != None and out_time != ""):
                print("out:", out_time)
                out_time = datetime.datetime.strptime(out_time, "%I:%M:%S %p")

            dates = value[3]
            if (dates != None and dates != ""):
                match = re.search(r'\d{4}-\d{2}-\d{2}', dates)
                dates = datetime.datetime.strptime(
                    match.group(), '%Y-%m-%d').date()
            else:
                dates = date.today().strftime("%Y-%m-%d")

        # check whether the emp id exists
        if (name != ""):
            # check whether the last time it is check in or checkout
            if (in_time == "" or in_time == None):
                in_time = datetime.datetime.now().strftime("%I:%M:%S %p")
                print(in_time)

                cursor.execute(
                    insert_sql, (in_time, "", dates, "Present", emp_id))
                db_conn.commit()
                isExist = 4
                # insert data
            elif (in_time != None):
                if (out_time == "" or in_time < out_time):  # if checkout then can check in
                    # insert data
                    in_time = datetime.datetime.now().strftime("%I:%M:%S %p")
                    cursor.execute(
                        insert_sql, (in_time, "", dates, "Present", emp_id))
                    db_conn.commit()
                    isExist = 4
                elif (in_time > out_time):  # else tell them that they have checked in
                    # display message box
                    isExist = 1
                else:
                    # display message box
                    isExist = 2

        else:
            # display message box
            isExist = 3

        return render_template('TakeAttendance.html', emp_id=emp_id, name=name, isExist=isExist)


@app.route("/addcheckout", methods=['GET'])
def addCheckOut():
    cursor = db_conn.cursor()
    name = ""
    isExist = 0
    msg = ""

    emp_id = 0
    attd_id = ""
    in_time = ""
    out_time = ""
    attd_status = ""
    dates = ""

    insert_sql = "UPDATE attendance SET out_time = %s WHERE emp_id = %s AND in_time = %s"
    getInTime_sql = "SELECT in_time FROM attendance WHERE emp_id = %s AND attd_id = (SELECT MAX(attd_id) FROM attendance WHERE emp_id = %s)"

    if (request.method == 'GET'):
        # request = page, args[''] = query string
        emp_id = request.args['emp_id']
        # value of emp_id is from data field
        cursor.execute("SELECT CONCAT(fname, ' ', lname) AS name, MAX(in_time), MAX(out_time), date FROM employee INNER JOIN attendance ON employee.id = attendance.emp_id WHERE id = (%s)", (emp_id))
        value = cursor.fetchone()
        if (value != None and len(value) > 0):
            name = value[0]
            print(name)

            in_time = value[1]
            # in_time_arr = in_time.split(':')
            if (in_time != None and in_time != ""):
                print("in:", in_time)
                in_time = datetime.datetime.strptime(in_time, "%I:%M:%S %p")

            out_time = value[2]
            if (out_time != None and out_time != ""):
                print("out:", out_time)
                out_time = datetime.datetime.strptime(out_time, "%I:%M:%S %p")

            dates = value[3]
            if (dates != None and dates != ""):
                match = re.search(r'\d{4}-\d{2}-\d{2}', dates)
                dates = datetime.datetime.strptime(
                    match.group(), '%Y-%m-%d').date()

        # check whether the emp id exists
        if (name != ""):
            # check whether the last time it is check in or checkout
            if (in_time != None and (out_time == "" or out_time == None)):
                cursor.execute(getInTime_sql, (emp_id, emp_id))
                in_time = cursor.fetchone()[0]
                db_conn.commit()
                out_time = datetime.datetime.now().strftime("%I:%M:%S %p")
                print("out:", out_time)
                cursor.execute(insert_sql, (out_time, emp_id, in_time))
                db_conn.commit()
                isExist = 14
                # insert data
            elif (out_time != None):
                if (out_time < in_time):  # if check-in then can check out
                    # insert data
                    cursor.execute(getInTime_sql, (emp_id, emp_id))
                    in_time = cursor.fetchone()[0]
                    db_conn.commit()
                    out_time = datetime.datetime.now().strftime("%I:%M:%S %p")
                    cursor.execute(insert_sql, (out_time, emp_id, in_time))
                    db_conn.commit()
                    isExist = 14

                elif (out_time > in_time):  # else tell them that they have checked out
                    # display message box
                    isExist = 11
                else:
                    # display message box
                    isExist = 2

        else:
            # display message box
            isExist = 3

        return render_template('TakeAttendance.html', emp_id=emp_id, name=name, isExist=isExist)


@app.route("/applyleave", methods=['GET','POST'])
def applyLeave():
    cursor = db_conn.cursor()
    isExist = 21
    insert_sql = "INSERT INTO attendance(in_time, out_time, date, attd_status, leaveurl, emp_id) VALUES(%s, %s, %s, %s, %s, %s)"
    in_time = ""
    out_time = ""
    dates = ""
    emp_id = ""

    if request.method == "POST":
        emp_id = request.values['emp_id']
        emp_image_file = request.files['leave_file']

        if emp_image_file.filename == "":
            return "Please select a file"

        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_leave_evidence_" + str(date.today())
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(
                Key=emp_image_file_name_in_s3, Body=emp_image_file)
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
            print(object_url)

            in_time = datetime.datetime.now().strftime("%I:%M:%S %p")
            print("in:",in_time)

            dates = date.today().strftime("%Y-%m-%d")
            print("date:",dates)

            cursor.execute(
                        insert_sql, (in_time, "", dates, "Leave", object_url, emp_id))
                
            db_conn.commit()

        except Exception as e:
            return str(e)

        finally:
            cursor.close()

    return render_template('UpdateAttdStatus.html', isExist=isExist) 

@app.route("/viewattdlog", methods=['GET'])
def ViewAttdLog():
    flagDate = 0
    flagTime = 0
    cursor = db_conn.cursor()
    name = ""
    isExist = 0
    msg = ""

    emp_id = ""
    fstart = ""
    fend = ""
    intime = ""
    outtime = ""
    values = []

    #insert_sql = "UPDATE attendance SET out_time = %s WHERE emp_id = %s AND in_time = %s"
    getInTime_sql = "SELECT image_url, id, fname, lname, position, attendance.date, in_time, out_time, attd_status FROM employee LEFT JOIN attendance ON employee.id = attendance.emp_id WHERE "  

    if (request.method == 'GET'):
        # request = page, args[''] = query string
        emp_id = request.args['emp_id']
        fstart = request.args['fstart']
        fend = request.args['fend']
        intime = request.args['intime']
        outtime = request.args['outtime']

        if(emp_id != ""):
            getInTime_sql += "employee.emp_id = %s OR "
            values.append(emp_id)

        if(fstart != ""): #have start
            fstart = datetime.datetime.strptime(fstart,"%Y-%m-%d")
            getInTime_sql += "(STR_TO_DATE(attendance.date, '%Y-%m-%d') >= %s OR " 
            flagDate+=1
            values.append(fstart)

        if(flagDate > 0 and fend != ""): #have start have end
            fend = datetime.datetime.strptime(fend,"%Y-%m-%d")
            getInTime_sql = getInTime_sql.rstrip("OR ")
            getInTime_sql += "AND STR_TO_DATE(attendance.date, '%Y-%m-%d') <= %s) OR "
            values.append(fend)

        elif(fend != ""): #no start have end
            fend = datetime.datetime.strptime(fend,"%Y-%m-%d")
            getInTime_sql += "STR_TO_DATE(attendance.date, '%Y-%m-%d') <= %s) OR "
            values.append(fend)

        if(intime != ""): #have start
            intime = datetime.datetime.strptime(intime, "%I:%M:%S %p")
            getInTime_sql += "(in_time >= %s AND in_time <= %s) OR "
            flagTime +=1
            values.append(intime)

        if(flagTime >0 and outtime != ""): #have start have end
            outtime = datetime.datetime.strptime(outtime, "%I:%M:%S %p")
            getInTime_sql = getInTime_sql.rstrip("OR ")
            getInTime_sql += "AND (out_time >= %s AND out_time <= %s)"
            values.append(outtime)

        elif(outtime!=""): #no start have end
            outtime = datetime.datetime.strptime(outtime, "%I:%M:%S %p")
            getInTime_sql += "STR_TO_DATE(attendance.date, '%Y-%m-%d') <= %s) OR "
            values.append(outtime)
            
        cursor.execute(getInTime_sql, tuple(values))
        

        return render_template('TakeAttendance.html', emp_id=emp_id, name=name, isExist=isExist, result=result)

# @@@@@@@@@@Payroll


# DON'T TOUCH!
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
