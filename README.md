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
title="search results"
height="350px" />

A box with thin borders surrounds a subset as suggestions. Suggested products are shown along with their image in a ribbon below the graph. You can browse horizontally (with the finger on smartphones) to fetch a product, or using the left and right arrows below the ribbon. Tap on a product to select it: a red spot will highlight in the graph and its product code is filled in the appropriate search field.
Click on the magnifying glass to see some description of the product.

<img src="https://github.com/oricdev/off_product_comparator/blob/master/documentation/images/scr_details_suggested_product.png"
title="details of a similar product chosen in the ribbon"
height="350px" />

<h2>KNOWN RESTRICTIONS</h2>
This project is in early stage and has currently some restrictions which need to be cleared off in later stages:
<il>
<ul>1 user request at a time</ul>
<ul>optimization of matching searches</ul>
</il>

<h2>How to install</h2>
<h3>Configuring your WSGI site</h3>
Set your application path so that it points to <quote>/off_product_comparator/wsgi.py</quote>

<h3>Installing the OpenFoodFacts Mongo-database</h3>
Refer to <a href='https://fr.openfoodfacts.org/data'>OpenFoodFacts Data</a>, section <b>Dump MongoDB</b>.
<h3>Updating your Mongo-Db connection details</h3>
<p>Connection details are presently hard-coded in the application.</p>
<p>Simply update in <i>module/Querier/`__init__`.py::connect()</i> the 2 following lines with the connection data to your OpenFoodFacts MongoDb:
</p>
<p>
<quote>
self.pongo = MongoClient("mongodb://<user>:<password>@<mongodb_url>/<mongodb_path>")
self.db = self.pongo["<mongodb_path>"]
</quote>
</p>
<h3>Running the application</h3>
<p>Deploy the whole thing on your Python environment and start the instance.</p>
<p>The instance will use the entry point <quote>wsgi.py</quote> and listen to incoming requests (REST) defined in <quote>app.py</quote>.</p>
<p>On the client side, open a browser and enter the http-address of your server, for instance:
<quote>https://tuttifrutti.alwaysdata.net</quote></p>

<p>The server delivers the <quote>templates/index.html</quote> file based on resources' template defined in <quote>templates/layout.html</quote>.
That is it.


