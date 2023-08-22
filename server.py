# Description: This file is the main server file for the application.
import flask 
from flask import Flask, render_template, request, redirect, url_for, jsonify
import flask_login
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime
from accounts import *
import math, random, os ,logging, json

# Basic startup
load_dotenv()
app = Flask(__name__)

# Setup MongoDB
#from flask_pymongo import PyMongo
#app.config["MONGO_URI"] = os.getenv("MONGO_URI")
#mongo = PyMongo(app)

# Setup OpenAI
#import openai
#openai.api_key = os.getenv("OPENAI_API_KEY")

# Setup neo4j
from neo4j import GraphDatabase
driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))
session = driver.session()

# Setup accounts
login_manager = init_accounts(app,session)

def add_stressor(name,topic, level,is_stress_relax,description):
    username = flask_login.current_user.id
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stressor = {
        'NAME': name,
        'TOPIC': topic,
        'LEVEL': level,
        'STRESS_RELAX': is_stress_relax,
        'DESCRIPTION': description,
        'DATE': date
    }
    return session.run("MATCH (u:User WHERE u.username = '"+username+"') CREATE (node:Stressor {name: $NAME, topic: $TOPIC, level: $LEVEL, stress_relax: $STRESS_RELAX, description: $DESCRIPTION, date: $DATE})<-[:EXPRESSED]-(u) RETURN node", stressor).single().value()

def get_stressors():
    username = flask_login.current_user.id
    # Get only stressors with the name of the username
    nodes = session.run(f"MATCH (node:Stressor WHERE node.name = '{username}') RETURN node").data()
    nodes = reversed([n['node'] for n in nodes])
    return nodes

@app.route('/fonts')
def show_all_fonts():
    return render_template('/pages/fonts.html')

@app.route('/archive', methods=['GET','POST'])
@flask_login.login_required
def page_archive():
    nodes = get_stressors()
    return render_template('/pages/archive.html',nodes=nodes)


@app.route('/', methods=['GET'])
@flask_login.login_required
def page_prompt_stressor():
    return render_template('/pages/index.html')

@app.route('/', methods=['POST'])
@flask_login.login_required
def page_set_stressor():
    def validate(form):
        if form['name'] == '':
            return False
        if form['topic'] == '':
            return False
        if form['level'] == '':
            return False
        if form['is_stress_relax'] == '':
            return False
        if form['description'] == '':
            return False
        return True

    if validate(request.form):
        add_stressor(request.form['name'],request.form['topic'],request.form['level'],request.form['is_stress_relax'],request.form['description'])
        return redirect(url_for('page_archive'))
        #return render_template('/pages/index.html',results=dict(request.form))
    else:
        return render_template('/pages/index.html',results=dict(request.form)|{'error':'Please fill out all fields'})


if __name__ == '__main__':
    app.run(host="0.0.0.0",port=5000,debug=True)