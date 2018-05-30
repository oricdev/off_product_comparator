# coding=utf-8
import os
import time
from threading import Thread
from flask import Flask, session
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
# # Session(app)
# SESSION_TYPE = 'redis'
# app.config.from_object(__name__)
# Session(app)


@app.route("/")
def helloAjax():
    # return render_template('index.html')
    return render_template('site_under_maintenance.html')

@app.route("/admin")
def helloAjaxAdmin():
    return render_template('index_full.html')
    # return render_template('site_under_maintenance.html')

@app.route("/dev")
def devAjax():
    return render_template('index.html')

@app.route('/fetchAjax/', methods=['GET'])
def fetchAjax():
    pprint("[/fetchAjax/] request is:%r" % request)

    code = str(request.args.get('barcode'))
    country = str(request.args.get('country'))
    store = str(request.args.get('store'))
    # initialize log for user's Ajax requests
    Log.Log()
    all_data = ProductFetcher.fetch_product(code, country, store, request.remote_addr)
    Log.Log.add_msg("Request received by server!")
    Log.Log.add_msg("Your IP-address is %s" % request.remote_addr)
    Log.Log.add_msg("&nbsp;")
    Log.Log.add_msg("search of matching products started for product %s" % code)
    Log.Log.add_msg("&nbsp;")
    ret_data = {"value": all_data}
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
    pongo = MongoClient("mongodb://tuttifrutti_oric:Oric1!@mongodb-tuttifrutti.alwaysdata.net/tuttifrutti_off")
    db = pongo["tuttifrutti_off"]
    coll_products = db["products"]
    print "%d products are referenced" % (coll_products.find().count())
    strCountProducts = str(coll_products.find().count())
    strOutput = """<h1>Product comparator</h1><br />
    This site uses data from the <b><a href='http://www.openfoodfacts.org' title='openfoodfacts' target='_blank'>
    Open Food Facts</a></b> database.<br />
    <br />
    <b>""" + strCountProducts + """</b> products are referenced.<br />
    <br />
    Enter a product reference to start the comparison with similar products: <input id='product_code' type='text'
      value='3560070800384' />
    <input type='submit' style='background-color: blue; color: white'
    value='Go!' onclick="window.location='http://tuttifrutti.alwaysdata.net/fetch/'+
    document.getElementById('product_code').value+''" /><br />
    <br />
    <div style='color: grey'>NOTE: the number of products shown is intentionally limited.<br />
    Once you've launched the request, you may wait a few seconds<br />
    before being able to see the resulting graph. Please be patient..!
    """
    return strOutput


@app.route('/fetchStores/', methods=['GET'])
def fetch_stores():
    pprint ("request is:%r" % request)
    country = request.args.get('country')
    print "country is %r" % country
    print "fetching stores.."
    Log.Log()
    data_env1 = DataEnv.DataEnv(["countries_tags", "stores_tags"])
    gui = Gui.Gui(data_env1)
    querier = Querier.Querier(data_env1, True)

    # connecting to server
    querier.connect()

    # retrieve stores for the country
    stores = querier.fetch_stores(country)

    querier.disconnect()
    # reset Log (request accomplished)
    Log.Log()
    return jsonify(stores)


@app.route('/fetchone/<string:code>', methods=['GET'])
def fetch_single(code):
    a_product = fetch_single_product(code)
    Log.Log.add_msg("product fetched is:")
    pprint (a_product.dic_props)
    return "%r" % a_product.dic_props


@app.route('/fetch/<string:code>', methods=['GET'])
def fetch(code):
    all_points = fetch_product(code)
    return output_html(code, all_points)


def fetch_single_product(code):
    data_env1 = DataEnv.DataEnv(["code", "generic_name", "product_name", "countries_tags",
                                  "categories_tags", "brands_tags", "nutriments", "images"])
    gui = Gui.Gui(data_env1)
    querier = Querier.Querier(data_env1, True)

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

