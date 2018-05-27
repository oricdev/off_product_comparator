/* draw SVG graph:
 - id_attach_graph: id of html-item for attaching the graph itself
 - prod_ref: object containing all required data for showing object details (score, categories, image, url)
 - prod_matching: array of all matching products objects containing all required information (score, tooltip, etc.)
 - item_display_code_of_selected_product : html item receiving the code of the selected product in the graph (ex.: div's id)
 - open_off_page: true (/false) opens in a separate tab the off page for the selected product in the graph
 */
function draw_graph(id_attach_graph,
                    prod_ref,
                    prod_matching,
                    item_display_code_of_selected_product,
                    open_off_page) {
    // Set the dimensions of the canvas / graph
    var margin = {top: 30, right: 30, bottom: 60, left: 50},
        width = GRAPH_WIDTH - margin.left - margin.right,
        height = GRAPH_HEIGHT - margin.top - margin.bottom;

    var x = d3.scale.linear().range([0, width]);
    var y = d3.scale.linear().range([height, 0]);

    var nb_categs = 7;
    var nb_nutrition_grades = 5;

    // Define the axes
    var xAxis = d3.svg.axis().scale(x)
        .orient("bottom").ticks(nb_categs)
        .tickFormat(function (d) {
            if (d == 0)
                return "low";
            if (d == 1)
                return "high";
            return "";
        });

    var yAxis = d3.svg.axis().scale(y)
        .orient("left")
        .ticks(nb_nutrition_grades)
        .tickFormat(function (d) {
            if (d == 1)
                return "E";
            if (d == 2)
                return "D";
            if (d == 3)
                return "C";
            if (d == 4)
                return "B";
            if (d == 5)
                return "A";
            return "";
        });

    // Define the div for the tooltip
    var div = d3.select("body").append("div")
        .attr("class", "tooltip")
        .style("opacity", 0);

    // Adds the svg canvas
    var svg = d3.select("body")
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform",
            "translate(" + margin.left + "," + margin.top + ")");

    // Scale the range of the data
    x.domain([0, 1]);
    y.domain([0, nb_nutrition_grades]);

    var data_rect = [{'v': 1, 'color': 'rgb(230,62,17)'}, {'v': 2, 'color': 'rgb(238,129,0)'}, {
        'v': 3,
        'color': 'rgb(254,203,2)'
    }, {'v': 4, 'color': 'rgb(133,187,47)'}, {'v': 5, 'color': 'rgb(3,129,65)'}]
    svg.selectAll("rect")
        .data(data_rect)
        .enter()
        .append("rect")
        .attr("width", width)
        .attr("height", height / 5)
        .attr("y", function (d) {
            return (5 - d.v) * height / 5
        })
        .attr("fill", function (d) {
            return d.color
        })
        .attr("fill-opacity", 1.0);
    // *****

    // Add the scatterplot
    // .. for the product reference
    var data_prod_ref = [{'nutrition_grade': 1}];
    if (prod_ref.length != 0)
        data_prod_ref = [{'nutrition_grade': prod_ref["y_val_real"]}];
    svg.selectAll("ellipse")
        .data(data_prod_ref)
        .enter().append("ellipse")
        .attr("cx", width * (1 - (1 / nb_categs) / 2))
        .attr("cy", function (d) {
            return (height * (1 - (d.nutrition_grade / nb_nutrition_grades)) + (height / nb_nutrition_grades * 0.5));
        })
        .attr("rx", width / nb_categs * 0.5)
        .attr("ry", (height / nb_nutrition_grades) * 0.5)
        .attr("fill", "#ffffff")
        .attr("fill-opacity", 0.75)
    // .. for all matching products
    var data_others = prod_matching;

    svg.selectAll("circle")
        .data(data_others)
        .enter().append("circle")
        .attr("r", 3)
        .attr("stroke", "#000080")
        .attr("stroke-width", 1)
        .attr("fill", "steelblue")
        .attr("cx", function (d) {
            return d.x * width;
        })
        .attr("cy", function (d) {
            return height * (1 - d.y / nb_nutrition_grades);
        })
        .on("mouseover", function (d) {
            div.transition()
                .duration(200)
                .style("opacity", .85);
            div.html(d.content)
                .style("left", (d3.event.pageX) + "px")
                .style("top", (d3.event.pageY - 28) + "px");
        })
        .on("mouseout", function (d) {
            div.transition()
                .duration(500)
                .style("opacity", 0);
        })
        .on("click", function (d) {
            $(item_display_code_of_selected_product).val(d.code);
            $(item_display_code_of_selected_product).css("background-color", OFF_BACKGROUND_COLOR);
            if (open_off_page) {
                window.open(d.url, '_blank');


            }
        });

    // Add the X Axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    // Add the X-axis label
    svg.append("text")
        .attr("x", width * 0.5)
        .attr("y", height + 30)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .style("font-size", "12pt")
        .text("Similarity with product reference");

    // Add the Y Axis
    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis);

    // Add the Y-axis label
    svg.append("text")
        .attr("transform", "rotate(-90)")
        .attr("x", -(height * 0.5))
        .attr("y", -45)
        .attr("dy", "1em")
        .style("text-anchor", "middle")
        .style("font-size", "12pt")
        .text("Nutrition grade");

    $(id_attach_graph).empty();
    $("svg").detach().appendTo(id_attach_graph);
}

function display_product_ref_details(prod_ref,
                                     id_code,
                                     id_input_code,
                                     id_name,
                                     id_img,
                                     id_categories,
                                     id_off,
                                     id_json,
                                     id_warning) {
    code = prod_ref["code"];
    name = prod_ref["name"];
    image = prod_ref["images"];
    if (image == "") {
        image = prod_ref["image_fake_off"];
    }
    no_nutriments = prod_ref["no_nutriments"];
    categories = prod_ref["categories_tags"].join("<br />");
    url_off = prod_ref["url_product"];
    url_json = prod_ref["url_json"];
    $(id_code).empty();
    $(id_code).append(code);
    $(id_input_code).empty();
    $(id_input_code).append(code);
    $(id_name).empty();
    $(id_name).append(name);
    $(id_img).attr("src", image);
    $(id_categories).empty();
    $(id_categories).append(categories);
    $(id_off).attr("href", url_off);
    $(id_json).attr("href", url_json);
    $(id_warning).empty();
    if (no_nutriments) {
        $(id_warning).append(MSG_NO_NUTRIMENTS_PROD_REF);
    }
}

function draw_page(prod_ref, prod_matching) {
    display_product_ref_details(prod_ref,
        ID_PRODUCT_CODE,
        ID_INPUT_PRODUCT_CODE,
        ID_PRODUCT_NAME,
        ID_PRODUCT_IMG,
        ID_PRODUCT_CATEGORIES,
        ID_PRODUCT_OFF,
        ID_PRODUCT_JSON,
        ID_WARNING);
    draw_graph(ID_GRAPH,
        prod_ref,
        prod_matching,
        ID_INPUT_PRODUCT_CODE,
        OPEN_OFF_PAGE_FOR_SELECTED_PRODUCT);
}