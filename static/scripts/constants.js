/**
 * Created by olivier on 18/03/18.
 */
// Minimum proximity of matching products with reference-product for being part of suggestions
var MAX_GRADE = 5;
var MIN_SCORE_FOR_SUGGESTIONS = 70;
var MAX_SUGGESTIONS = 50;
// IMPORTANT: strings received from server telling the matching process is ended or there is a warning and cannot run.
// Is Used to clear setInterval Ajax requests!
var MSG_START_OF_LOG_WARNING = "WARNING";
var MSG_END_OF_LOG = "ciao!";
// popup messages
var MSG_WAITING_SCR_FETCH_STORES = ".. fetching stores ..";
var MSG_WAITING_SCR_MATCH_REQUEST = ".. please wait ..";

var GRAPH_WIDTH = $(window).innerWidth();
var GRAPH_HEIGHT = $(window).innerHeight() * 40 / 100;
var OPEN_OFF_PAGE_FOR_SELECTED_PRODUCT = false;
var TIME_SLOT = 2000;
// var PRODUCT_CODE_DEFAULT = '4104420017849';
var PRODUCT_CODE_DEFAULT = '3560070614134';
var OFF_BACKGROUND_COLOR = "#09f";
// fake score for product reference which means no nutriments data were available
var NO_NUTRITION_SCORE_FOR_PRODUCT_REF = -99;

/* ids of html-item for attaching graph data and product reference details (image, etc.) */
var ID_CELL_BANNER = "#banner";
var ID_SERVER_LOG = '#echoResultLog';
var ID_SERVER_ACTIVITY = "#server_activity";
var ID_PRODUCT_CODE = "#prod_ref_code";
var ID_PRODUCT_NAME = "#prod_ref_name";
var ID_INPUT_PRODUCT_CODE = "#input_product_code";
var ID_INPUT_COUNTRY = "#input_country";
var ID_INPUT_STORE = "#input_store";
var ID_PRODUCT_IMG = "#prod_ref_image";
var ID_PRODUCT_CATEGORIES = "#prod_ref_categories";
var ID_PRODUCT_OFF = "#url_off_prod";
var ID_PRODUCT_JSON = "#url_off_json_prod";
var ID_GRAPH = "#graph";
var ID_WARNING = "#msg_warning_prod_ref";
var ID_IMG_OFF = "#img_off_prod";
var ID_IMG_JSON = "#img_off_json";
var ID_PRODUCTS_SUGGESTION = "#products_suggestion";
var ID_MENU_SELECTION = "#menu_selection";
var ID_BTN_SUBMIT = "#submitBtn";
// no # in partial id below !! (used to assign live ids to products' images)
var ID_PRODUCT_IMAGE_PARTIAL = "prod_img_";
var ID_NB_SUGGESTIONS = "#nb_suggestions";
var ID_DETAILS_SELECTED_PRODUCT = "#selected_product_details";

// Messages
var MSG_NO_NUTRIMENTS_PROD_REF = "Beware: no nutriments are known for this product.. check in OFF for details!";
var MSG_NO_DATA_RETRIEVED = "Beware: it seems no data for making the comparison could be retrieved for the selected product. Please try with another product.";

// Others
// Circles drawn in SVG in the graph are appended after some basic other SVG-items; thereafter, 1 circle is bound to 1 product with the shift constant below
var SHIFT_ARRAY_POSITION_SVG_CIRCLES_VS_PRODUCTS = 7;
var CIRCLE_COLOR_DEFAULT = "steelblue";
var CIRCLE_COLOR_SELECTED = "red";
var CIRCLE_RADIUS_DEFAULT = 2;
var CIRCLE_RADIUS_SELECTED = 15;