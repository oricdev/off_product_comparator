/**
 * Created by Olivier Richard (oric.dev@iznogoud.neomailbox.ch) richard on 23/08/18.
 */

/*
scan a barcode on Android smartphone using the App barcode Scanner
ref:
- https://github.com/zxing/zxing/wiki/Scanning-From-Web-Pages [url to generate for calling the backend App]
- https://github.com/zxing/zxing
- https://play.google.com/store/apps/details?id=com.google.zxing.client.android&hl=en_US
 */
function scan_barcode_http() {
    app_url = "http://zxing.appspot.com/scan?ret=http%3A%2F%2F";
    app_url = app_url + encodeURI("tuttifrutti.alwaysdata.net/?barcode=")+"%7BCODE%7D";
    app_url = app_url + "&SCAN_FORMATS=UPC_A,EAN_13";
    window.location.href = app_url;
}

function scan_barcode_zxing() {
    app_url = "zxing://scan/?ret=http%3A%2F%2F";
    app_url = app_url + encodeURI("tuttifrutti.alwaysdata.net/?barcode=")+"%7BCODE%7D";
    app_url = app_url + "&SCAN_FORMATS=UPC_A,EAN_13";
    window.location.href = app_url;
}