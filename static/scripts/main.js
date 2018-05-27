var nav_language = window.navigator.userLanguage || window.navigator.language;
var current_product = null;

function init() {
    // $(ID_SERVER_ACTIVITY).css("display", "none");
    $(ID_CELL_BANNER).css("background-color", OFF_BACKGROUND_COLOR);
    $(ID_SERVER_ACTIVITY).css("visibility", "hidden");
    $(ID_INPUT_PRODUCT_CODE).val(PRODUCT_CODE_DEFAULT);
    draw_graph(ID_GRAPH, [], [], ID_INPUT_PRODUCT_CODE, OPEN_OFF_PAGE_FOR_SELECTED_PRODUCT);
    cleanup_suggestions();
    $(function () {
        $("#submitBtn").click(server_log);
    });
    // Leave at the end since Ajax request with callback there!
    guess_country_from_nav_lang();
}

function guess_country_from_nav_lang() {
    is_found = false;
    country = ( (nav_language.indexOf('-')>=0)? nav_language.split('-')[1] : nav_language).toLowerCase();
    for (var index_option in $(ID_INPUT_COUNTRY)[0]) {
        current_option = $(ID_INPUT_COUNTRY)[0][index_option];
        if (current_option.value === country) {
            is_found = true;
            current_option.selected = true;
            break;
        }
    }
    if (is_found) {
        // Load stores for guessed country
        fetch_stores($(ID_INPUT_COUNTRY)[0][index_option]);
        // fetch_stores("en:luxembourg");
    } else
        unblock_screen();
}

function fetch_stores(ctrlCountries) {
    block_screen(MSG_WAITING_SCR_FETCH_STORES);
    $.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/fetchStores/",
        contentType: "application/json; charset=utf-8",
        data: {
            country: ctrlCountries.text
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