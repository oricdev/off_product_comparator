<h1>OpenFoodFacts Product Comparator</h1>

<p>Also known as OFF-Graph, the Comparator uses the products' database delivered by the <a href="https://world.openfoodfacts.org" target="_blank">OpenFoodFacts</a> community. It makes it possible to type in (or <a href="https://offgraphs.blogspot.com/2018/09/create-your-off-graph-app.html" target="_blank">scan</a>) the barcode of a product in order to get almost instantly within a user-friendly graph 
one of its scores (<a href="https://world.openfoodfacts.org/nutriscore" target="_blank">Nutrition score</a>, <a href="https://www.bmj.com/content/bmj/360/bmj.k322.full.pdf" target="_blank">Nova Classification</a> score), or even your <a href="https://offmatch.blogspot.com/2018/10/how-can-i-request-new-score-database.html" target="_blank">own score</a> if you wish to build it!
</p>
<p>
Language of the application is <b>English</b>.
</p>
<p>
Refer to the following links for more details:<br/>
<ul>
<li>For using the application: <a href="https://tuttifrutti.alwaysdata.net" target="_blank">tuttifrutti.alwaysdata.net</a></li>
<li><a href="https://offgraphs.blogspot.com/" target="_blank">OFF-Graph blog</a></li>
<li><b>PROSIM</b> backend engine (<a href="https://github.com/oricdev/prosim" target="_blank">source code here</a>) and blog <a href="https://offmatch.blogspot.com/" target="_blank">here</a></li>
<li><b>API</b> starting point is provided by <b>app.py</b> and detailed <a href="https://offgraphs.blogspot.com/2018/09/api-usage-for-getting-similar-products.html" target="_blank">here</a>.
<li>follow on <a href="https://twitter.com/GraphProsim" target="_blank">Twitter</a></li>
</ul>
</p>
<p>
<u><b>Note:</b></u> some pieces of code or even some files may be unused and were not cleaned up. Sorry about this inconvenience guys! In case of doubt, feel free to ask me ;)
</p>
<h2>Tech used</h2>
<p>This project uses data from the <a href="https://world.openfoodfacts.org/">OPENFOODFACTS</a> database.</p>
<p>It is developped using Python 2.7 WSGI (backend) and html/css/ajax/js/d3js (frontend).</p>
<p>It is browser-based and hence intended to be used on any kind of devices (smartphones, tablets, desktops).</p>

<h2>How to use?</h2>
At startup, the country field may be automatically filled or choose it in the list.
Then the registered stores for your country are loaded: you may then choose one in the "store" field to restrict the search (optional)
Enter the product code and click on the blue *Go* button.
After a few seconds, the server returns a list of similar products to yours (shown as an ellipse in the graph) which are classified by similarity (brands_categories)
and nutrition score.

<img src="https://github.com/oricdev/off_product_comparator/blob/master/_documentation/images/scr_search_results.png"
title="search results"
height="350px" />

A box with thin borders surrounds a subset as suggestions. Suggested products are shown along with their image in a ribbon below the graph. You can browse horizontally (with the finger on smartphones) to fetch a product, or using the left and right arrows below the ribbon. Tap on a product to select it: a red spot will highlight in the graph and its product code is filled in the appropriate search field.
Click on the magnifying glass to see some description of the product.

<img src="https://github.com/oricdev/off_product_comparator/blob/master/_documentation/images/scr_details_suggested_product.png"
title="details of a similar product chosen in the ribbon"
height="350px" />

<h2>How to install</h2>
<h3>Configuring your WSGI site</h3>
Set your application path so that it points to <blockquote>/off_product_comparator/wsgi.py</blockquote>

<h3>Installing the OpenFoodFacts Mongo-database</h3>
Refer to <a href='https://fr.openfoodfacts.org/data' target="_blank">OpenFoodFacts Data</a>, section <b>Dump MongoDB</b>.
<h3>Updating your Mongo-Db connection details</h3>
<p>Connection details are presently hard-coded in the application.</p>
<p>Simply update in <i>module/Querier/`__init__`.py::connect()</i> the 2 following lines with the connection data to your OpenFoodFacts MongoDb:
</p>
<p>
<code>
self.pongo = MongoClient("mongodb://&lt;user&gt;:&lt;password&gt;@&lt;mongodb_url&gt;/&lt;mongodb_path&gt;")
<br />
self.db = self.pongo["&lt;mongodb_path&gt;"]
</code>
</p>
<h3>Running the application</h3>
<p>Deploy the whole thing on your Python environment and start the instance.</p>
<p>The instance will use the entry point <blockquote>wsgi.py</blockquote> and listen to incoming requests (REST) defined in <blockquote>app.py</blockquote>.</p>
<p>On the client side, open a browser and enter the http-address of your server, for instance:
<blockquote>https://tuttifrutti.alwaysdata.net</blockquote></p>
<p>The server will respond to the route <code>/</code> by executing the function <code>helloAjax</code> defined in <code>app.py</code>.
<p>The server delivers the <blockquote>templates/index.html</blockquote> file based on resources' template defined in <blockquote>templates/layout.html</blockquote>
<p>All the server-side engine is located under the <code>/module</code> directory.</p>
That is it!
</p>
<p>Feel free to contact the author in case of questions or remarks :).
</p>


