from __future__ import print_function
from flask import Flask, url_for, render_template, request, redirect, session, flash
import ibm_db

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=815fa4db-dc03-4c70-869a-a9cc13f33084.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30367;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=pfd63832;PWD=zwaHYyyJwyf52umN",'','')

from datetime import date



app = Flask(__name__)

currentMonth=date.today()
import os
from flask_mail import Mail, Message

# configuration of mail
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'os.environ.get("username")'
app.config['MAIL_PASSWORD'] = 'os.environ.get("password")'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
   

def sendmail(email):
   msg = Message(
                'ALERT',
                sender ='esvar60@gmail.com',
                recipients = [email]
               )
   msg.body = 'Your Expense Amount reached limit . Visit the tracker to check the datails'
   mail.send(msg)
   return 'sent'


@app.route('/')
def home():
    return render_template('home.html')

def getWallet():
    sql = "SELECT AMOUNT FROM WALLET WHERE USERID=?"
    stmt = ibm_db.prepare(conn, sql)        
    ibm_db.bind_param(stmt, 1,session['id'])
    ibm_db.execute(stmt)
    data=ibm_db.fetch_assoc(stmt)
    return data        

def ExpenseCount():
    sql = "SELECT COUNT(*) FROM EXPENSES WHERE USERID=?"
    stmt = ibm_db.prepare(conn, sql)        
    ibm_db.bind_param(stmt, 1,session['id'])
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt) 
    return data  


def categorylist():
    categoryList=['Food','Shopping','Transport','Movie','Healthcare']
    sql = "SELECT * FROM category WHERE userid=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session['id'])
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt)
    while data!=False:
        categoryList.append(data["NAME"])
        data=ibm_db.fetch_assoc(stmt)
    return categoryList


def current_month_expense_amount():
    sql="SELECT SUM(AMOUNT) FROM EXPENSES WHERE MONTH(DATEOFEXPENSE)=? AND YEAR(DATEOFEXPENSE)=? AND USERID=?"
    stmt = ibm_db.prepare(conn, sql)       
    ibm_db.bind_param(stmt, 1,currentMonth.month)
    ibm_db.bind_param(stmt, 2,currentMonth.year)
    ibm_db.bind_param(stmt, 3,session['id'])
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt) 
    return data


def GetCatergoryMonth():  
    Category=[] 
    sql = "SELECT CATEGORY FROM EXPENSES WHERE MONTH(DATEOFEXPENSE)=? AND  USERID=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, currentMonth.month)
    ibm_db.bind_param(stmt, 2, session['id'])
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt)
    while data!=False:
        Category.append(data["CATEGORY"])
        data=ibm_db.fetch_assoc(stmt)
    return Category
    
def GetCatergoryYear():  
    Category=[] 
    sql = "SELECT CATEGORY FROM EXPENSES WHERE userid=?"
    stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(stmt, 1, session['id'])
    ibm_db.execute(stmt)
    data = ibm_db.fetch_assoc(stmt)
    while data!=False:
        Category.append(data["CATEGORY"])
        data=ibm_db.fetch_assoc(stmt)
    print(Category)
    return Category
    


def monthExpense():
    category=GetCatergoryMonth()
    finalData=[]
    temp1=[]
    temp2=[]
    for value in category:
        
        sql="SELECT SUM(AMOUNT) FROM EXPENSES WHERE CATEGORY=? AND MONTH(DATEOFEXPENSE)=? AND YEAR(DATEOFEXPENSE)=?  AND USERID=?"
        stmt = ibm_db.prepare(conn, sql)     
        ibm_db.bind_param(stmt, 1,value)  
        ibm_db.bind_param(stmt, 2,currentMonth.month)
        ibm_db.bind_param(stmt, 3,currentMonth.year)
        ibm_db.bind_param(stmt, 4,session['id'])
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt)
        
        if data["1"]!=None:
            temp1.append(value)
            temp2.append(data["1"])

    finalData.append(temp1)
    finalData.append(temp2)
    return finalData


