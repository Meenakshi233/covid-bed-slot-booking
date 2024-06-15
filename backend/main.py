from flask import Flask,redirect,render_template
from flask_sqlalchemy import SQLAlchemy

# mydatabase connection
local_server = True
app = Flask(__name__)
app.secret_key = "hemmee"

#app.config['SQLALCHEMY_DATABASE_URI']= "mysql://username:password@localhost/databasename"
app.config['SQLALCHEMY_DATABASE_URI']= "mysql://root:@localhost/SARS_Cov_2"
db=SQLAlchemy(app)

class Test(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50))

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/usersignup")
def usersignup():
    return render_template("usersignup.html")

@app.route("/userlogin")
def userlogin():
    return render_template("userlogin.html")

#testing whether db is connected or not
@app.route("/test")
def test():
    try:
        a=Test.query.all()
        print(a)
        return "My database is connected"
    except Exception as e:
        print(e)
        return "My database is not connected"
    
app.run(debug=True)