from flask import Flask, render_template, request
from flask_caching import Cache
import json
import psycopg2.extras

from dotenv import load_dotenv
import os
load_dotenv()

from sql_client import SQLClient

app = Flask(__name__)
db = SQLClient()
cur = db.cur
dict_cur = db.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
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


@cache.memoize(timeout=60)
def get_num_matches():
    match_counts = {}
    cur.execute(f"SELECT COUNT(*) FROM matches;")
    conn.commit()
    match_counts['total'] = cur.fetchall()[0][0]

    cur.execute(f"SELECT COUNT(*) FROM matches m WHERE m.startdatetime > (CURRENT_DATE - INTERVAL '3 days');")
    conn.commit()
    match_counts['3d'] = cur.fetchall()[0][0]

    cur.execute(f"SELECT COUNT(*) FROM matches m WHERE m.startdatetime < to_timestamp(1642542300);")
    conn.commit()
    match_counts['prepatch'] = cur.fetchall()[0][0]

    cur.execute(f"SELECT COUNT(*) FROM matches m WHERE m.startdatetime > to_timestamp(1642542300);")
    conn.commit()
    match_counts['postpatch'] = cur.fetchall()[0][0]

    return match_counts

@app.route("/")
def index():
    match_counts = get_num_matches()

    return render_template("index.html", match_counts=match_counts)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/aghs/")
def aghs_index():
    return render_template("aghs.html", heroes=heroes)



@cache.memoize(timeout=60)
def get_ability_data(table_name, hero_name):
    cur.execute(f"SELECT * FROM {table_name} WHERE icon LIKE '%{hero_name}%' LIMIT 100;")
    conn.commit()
    return cur.description, cur.fetchall()

@cache.memoize(timeout=60)
def get_hero_data(table_name, hero_name):
    dict_cur.execute(f"SELECT * FROM {table_name} WHERE shortname LIKE '{hero_name}' LIMIT 100;")
    conn.commit()

    return dict_cur.fetchone()

@app.route(f"/aghs/hero/<hero_name>")
def hero_table(hero_name):
    if hero_name not in all_heroes:
        return "Invalid hero"


    time_window = request.args.get('time', default = 'all', type = str)
    table_suffixes = {
        "all": "",
        "3days": "_3d",
        "prepatch": "_prepatch",
        "postpatch": "_postpatch",
        }
    ab_table = "abilityagg" + table_suffixes.get(time_window, '')
    hero_table = "heroagg" + table_suffixes.get(time_window, '')

    hero_info = get_hero_data(hero_table, hero_name)


    if hero_name == "sand_king":
        hero_name = "sandking"

    cols, rows = get_ability_data(ab_table, hero_name)

    return render_template("aghs_hero.html", cols=cols, rows=rows, hero_info=hero_info, active_page=time_window)

