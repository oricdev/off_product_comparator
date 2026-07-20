# coding=utf-8
from __future__ import division
from module import Product, DataEnv
from module import Log


class Gui:
    """
    Gui Object
    """

    def __init__(self, data_env):
        assert isinstance(data_env, DataEnv.DataEnv)
        self.data_env = data_env

    def display(self, a_product):
        """
        Display all properties of the product if prop_to_display not set
        :param a_product: product for which we want to display the properties and their values
        """
        assert isinstance(a_product, Product.Product)
        if len(self.data_env.prod_props_to_display) == 0:
            props_to_show = a_product.dic_props
        else:
            props_to_show = self.data_env.prod_props_to_display
            Log.Log.add_msg("DETAILS:")
        for prop in props_to_show:
            if prop in a_product.dic_props:
                Log.Log.add_msg('\'%s\' = %r' % (prop, a_product.dic_props[prop]))

        # additionally, show scores if available
        if not a_product.isRef:
            Log.Log.add_msg("score proximity with ref. product = %r" % a_product.score_proximity)
            Log.Log.add_msg("score nutritional = %r" % a_product.score_nutrition)

