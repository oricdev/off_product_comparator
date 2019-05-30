"""
 * OFF-Graph / OpenFoodFacts Product Comparator
 *
 * Contact: Olivier Richard (oric_dev@iznogoud.neomailbox.ch)
 * License: GNU Affero General Public License v3.0
 * License url: https://github.com/oricdev/off_product_comparator/blob/master/LICENSE
"""
# coding=utf-8
from __future__ import division
from pymongo import MongoClient
from module import Product, DataEnv
from pprint import pprint
import json


class Querier:
    """
    MongoClient Querier
    """

    def __init__(self, scoreDb, data_env, verbose):
        """
        :param verbose: True for verbosity of the Querier
        :return:  nothing
        """
        assert isinstance(data_env, DataEnv.DataEnv)
        self.data_env = data_env
        self.verbose = verbose
        # Log.Log.add_msg("&nbsp;")
        # if verbose:
        #     Log.Log.add_msg("server verbosity = ON")
        # else:
        #     Log.Log.add_msg("server verbosity = OFF")
        # Log.Log.add_msg("&nbsp;")

        self.pongo = None
        self.db = None
        self.db_object = None
        # bottomUp is a property of db object stating where the min value is located vertically in the graph (True means at the bottom)
        self.db_bottom_up = True
        self.db_min_value = 1
        self.db_max_value = 5
        # Determine databse to use for the request
        file_dbs = "./static/data/db_stats.json"
        with open(file_dbs, "r") as fileHandler:
            score_dbs = json.load(fileHandler)

        self.db_name = None
        try:
            for db in score_dbs:
                if self.db_name is None:
                    if db["dbNickname"] == scoreDb:
                        self.db_name = db[u"dbName"]
                        self.db_object = db
                        self.db_bottom_up = db[u"bottomUp"]
                        self.db_min_value = db[u"scoreMinValue"]
                        self.db_max_value = db[u"scoreMaxValue"]

        except Exception:
            self.db_name = "tuttifrutti_nutriscore"
            self.db_object = None

        print "Database being used is: %r" % self.db_name

        self.coll_products = None
        # maximum number of products being retrieved for a single category
        self.limitOfRetrieval = 5

    def P_connect(self):
        """
        Connection to the NEW OFF-Product database
        :return:
        """
        # todo: review since hard-coded!
        # pprint("connecting to OFF MATCH database")
        self.pongo = MongoClient(
            "mongodb://tuttifrutti_reader:reader@mongodb-tuttifrutti.alwaysdata.net/%s" % self.db_name)
        self.db = self.pongo[self.db_name]
        self.coll_products = self.db["Prosim"]
        nb_products_in_db = self.coll_products.find().count()
        # if self.verbose:
        #     pprint("%d products are referenced" % (nb_products_in_db))

        return nb_products_in_db

    def P_disconnect(self):
        """
        Closing connection
        :return:
        """
        # if self.verbose:
        #     pprint("closing connection")
        self.pongo.close()

    def P_fetch(self, prop, val):
        """
        Fecthes PROSIM product
        :param prop: criterium key
        :param val: criterium value
        :return: product
        """
        # preparing projection fields for the find request (no _id)
        fields_projection = {}
        # note: no _id key since it holds the non-serializable ObjectId() staff !
        fields_projection["_id"] = 0
        fields_projection["code"] = 1
        fields_projection["generic_name"] = 1
        fields_projection["product_name"] = 1
        fields_projection["categories_tags"] = 1
        fields_projection["languages_codes"] = 1
        fields_projection["brands_tags"] = 1
        fields_projection["nutriments"] = 1
        fields_projection["images"] = 1
        fields_projection["similarity"] = 1
        fields_projection["score"] = 1

        products_json = self.coll_products.find({
            prop: val
        }, fields_projection)

        print "nb of products found = %s" % (products_json.count())
        if products_json.count() > 0:
            return products_json
        else:
            return {}

    def PG_fetch_sim(self, prod_ref, codes_matching, stats_codes, country, store):
        """
        Fetches all matching products, and filter on country and store if available
        :param codes_matching: list of products' barcodes matching reference product
        :param country: filter criterium
        :param store: filter criterium
        :return: details of all matching products with restriction on a subset because data are used for graph (need optimization)
        """
        products_fetched = []
        # preparing projection fields for the find request (no _id)
        fields_projection = {}
        # fields_projection["_id"] = 0
        fields_projection["code"] = 1
        fields_projection["generic_name"] = 1
        fields_projection["product_name"] = 1
        fields_projection["categories_tags"] = 1
        fields_projection["languages_codes"] = 1
        fields_projection["brands_tags"] = 1
        fields_projection["nutriments"] = 1
        fields_projection["images"] = 1
        fields_projection["score"] = 1
        # do not retrieve similarity, not necessary for matching products
        # fields_projection["similarity"] = 0

        if store != '' and country != '':
            products_json = self.coll_products.find({
                "code": {"$in": codes_matching},
                "countries_tags": country,
                "stores_tags": store
            }, fields_projection)
        elif country != '':
            products_json = self.coll_products.find({
                "code": {"$in": codes_matching},
                "countries_tags": country
            }, fields_projection)
        else:
            products_json = self.coll_products.find({
                "code": {"$in": codes_matching}}, fields_projection)

        print "nb of products found = %s" % (products_json.count())
        prod_ref_grade = prod_ref.score

        # Prepare limiting number of items retrieved for performance-prupose
        # products_counter = {"1": 0, "2": 0, "3": 0, "4": 0, "5": 0}
        products_counter = {}
        for c in range(self.db_min_value, self.db_max_value+1):
            products_counter[str(c)] = 0

        if products_json.count() > 0:
            for product_json in products_json:
                product = Product.Product(product_json)
                product.score_proximity = int(stats_codes[product_json["code"]][0]);
                product.score = int(stats_codes[product_json["code"]][1]);
                # pprint("PRODUCT %s" % product_json["code"])
                # pprint("prox %s / score %s" % (product.score_proximity, product.score))

                # BOTTOMUP = True
                if self.db_bottom_up == True:
                    # for graph, restrict products only to those matching these criteria:
                    # - if similarity below 75%, limit to 50
                    # - if same grade as product reference, limit to 20 (except for 1st row (best scoring) for which there is no limit)
                    # - if matching product grade/score is strictly below to grade of product reference, limit to 50
                    if product.score < prod_ref_grade:
                        if products_counter[str(product.score)] < 50:
                            products_fetched.append(product)
                            products_counter[str(product.score)] = products_counter[str(product.score)] + 1

                    elif product.score_proximity < 75 or ((product.score == prod_ref_grade and prod_ref_grade != self.db_max_value) or (
                            product.score < prod_ref_grade)):
                        if products_counter[str(product.score)] < 50:
                            products_fetched.append(product)
                            products_counter[str(product.score)] = products_counter[str(product.score)] + 1

                    else:
                        # don't count, just add and show in graph
                        products_fetched.append(product)
                else:
                    # BOTTOMUP = False
                    # for graph, restrict products only to those matching these criteria:
                    # - if similarity below 75%, limit to 50
                    # - if same grade as product reference, limit to 20 (except for 1st row (best scoring) for which there is no limit)
                    # - if matching product grade/score is strictly higher to grade of product reference, limit to 50
                    if product.score > prod_ref_grade:
                        if products_counter[str(product.score)] < 50:
                            products_fetched.append(product)
                            products_counter[str(product.score)] = products_counter[str(product.score)] + 1

                    elif product.score_proximity < 75 or ((product.score == prod_ref_grade and prod_ref_grade != self.db_min_value) or (
                            product.score > prod_ref_grade)):
                        if products_counter[str(product.score)] < 50:
                            products_fetched.append(product)
                            products_counter[str(product.score)] = products_counter[str(product.score)] + 1

                    else:
                        # don't count, just add and show in graph
                        products_fetched.append(product)

            return products_fetched
        else:
            return {}

    def PM_fetch_sim(self, codes_matching, stats_codes, country, store):
        """
        Fetches all matching products, and filter on country and store if available
        :param codes_matching: list of products' barcodes matching reference product
        :param country: filter criterium
        :param store: filter criterium
        :return: details of all matching products, NO restriction because not used for graph, just as API
        """
        products_fetched = []
        # preparing projection fields for the find request (no _id)
        fields_projection = {}
        # note: no _id key since it holds the non-serializable ObjectId() staff !
        fields_projection["_id"] = 0
        fields_projection["code"] = 1
        fields_projection["generic_name"] = 1
        fields_projection["product_name"] = 1
        fields_projection["categories_tags"] = 1
        fields_projection["languages_codes"] = 1
        fields_projection["brands_tags"] = 1
        fields_projection["nutriments"] = 1
        fields_projection["images"] = 1
        fields_projection["score"] = 1
        # do not retrieve similarity, not necessary for matching products
        # fields_projection["similarity"] = 0

        if store != '' and country != '':
            products_json = self.coll_products.find({
                "code": {"$in": codes_matching},
                "countries_tags": country,
                "stores_tags": store
            }, fields_projection)
        elif country != '':
            products_json = self.coll_products.find({
                "code": {"$in": codes_matching},
                "countries_tags": country
            }, fields_projection)
        else:
            products_json = self.coll_products.find({
                "code": {"$in": codes_matching}}, fields_projection)

        print "nb of products found = %s" % (products_json.count())
        if products_json.count() > 0:
            for product_json in products_json:
                products_fetched.append(product_json)

            return products_fetched
        else:
            return {}
