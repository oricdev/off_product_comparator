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
# from Flask_Session import Session
from flask import jsonify, render_template, request
from pymongo import MongoClient

from module import ProductFetcher
from module import DataEnv
from module import Gui
from module import Querier
from module import Product
from module import Graph
from module import Log

from pprint import pprint

app = Flask(__name__)
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
def helloAjax():
    pprint("INCOMING (/) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return render_template('index.html')
    #return render_template('site_under_maintenance.html')

@app.route("/admin")
def helloAjaxAdmin():
    pprint("INCOMING (/admin) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return render_template('index_full.html')
    # return render_template('site_under_maintenance.html')

# Leave /test since JS filters dbs (see 'filterDatabases')
@app.route("/testdev")
def devAjax():
    pprint("INCOMING (/testdev) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return render_template('index_dev.html')
    # return render_template('index.html')

@app.route("/test")
def testAjax():
    pprint("INCOMING (/test) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return render_template('index_test.html')

@app.route("/stats")
def statsAjax():
    pprint("INCOMING (/stats) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return render_template('stats.html')

@app.route('/fetchAjax/', methods=['GET'])
def fetchAjax():
    pprint("INCOMING (/fetchAjax) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    #pprint("[/fetchAjax/] request is:%r" % request)

    code = str(request.args.get('barcode'))
    country = str(request.args.get('country'))
    store = str(request.args.get('store'))
    score= str(request.args.get('score'))

    # initialize log for user's Ajax requests
    Log.Log()
    all_data = ProductFetcher.fetch_product(code, country, store, score, request.remote_addr)
    Log.Log.add_msg("Request received by server!")
    Log.Log.add_msg("Your IP-address is %s" % request.remote_addr)
    Log.Log.add_msg("&nbsp;")
    Log.Log.add_msg("search of matching products started for product %s" % code)
    Log.Log.add_msg("&nbsp;")
    ret_data = {"graph": all_data}
    return jsonify(ret_data)

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

@app.route('/logAjax/', methods=['GET'])
def logAjax():
    from_ptr = int(request.args.get('fromPtr'))
    # print "logAjax.."
    # print from_ptr
    bunch = Log.Log.get_bunch(from_ptr)
    ret_data = {"value": bunch}
    if len(bunch) > 2 and bunch[len(bunch)-2] == "ciao!":
        # clear Log in order to allow other incoming requests
        Log.Log()

    return jsonify(ret_data)


@app.route("/hello")
def hello():
    pprint("INCOMING (/hello/) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    return redirect("https://offmatch.blogspot.com/search/label/stats", code=302)

    # data_env1 = DataEnv.DataEnv(
    #     ["countries_tags", "categories_tags", "images", "generic_name", "product_name", "similarity"])
    # querier = Querier.Querier("", data_env1, True)
    # # connecting to server
    # nb_products_in_db = querier.P_connect()
    # querier.P_disconnect()
    # strCountProducts = str(nb_products_in_db)
    # strOutput = """<h1>PROSIM Engine Stats</h1><br />
    # The <b>PROSIM engine</b> aggregates data from the <a href='http://www.openfoodfacts.org' title='openfoodfacts' target='_blank'>
    # Open Food Facts</a> database in order to deliver matching products with similarity and scoring details (nutrition-score, nova-score, ... depending on the state of the art).<br />
    # <br />
    # <b>""" + strCountProducts + """</b> products are actually referenced.<br />
    # <br />Find more details or build your own customized engine by visiting its <a href="https://offmatch.blogspot.com/" target="_blank">official blog</a>.
    # """
    # return strOutput


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

@app.route('/fetchone/<string:score>/<string:code>', methods=['GET'])
def fetch_single(code):
    a_product = fetch_single_product(code, score)
    Log.Log.add_msg("product fetched is:")
    pprint (a_product.dic_props)
    return "%r" % a_product.dic_props


@app.route('/fetch/<string:score>/<string:code>', methods=['GET'])
def fetch(code):
    pprint("INCOMING (/fetch/score/code) %s [%s]" % (request.remote_addr, datetime.datetime.now()))
    all_points = fetch_product(code, score)
    return output_html(code, all_points)


def fetch_single_product(code, score):
    data_env1 = DataEnv.DataEnv(["code", "generic_name", "product_name", "countries_tags",
                                  "categories_tags", "brands_tags", "nutriments", "images"])
    gui = Gui.Gui(data_env1)
    querier = Querier.Querier(score, data_env1, True)

    # connecting to server
    querier.connect()

    # prod_code = "3017620429484"
    # prod_code = "8001505005592"
    # prod_code = "3456778743224"
    prod_code = code
    Log.Log.add_msg(".. fetching default product with code '%s'" % prod_code)

    # retrieve product details into object
    product = querier.fetch_single("code", prod_code)

    querier.disconnect()
    return product





def get_categories_html(ref_categs_list, categories):
    # todo: duplicated with Graph.py => static class/method to use instead
    categories_product = '<div style="padding-bottom: 5px"><b>Categories</b><br /></div><div>'
    for v in categories:
        if v in ref_categs_list:
            categories_product = categories_product + "<b>" + v + "</b><br />"
        else:
            categories_product = categories_product + v + "<br />"

    categories_product = categories_product + '</div>'
    return categories_product


def output_html(code, points):

    prod_ref = points[0]
    print "FINAL prod ref ="
    pprint (prod_ref)
    if str(points).startswith('\n'):
        # product does not exist in the database
        prod_ref_code = code
        prod_ref_name = 'Unkown product!'
        prod_ref_y = '1'
        url_off_prod = 'https://world.openfoodfacts.org'
        prod_ref_categories = ''
        url_off_json_prod = ''
        str_prod_others_points = '[]'
    else:
        prod_ref, prod_others_points = points
        prod_ref_code = str(prod_ref["code"])
        prod_ref_name = prod_ref["name"]
        prod_ref_categories = get_categories_html([], prod_ref["categories_tags"])
        prod_ref_image = prod_ref["images"]
        prod_ref_y = str(prod_ref["y"])
        url_off_prod = "https://world.openfoodfacts.org/product/" + prod_ref_code
        url_off_json_prod = "https://fr.openfoodfacts.org/api/v0/produit/" + prod_ref_code + ".json"
        # prod_ref_code = "3564700700938"
        # prod_ref_name = "nutella"
        # prod_ref_y = "1"
        # url_off_prod = "https://world.openfoodfacts.org/product/" + prod_ref_code
        # url_off_json_prod = "https://fr.openfoodfacts.org/api/v0/produit/" + prod_ref_code + ".json"
        # prod_others_points = points[1]
        # prod_others_points = points
        str_prod_others_points = str(prod_others_points)

    out_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <style> /* set the CSS */

        body {
            font: 10px Arial;
        }

        .axis path,
        .axis line {
            fill: none;
            stroke: grey;
            stroke-width: 1;
            shape-rendering: crispEdges;
        }

        div.tooltip {
            position: absolute;
            text-align: center;
            width: 450px;
            height: 140px;
            padding: 2px;
            font: 10px sans-serif;
            background: lightsteelblue;
            border: 0px;
            border-radius: 8px;
            pointer-events: none;
        }

        </style>
    </head>
    <body bgcolor='#e8e8e8'>
    <div style='width: 975px; text-align: right;'>
    <table style='width: 975px; text-align: right'>
        <tr style = "text-align: left; font-size: 16pt; background-color: red; color: white;">
            <td colspan="2" style='border-radius: 5px;'><a href='https://world.openfoodfacts.org' target='_blank'>OPENFOODFACTS</a>
             PRODUCT COMPARATOR .. in construction</td>
        </tr>
        <tr>
            <td style='border-radius: 5px;'>
            <table><tr style='text-align: right; vertical-align: top; background-color: #d0d0d0;'>
            <td>
                <img src='""" + prod_ref_image + """' height='176' />
            </td>
            <td style='padding: 2ex;'>
            """ + prod_ref_categories + """
            </td>
            </tr>
            </table>
            </td>
            <td >
            <p style='font-size: 16pt;'><b>""" + prod_ref_code + """</b> &nbsp;&nbsp;""" + prod_ref_name + """</p>
            <p style='font-size: 14pt;'>
            <b>White circle: </b>Your selected product &nbsp;&nbsp;
            <a href='""" + url_off_prod + """' target='_blank'>
            <img src='https://static.openfoodfacts.org/images/favicon/apple-touch-icon-57x57.png' width='28'
            title='see the product details in the openfoodfacts website.' />
            </a><a href='""" + url_off_json_prod + """' target='_blank'>
            <img
            src='https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/JSON_vector_logo.svg/160px-JSON_vector_logo.svg.png'
            width='28'
            title='see json details for the product (best seen on Firefox).' />
            </a>
            </p><br />
            <p>Product reference:
                <input id='product_code' type='text' value='' />
                <input type='submit' value='Go!' onclick="window.location='http://tuttifrutti.alwaysdata.net/fetch/'+
                document.getElementById('product_code').value+''" />
            </p>
            </td>
        </tr>
    </table>

    <p style='font-size: 12pt;'>Enter a product reference in the above field,
    or click on a blue spot below to show the own graph of the selected product.<br /><br />
    <span style='text-decoration: underline'>Note:</span>
    the SIMILARITY between your product and another-one is the intersection of
    common categories for these two products.
    </p>
    </div>

    <!-- load the d3.js library -->
    <script src="http://d3js.org/d3.v3.min.js"></script>

    <script>

        // Set the dimensions of the canvas / graph
        var margin = {top: 30, right: 30, bottom: 60, left: 50},
                width = 1000 - margin.left - margin.right,
                height = 600 - margin.top - margin.bottom;

        //    alert(height);
        //    alert(width);
        //    // Parse the date / time
        //    var parseDate = d3.time.format("%d-%b-%y").parse;
        //    var formatTime = d3.time.format("%e %B");

        // Set the ranges
        //    var x = d3.time.scale().range([0, width]);
        //    var y = d3.scale.linear().range([height, 0]);

        var x = d3.scale.linear().range([0, width]);
        var y = d3.scale.linear().range([height, 0]);

        var nb_categs = 7;
        var nb_nutrition_grades = 5;

        // Define the axes
        var xAxis = d3.svg.axis().scale(x)
                .orient("bottom").ticks(nb_categs)
                .tickFormat(function (d) {
                    if (d == 0)
                        return "low";
                    if (d == 1)
                        return "high";
                    return "";
                });

        var yAxis = d3.svg.axis().scale(y)
                .orient("left")
                .ticks(nb_nutrition_grades)
                .tickFormat(function (d) {
                    if (d == 1)
                        return "E";
                    if (d == 2)
                        return "D";
                    if (d == 3)
                        return "C";
                    if (d == 4)
                        return "B";
                    if (d == 5)
                        return "A";
                    return "";
                });

        // Define the div for the tooltip
        var div = d3.select("body").append("div")
                .attr("class", "tooltip")
                .style("opacity", 0);

        // Adds the svg canvas
        var svg = d3.select("body")
                .append("svg")
                .attr("width", width + margin.left + margin.right)
                .attr("height", height + margin.top + margin.bottom)
                .append("g")
                .attr("transform",
                        "translate(" + margin.left + "," + margin.top + ")");

                // Scale the range of the data
                x.domain([0, 1]);
        y.domain([0, nb_nutrition_grades]);

        // TODO: ajouter les stripes en s'inspirant du code ci-dessous
        // *****
        var data_rect = [{'v': 1, 'color': 'rgb(230,62,17)'}, {'v': 2, 'color': 'rgb(238,129,0)'}, {
            'v': 3,
            'color': 'rgb(254,203,2)'
        }, {'v': 4, 'color': 'rgb(133,187,47)'}, {'v': 5, 'color': 'rgb(3,129,65)'}]
        svg.selectAll("rect")
                .data(data_rect)
                .enter()
                .append("rect")
                .attr("width", width)
                .attr("height", height / 5)
                .attr("y", function (d) {
                    return (5 - d.v) * height / 5
                })
                .attr("fill", function (d) {
                    return d.color
                })
                .attr("fill-opacity", .7);
        // *****

        // Add the scatterplot
        // .. for the product reference
        var data_prod_ref = [{'nutrition_grade': """ + prod_ref_y + """}]
        svg.selectAll("ellipse")
                .data(data_prod_ref)
                .enter().append("ellipse")
                .attr("cx", width * (1 - (1 / nb_categs) / 2))
                .attr("cy", function (d) {
                    return (height * (1 - (d.nutrition_grade / nb_nutrition_grades)) + (height / nb_nutrition_grades * 0.5));
                })
                .attr("rx", width / nb_categs * 0.5)
                .attr("ry", (height / nb_nutrition_grades) * 0.5)
                .attr("fill", "#ffffff")
                .attr("fill-opacity", 0.75)
        // .. for all matching products
        var data_others = """ + str_prod_others_points + """;

            svg.selectAll("circle")
                .data(data_others)
                .enter().append("circle")
                .attr("r", 3)
                .attr("stroke", "#000080")
                .attr("stroke-width", 1)
                .attr("fill", "steelblue")
                .attr("cx", function (d) {
                    return d.x * width;
                })
                .attr("cy", function (d) {
                    return height * (1 - d.y / nb_nutrition_grades);
                })
                .on("mouseover", function (d) {
                    div.transition()
                            .duration(200)
                            .style("opacity", .85);
                    div.html(d.content)
                            .style("left", (d3.event.pageX) + "px")
                            .style("top", (d3.event.pageY - 28) + "px");
                })
                .on("mouseout", function (d) {
                    div.transition()
                            .duration(500)
                            .style("opacity", 0);
                })
                .on("click", function (d) {
                    window.open(d.url);
                });

        // Add the X Axis
        svg.append("g")
                .attr("class", "x axis")
                .attr("transform", "translate(0," + height + ")")
                .call(xAxis);

        // Add the X-axis label
        svg.append("text")
                .attr("x", width * 0.5)
                .attr("y", height + 30)
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .style("font-size", "12pt")
                .text("Similarity with product reference");

        // Add the Y Axis
        svg.append("g")
                .attr("class", "y axis")
                .call(yAxis);

        // Add the Y-axis label
        svg.append("text")
                .attr("transform", "rotate(-90)")
                .attr("x", -(height * 0.5))
                .attr("y", -45)
                .attr("dy", "1em")
                .style("text-anchor", "middle")
                .style("font-size", "12pt")
                .text("Nutrition grade");

    </script>
    </body>
    </html>
    """
    return out_html

