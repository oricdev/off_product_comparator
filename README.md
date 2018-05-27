Openfoodfacts Product Comparator

First, update in module/Querier/__init__.py::connect() the 2 following lines with the connection data to your OpenFoodFacts MongoDb:

self.pongo = MongoClient("mongodb://<user>:<password>@<mongodb_url>/<mongodb_path>")
self.db = self.pongo["<mongodb_path>"]

        
        