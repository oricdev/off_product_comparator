"""
 * OFF-Graph / OpenFoodFacts Product Comparator
 *
 * Contact: Olivier Richard (oric_dev@iznogoud.neomailbox.ch)
 * License: GNU Affero General Public License v3.0
 * License url: https://github.com/oricdev/off_product_comparator/blob/master/LICENSE
"""
# coding=utf-8
import os
import time
import json
from flask import jsonify
from pymongo import MongoClient


from module import DataEnv
from module import Gui
from module import Querier
from module import Product
from module import Graph
from module import Log

from pprint import pprint


def fetch_product(code, country, store, score, addr):
    print "code is"
    print code
    print "country is %r" % country
    print "store is %r" % store
    print "score is %r" % score
    print "threads prints remote_addr"
    print addr

    # print "session is"
    # pprint(request.args["session"])
    # session["logs"] = ['coucou', 'coco']
    # print "session logs is"
    # pprint(request.session["logs"])
    # ##########################
    # ENTRY POINT FOR THE CODE #
    # ##########################

    # Optional items to retrieve from database
    data_env1 = DataEnv.DataEnv(["countries_tags", "lc", "categories_tags", "generic_name", "product_name"])
    gui = Gui.Gui(data_env1)
    querier = Querier.Querier(score, data_env1, True)

    # connecting to server
    querier.connect()

    prod_code = code
    Log.Log.add_msg("fetching details for reference product '%s'" % prod_code)

    # retrieve product details into object
    products = querier.fetch("code", prod_code)

    all_points = """
        """
    if len(products) == 0:
        Log.Log.add_msg("WARNING: the product with code '%s' could not be found!" % prod_code)
    else:
        if len(products) > 1:
            Log.Log.add_msg("WARNING: more than 1 product match ... choosing 1st product")

        myProduct = products[0]
        assert isinstance(myProduct, Product.Product)
        # Is the  product reference!
        myProduct.set_as_reference(True)
        gui.display(myProduct)

        # fetch similar products with the same categories
        props_to_match = [
            "categories_tags"]  # for the search of similar products based on this set of properties (matching criteria)
        # products_match = querier.find_match_old(myProduct, props_to_match)
        products_match = querier.find_match(myProduct, props_to_match, country, store)
        Log.Log.add_msg(".. NUMBER of matching distinct products found: %d" % len(products_match))

        # for ij in range(0, 10):
        #     print "%d" % ij
        #     gui.display(products_match[ij])
        # print "\t code: %r" % products_match[ij].dic_props["code"]
        # print "\t\t proximity: %r" % products_match[ij].score_proximity
        # print "\t\t nutriments %r" % products_match[ij].dic_props["nutriments"]["nutrition-score-uk"]

        # todo: plus tard
        statsProps = [
            "nutriments"]  # for all products, extracting of these specific items for building the statistical graphs
        g = Graph.Graph(statsProps, myProduct, products_match, True)
        all_points = g.show()

    querier.disconnect()
    Log.Log.add_msg("ALL DONE! .. sending back data to client")
    Log.Log.add_msg("ciao!")
    # BEWARE: DO NOT add any further message, or update
    # adding graph's data to Log for being displayed by the client
    Log.Log.add_msg(all_points)

    return all_points

def P_fetch_product_details(code, score):
    # Optional items to retrieve from database
    data_env1 = DataEnv.DataEnv(["countries_tags", "categories_tags", "images", "generic_name", "product_name", "similarity", "score"])
    gui = Gui.Gui(data_env1)
    querier = Querier.Querier(score, data_env1, True)

    # connecting to server
    querier.P_connect()
    # retrieve product details into object
    products = querier.P_fetch("code", code)
    if products.count() == 0:
        querier.P_disconnect()
        return {}

    querier.P_disconnect()
    return products[0]

def PG_fetch_product(code, country, store, score):
    """ Products for Graph purpose
    Fetches product and similar ones for building the graph
    Note: for optimization, a subset only of matching products is kept
    :param code:
    :param country:
    :param store:
    :return:
    """
    # Optional items to retrieve from database
    data_env1 = DataEnv.DataEnv(["countries_tags", "categories_tags", "images", "generic_name", "product_name", "similarity"])
    gui = Gui.Gui(data_env1)
    querier = Querier.Querier(score, data_env1, True)

    # connecting to server
    querier.P_connect()
    # retrieve product details into object
    products = querier.P_fetch("code", code)
    if type(products) is dict:
        if len(products) == 0:
            return {}
    elif products.count() == 0:
            return {}

    myProduct = Product.Product(products[0])
    assert isinstance(myProduct, Product.Product)
    myProduct.set_as_reference(True)
    #pprint("score = %s" % myProduct.score)

    # retrieve list of all barcodes in tag 'similarity'
    (codes_matching, stats_codes) = myProduct.extract_similarity_codes()
    # fetch details of all these matching products
    products_match = querier.PG_fetch_sim(myProduct, codes_matching, stats_codes, country, store)
    statsProps = [
        "nutriments"]  # for all products, extracting of these specific items for building the statistical graphs
    g = Graph.Graph(statsProps, myProduct, products_match, True)
    all_points = g.show()

    querier.P_disconnect()
    return all_points

def PM_fetch_product(code, country, store, score):
    """ Products for Matching purpose (API)
    Fetches product and similar-ones for API purposes.
    Not intended for tuttifrutti graph
    Note: ALL matching products is returned in raw-format
    :param code:
    :param country:
    :param store:
    :return:
    """
    # Optional items to retrieve from database
    data_env1 = DataEnv.DataEnv(["countries_tags", "categories_tags", "images", "generic_name", "product_name", "similarity"])
    gui = Gui.Gui(data_env1)
    querier = Querier.Querier(score, data_env1, True)

    # connecting to server
    querier.P_connect()
    # retrieve product details into object
    products = querier.P_fetch("code", code)
    if type(products) is dict:
        if len(products) == 0:
            return {}
    elif products.count() == 0:
            return {}

    product_ref = products[0]
    myProduct = Product.Product(products[0])
    assert isinstance(myProduct, Product.Product)
    myProduct.set_as_reference(True)

    # retrieve list of all barcodes in tag 'similarity'
    (codes_matching, stats_codes) = myProduct.extract_similarity_codes()
    # fetch details of all these matching products
    products_match = querier.PM_fetch_sim(codes_matching, stats_codes, country, store)

    querier.P_disconnect()
    return (product_ref, products_match)
