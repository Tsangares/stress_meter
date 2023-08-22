from flask_login import current_user, UserMixin, LoginManager, login_required, login_user, logout_user
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
import hashlib
import os
import logging
load_dotenv()

# Hash password with SECRET_KEY as salt
def hash_pass(password):
    return hashlib.sha256((password + os.getenv("SECRET_KEY")).encode('utf-8')).hexdigest()

def set_secret(app):
    app.secret_key = os.getenv("SECRET_KEY")

def get_login_manager(app):
    login_manager = LoginManager()
    login_manager.init_app(app)
    return login_manager

class User(UserMixin):
    def __init__(self, data=None):
        logging.error(str(data))
        if data is not None:
            self.id = data['username']
            self.password = data['password']



# app is a Flask app and session is a neo4j session
def init_accounts(app, session):
    set_secret(app)
    login_manager = get_login_manager(app)

    # Find a username and password match using the neo4j database
    def find_user(username,password):
        user = session.run("MATCH (node:User {username: $USERNAME, password: $PASSWORD}) RETURN node", {'USERNAME': username, 'PASSWORD': password}).single()
        if user is not None:
            return User(user.data()['node'])
        return user

    @app.route('/login', methods=['GET','POST'])
    def page_login():
        if request.method == 'GET':
            return render_template('/pages/login.html')
        
        # Get username and password from form
        username = request.form['username']
        password = request.form['password']

        #Validate password is not empty
        if password == '':
            return render_template('/pages/login.html', error='Password is empty')
        
        password = hash_pass(password)

        # Find a username and password match using the neo4j database
        user = find_user(username,password)

        # If no match then create a new user in the neo4j database
        if user is None:
            session.run("CREATE (node:User {username: $USERNAME, password: $PASSWORD})", {'USERNAME': username, 'PASSWORD': password})
            user = find_user(username,password)
        if login_user(user):
            return redirect('/')
        else:
            return render_template('/pages/login.html', error='Invalid username or password')

    login_manager.login_view = 'page_login'

    @login_manager.user_loader
    def load_user(username):
        user = User()
        user.id = username
        return user
    
    @login_manager.request_loader
    def load_user_from_request(request):
        username = request.form.get('username',None)
        password = request.form.get('password',None)
        if username is None or password is None:
            return None
        password = hash_pass(password)
        
        user = find_user(username,password)
        return user
    
    @login_manager.unauthorized_handler
    def unauthorized_handler():
        return redirect(url_for('page_login'))
    
    return login_manager
