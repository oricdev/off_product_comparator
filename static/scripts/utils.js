/**
 * Created by olivier on 16/05/18.
 */

/*
 see https://stackoverflow.com/questions/6129952/javascript-sort-array-by-two-fields
 Triple sort function; usage here: http://gregtaff.com/misc/multi_field_sort/
 */
function getSortMethod() {
    var _args = Array.prototype.slice.call(arguments);
    return function (a, b) {
        for (var x in _args) {
            var ax = Number(a[_args[x].substring(1)]);
            var bx = Number(b[_args[x].substring(1)]);
            var cx;

            if (_args[x].substring(0, 1) == "-") {
                cx = ax;
                ax = bx;
                bx = cx;
            }
            if (ax != bx) {
                return ax < bx ? -1 : 1;
            }
        }
    }
}

var function_sort_products = getSortMethod('-final_grade', '-score');
var function_sort_min_abscisse = getSortMethod('+x');

function filter_suggestions(prod_ref, matching_products) {
    return matching_products.filter(
        function (a) {
            return ( (prod_ref.y_val_real == MAX_GRADE) ? a.final_grade >= prod_ref.y_val_real : a.final_grade > prod_ref.y_val_real)
                && a.score >= MIN_SCORE_FOR_SUGGESTIONS
        }
    );
}
