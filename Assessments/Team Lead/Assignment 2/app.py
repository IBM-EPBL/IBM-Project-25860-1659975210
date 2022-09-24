from flask import Flask, url_for, render_template, request, redirect, session,flash
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))

    def __init__(self, username, password,email):
        self.username = username
        self.email = email
        self.password = password
        


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        name = request.form['username']
        passw = request.form['password']
        data = User.query.filter_by(username=name, password=passw).first()
        if data is not None:
            session['logged_in'] = True
            session['name']=name
            return redirect(url_for('home'))
        else:                
            flash('Invalid Credentials ')
            return render_template('login.html')


@app.route('/signup/', methods=['GET', 'POST'])
def signup():
    
    if request.method == 'POST':
        if(request.form['password']==request.form['confirm-password']):
            new_user = User(
                username=request.form['username'],
                email=request.form['email-address'],
                password=request.form['password'],
                )
            db.session.add(new_user)
            db.session.commit()
            flash('Registered Successfully!')
            return render_template('login.html')
        else:
            flash("Password must be Same")
            return render_template('signup.html')
    return render_template('signup.html')


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.debug = True
    db.create_all()
    app.secret_key = "123"
    app.run()
    