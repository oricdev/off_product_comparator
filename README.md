<h1>OpenFoodFacts Product Comparator</h1>

<h2>Tech used</h2>
This project is developped using Python 2.7 WSGI (backend) and html/css/ajax (frontend).It is intended to be used on any kind of devices (smartphones, tablets, desktops).

<h2>How to use?</h2>
At startup, the country field may be automatically filled or choose it in the list.
Then the registered stores for your country are loaded: you may then choose one in the "store" field to restrict the search (optional)
Enter the product code and click on the blue *Go* button.
After a few seconds, the server returns a list of similar products to yours (shown as an ellipse in the graph) which are classified by similarity (brands_categories)
and nutrition score.

<img src="https://github.com/oricdev/off_product_comparator/blob/master/documentation/images/scr_search_results.png"
title="search results" />

A box with thin borders surrounds a subset as suggestions. Suggested products are shown along with their image in a ribbon below the graph. You can browse horizontally (with the finger on smartphones) to fetch a product, or using the left and right arrows below the ribbon. Tap on a product to select it: a red spot will highlight in the graph and its product code is filled in the appropriate search field.
Click on the magnifying glass to see some description of the product.

<img src="https://github.com/oricdev/off_product_comparator/blob/master/documentation/images/scr_details_suggested_product.png"
title="details of a similar product chosen in the ribbon" />

**KNOWN RESTRICTIONS**
This project is in early stage and has currently some restrictions which need to be cleared off in later stages:
- 1 user request at a time
- optimization of matching searches

**How to install**
First, update in module/Querier/__init__.py::connect() the 2 following lines with the connection data to your OpenFoodFacts MongoDb:

self.pongo = MongoClient("mongodb://<user>:<password>@<mongodb_url>/<mongodb_path>")
self.db = self.pongo["<mongodb_path>"]

