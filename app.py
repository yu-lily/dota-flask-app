from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

from dotenv import load_dotenv
import os
load_dotenv()

from sql_client import SQLClient

app = Flask(__name__)
db = SQLClient()
cur = db.cur

@app.route("/")
def table():
    cur.execute("SELECT * FROM abilityagg LIMIT 10;")
    return render_template("table.html", cols=cur.description, rows=cur.fetchall())