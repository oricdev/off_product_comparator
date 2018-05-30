function server_log() {
    // clear some staff
    $(ID_INPUT_PRODUCT_CODE).css("background-color", "white");
    $(ID_WARNING).empty();

    block_screen(MSG_WAITING_SCR_MATCH_REQUEST);
    $.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/fetchAjax/",
        contentType: "application/json; charset=utf-8",
        data: {barcode: $(ID_INPUT_PRODUCT_CODE).val(),
            country: $(ID_INPUT_COUNTRY+" option:selected")[0].value,
            store: $(ID_INPUT_STORE+" option:selected")[0].text},
        success: function (data) {
            unblock_screen();
            try {
                var product_ref = data.value[0];
                var products_matching = data.value[1];
                draw_page(product_ref, products_matching);
            } catch (e) {
                // possibly no data retrieved (product may habe been excluded from search due to a lack of information (nutriments, etc.)
                $(ID_WARNING).empty();
                $(ID_WARNING).append(MSG_NO_DATA_RETRIEVED);
            }
        }
    });
}
