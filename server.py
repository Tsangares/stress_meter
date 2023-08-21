# Description: This file is the main server file for the application.
import flask 
from flask import Flask, render_template, request, redirect, url_for, jsonify
from dotenv import load_dotenv
from io import BytesIO
from datetime import datetime
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

def add_stressor(name,level,is_stress_relax,description):
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    stressor = {
        'NAME': name,
        'LEVEL': level,
        'STRESS_RELAX': is_stress_relax,
        'DESCRIPTION': description,
        'DATE': date
    }
    return session.run("CREATE (s:Stressor {NAME: $NAME, LEVEL: $LEVEL, STRESS_RELAX: $STRESS_RELAX, DESCRIPTION: $DESCRIPTION, DATE: $DATE}) RETURN s", stressor)

def get_stressors():
    nodes = session.run("MATCH (node:Stressor) RETURN node").data()
    return [node['node'] for node in nodes]

@app.route('/fonts')
def show_all_fonts():
    return render_template('/pages/fonts.html')

@app.route('/archive')
def page_archive():
    nodes = get_stressors()
    return render_template('/pages/archive.html',nodes=nodes)


@app.route('/', methods=['GET'])
def page_prompt_stressor():
    return render_template('/pages/index.html')

@app.route('/', methods=['POST'])
def page_set_stressor():
    def validate(form):
        if form['name'] == '':
            return False
        if form['level'] == '':
            return False
        if form['is_stress_relax'] == '':
            return False
        if form['description'] == '':
            return False
        return True

    if validate(request.form):
        add_stressor(request.form['name'],request.form['level'],request.form['is_stress_relax'],request.form['description'])
        return redirect(url_for('page_archive'))
        #return render_template('/pages/index.html',results=dict(request.form))
    else:
        return render_template('/pages/index.html',results=dict(request.form)|{'error':'Please fill out all fields'})


if __name__ == '__main__':
    app.run(debug=True)