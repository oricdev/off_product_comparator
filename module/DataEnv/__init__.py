# coding=utf-8


class DataEnv:
    """
    Environment for data. Specifies the set of fields retrieved from server for matching
    products (Querier)
    """

    def __init__(self, set_of_properties):
        """
        :type set_of_properties: [] of properties
        """
        # _id a dn code must be there!
        if not ("code" in set_of_properties):
            set_of_properties.insert(0, "code")
        if not ("_id" in set_of_properties):
            set_of_properties.insert(0, "_id")
        self.prod_props_to_display = set_of_properties

