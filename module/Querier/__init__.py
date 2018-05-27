# coding=utf-8
from __future__ import division
from pymongo import MongoClient
from module import Product, DataEnv
from module import Log
from pprint import pprint

class Querier:
    """
    MongoClient Querier
    """

    def __init__(self, data_env, verbose):
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
        self.coll_products = None
        # maximum number of products being retrieved for a single category
        self.limitOfRetrieval = 5

    def connect(self):
        """
        Connection to the OFF-Product database
        :return:
        """
        if self.verbose:
            Log.Log.add_msg("connecting to OPENFOODFACTS database")
        # todo: set here your own hard-coded connection details to your MongoDb instance
        self.pongo = MongoClient("mongodb://<user>:<password>@<mongodb_url>/<mongodb_path>")
        self.db = self.pongo["<mongodb_path>"]
        self.coll_products = self.db["products"]
        if self.verbose:
            Log.Log.add_msg("%d products are referenced" % (self.coll_products.find().count()))
        # create appropriate index if missing
        self.coll_products.create_index([("categories_tags", 1)], name='categories_tags')

    def disconnect(self):
        """
        Closing connection
        :return:
        """
        if self.verbose:
            Log.Log.add_msg("closing connection")
        self.pongo.close()

    def fetch_stores(self, country):
        stores_json = self.coll_products.distinct("stores_tags",
                                                  {"countries_tags": country})
        # print "stores are %r" % stores_json
        return stores_json

    def fetch_single(self, prop, val):
        products_fetched = []
        products_json = self.coll_products.find({
            prop: val
        })
        if products_json.count() > 0:
            for product_json in products_json:
                products_fetched.append(Product.Product(product_json))

        return products_fetched[0]

    def fetch(self, prop, val):
        """
        Fecthes all products matching a single criterium
        :param prop: criterium key
        :param val: criterium value
        :return: list of Product
        """
        products_fetched = []
        # preparing projection fields for the find request (no _id)
        fields_projection = {}
        for a_prop in self.data_env.prod_props_to_display:
            fields_projection[a_prop] = 1
        # id, code and categories always retrieved (used as filter criteria = projection)
        fields_projection["_id"] = 1
        fields_projection["code"] = 1
        fields_projection["generic_name"] = 1
        fields_projection["product_name"] = 1
        fields_projection["categories_tags"] = 1
        fields_projection["brands_tags"] = 1
        fields_projection["nutriments"] = 1
        fields_projection["images"] = 1
        fields_projection["languages_codes"] = 1

        # if self.verbose:
        #     Log.Log.add_msg(".. fetching product details with { %s: %r } .." % (prop, val))

        products_json = self.coll_products.find({
            prop: val
        }, fields_projection)
        # products_json = self.coll_products.find({
        #      prop: val
        #  })
        if products_json.count() > 0:
            for product_json in products_json:
                products_fetched.append(Product.Product(product_json))

        if self.verbose:
            if len(products_fetched) < self.limitOfRetrieval:
                Log.Log.add_msg("\t %s \t\t --> found %d" % (val, len(products_fetched)))
            else:
                Log.Log.add_msg("\t %s \t\t --> found %d reduced to %d (LIMITED)" % \
                                (val, len(products_fetched), self.limitOfRetrieval))

        return products_fetched[0:self.limitOfRetrieval]
        # return products_fetched

    def find_match_old(self, a_product, properties_to_match):
        """
        Perform a find for each watched criterion in aProduct
        :param properties_to_match: property-set for finding matching products
        :param a_product:  product with watched criteria
        :return: list of unique products matching the watched criteria of the aProduct
        """
        assert isinstance(a_product, Product.Product)
        if self.verbose:
            Log.Log.add_msg("&nbsp;")
            Log.Log.add_msg("MATCHING process.. looking for matching products in eah category")

        tmp_matching_products = {}  # dictionary in order to avoid duplicates
        _id_prod_ref = a_product.get_id()
        for criterium in properties_to_match:
            for crit_value in a_product.dic_props[criterium]:
                prods = self.fetch(criterium, crit_value)
                # add matching products (no duplicate since we are using a dictionary)
                for prod in prods:
                    # print "QUERY result product listing of all fields::"
                    # pprint (prod)
                    assert isinstance(prod, Product.Product)
                    # removing identity product / add product
                    _id_prod = prod.get_id()
                    if _id_prod != _id_prod_ref:
                        if not (_id_prod in tmp_matching_products):
                            tmp_matching_products[_id_prod] = prod
                        # else:
                        #     assert isinstance(tmp_matching_products[_id_prod], Product.Product)
                        #     tmp_matching_products[_id_prod].incr_intersection_with_ref()

        # build a simple list from the temporary dictionary and return it
        matching_products = list(tmp_matching_products.values())

        return matching_products

    def find_match(self, a_product, properties_to_match, country, store):
        """
        Perform a find for each watched criterium in aProduct
        :param properties_to_match: property-set for finding matching products
        :param a_product:  product with watched criteria
        :return: list of unique products matching the watched criteria of the aProduct
        """
        assert isinstance(a_product, Product.Product)
        Log.Log.add_msg("&nbsp;")
        Log.Log.add_msg("MATCHING process started for:")
        Log.Log.add_msg("&nbsp;&nbsp;country: %r" % country)
        Log.Log.add_msg("&nbsp;&nbsp;shop&nbsp;&nbsp;&nbsp;: %r" % store)

        _id_prod_ref = a_product.get_id()
        products_fetched = []
        # preparing projection fields for the find request (no _id)
        fields_projection = {}
        for a_prop in self.data_env.prod_props_to_display:
            fields_projection[a_prop] = 1
        # id, code and categories always retrieved
        fields_projection["_id"] = 1
        fields_projection["code"] = 1
        fields_projection["generic_name"] = 1
        fields_projection["product_name"] = 1
        fields_projection["categories_tags"] = 1
        fields_projection["brands_tags"] = 1
        fields_projection["nutriments"] = 1
        fields_projection["images"] = 1
        fields_projection["languages_codes"] = 1

        products_json = []
        if store != '' and country != '':
            products_json = self.coll_products.find({
                "categories_tags": {'$in': a_product.dic_props["categories_tags"]
            }, "countries_tags": country, "stores_tags": store}, fields_projection)
        elif country != '':
            products_json = self.coll_products.find({
                "categories_tags": {'$in': a_product.dic_props["categories_tags"]
                                    }, "countries_tags": country}, fields_projection)
        else:
            products_json = self.coll_products.find({
                "categories_tags": {'$in': a_product.dic_props["categories_tags"]
                                    }}, fields_projection)
        if products_json.count() > 0:
            for product_json in products_json:
                product = Product.Product(product_json)
                # removing identity product / add product
                _id_prod = product.get_id()
                if _id_prod != _id_prod_ref:
                    products_fetched.append(product)

        # build a simple list from the temporary dictionary and return it
        return products_fetched