"""
 * OFF-Graph / OpenFoodFacts Product Comparator
 *
 * Contact: Olivier Richard (oric_dev@iznogoud.neomailbox.ch)
 * License: GNU Affero General Public License v3.0
 * License url: https://github.com/oricdev/off_product_comparator/blob/master/LICENSE
"""

# coding=utf-8
import os
import datetime
import time
import json
import urllib
from threading import Thread
from flask import Flask, session, redirect
from flask import copy_current_request_context
# flask-cors makes it possible to allow server-side Ajax requests from any domain:
#  useful if you want to let users access your API using a local Javascript browser.
#  However use it with care and knowing what you do!
# If you don't use import and configure CORS, your local JS files will catch a 'Cross-Origin Request' failure.
# More details here: https://flask-cors.readthedocs.io/en/latest/
from flask_cors import CORS
# from Flask_Session import Session
from flask import jsonify, render_template, request
from pymongo import MongoClient

from module import ProductFetcher
from module import DataEnv
from module import Querier
from module import Product
from module import Graph

from pprint import pprint

app = Flask(__name__)
CORS(app)

# enabling session for storing the logs;
# read https://pythonhosted.org/Flask-Session/
app.secret_key = os.urandom(24)
# app.secret_key = "toto cutugno"
app.config['SESSION_TYPE'] = 'filesystem'

# load countries
file_countries = "./static/data/countries.json"
with open(file_countries, "r") as fileHandler:
    data_countries = json.load(fileHandler)


@app.route("/")
def start():
    pprint("INCOMING (/) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return render_template('index.html')
    #return render_template('site_under_maintenance.html')


@app.route("/testdev")
def startDevMode():
    pprint("INCOMING (/testdev) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return render_template('index_dev.html')
    # return render_template('index.html')


@app.route("/stats")
def showStatsDbs():
    pprint("INCOMING (/stats) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return render_template('stats.html')


@app.route("/blogstats")
def showStatsDbsOnBlog():
    """
    Displays statistics related to the generation of the databases being aggregated (redirect to blog)
    :return:
    """
    pprint("INCOMING (/blogstats/) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return redirect("https://offmatch.blogspot.com/search/label/stats", code=302)


@app.route('/fetchP/', methods=['GET'])
def fetchP():
    """
    Fetches details of 1 single product code, including those in tag 'similarity'
    Raw data, nt intended for tuttifrutti graph
    :return:
    """
    pprint("INCOMING (/fetchP/) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    #pprint("[/fetchP/] request is:%r" % request)

    code = str(request.args.get('barcode'))
    score = str(request.args.get('score'))
    #country = str(request.args.get('country'))
    #store = str(request.args.get('store'))
    if score == 'None':
        score = ''

    product = ProductFetcher.P_fetch_product_details(code, score)
    #ret_data = {"value": product}
    return json.dumps(product)


@app.route('/fetchPMatch/', methods=['GET'])
def fetchPMatch():
    """
    Fetches product reference details (with similarity details) and retrieves
     ALL matching products referenced in tag 'similarity'
     Raw data, nt intended for tuttifrutti graph
    :return:
    """
    pprint("INCOMING (/fetchPMatch/) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    #pprint("[/fetchPMatch/] request is:%r" % request)

    code = str(request.args.get('barcode'))
    country = str(request.args.get('country'))
    store = str(request.args.get('store'))
    score = str(request.args.get('score'))
    if country == 'None':
        country = ''
    if store == 'None':
        store = ''
    if score == 'None':
        score = ''

    (prod_ref, matching_products) = ProductFetcher.PM_fetch_product(code, country, store, score)
    # Log.Log.add_msg("Request received by server!")
    # Log.Log.add_msg("Your IP-address is %s" % request.remote_addr)
    # Log.Log.add_msg("&nbsp;")
    # Log.Log.add_msg("search of matching products started for product %s" % code)
    # Log.Log.add_msg("&nbsp;")
    # pprint("prod_ref = %s" % prod_ref)
    #pprint("prod_match = %s" % matching_products[0])
    ret_data = {
        'product_reference': prod_ref,
        'matching_products': matching_products
    }
    # ret_data_encoded = ret_data.encode('utf-8')
    # return ret_data_encoded
    #return ret_data.decode('utf-8')
    return json.dumps(ret_data, encoding="utf-8")


@app.route('/fetchPGraph/', methods=['GET'])
def fetchPGraph():
    """
    Fetches product reference details (with similarity details) and retrieves a subset of matching
    products referenced in tag 'similarity'
    Data are processed with coordinates, suitable for tuttifrutti graph
    :return:
    """
    pprint("INCOMING (/fetchPGraph/) %s [%s]" % (request.remote_addr, datetime.datetime.now()))

    code = str(request.args.get('barcode'))
    country = str(request.args.get('country'))
    store = str(request.args.get('store'))
    score = str(request.args.get('score'))
    #pprint("score %s" % score)
    if country == 'None':
        country = ''
    if store == 'None':
        store = ''
    if score == 'None':
        score = ''

    all_data = ProductFetcher.PG_fetch_product(code, country, store, score)
    # Log.Log.add_msg("Request received by server!")
    # Log.Log.add_msg("Your IP-address is %s" % request.remote_addr)
    # Log.Log.add_msg("&nbsp;")
    # Log.Log.add_msg("search of matching products started for product %s" % code)
    # Log.Log.add_msg("&nbsp;")
    ret_data = {"graph": all_data}
    return jsonify(ret_data)


@app.route('/fetchStores/', methods=['GET'])
def fetch_stores():
    pprint("INCOMING (/fetchStores/) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    stores = None
    # pprint ("request is:%r" % request)
    country = request.args.get('country')
    print "country is %r" % country
    # check country is registered (e.g.: "en:france")
    if country in data_countries:
        # check if local file exists
        file_stores = "./static/data/stores/stores_%s.json" % country[3:]
        if not os.path.exists(file_stores):
            # file does not exist locally => download it
            url_list_stores_for_country = "https://world.openfoodfacts.org/country/%s/stores.json" % country[3:]
            urllib.urlretrieve(url_list_stores_for_country, file_stores)

        with open(file_stores, "r") as fileHandler:
            stores = json.load(fileHandler)

    return jsonify(stores)


@app.route('/fetchScoreDbs', methods=['GET'])
def fetch_score_dbs():
    pprint("INCOMING (/fetchStats) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    file_stats = "./static/data/db_stats.json"
    with open(file_stats, "r") as fileHandler:
        db_stats = json.load(fileHandler)

    # get modification time
    try:
        mtime = os.path.getmtime(file_stats)
    except OSError:
        mtime = 0
    last_modified_date = time.ctime(mtime)
    ret_stats = {"datefile": last_modified_date, "stats": db_stats}
    return jsonify(ret_stats)