def yearExpense():
    category=GetCatergoryYear()
    finalData=[]
    temp1=[]
    temp2=[]
    for value in category:
        
        sql="SELECT SUM(AMOUNT) FROM EXPENSES WHERE CATEGORY=? AND  YEAR(DATEOFEXPENSE)=?  AND USERID=?"
        stmt = ibm_db.prepare(conn, sql)     
        ibm_db.bind_param(stmt, 1,value)  
        ibm_db.bind_param(stmt, 2,currentMonth.year)
        ibm_db.bind_param(stmt, 3,session['id'])
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt)
        if data["1"]!=None:
            temp1.append(value)
            temp2.append(data["1"])
            
    finalData.append(temp1)
    finalData.append(temp2)
    return finalData

@app.route('/dashboard')
def dashboard():
    monthExp=monthExpense()
    yearExp=yearExpense()
    current_month_expense=current_month_expense_amount()
    wallet=getWallet()
    expense=ExpenseCount()
    if current_month_expense and wallet:
      if current_month_expense["1"] >wallet["AMOUNT"]:
         SendMail(session['email'])


    return render_template('dashboard.html',wallet=wallet,expense=expense,
    current_month_expense=current_month_expense,month=monthExp,year=yearExp
  
   
    )



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        passw = request.form['password']
        sql = "SELECT * FROM users WHERE email=? and password=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.bind_param(stmt, 2, passw)
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt)
        if data:
            session['logged_in'] = True
            session['name'] = data["NAME"]
            session['id']=data["ID"]
            session['email']=data['EMAIL']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid Credentials!')
            return render_template('login.html',error=True)


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    if request.method == "GET":
        return render_template('signup.html')
    else:
        name=request.form['name']
        email = request.form['email']
        passw = request.form['password']
        sql = "SELECT * FROM users WHERE email=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, email)
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt)
        if not data:
            if len(passw)>7:
                if (request.form['password'] == request.form['confirm-password']):
                    insert_sql = "INSERT INTO users(EMAIL,NAME,PASSWORD) VALUES (?,?,?)"
                    prep_stmt = ibm_db.prepare(conn, insert_sql)
                    ibm_db.bind_param(prep_stmt, 1,email)
                    ibm_db.bind_param(prep_stmt, 2,name)
                    ibm_db.bind_param(prep_stmt, 3,passw)
                    ibm_db.execute(prep_stmt)
                    flash('Registered Successfully!')
                    return  redirect(url_for('login'))
                else:
                    flash("Password must be same")
                    return redirect(url_for('signup'))
            else:
                flash("Length should be greater than 8")
                return redirect(url_for('signup'))
        else:
            flash("Email is already exist")
            return redirect(url_for('signup'))


@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home'))






@app.route("/AddCategory", methods=['GET', 'POST'])
def addCategory():
    if request.method == "GET":
        sql = "SELECT * FROM category WHERE userid=?"
        stmt = ibm_db.prepare(conn, sql)
        ibm_db.bind_param(stmt, 1, session['id'])
        ibm_db.execute(stmt)
        categ=[]
        data = ibm_db.fetch_assoc(stmt)
        while data!=False:
            categ.append(data)
            data=ibm_db.fetch_assoc(stmt)
        return render_template('addCategory.html',CAT=categ)
    if request.method=="POST":
        insert_sql = "INSERT INTO category(userid,name,description) VALUES (?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1,session['id'])
        ibm_db.bind_param(prep_stmt, 2,request.form['name'].capitalize())
        ibm_db.bind_param(prep_stmt, 3,request.form['description'])
        ibm_db.execute(prep_stmt)
        flash('Category added successfully')
        return redirect(url_for('addCategory'))



@app.route('/delete/<id>/')
def deleteCategory(id):
    sql = "DELETE FROM CATEGORY WHERE ID=?"
    prep_stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(prep_stmt, 1,id)
    ibm_db.execute(prep_stmt)
    flash("Category deleted successfully")
    return redirect(url_for('addCategory'))

 
