from webbrowser import get
from flask import Flask, render_template, request, redirect, session
import sqlite3 as sql

app = Flask(__name__)
app.secret_key = '`fasdgfdgdfg`'


@app.route('/')
def home():
   return render_template('home.html')

@app.route('/addstudent')
def new_student():
   return render_template('add_student.html')

@app.route('/addrec',methods = ['POST', 'GET'])
def addrec():
   
   if request.method == 'POST':
      try:
         name = request.form['name']
         pin = request.form['pin']
         
         
         with sql.connect("student_database.db") as con:
            cur = con.cursor()
            cur.execute("INSERT INTO students (name,pin) VALUES (?,?)",(name,pin) )
            con.commit()
            msg = "Record successfully added!"
      except:
         con.rollback()
         msg = "error in insert operation"
      
      finally:
         return render_template("list.html",msg=msg)
         con.close()

@app.route('/list')
def list():
   con = sql.connect("student_database.db")
   con.row_factory = sql.Row
   
   cur = con.cursor()
   cur.execute("select * from students")
   
   students = cur.fetchall();
   return render_template("list.html", students = students)
@app.route('/sign',methods = ['POST', 'GET'])
def sign():
   
   if request.method == 'GET':
         name = request.values.get("name")
         pin = request.values.get("pin")
         with sql.connect("student_database.db") as con:
          cur = con.cursor()
         statement = f"SELECT name from students WHERE name='{name}' AND Pin= '{pin}';"
         cur.execute(statement)
         if not cur.fetchone():  # An empty result evaluates to False.
           return("Login failed")
         else:
           return("Welcome")
         
       
      

         
         

   
@app.route('/signin')
def signin():
   return render_template('signin.html')  



if __name__ == '__main__':
   app.run(debug = True)