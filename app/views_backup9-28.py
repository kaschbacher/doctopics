from flask import render_template, request
from app import app
import cPickle as pickle

# ps auxwww | grep mysql
# look for the port number, mysql default is supposed to be 3306
# this computer has mysql running on 3307

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Kirstin' },
       )
    
@app.route("/input")
def cities_input():
    return render_template("input.html")

def get_topics(bid, bid_df):
    """Given arguments: a bid (doctor ID) and the bid_df (dataframe), 
    Extract and return a sorted series for one bid with the top 10 topics
    Eventually, extend this to include the doctor's name. """
    all_topics = bid_df.ix[bid,:]#type Series
    all_topics.sort(axis=0, ascending=False)
    doc_topics = all_topics[:10]
    return doc_topics

@app.route("/output")
def output():
  #pull 'ID' from input field and store it
  #cities = ['one','two','three']
  #table_dict = pickle.load(open('table_dict.p','rb'))
  local_id = request.args.get("yelp_id")
  yelpimg = "error"
  bid=5
  if local_id.find("Mohammad Diab")>-1: 
    yelpimg='"static/img/bid10 mohammad.jpg"'
    bid=10
  if local_id.find("Keith W Chan")>-1: 
    yelpimg='"static/img/bid14 KeithChan.jpg"'
    bid=14
  if local_id=="Nikolaj Wolfson": 
    yelpimg='"static/img/bid16 nikolaj wolfson.jpg"'
    bid=16
  topicimg = '"'+'static/img/bid'+str(bid)+'.png"'

  bid_df = pickle.load(open('bid_tmeans.p', 'rb'))#Made in LDA_Doctor_Topics
  topic_word_df = pickle.load(open('topic_word_df.p','rb'))#Made in Get_words
  doc_topics = get_topics(bid, bid_df)#returns series of 10 topics in sorted order
  selected = doc_topics.index
  # Make a Topic-Word Table
  topic_table = topic_word_df.loc[selected,:]
  words_lol = topic_table.values.tolist()

  return render_template("output.html", local_id=local_id, yelpimg=yelpimg, topicimg=topicimg,
    words_lol=words_lol)

@app.route("/graph")
def vis_figure():
  #vis_id = request.args.get("vis_b	utton")

  return render_template("vis_fig_30t_pos.html")




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