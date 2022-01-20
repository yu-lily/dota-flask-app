from flask import Flask, render_template, request
from flask_caching import Cache
import json

from dotenv import load_dotenv
import os
load_dotenv()

from sql_client import SQLClient

app = Flask(__name__)
db = SQLClient()
cur = db.cur
conn = db.conn

config = {
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 300
}
app.config.from_mapping(config)
cache = Cache(app)


with open('heroes.json', 'r') as f:
    heroes = json.load(f)
    #ATTRIBUTES = ['str', 'agi', 'int']
    all_heroes = []
    for attribute in heroes.keys():
        all_heroes.extend(heroes[attribute])

@app.route("/")
def index():
    cur.execute(f"SELECT COUNT(*) FROM matches;")
    conn.commit()

    return render_template("index.html", num_matches = cur.fetchall())

@app.route("/about")
def about():
    return render_template("about.html")


print(all_heroes)

@app.route("/aghs/")
def aghs_index():
    return render_template("aghs.html", heroes=heroes)

@cache.memoize(timeout=60)
def get_hero_data(table_name, hero_name):
    cur.execute(f"SELECT * FROM {table_name} WHERE icon LIKE '%{hero_name}%' LIMIT 100;")
    conn.commit()
    return cur.description, cur.fetchall()

@app.route(f"/aghs/hero/<hero_name>")
def hero_table(hero_name):
    time_window = request.args.get('time', default = 'all', type = str)
    tables = {
        "all": "abilityagg",
        "3days": "abilityagg_3d",
        "prepatch": "abilityagg_prepatch",
        "postpatch": "abilityagg_postpatch",
        }
    table_name = tables[time_window]

    if hero_name not in all_heroes:
        return "Invalid hero"
    if hero_name == "sand_king":
        hero_name = "sandking"

    cols, rows = get_hero_data(table_name, hero_name)

    return render_template("aghs_hero.html", cols=cols, rows=rows, hero_name=hero_name)

