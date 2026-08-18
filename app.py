
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///jobs.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

class User(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name=db.Column(db.String(100), nullable=False)
    email=db.Column(db.String(150), unique=True, nullable=False)
    password_hash=db.Column(db.String(255), nullable=False)
    role=db.Column(db.String(20), default="applicant")
    profile=db.Column(db.Text, default="")

class Job(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    title=db.Column(db.String(150), nullable=False)
    company=db.Column(db.String(150), nullable=False)
    location=db.Column(db.String(100), nullable=False)
    description=db.Column(db.Text, nullable=False)
    skills=db.Column(db.String(300), default="")
    created_at=db.Column(db.DateTime, default=datetime.utcnow)
    posted_by=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

class Application(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    job_id=db.Column(db.Integer, db.ForeignKey("job.id"), nullable=False)
    applicant_id=db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    resume=db.Column(db.String(300), default="")
    status=db.Column(db.String(30), default="Applied")
    created_at=db.Column(db.DateTime, default=datetime.utcnow)

with app.app_context(): db.create_all()

def login_required(f):
    @wraps(f)
    def wrap(*a, **kw):
        if "user_id" not in session: return redirect(url_for("login"))
        return f(*a, **kw)
    return wrap

def role_required(role):
    def deco(f):
        @wraps(f)
        def wrap(*a, **kw):
            if session.get("role") != role: return "Forbidden", 403
            return f(*a, **kw)
        return wrap
    return deco

@app.route("/")
def index():
    q=request.args.get("q","").strip()
    query=Job.query
    if q:
        like=f"%{q}%"
        query=query.filter(db.or_(Job.title.ilike(like),Job.company.ilike(like),Job.location.ilike(like),Job.skills.ilike(like)))
    return render_template("index.html", jobs=query.order_by(Job.created_at.desc()).all(), q=q)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        email=request.form["email"].lower().strip()
        if User.query.filter_by(email=email).first():
            flash("Email already registered."); return redirect(url_for("register"))
        role=request.form.get("role","applicant")
        if role not in ("applicant","employer"): role="applicant"
        u=User(name=request.form["name"].strip(), email=email, role=role,
               password_hash=generate_password_hash(request.form["password"]))
        db.session.add(u); db.session.commit()
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        u=User.query.filter_by(email=request.form["email"].lower().strip()).first()
        if u and check_password_hash(u.password_hash,request.form["password"]):
            session.update(user_id=u.id,name=u.name,role=u.role)
            return redirect(url_for("dashboard"))
        flash("Invalid login.")
    return render_template("login.html")

@app.route("/logout")
def logout(): session.clear(); return redirect(url_for("index"))

@app.route("/dashboard")
@login_required
def dashboard():
    if session["role"]=="employer":
        jobs=Job.query.filter_by(posted_by=session["user_id"]).all()
        applications=Application.query.join(Job).filter(Job.posted_by==session["user_id"]).all()
    else:
        jobs=[]
        applications=Application.query.filter_by(applicant_id=session["user_id"]).all()
    return render_template("dashboard.html",jobs=jobs,applications=applications)

@app.route("/jobs/new",methods=["GET","POST"])
@login_required
@role_required("employer")
def new_job():
    if request.method=="POST":
        db.session.add(Job(title=request.form["title"],company=request.form["company"],
            location=request.form["location"],description=request.form["description"],
            skills=request.form["skills"],posted_by=session["user_id"]))
        db.session.commit(); return redirect(url_for("dashboard"))
    return render_template("job_form.html")

@app.route("/jobs/<int:job_id>/apply",methods=["POST"])
@login_required
@role_required("applicant")
def apply(job_id):
    if not Job.query.get_or_404(job_id): return "Not found",404
    exists=Application.query.filter_by(job_id=job_id,applicant_id=session["user_id"]).first()
    if not exists:
        db.session.add(Application(job_id=job_id,applicant_id=session["user_id"],resume=request.form.get("resume","")))
        db.session.commit()
    return redirect(url_for("index"))

@app.route("/applications/<int:app_id>/status",methods=["POST"])
@login_required
@role_required("employer")
def status(app_id):
    a=Application.query.get_or_404(app_id)
    job=Job.query.get(a.job_id)
    if job.posted_by != session["user_id"]: return "Forbidden",403
    a.status=request.form["status"]; db.session.commit()
    return redirect(url_for("dashboard"))

@app.route("/profile",methods=["GET","POST"])
@login_required
def profile():
    u=User.query.get_or_404(session["user_id"])
    if request.method=="POST":
        u.name=request.form["name"]; u.profile=request.form["profile"]; db.session.commit()
    return render_template("profile.html",user=u)

@app.route("/api/jobs")
def api_jobs():
    jobs=Job.query.order_by(Job.created_at.desc()).all()
    return jsonify([{"id":j.id,"title":j.title,"company":j.company,"location":j.location,"skills":j.skills} for j in jobs])

if __name__=="__main__": app.run(debug=True)
