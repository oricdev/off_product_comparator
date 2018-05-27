# coding=utf-8
from __future__ import division
from collections import Counter
from pprint import pprint
import numpy

from module import PointRepartition
from module import Product
from module import Log


class Graph:
    """
    Handle statistics:
    - gather and prepare data to show
    - build graph
    """

    def __init__(self, stats_props, product_ref, products_others, verbose):
        assert isinstance(product_ref, Product.Product)

        self.verbose = verbose
        self.statsProps = stats_props
        self.product_ref = product_ref
        # x, y coordinates on the graph and label to display for the product reference
        self.prod_ref_real = []
        self.xaxis_prod_ref_real = []
        self.yaxis_prod_ref_real = []
        self.label_prod_ref = []

        self.products_matching = products_others
        # x, y coordinates on the graph and label to display for all matching products
        self.xaxis_others_real = []
        self.yaxis_others_real = []
        self.labels_others = []

        # print "length is %d" % len(self.products_matching)
        # Graph uses its own data set which is a conversion of products_matching: preparation of these datasets
        self.data_set_ref = []
        self.data_set_others = []
        self.xaxis_others_distributed = []
        self.yaxis_others_distributed = []
        self.d3_json = []

    def show(self):
        if self.verbose:
            Log.Log.add_msg("&nbsp;")
            Log.Log.add_msg("GRAPH process started..")

        self.prepare_data()
        return self.prepare_graph()

    def prepare_data(self):
        if self.verbose:
            Log.Log.add_msg("preparing the data..")

        try:
            # preparing product reference
            name_ref_prod = self.get_product_name(self.product_ref.dic_props)
            url_ref_prod = "https://world.openfoodfacts.org/product/%s" % self.product_ref.dic_props["code"]
            url_json = "https://world.openfoodfacts.org/api/v0/produit/%s.json" % self.product_ref.dic_props["code"]
            # print "REF RETRIEVED = "
            # pprint (self.product_ref.dic_props)
            mini_prod = {"code": self.product_ref.dic_props["code"],
                         "name": name_ref_prod,
                         "brands_tags": self.product_ref.dic_props["brands_tags"],
                         "categories_tags": self.product_ref.dic_props["categories_tags"],
                         "url_product": url_ref_prod,
                         "url_json": url_json,
                         # "url_img": "",
                         # "lc": self.product_ref.dic_props["lc"],
                         "languages_codes": self.product_ref.dic_props["languages_codes"],
                         "image_fake_off": \
                             'https://static.openfoodfacts.org/images/misc/openfoodfacts-logo-fr-178x150.png',
                         "no_nutriments": self.product_ref.noNutriments,
                         "score_proximity": self.product_ref.score_proximity,
                         "score_nutrition": self.product_ref.score_nutrition,
                         "x_val_real": self.product_ref.score_proximity,
                         "y_val_real": self.product_ref.convert_scoreval_to_note()
                         # ,
                         # "x_val_graph": self.product_ref.score_proximity,
                         # "y_val_graph": self.convert_scoreval_to_note(self.product_ref.score_nutrition)
                         }
            # print "IMAGE PROD REF="
            # pprint (mini_prod)
            mini_prod['images'] = self.get_url_image(self.product_ref.dic_props)
            # if u'image_small_url' in self.product_ref.dic_props:
            #     mini_prod['images'] = self.product_ref.dic_props["image_small_url"]
            # elif u'image_url' in self.product_ref.dic_props:
            #     mini_prod['images'] = self.product_ref.dic_props["image_url"]
            # else:
            #     mini_prod['images'] = 'https://static.openfoodfacts.org/images/misc/openfoodfacts-logo-fr-178x150.png'
            self.data_set_ref.append(mini_prod)

            # preparing data for all other matching products
            if self.verbose:
                Log.Log.add_msg("computing NUTRITION SCORE for %i products" % len(self.products_matching))

            products_ignored = 0
            products_ignored_codes = []
            products_intersection_too_low = 0
            for product in self.products_matching:
                # product = product.encode('utf-8')
                assert isinstance(product, Product.Product)
                product.compute_scores(self.product_ref)

                if not product.excludeFromGraph and not product.excludeIntersectTooLow:
                    name = self.get_product_name(product.dic_props)
                    if u'brands_tags' in product.dic_props:
                        brands = product.dic_props['brands_tags']
                    else:
                        brands = '??'
                    mini_prod = {"code": product.dic_props["code"],
                                 "name": name,
                                 "brands_tags": brands,
                                 "categories_tags": product.dic_props["categories_tags"],
                                 # "url_product": "",
                                 # "url_img": "",
                                 # "lc": product.dic_props["lc"],
                                 "languages_codes": product.dic_props["languages_codes"],
                                 "score_nutrition": str(product.score_nutrition),
                                 "final_grade": str(product.final_grade),
                                 "image_fake_off": \
                                     'https://static.openfoodfacts.org/images/misc/openfoodfacts-logo-fr-178x150.png'
                                 }
                    if u'images' in product.dic_props:
                        if len(product.dic_props["images"]) > 0:
                            mini_prod["images"] = product.dic_props["images"]

                    # if u"image_small_url" in product.dic_props:
                    #     mini_prod["images"] = product.dic_props["image_small_url"]
                    # elif u"image_url" in product.dic_props:
                    #     mini_prod["images"] = product.dic_props["image_url"]
                    # else:
                    #     mini_prod["images"] = 'https://static.openfoodfacts.org/images/misc/openfoodfacts-logo-fr-178x150.png'
                    mini_prod["score_proximity"] = product.score_proximity
                    mini_prod["score_nutrition"] = product.score_nutrition
                    mini_prod["x_val_real"] = product.score_proximity
                    mini_prod["y_val_real"] = product.final_grade
                    self.xaxis_others_real.append(mini_prod["x_val_real"])
                    self.yaxis_others_real.append(mini_prod["y_val_real"])
                    self.data_set_others.append(mini_prod)
                elif product.excludeFromGraph:
                    products_ignored += 1
                    products_ignored_codes.append(product.dic_props["code"])
                elif product.excludeIntersectTooLow:
                    products_intersection_too_low += 1

            if products_intersection_too_low > 0 and self.verbose:
                Log.Log.add_msg("%i products have a score similarity with product ref. below 50%% and have been excluded" %
                                (products_intersection_too_low))
            if products_ignored > 0 and self.verbose:
                # Log.Log.add_msg("%i additional products have been excluded due to a lack of information (%r)" %
                #                 (products_ignored, products_ignored_codes))
                Log.Log.add_msg("%i additional products have been excluded due to a lack of information" %
                                (products_ignored))
        except Exception:
            self.data_set_others = []
            Log.Log.add_msg("&nbsp;")
            Log.Log.add_msg("sorry, the process has been aborted!")

    def prepare_graph(self):
        """
        Prepare data before building the graph:
        - check that units for extracted properties are the same. If not, perform a conversion
        Algorithm of " Uniformly Distributed Random Points Inside a Circle (2)" here:
        http://narimanfarsad.blogspot.ch/2012/11/uniformly-distributed-points-inside.html
        :return:
        """
        if len(self.data_set_ref) == 0:
            Log.Log.add_msg('')
            Log.Log.add_msg('No data retrieved for the code you have entered!')
        else:
            if self.verbose:
                Log.Log.add_msg('')
                Log.Log.add_msg("for all %i matching products:" % len(self.data_set_others))
                Log.Log.add_msg("&nbsp;&nbsp;&nbsp;&nbsp;computing COORDINATES")

            # prepare for product reference
            nb_categs_ref = len(self.product_ref.dic_props["categories_tags"])
            self.xaxis_prod_ref_real.append(nb_categs_ref * self.data_set_ref[0]["x_val_real"])
            self.yaxis_prod_ref_real.append(self.data_set_ref[0]["y_val_real"])
            label_prod_ref = self.data_set_ref[0]["code"]
            self.label_prod_ref.append(label_prod_ref)

            # prepare for all other matching products
            # .. using a uniform repartition
            sample = PointRepartition.PointRepartition(len(self.data_set_others))
            x, y = sample.new_positions_spherical_coordinates()
            # print "x = %r // y = %r" % (x, y)
            v_x = []
            v_y = []
            for x0, y0 in zip(x, y):
                # print "%r // %r " % (x0[0], y0[0])
                v_x.append(x0[0])
                v_y.append(y0[0])

            if self.verbose:
                Log.Log.add_msg("&nbsp;&nbsp;&nbsp;&nbsp;preparing TOOLTIPS")

            for mini_prod, x0, y0 in zip(self.data_set_others, v_x, v_y):
                x, y = mini_prod["x_val_real"], mini_prod["y_val_real"]
                # print "miniprod = %d, %d" % (x, y)
                # NOTE: since we display 2 graphs (1 for all points, and 1 for the coloured stripes with a specific design
                #  for the CELL matching the product reference, we need to extend the x Values (mult. by nb categs
                #  of product reference)
                # x_coord = nb_categs_ref * (x - (
                #     1 / (2 * nb_categs_ref) * (1 - x0)))
                x_coord = (x - (
                        1 / (2 * nb_categs_ref) * (1 - x0)))
                y_coord = y - (
                    0.5 * (1 - y0))
                # print "computed for display = %d, %d" % (x_dspl, y_dspl)

                self.xaxis_others_distributed.append(x_coord)
                self.yaxis_others_distributed.append(y_coord)
                code_curr_product = mini_prod["code"]
                # print "code product = %r " % code_curr_product
                # if code_curr_product == "0028000682309":
                #     print "stop"
                url_prod = "https://world.openfoodfacts.org/product/%s" % mini_prod["code"]
                url_prod = url_prod.encode('utf-8')
                url_img = self.get_url_image(mini_prod)
                categs = self.get_categories_html(self.data_set_ref[0]["categories_tags"], mini_prod["categories_tags"])
                score_proximity = str(int(mini_prod["score_proximity"]*100))

                # print "URL IMG:"
                # print url_img
                the_label = "<div style='background-color: #e0e0e0'>%s / %s<br /><b>%s</b><br/>" \
                            "<div style ='color: purple'>[Similarity: %s %%]</div>" \
                            "<table><tr><td><img src='%s' width = '85px' /></td>" \
                            "<td style='color: #101010; text-align:right'>%s</td></tr></table>" \
                            "</div>" % \
                            (mini_prod["code"],
                             " // ".join(mini_prod["brands_tags"]),
                             mini_prod["name"],
                             score_proximity,
                             url_img,
                             categs)
                # print "ALL properties of objects: "
                # pprint (mini_prod)
                the_label = the_label.encode('utf-8')
                self.labels_others.append(url_prod)
                self.labels_others.append(the_label)
                # print "d3json.. appending"
                self.d3_json.append({"code": mini_prod["code"],
                                     "x": x_coord, "y": y_coord,
                                     "url": url_prod,
                                     "content": the_label,
                                     "brands": " // ".join(mini_prod["brands_tags"]),
                                     "name": mini_prod["name"],
                                     "score": score_proximity,
                                     "img": url_img,
                                     "categories": categs,
                                     "score_nutrition": mini_prod["score_nutrition"],
                                     "final_grade": mini_prod["final_grade"]})

            # self.prod_ref_real = {"code": self.product_ref.dic_props["code"],
            #                       "generic_name": self.product_ref.dic_props["generic_name"],
            #                       "y": self.yaxis_prod_ref_real,
            #                       "image": self.data_set_ref[0]["image"]
            #                       }
            self.data_set_ref[0]["y"] = self.yaxis_prod_ref_real
            # verbosity details
            # if self.verbose:
            # print
            # pprint("Product ref. x / y: %r ∕ %r" % (self.xaxis_prod_ref_real, self.yaxis_prod_ref_real))
            # pprint("Matching products with COUNTER:")
            # pprint("\t Counter(x): %r" % Counter(self.xaxis_others_real))
            # pprint("\t x = %r" % self.xaxis_others_distributed)
            # pprint("\t Counter(y): %r" % Counter(self.yaxis_others_real))
            # pprint("\t y = %r" % self.yaxis_others_distributed)
            # print
            # print " json for d3 object = %r" % self.d3_json
            return self.data_set_ref[0], self.d3_json
            # return self.d3_json


    def get_product_name(self, props):
        # Consider the smallest product or generic name which is not empty for describing the product
        generic_name = ''
        product_name = ''
        name = ''

        if u'generic_name' in props:
            generic_name = props[u'generic_name']

        if u'product_name' in props:
            product_name = props[u'product_name']

        if len(generic_name) > 0 and len(product_name) > 0:
            if len(generic_name) >= len(product_name):
                name = generic_name
            else:
                name = product_name
        elif len(generic_name) == 0 and len(product_name) == 0:
            name = '??'
        elif len(product_name) == 0:
            name = generic_name
        else:
            name = product_name

        return name

    def get_url_image(self, prod):
        # init
        url_img = ''
        language_to_use_for_pic = ''

        try:
            for lc in prod["languages_codes"]:
                # print "language is %s" % lc
                lc_front = 'front_' + lc
                if 'images' in prod:
                    if lc_front in prod['images']:
                        if len(prod['images'][lc_front]) > 0:
                            if len(language_to_use_for_pic) == 0:
                                # print "the above-one is top!"
                                language_to_use_for_pic = lc_front

            if len(language_to_use_for_pic) > 0:
                front_lbl = language_to_use_for_pic
            else:
                front_lbl = lc_front

            # print front_lbl

            if 'images' in prod:
                if len(prod["code"]) >= 13:
                    url_img = "https://static.openfoodfacts.org/images/products/" + prod["code"][0:3] + "/" \
                              + prod["code"][3:6] \
                              + "/" + prod["code"][6:9] + "/" + prod["code"][9:] \
                              + "/" + front_lbl + "." \
                              + str(prod['images'][front_lbl]["rev"]) \
                              + ".400.jpg"
                else:
                    url_img = "https://static.openfoodfacts.org/images/products/" + prod["code"] \
                              + "/" + front_lbl + "." + str(prod['images'][front_lbl]["rev"]) + ".400.jpg"
            else:
                url_img = prod["image_fake_off"]

        except Exception:
            url_img = prod["image_fake_off"]

        return url_img

    def get_categories_html(self, ref_categs_list, categories):
        # todo: duplicated with app.py => static class/method to use instead
        categories_product = '<div style="padding-bottom: 5px"><b>Categories</b><br /></div><div>'
        for v in categories:
            if v in ref_categs_list:
                categories_product = categories_product + "<b>" + v + "</b><br />"
            else:
                categories_product = categories_product + v + "<br />"

        categories_product = categories_product + '</div>'
        return categories_product
