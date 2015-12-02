function countLeaves(node) {
    if(!node.children) {
        return 1;
    }
    var total = 0;
    node.children.forEach(function(d) {
        total += countLeaves(d);
    })
    return total;
}

var width = 700,
    widthTree = width - 400,
    height = countLeaves(data) * 25;

var tree = d3.layout.cluster()
    .size([height, widthTree]);

var svg = d3.select("div#content").append("svg")
    .attr("width", width)
    .attr("height", height)
    .append("g")
        .attr("transform", "translate(40,0)");

var nodes = tree.nodes(data),
    links = tree.links(nodes);

var link = svg.selectAll(".link")
    .data(links)
    .enter()
        .append("polyline")
            .attr("class", "link")
            .attr("points", function(d) { return [[d.source.y, d.source.x], [d.source.y, d.target.x], [d.target.y, d.target.x]]; });

var node = svg.selectAll(".node")
    .data(nodes)
    .enter()
        .append("g")
            .attr("class", "node")
            .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })

node.append("circle")
    .attr("r", 4.5)
    .attr("class", "internal")
    .on("mouseover", function(d) { d3.select(this).attr('r', 7); })
    .on("mouseout", function(d) { d3.select(this).attr('r', 4.5); })
    .on("click", function(d) { window.location.href = d.browse_rabs_url; }) ;

node.append("text")
    .attr("dx", 8)
    .attr("dy", 3)
    .attr("text-anchor", "start")
    .text(function(d) { return d.children ? "" : d.name; });

node.append("title")
    .text(function(d) {return d.name; })

d3.select(self.frameElement).style("height", height + "px");