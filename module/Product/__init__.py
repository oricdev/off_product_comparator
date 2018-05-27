# coding=utf-8
from __future__ import division
from module import Log


class Product:
    def __init__(self, properties):
        # product reference (no by default)
        self.isRef = False
        # Nb of categories' intersections with reference product:
        # while fetching similar products, always 1 at creation since there was a match on a category
        self.nb_categories_intersect_with_ref = 0
        # Proximity with product reference is computed later on
        self.score_proximity = 0  # X-axis
        self.score_nutrition = 0  # Y-axis
        self.final_grade = 1  # default grade (E)
        self.dic_props = properties
        # exclude from graph if no comparison possible (no nutriment information available for instance)
        self.excludeFromGraph = False
        # exclude from graph if similarity with reference product too low (nb categories intersections too low)
        self.excludeIntersectTooLow = False
        # We can add exclusion criteria such as:
        #  * generic-name is empty
        self.noNutriments = False

    def get_id(self):
        return self.dic_props["_id"]

    def set_as_reference(self, is_ref):
        self.isRef = is_ref
        if is_ref:
            self.score_proximity = 1
            # compute also the nutrition score
            self.calc_score_nutrition()

    def incr_intersection_with_ref(self):
        """
        When a match on category is found with product reference, then we increment the number of intersected categories
        in order to speed up a bit the proximity computation thereafter
        :return:
        """
        self.nb_categories_intersect_with_ref += 1

    def compute_scores(self, product_ref):
        self.calc_intersect_categories(product_ref)
        self.calc_score_proximity(product_ref)
        self.calc_score_nutrition()
        self.calc_final_grade()

    def calc_intersect_categories(self, product_ref):
        categs_product = self.dic_props["categories_tags"]
        categs_prod_ref = product_ref.dic_props["categories_tags"]
        for categ in categs_product:
            if categ in categs_prod_ref:
                self.nb_categories_intersect_with_ref += 1

    def calc_score_proximity(self, product_ref):
        """
        The bigger the intersection of categories between self and product_ref, the closer
        Note: if intersection is 100%, then proximity is 100%
        Proximity = nb_categ_intersect / nb_categ_prod_ref
        :rtype: None
         :param product_ref:
         :return:
         """
        assert isinstance(product_ref, Product)
        nb_categs_ref = len(product_ref.dic_props["categories_tags"])
        self.score_proximity = self.nb_categories_intersect_with_ref / nb_categs_ref
        if self.score_proximity < 0.5:
            self.excludeIntersectTooLow = True
        # print "SCORE:"
        # print self.get_id()
        # print self.nb_categories_intersect_with_ref
        # print self.score_proximity
        # print "------"

    def calc_score_nutrition(self):
        """
        see : http://fr.openfoodfacts.org/score-nutritionnel-france
        :return:
        """
        nutriments = self.dic_props["nutriments"]

        if not ("nutrition-score-uk" in nutriments):
            self.noNutriments = True
            # add security in case this is the product reference (we want it to be shown in the graph)
            if self.isRef:
                # fake nutrition score which will be processed separatly on JS-side (9 is average score=middle of graph)
                self.score_nutrition = 9
                self.score_proximity = 0
            else:
                self.excludeFromGraph = True
        else:
            # todo: to be reviewed for waters, countries, etc., as explained in the above url
            # initialize: Data Environment, Gui for display, and Querier
            self.score_nutrition = int(nutriments["nutrition-score-uk"])

    def calc_final_grade(self):
        self.final_grade = self.convert_scoreval_to_note()

    def convert_scoreval_to_note(self):
        # todo: distinguer Eaux et Boissons des aliments solides .. ici, que aliments solides
        # ici http://fr.openfoodfacts.org/score-nutritionnel-france
        # A - Vert : jusqu'à -1
        # B - Jaune : de 0 à 2
        # C - Orange : de 3 à 10
        # D - Rose : de 11 à 18
        # E - Rouge : 19 et plus
        if self.score_nutrition < 0:
            return 5  # A
        elif self.score_nutrition < 3:
            return 4  # B
        elif self.score_nutrition < 11:
            return 3  # C
        elif self.score_nutrition < 19:
            return 2  # D
        else:
            return 1  # E

