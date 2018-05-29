function server_log() {
    // clear some staff
    $(ID_INPUT_PRODUCT_CODE).css("background-color", "white");
    $(ID_WARNING).empty();

    block_screen(MSG_WAITING_SCR_MATCH_REQUEST);
    $.ajax({
        type: "GET",
        url: $SCRIPT_ROOT + "/fetchAjax/",
        contentType: "application/json; charset=utf-8",
        data: {echoValue: $(ID_INPUT_PRODUCT_CODE).val(),
            country: $(ID_INPUT_COUNTRY+" option:selected")[0].value,
            store: $(ID_INPUT_STORE+" option:selected")[0].text},
        success: function (data) {
            // server activity received
            $(ID_SERVER_ACTIVITY).css("visibility", "visible");

            $(ID_SERVER_LOG).empty();
            $(ID_SERVER_LOG).append(data.value.join('<br />'));
            $(ID_SERVER_LOG).append("<br />");
            if (data.value[data.value.length - 1] == MSG_END_OF_LOG) {
                setTimeout(function() {
                    $(ID_SERVER_ACTIVITY).css("visibility", "hidden");
                    unblock_screen();
                }, 100);
                if (data.value[0].toString().substr(0, MSG_START_OF_LOG_WARNING.length) == MSG_START_OF_LOG_WARNING) {
                    $(ID_WARNING).empty();
                    $(ID_WARNING).append(data.value.splice(0, data.value.length-1).join(' '));
                }
            } else {
                var received_already = data.value.length;
                var logFetcherId =
                        setInterval(function () {
                            $.ajax({
                                type: "GET",
                                url: $SCRIPT_ROOT + "/logAjax/",
                                contentType: "application/json; charset=utf-8",
                                data: {fromPtr: received_already.toString()},
                                success: function (data) {
                                    received_already = received_already + data.value.length;
                                    var pos_in_log = 0;
                                    slot_print_char = Math.floor((TIME_SLOT * 0.80) / data.value.length);
                                    var logOutputterId = setInterval(function () {
                                        var lineOfData = "";
                                        if (pos_in_log < data.value.length) {
                                            lineOfData = data.value[pos_in_log];
                                            $(ID_SERVER_LOG).append(data.value[pos_in_log] + "<br />");
                                            pos_in_log++;

                                            var wtf = $(ID_SERVER_LOG);
                                            var height = wtf[0].scrollHeight;
                                            wtf.scrollTop(height);
                                        }
                                        if (lineOfData == MSG_END_OF_LOG) {
                                            clearInterval(logOutputterId);
                                            clearInterval(logFetcherId);
                                            $(ID_SERVER_ACTIVITY).css("visibility", "hidden");
                                            unblock_screen();
                                            try {
                                                var product_ref = data.value[data.value.length - 1][0];
                                                var products_matching = data.value[data.value.length - 1][1];
                                                draw_page(product_ref, products_matching);
                                            } catch (e) {
                                                // possibly no data retrieved (product may habe been excluded from search due to a lack of information (nutriments, etc.)
                                                $(ID_WARNING).empty();
                                                $(ID_WARNING).append(MSG_NO_DATA_RETRIEVED);
                                            }
                                        } else if (pos_in_log >= data.value.length) {
                                            clearInterval(logOutputterId);
                                        }
                                    }, slot_print_char);
                                }
                            });
                        }, TIME_SLOT)
                    ;

            }
        }
    });
}
