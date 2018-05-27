# coding=utf-8
import os
import time
from flask import jsonify
from pymongo import MongoClient


from module import DataEnv
from module import Gui
from module import Querier
from module import Product
from module import Graph
from module import Log

from pprint import pprint


def fetch_product(code, country, store, addr):
    print "code is"
    print code
    print "country is %r" % country
    print "store is %r" % store
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
    querier = Querier.Querier(data_env1, True)

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
