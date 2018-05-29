var nav_language = window.navigator.userLanguage || window.navigator.language;
var user_country = undefined;
var current_product = undefined;
var data_countries = undefined;

function init() {
    // load countries
    $.getJSON(FILE_COUNTRIES, function (json) {
        countries_json = json;
        data_countries = $.map(countries_json, function (value, index) {
            // add to each value the key of the object (e.g. "en:Poland") for future use in REST services
            value[COUNTRY_PROPERTY_EN_LABEL] = index;
            value[COUNTRY_PROPERTY_EN_NAME] = value.name["en"];
            if (value.hasOwnProperty("country_code_2")) {
                value[COUNTRY_PROPERTY_EN_CODE] = value.country_code_2["en"].toUpperCase();
            } else if (value.hasOwnProperty("country_code_3")) {
                value[COUNTRY_PROPERTY_EN_CODE] = value.country_code_3["en"].toUpperCase();
            } else {
                value[COUNTRY_PROPERTY_EN_CODE] = "";
            }
            return [value];
        });

        data_countries.sort(function_sort_countries);

        var options = data_countries.map(function (country) {
            return $("<option></option>").val(country[COUNTRY_PROPERTY_EN_LABEL]).text(country[COUNTRY_PROPERTY_EN_NAME]);
        });
        $(ID_INPUT_COUNTRY).empty();
        $(ID_INPUT_COUNTRY).append($("<option></option>").val('').text(''));
        $(ID_INPUT_COUNTRY).append(options);
        // Leave at the end since Ajax request with callback there!
        guess_country_from_nav_lang();
    });


    // $(ID_SERVER_ACTIVITY).css("display", "none");
    $(ID_CELL_BANNER).css("background-color", OFF_BACKGROUND_COLOR);
    $(ID_SERVER_ACTIVITY).css("visibility", "hidden");
    $(ID_INPUT_PRODUCT_CODE).val(PRODUCT_CODE_DEFAULT);
    draw_graph(ID_GRAPH, [], [], ID_INPUT_PRODUCT_CODE, OPEN_OFF_PAGE_FOR_SELECTED_PRODUCT);
    cleanup_suggestions();
    $(function () {
        $("#submitBtn").click(server_log);
    });

}

function guess_country_from_nav_lang() {
    is_found = false;
    nav_country = ( (nav_language.indexOf('-') >= 0) ? nav_language.split('-')[1] : nav_language).toUpperCase();
    // filter countries and fetch the one holding the country code of the navigator
    user_country = data_countries.filter(
        function (ctry) {
            return ctry[COUNTRY_PROPERTY_EN_CODE] == nav_country;
        }
    );
    if (user_country != undefined) {
        for (var index_option in $(ID_INPUT_COUNTRY)[0]) {
            current_option = $(ID_INPUT_COUNTRY)[0][index_option];
            if (current_option.value === user_country[0][COUNTRY_PROPERTY_EN_LABEL]) {
                is_found = true;
                current_option.selected = true;
                break;
            }
        }
        if (is_found) {
            // Load stores for guessed country
            fetch_stores($(ID_INPUT_COUNTRY)[0][index_option]);
            // fetch_stores("en:luxembourg");
        }
    }
}

function fetch_stores(ctrlCountries) {
    block_screen(MSG_WAITING_SCR_FETCH_STORES);
    $.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/fetchStores/",
        contentType: "application/json; charset=utf-8",
        data: {
            country: ctrlCountries.value
        },
        success: function (data) {
            var options = data.sort().map(function (store) {
                return $("<option></option>").val(store).text(store);
            });
            $(ID_INPUT_STORE).empty();
            $(ID_INPUT_STORE).append($("<option></option>").val('').text(''));
            $(ID_INPUT_STORE).append(options);
            unblock_screen();
        }
    });
}