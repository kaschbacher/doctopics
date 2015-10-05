from flask import render_template, request
from app import app
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import json 
# KA files
import KAsql2 as ka
import cPickle as pickle


# ps auxwww | grep mysql
# look for the port number, mysql default is supposed to be 3306
# this computer has mysql running on 3307

def get_topics(bid, bid_df):
    """Given arguments: a bid (doctor ID) and the bid_df (dataframe), 
    Extract and return a sorted series for one bid with the top 10 topics
    Eventually, extend this to include the doctor's name. """
    
    all_topics = bid_df.ix[bid,:]#type Series
    all_topics.sort(axis=0, ascending=False)
    doc_topics = all_topics[:5]
    return doc_topics

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html",
       title = 'Home', user = { 'nickname': 'Kirstin' },
       )

def get_yelpid(local_id):
    if local_id.find("Kenneth Akizuki")>-1: 
      yelp_id = 'kenneth-akizuki-md-san-francisco'
      #yelpimg='"static/img/Kenneth_Akizuki.jpg"'
      yelpimg='"static/img/knee.jpg"'
      insight = "Topics involving 'knees' and 'hips' come up frequently. If that's an injury you have too, you might want to read up on this doctor."
      myrev1 = "BID309_Topic17_RID20609.txt"

    if local_id.find("Jon Dickinson")>-1: 
      yelp_id = 'jon-dickinson-md-san-francisco'
      yelpimg='"static/img/Jon_Dickinson.jpg"'
      insight = "This doctor's patients comment often about his hip surgeries."
      myrev1 = "BID319_Topic22_RID20802.txt"
      #bodyimg='"static/img/hip.jpg"'

    if local_id.find("Saxena Amol")>-1: 
      yelp_id = 'saxena-amol-dpm-palo-alto'
      yelpimg='"static/img/Saxena_Amol.jpg"'
      insight = "This doctor's patients may be feeling rushed. They talk a lot about the number of minutes he spent with them."
      myrev1 = "BID588_Topic11_RID23362.txt"

    if local_id.find("Scott M. Taylor")>-1: 
      yelp_id = 'scott-m-taylor-md-oakland'
      yelpimg='"static/img/Taylor.jpg"'
      insight = "His patients are talking a lot about medical injections. Find out more below."
      myrev1 = "BID427_Topic16_RID22088.txt"

    if local_id.find("Gordon A. Brody")>-1: 
      yelp_id = 'gordon-a-brody-md-redwood-city'
      yelpimg='"static/img/injection.jpg"'
      insight = "Yelpers have a lot to say about this doctor's injections."
      myrev1 = "BID566_Topic16_RID23137.txt"
    return [yelp_id, yelpimg, insight, myrev1]

def get_reviews(filename):
    with open(filename, "r") as text_file:
      myreview = text_file.read()#type string  
    #print myreview
    return myreview

@app.route("/output")
def output():

  # Load Dataframes - AWS can't read pickles - outdated pandas version
  #bid_df = pd.read_pickle('bid_tmeans.p')#index of this df is the bid, but can't be indexed by 'BID'
  #bid_topic_word_df = pd.read_pickle('bid_topic_word_df.p')
  #Represent_Revs = pd.read_pickle('Represent_Revs.p')

  # work-around
  f=open('btw_pickled','r')
  output = eval(f.read())
  btw = pickle.loads(output)
  f.close()
  bid_topic_word_df = pd.DataFrame(btw)

  f=open('rr_pickled','r')
  output = eval(f.read())
  rr = pickle.loads(output)
  f.close()
  Represent_Revs = pd.DataFrame(rr)
  
  
  # Initialize defaults
  bstars=''
  insight='No insights yet.'
  keytopic='None'
  myrev1='No Review yet'

  # Given input from Index.html dropdown menu
  # Obtain yelp_id-->BID, image, and insight
  local_id = request.args.get("yelp_id")
  [yelp_id, yelpimg, insight, myrev1] = get_yelpid(local_id) #Map drop-down input to yelp_id and yelpimg (the doctor's picture)
  bid = get_bid(yelp_id)# SQL query to get bid
  print "BID: ",bid

  # Get Doctor's Average Star-Rating
  bstars = get_bstars(bid)

  # Get KeyTopic (capitalize the first letter)
  f = lambda word: word[0].upper()+word[1:]
  bid_topic_word_df.Word = bid_topic_word_df.Word.apply(f)
  keytopic = bid_topic_word_df.Word[bid_topic_word_df.BID==bid].values[0]
  if keytopic == "Minute": keytopic = "Time"
  if bid == 309: keytopic = "Knee/Hip"

  # Query SQL for RID, BID, RSTARS
  star_df = get_rstars()#queries MySQL for data
  #get review stars for that doctor in a sorted list
  doc_stars= star_df.rstars[star_df.BID==bid]#series
  doc_stars.sort('rstars',ascending=False)
  star_list = doc_stars.tolist()
  #print star_list#debug

  # DATA FOR STAR GRAPH
  #make dict of counts for each star-type
  star_count = {}
  star_count[i] =[star_list.count(i) for i in range(5,0,-1)]
  bid_stars = star_count.values()[0]
  print 'VALUES: ',bid_stars#list
  print 'BID: ',bid
  star_names = ['5 Stars','4 Stars','3 Stars','2 Stars','1 Star']

  # SQL query for review text
  # myRID = Represent_Revs.RID[Represent_Revs.BID==bid].values[0]
  # myReview = get_Review(myRID)
  # print myReview
  #path = "'static/img/"
  myReview = get_reviews(myrev1)

  return render_template("output.html", local_id=local_id, yelpimg=yelpimg, insight = insight, 
    star_count=bid_stars, keytopic=keytopic, bstars=bstars, myReview=myReview)


@app.route("/graph")
def vis_figure():
  #vis_id = request.args.get("vis_b	utton")
  return render_template("vis_fig_30t_pos.html")

@app.route("/slides")
def slides():
  print 'inside slides'
  slide_url = "https://docs.google.com/presentation/d/1EqePwqvQakrtjYn2rWd_EXTdg1XfsFMbf-MXwJRyJtA/edit?usp=sharing"
  return render_template(slide_url)


# import KAsql2 as ka
def get_rstars():
    sql = 'SELECT id, business_id, stars FROM ortho.review;' 
    rows = ka.query_SQL(sql)# extracts unique yelp_ids
    df = pd.DataFrame(np.array(rows),columns=['RID','BID','rstars'])
    return df

def get_bid(yelp_id):
    #select id from ortho.business where yelp_id="pang-donald-md-fremont";
    sql = 'SELECT id FROM ortho.business WHERE yelp_id='+'"'+yelp_id+'"'+';' 
    print yelp_id
    print "SQL = ",sql
    rows = ka.query_SQL(sql)# extracts unique yelp_ids
    new_bid = np.array(rows)[0]
    print type(new_bid[0])
    return new_bid[0]

# Yes, this should be condensed with above functions... but little time sigh
def get_bstars(bid):
    sql = 'SELECT stars FROM ortho.business WHERE id='+str(bid)+';' 
    print "SQL = ",sql
    rows = ka.query_SQL(sql)# extracts unique yelp_ids
    bstars = np.array(rows)[0]
    print type(bstars[0])
    print bstars[0]
    return bstars[0]

# def get_Review(myRID):
#     sql = 'SELECT comment FROM ortho.review WHERE id='+str(myRID)+';' 
#     print "SQL = ",sql
#     rows = ka.query_SQL(sql)# extracts unique yelp_ids
#     myReview = np.array(rows)[0]
#     return myReview[0]

