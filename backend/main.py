
# importing libraries
from flask import Flask, json,redirect,render_template,flash
from flask.globals import request, session
from flask.helpers import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
import logging

from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
import json

import os
from flask_mail import Mail

# database connection
local_server = True
app = Flask(__name__,static_folder='static',template_folder='templates')
app.secret_key = "hemmee"
  

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


#app.config['SQLALCHEMY_DATABASE_URI']= "mysql://username:password@localhost/databasename"
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/covid'
db=SQLAlchemy(app)

# setting login manager inorder to get unique user access
login_manager = LoginManager(app)
login_manager.init_app(app)
login_manager.login_view = 'login'

# Get the directory of the current file (main.py)
current_dir = os.path.dirname(__file__)

# Construct the full path to the config.json file
config_path = os.path.join(current_dir, 'config.json')



with open(config_path,'r') as c:
    params=json.load(c)["params"]


app.config.update(
    MAIL_SERVER= 'smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL= True,
    MAIL_USERNAME= params['gmail-user'],
    MAIL_PASSWORD= params['gmail-password']
)
mail = Mail(app)



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



@app.context_processor
def inject_user():
    return dict(current_user=current_user)

class Test(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(50))

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(100))
    dob=db.Column(db.String(1000))
    
class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    email=db.Column(db.String(100))
    password=db.Column(db.String(1000))
  
    

class Hospitaldata(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(200),unique=True)
    hname=db.Column(db.String(200))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)


class Bookingpatient(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(50),unique=True)
    bedtype=db.Column(db.String(50))
    hcode=db.Column(db.String(50))
    spo2=db.Column(db.Integer)
    pname=db.Column(db.String(50))
    pphone=db.Column(db.String(12))
    paddress=db.Column(db.String(100))

# <------ routing start ------->

@app.route("/")
def home():
    return render_template("index.html")



@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        srfid=request.form.get('srf')
        email=request.form.get('email')
        dob=request.form.get('dob')
        encpassword=generate_password_hash(dob)
        user=User.query.filter_by(srfid=srfid).first()
        emailUser=User.query.filter_by(email=email).first()
        if user or emailUser:
            flash("Email or srfid is already taken","warning")
            return render_template("usersignup.html")
        new_user=User(srfid=srfid,email=email,dob=encpassword)
        db.session.add(new_user)
        db.session.commit()
        flash("SignUp Success Please Login","success")
        return render_template("userlogin.html")
    return render_template("usersignup.html")



@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        dob=request.form.get('dob')
        user=User.query.filter_by(srfid=srfid).first()
        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")

    return render_template("userlogin.html")



@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Hospitaluser.query.filter_by(email=email).first()
        if user and user.password==password:
            login_user(user)
            session['user_id'] = user.id
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("hospitallogin.html")
    return render_template("hospitallogin.html")    




