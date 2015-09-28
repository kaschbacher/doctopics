from flask import render_template, request
from app import app
import pymysql as mdb
from a_Model import ModelIt

# ps auxwww | grep mysql
# look for the port number, mysql default is supposed to be 3306
# this computer has mysql running on 3307

db = mdb.connect(user="root", host="localhost", port=3307, db="world", charset='utf8')

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Kirstin' },
       )

@app.route('/db')
def cities_page():
    with db:
        cur = db.cursor()
        cur.execute("SELECT Name FROM City LIMIT 15;")
        query_results = cur.fetchall()
    cities = ""
    for result in query_results:
        cities += result[0]
        cities += "<br>"
    return cities

@app.route("/db_fancy")
def cities_page_fancy():
    with db:
        cur = db.cursor()
        cur.execute("SELECT Name, CountryCode, Population FROM City ORDER BY Population LIMIT 15;")
        query_results = cur.fetchall()
    cities = []
    for result in query_results:
        cities.append(dict(name=result[0], country=result[1], population=result[2]))
    return render_template('cities.html', cities=cities) 
    
@app.route("/input")
def cities_input():
    return render_template("input.html")

@app.route("/output")
def cities_output():
  #pull 'ID' from input field and store it
  cities = ['one','two','three']

  return render_template("output.html")