@app.route('/expense/delete/<id>')
def deleteExpense(id):
    sql = "DELETE FROM EXPENSES WHERE ID=?"
    prep_stmt = ibm_db.prepare(conn, sql)
    ibm_db.bind_param(prep_stmt, 1,id)
    ibm_db.execute(prep_stmt)
    flash("Expense deleted successfully")
    return redirect(url_for('addExpense'))

@app.route('/AddExpense/', methods=['GET', 'POST']) 
def addExpense():
    if request.method == "GET":
        CATEGorylist=categorylist()
        return render_template('addExpense.html',CATEGorylist=CATEGorylist)
    if request.method=='POST':
        amount=request.form['amount']
        categoryname=request.form['category']
        date=request.form['date']
        insert_sql = "INSERT INTO expenses(userid,amount,category,dateofexpense) VALUES (?,?,?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1,session['id'])
        ibm_db.bind_param(prep_stmt, 2,amount)
        ibm_db.bind_param(prep_stmt, 3,categoryname)
        ibm_db.bind_param(prep_stmt, 4,date)
        ibm_db.execute(prep_stmt)
        flash("Expense added successfully")
        return redirect(url_for('addExpense'))


@app.route('/expense/history',methods=["GET","POST"]) 
def ExpenseHistory():
    if request.method=="GET":
        sql = "SELECT * FROM EXPENSES WHERE USERID=? ORDER BY DATEOFEXPENSE DESC"
        stmt = ibm_db.prepare(conn, sql)        
        ibm_db.bind_param(stmt, 1,session['id'])
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt)    
        Expenses=[]
        i=0
        while (data!=False and i<5):
            Expenses.append(data)
            data=ibm_db.fetch_assoc(stmt)
            i=i+1
        print(Expenses)
        return render_template('expensehistory.html',Expense=Expenses ,num=5)
    if request.method=="POST":
        start=request.form['startDate']
        end=request.form['EndDate']
        print(end)
        sql="SELECT * FROM EXPENSES WHERE DATEOFEXPENSE BETWEEN ? AND ? AND USERID=?"
        stmt = ibm_db.prepare(conn, sql)        
        ibm_db.bind_param(stmt, 1,start)
        ibm_db.bind_param(stmt, 2,end)
        ibm_db.bind_param(stmt, 3,session['id'])
        ibm_db.execute(stmt)
        data = ibm_db.fetch_assoc(stmt) 
        
        Expenses=[]
        while (data!=False):
            Expenses.append(data)
            data=ibm_db.fetch_assoc(stmt)
        return render_template("expensehistory.html",Expense=Expenses)

@app.route('/wallet')
def wallet():
    is_wallet=getWallet()
    return render_template('wallet.html',is_wallet=is_wallet)


@app.route('/AddWallet',methods=["GET","POST"])
def AddWallet():
    if request.method=="POST":
        insert_sql = "INSERT INTO wallet(userid,amount) VALUES (?,?)"
        prep_stmt = ibm_db.prepare(conn, insert_sql)
        ibm_db.bind_param(prep_stmt, 1,session['id'])
        ibm_db.bind_param(prep_stmt, 2,request.form["amount"])
        ibm_db.execute(prep_stmt)
        flash('Wallet added successfully')
        return redirect(url_for('addExpense'))


@app.route('/UpdateWallet',methods=["GET","POST"])
def UpdateWallet():
    if request.method=="POST":
        sql="UPDATE WALLET SET AMOUNT=? WHERE ID=? AND USERID=?"
        stmt = ibm_db.prepare(conn, sql) 
        ibm_db.bind_param(stmt, 1,request.form["newamount"]) 
        ibm_db.bind_param(stmt, 2,1)
        ibm_db.bind_param(stmt, 3,session['id'])
        ibm_db.execute(stmt)
        flash("Wallet updated successfully")
        return redirect(url_for('wallet'))
        


if __name__ == '__main__':
    app.debug = True
    app.secret_key = "123"
    app.run()
