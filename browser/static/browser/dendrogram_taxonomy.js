var width = 700,
    height = profile_info.leaf_number * 25;

var tree = d3.layout.cluster()
    .size([height, width - 400]);

var svg = d3.select("div#content").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(40,0)");

var re = /\d+/;
var url_data = re.exec(window.location.pathname);

d3.json("/browser/taxonomy/data/" + url_data, function(error, json) {
  var nodes = tree.nodes(json),
      links = tree.links(nodes);

  var link = svg.selectAll(".link")
      .data(links)
    .enter().append("polyline")
      .attr("class", "link")
      .attr("points", function(d) { return [[d.source.y, d.source.x], [d.source.y, d.target.x], [d.target.y, d.target.x]]; });


  var node = svg.selectAll(".node")
      .data(nodes)
    .enter().append("g")
      .attr("class", "node")
      .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })

  node.append("circle")
      .attr("r", 4.5)
      .attr("class", "internal")
      .on("mouseover", function(d) { d3.select(this).attr('r', 7); })
      .on("mouseout", function(d) { d3.select(this).attr('r', 4.5); })
      .on("click", function(d) { window.location.href = d.browse_rabs_url; }) ;

  node.append("text")
      .attr("dx", function(d) { return d.children ? -8 : 8; })
      .attr("dy", 3)
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d) { return d.is_leaf ? d.name : ""; });

  node.append("title")
      .text(function(d) {return d.name; })
});

d3.select(self.frameElement).style("height", height + "px");