from flask import Flask, url_for, render_template, request, redirect, session, flash
import ibm_db
conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=815fa4db-dc03-4c70-869a-a9cc13f33084.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=30367;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=pfd63832;PWD=eTBT9FvOEaVoSk1V", '', '')
from datetime import date



app = Flask(__name__)

currentMonth=date.today()


def getWallet():
    sql = "SELECT AMOUNT FROM WALLET WHERE USERID=?"
    stmt = ibm_db.prepare(conn, sql)        
    ibm_db.bind_param(stmt, 1,session['id'])
    ibm_db.execute(stmt)
    data=ibm_db.fetch_assoc(stmt)
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



@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return redirect(url_for('dashboard'))

app.route('/login', methods=['GET', 'POST'])
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
        sql="UPDATE WALLET SET AMOUNT=? WHERE USERID=?"
        stmt = ibm_db.prepare(conn, sql) 
        ibm_db.bind_param(stmt, 1,request.form["newamount"]) 
        ibm_db.bind_param(stmt, 2,session['id'])
        ibm_db.execute(stmt)
        flash("Wallet updated successfully")
        return redirect(url_for('wallet'))
        


if __name__ == '__main__':
    app.debug = True
    app.secret_key = "123"
    app.run()
