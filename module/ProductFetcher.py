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
from module import Querier
from module import Product
from module import Graph

from pprint import pprint


def P_fetch_product_details(code, score):
    # Optional items to retrieve from database
    data_env1 = DataEnv.DataEnv(["countries_tags", "categories_tags", "images", "generic_name", "product_name", "similarity", "score"])
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
