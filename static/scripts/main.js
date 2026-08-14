/*
 * OFF-Graph / OpenFoodFacts Product Comparator
 *
 * Contact: Olivier Richard (oric_dev@iznogoud.neomailbox.ch)
 * License: GNU Affero General Public License v3.0
 * License url: https://github.com/oricdev/off_product_comparator/blob/master/LICENSE
 */
 var nav_language = window.navigator.userLanguage || window.navigator.language;
var user_country = undefined;
var current_product = undefined;
var current_db_for_graph = undefined;

function init() {
    // load score databases
    fetch_score_databases();
    // load countries and set country
    fetch_countries();

    // set score db being used if cached locally: this is useful when using the barcode scanner App
    // which knows nothing about the current context when it launches the URL back with barcode.
    // We want to remember which score database is being used by the user
    current_db_used = getCachedCurrentDatabase();
    if (current_db_used != undefined) {
        current_db_for_graph = current_db_used;
        $(ID_INPUT_SCORE_DB).val(current_db_used[FLD_DB_NICK_NAME]);
        //alert("using db "+current_db_used[FLD_DB_NICK_NAME]);
    }
    // $(ID_SERVER_ACTIVITY).css("display", "none");
    $(ID_CELL_BANNER).css("background-color", OFF_BACKGROUND_COLOR);
    $(ID_SERVER_ACTIVITY).css("visibility", "hidden");
    draw_graph(ID_GRAPH, current_db_for_graph, [], [], ID_INPUT_PRODUCT_CODE, OPEN_OFF_PAGE_FOR_SELECTED_PRODUCT);
    cleanup_suggestions();
    $(function () {
        $("#submitBtn").click(go_fetch);
    });

    // Insert barcode from url if available, otherwise default product barcode
    url_barcode = getParameterByName(URL_PARAM_BARCODE, window.location.href);
    if (url_barcode != undefined) {
        $(ID_INPUT_PRODUCT_CODE).val(url_barcode);
        go_fetch();
    } else {
        $(ID_INPUT_PRODUCT_CODE).val(PRODUCT_CODE_DEFAULT);
    }

}

function fillHtmlElementWithCountries(data_countries) {
    if (data_countries != null) {
        var options = data_countries.map(function (country) {
            return $("<option></option>").val(country[COUNTRY_PROPERTY_EN_LABEL]).text(country[COUNTRY_PROPERTY_EN_NAME]);
        });
        $(ID_INPUT_COUNTRY).empty();
        $(ID_INPUT_COUNTRY).append($("<option></option>").val('').text(''));
        $(ID_INPUT_COUNTRY).append(options);

        guess_country_from_nav_lang();
    }
}

function fillHtmlElementWithDatabases(score_databases) {
    if (score_databases != null) {
        var options = score_databases.map(function (score_db) {
            return $("<option></option>").val(score_db[FLD_DB_NICK_NAME]).text(score_db[FLD_DB_DISPLAY_NAME]);
        });
        $(ID_INPUT_SCORE_DB).empty();
        $(ID_INPUT_SCORE_DB).append(options);
    } else {
        $(ID_INPUT_SCORE_DB).empty();
        $(ID_INPUT_SCORE_DB).append($("<option></option>").val('').text(''));
    }
}

function go_fetch() {
    // clear some staff
    $(ID_INPUT_PRODUCT_CODE).css("background-color", "white");
    $(ID_WARNING).empty();

    block_screen(MSG_WAITING_SCR_MATCH_REQUEST);
    //url_score = getParameterByName(URL_PARAM_SCORE, window.location.href);
    $.ajax({
        type: "GET",
        /* url: $SCRIPT_ROOT + "/fetchAjax/",*/
        url: $SCRIPT_ROOT + "/fetchPGraph/",
        contentType: "application/json; charset=utf-8",
        data: {barcode: $(ID_INPUT_PRODUCT_CODE).val(),
            country: $(ID_INPUT_COUNTRY+" option:selected")[0].value,
            store: '',
            score: 'tuttifrutti_'+$(ID_INPUT_SCORE_DB+" option:selected")[0].value+'_'+$(ID_INPUT_COUNTRY+" option:selected")[0].value
        },
        success: function (data) {
            unblock_screen();
            try {
                var parsedData = JSON.parse(data);
                var product_ref = parsedData.graph[0];
                var products_matching = parsedData.graph[1];
                draw_page(product_ref, products_matching);
            } catch (e) {
                // possibly no data retrieved (product may have been excluded from search due to a lack of information (nutriments, etc.)
                $(ID_WARNING).empty();
                $(ID_WARNING).append(MSG_NO_DATA_RETRIEVED);
                clear_graph();
                cleanup_suggestions();
                // Default image for product reference
                $(ID_PRODUCT_IMG).attr("src", 'https://static.openfoodfacts.org/images/misc/openfoodfacts-logo-en-178x150.png');
                //$(ID_PRODUCT_IMG).attr("height", "" + ($(window).innerHeight() / 7) + "px");
                //$(ID_PRODUCT_IMG).attr("class", style_for_border_colour);
            }
        }
    });
}
