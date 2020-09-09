# -*- coding: utf-8 -*-
"""
Created on Fri Aug 28 10:33:18 2020

@author: raghav

"""

from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
#from flask_mail import Mail
#import json
#from json import loads
from datetime import datetime
import os
import math

with open('config.json') as c:
    params = c.read()
     
upload_location = "C:\\Users\\admin\\flask_app\\static"

local_server = True
app = Flask(__name__)
app.secret_key = 'super-market'
app.config['UPLOAD_FOLDER'] = upload_location;

#app.config.update(
 #    MAIL_SERVER = ''
  #  )

#app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/codingthunder'
if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/codingthunder'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/codingthunder'

db = SQLAlchemy(app)

class Contacts(db.Model):    
   #   sno, name phone_num, msg, date, email    

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(20), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable = False)
    date = db.Column(db.String(12), nullable=True)
    

class Posts(db.Model):    
   #   sno, name phone_num, msg, date, email    

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(22), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), nullable=True)
    img_file = db.Column(db.String(12), nullable=True)

no_of_posts = 3

@app.route("/")
def home():    
    posts = Posts.query.filter_by().all()
    last = math.ceil(len(posts)) / int(no_of_posts)
    
    page = request.args.get('page')
    if (not str(page).isnumeric()):
        page=1
    
    page = int(page)
    posts = posts[(page-1) *int(no_of_posts): (page-1) *int(no_of_posts) + int(no_of_posts)]
    
    #pagination
    if(page == 1):
        prev = "#"
        next = "/?page=" + str(page+1)
    elif(page==last):
        prev = "/?page=" + str(page-1)
        next = "#"
    else:
        prev = "/?page=" + str(page-1)
        next = "/?page=" + str(page+1)

    return render_template('index.html',params=params, posts = posts,prev=prev,next=next)

    
@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    
    return render_template('post.html',params=params, post=post)


@app.route("/about")
def about():
    return render_template('about.html',params = params)


admin_user = "raghav"
admin_pass = "raghav"

@app.route("/dashboard", methods=['GET','POST'])
def dashboard():
    
    if 'user' in session and session['user'] == admin_user:
        posts = Posts.query.all()
        return render_template('dashboard.html',params=params,posts=posts)
    
    
    if request.method == 'POST':
        # Redirect to ADMIN Pannel
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        
        if (username == admin_user and userpass == admin_pass):
            #set the session variable
            session['user'] = username
            posts = Posts.query.all()
            return render_template('dashboard.html',params=params,posts=posts)
        
    else:
        return render_template('login.html', params= params)


@app.route("/edit/<string:sno>", methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user'] == admin_user:
        if request.method == 'POST':
            box_title = request.form.get('title')
            tagline = request.form.get('tline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            img_file = request.form.get('img_file')
            date = datetime.now()
            
            if sno == '0':
                post = Posts(title=box_title,tagline=tagline,slug=slug,content= content,img_file=img_file,date=date)
                db.session.add(post)
                db.session.commit()
            
            else:
                post.title = box_title
                post.tagline = tagline
                post.slug = slug
                post.content = content
                post.img_file = img_file
                post.date = date
                db.session.commit()
                return redirect('/edit/',sno)
            
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params,post=post)



@app.route("/uploader", methods=['GET','POST'])
def uploader():
    if 'user' in session and session['user'] == admin_user:
        if(request.method == 'POST'):
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return "Uploaded Successfully"
            
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/delete/<string:sno>", methods=['GET','POST'])
def delete(sno):
    if 'user' in session and session['user'] == admin_user:
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/dashboard')


@app.route("/contact", methods=['GET','POST'])
def contact():
    if(request.method == 'POST'):
        # add the entries to the databases by taking from form
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        
        # adding entries to db from above.
        entry = Contacts(name=name,email=email,phone_num=phone, msg=message,date=datetime.now())
        db.session.add(entry)
        db.session.commit()
    
    return render_template('contact.html', params=params)

app.run(debug=True)
