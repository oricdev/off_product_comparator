"""
 * OFF-Graph / OpenFoodFacts Product Comparator
 *
 * Contact: Olivier Richard (oric_dev@iznogoud.neomailbox.ch)
 * License: GNU Affero General Public License v3.0
 * License url: https://github.com/oricdev/off_product_comparator/blob/master/LICENSE
"""
# coding=utf-8
from __future__ import division


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
        self.score = properties["score"]
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
        # if is_ref:
        #     self.score_proximity = 1
        #     # compute also the nutrition score
        #     self.calc_score_nutrition()
        #     # compute final grade from 1 to 5 (E to A for Nutriscore)
        #     self.calc_final_grade()

    def extract_similarity_codes(self):
        """
        extract all barcodes under 'similarity' tag
        :return: all barcodes under 'similarity' tag
        """
        all_codes = []
        # stats_codes: for each code, its similarity percentage with product reference and scoring
        stats_codes = {}
        tag_similarity = self.dic_props["similarity"]

        for proximity in tag_similarity:
            for score in tag_similarity[proximity]:
                all_codes = all_codes + tag_similarity[proximity][score]
                for product_code in tag_similarity[proximity][score]:
                    stats_codes[product_code] = (proximity, score)

        return all_codes, stats_codes


