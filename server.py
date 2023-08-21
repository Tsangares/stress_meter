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
#from neo4j import GraphDatabase
#driver = GraphDatabase.driver(os.getenv("NEO4J_URI"), auth=(os.getenv("NEO4J_USER"), os.getenv("NEO4J_PASSWORD")))
#session = driver.session()

@app.route('/')
def index():
    return render_template('/pages/index.html')

if __name__ == '__main__':
    app.run(debug=True)