@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        if(username== params['user'] and password==params['password']):
            session['user']=username
            flash("login success","info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/addHospitalUser',methods=['POST','GET'])
def hospitalUser():
   
    if('user' in session and session['user']==params['user']):
        if request.method=="POST":
            hcode=request.form.get('hcode')
            email=request.form.get('email')
            password=request.form.get('password')        
            encpassword = generate_password_hash(password)
            hcode=hcode.upper()      
            emailUser=Hospitaluser.query.filter_by(email=email).first()
            if  emailUser:
                flash("Email is already taken","warning")
                return render_template("addHosUser.html")
            else:
                query=Hospitaluser(hcode=hcode,email=email,password=password)
                db.session.add(query)
                db.session.commit()
                try:
                    mail.send_message('covid care center',
                                        sender=params['gmail-user'],
                                        recipients=[email],
                                        body=f"Welcome! Thanks for choosing us\nYour Login credentials are\nEmail Address: {email}\nPassword: {password}\nHospital Code: {hcode} \n\nDo not share your password\n\nThank you")
                    flash("Data Sent and Inserted Successfully", "warning")
                except Exception as e:
                    flash(f"Failed to send email: {e}", "danger")
                return render_template("addHosUser.html")
    else:
        flash("Login and try Again","warning")
        return render_template("admin.html")
    
    
    
@app.route("/test")
def test():
    try:
        a = Test.query.all()
        print(a)
        return "My database is connected"
    except Exception as e:
        print(e)
        return "My database is not connected"
    
@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logged out admin", "primary")
    return redirect('/admin')

@app.route("/logouthospitaluser")
def logouthospitaluser():
    session.pop('user_id', None)  # Clear user ID from session
    flash("You have been logged out", "info")
    return redirect(url_for('hospitallogin'))  # Redirect to login page after logout



@app.route("/addhospitalinfo",methods=['POST','GET'])
def addhospitalinfo():
    user_id = session.get('user_id')
    if user_id:
        user = Hospitaluser.query.get(user_id)
        if user:
            email = user.email
            posts = Hospitaluser.query.filter_by(email=email).first()
            code = posts.hcode
            postsdata = Hospitaluser.query.filter_by(hcode=code).first()
    

            if request.method=="POST":
                hcode=request.form.get('hcode')
                hname=request.form.get('hname')
                nbed=request.form.get('normalbed')
                hbed=request.form.get('hicubed')
                ibed=request.form.get('icubed')
                vbed=request.form.get('ventbed')
                hcode=hcode.upper()
                huser=Hospitaluser.query.filter_by(hcode=hcode).first()
                hduser=Hospitaldata.query.filter_by(hcode=hcode).first()
                if hduser:
                    flash("Data is already present. You can update it", "primary")
                    return render_template("hospitaldata.html", postsdata=hduser )
                if huser:
                    query=Hospitaldata(hcode=hcode,hname=hname,normalbed=nbed,hicubed=hbed, icubed=ibed,vbed=vbed)
                    db.session.add(query)
                    db.session.commit()
                    flash("Data has been added", "success")
                    return render_template("hospitaldata.html")
                else:
                    flash("Invalid Hospital code", "warning")
                    return render_template("hospitaldata.html")
            else:
                hduser=Hospitaldata.query.filter_by(hcode=code).first()
                if hduser:
                    flash("Data is already present. You can update it", "primary")
                    return render_template("hospitaldata.html", postsdata=hduser )
                return render_template("hospitaldata.html", postsdata = postsdata)

@app.route("/hedit/<string:id>", methods=['POST','GET'])
# @login_required
def hedit(id):
    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubed')
        ibed=request.form.get('icubed')
        vbed=request.form.get('ventbed')
        hcode = hcode.upper()
        existing_record = Hospitaldata.query.filter_by(hcode=hcode).first()
        if existing_record:
            # Update existing record
            existing_record.hname = hname
            existing_record.normalbed = nbed
            existing_record.hicubed = hbed
            existing_record.icubed = ibed
            existing_record.vbed = vbed
            flash("Data has been updated", "success")
            db.session.commit()
            return redirect(url_for('addhospitalinfo'))  
    posts=Hospitaldata.query.filter_by(id=id).first()
    return render_template("hedit.html", posts=posts)


@app.route("/hdelete/<string:id>", methods=['POST','GET'])
# @login_required
def hdelete(id):
    # Query the record by ID
    record_to_delete = Hospitaldata.query.get_or_404(id)

    try:
        # Delete the record
        db.session.delete(record_to_delete)
        db.session.commit()
        flash("Data deleted successfully", "success")
    except Exception as e:
        db.session.rollback()  # Roll back the changes on error
        flash(f"Failed to delete data: {e}", "danger")
    return redirect(url_for('addhospitalinfo')) 


@app.route("/pdetails", methods=['GET'])
# @login_required
def pdetails():
    code=current_user.srfid
    data=Bookingpatient.query.filter_by(srfid=code).first()

    return render_template("details.html",data=data)



@app.route("/slotbooking", methods=['POST','GET'])
@login_required
def slotbooking():
    query = Hospitaldata.query.all()
    if request.method=="POST":
        srfid = request.form.get('srfid')
        bedtype = request.form.get('bedtype')
        hcode = request.form.get('hcode')
        spo2 = request.form.get('spo2')
        pname = request.form.get('pname')
        pphone = request.form.get('pphone')
        paddress = request.form.get('paddress')
        code = hcode
        try:
            # Query the record by hcode
            hospital_record = Hospitaldata.query.filter_by(hcode=code).first()

            if not hospital_record:
                flash("Hospital record not found", "danger")
                return redirect(url_for('some_view'))  # Replace 'some_view' with the appropriate view name

            # Update the appropriate bed type
            if bedtype == "Normalbed":
                if hospital_record.normalbed > 0:
                    hospital_record.normalbed -= 1
                    booking_successful = True
                else:
                    booking_successful = False
                    flash("No normal beds available in this hospital", "warning")
            elif bedtype == "HICUbed":
                if hospital_record.hicubed > 0:
                    hospital_record.hicubed -= 1
                    booking_successful = True
                else:
                    booking_successful = False
                    flash("No HICU beds available in this hospital", "warning")
            elif bedtype == "ICUbed":
                if hospital_record.icubed > 0:
                    hospital_record.icubed -= 1
                    booking_successful = True
                else:
                    booking_successful = False
                    flash("No ICU beds available in this hospital", "warning")
            elif bedtype == "Ventilatorbed":
                if hospital_record.vbed > 0:
                    hospital_record.vbed -= 1
                    booking_successful = True
                else:
                    booking_successful = False
                    flash("No ventilator beds available in this hospital", "warning")
            else:
                booking_successful = False
                flash("Invalid bed type", "danger")
            
            if booking_successful:
                db.session.commit()
                # Insert patient data into Bookingpatient table
                new_patient = Bookingpatient(
                    srfid=srfid,
                    bedtype=bedtype,
                    hcode=hcode,
                    spo2=spo2,
                    pname=pname,
                    pphone=pphone,
                    paddress=paddress
                )
                db.session.add(new_patient)
                db.session.commit()
                flash("Your bed slot is booked successfully", "success")

        except Exception as e:
            db.session.rollback()
            flash(f"An error occurred: {e}", "danger")


    return render_template("booking.html", query = query)



# <------ routing end -------->

if __name__ == "__main__":
    app.run(debug=True)