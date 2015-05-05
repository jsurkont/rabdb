var width = 600,
    height = profile_info.leaf_number * 25;

var tree = d3.layout.cluster()
    .size([height, width - 300]);

var svg = d3.select("div#content").append("svg")
    .attr("width", width)
    .attr("height", height)
  .append("g")
    .attr("transform", "translate(40,0)");

//var diagonal = d3.svg.diagonal()
//    .projection(function(d) { return [d.y, d.x]; });

var re = /tax\S+/;
var url_data = re.exec(window.location.pathname);
//document.write(url_data);

d3.json("/browser/profile/data/" + url_data, function(error, json) {
  var nodes = tree.nodes(json),
      links = tree.links(nodes);

  /*var link = svg.selectAll(".link")
      .data(links)
    .enter().append("path")
      .attr("class", "link")
      .attr("d", diagonal);
  */

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
      .style("fill", function(d) {
        if (d.is_leaf) {
            if (d.has_rab) { return "lime"; }
            else { return "red"; }
        } else { return "grey"; }
      })
      //.on("mouseover", function(d) { d3.select(this).style({fill:"white"}); })
      //.on("mouseover", function(d) { d3.select(this).transition().duration(200).attr('r', 7); })
      .on("mouseover", function(d) { d3.select(this).attr('r', 7); })
      //.on("mouseout", function(d) { d3.select(this).style({fill:(d.has_rab == true) ? "green" : "red" }); })
      .on("mouseout", function(d) { d3.select(this).attr('r', 4.5); })
      //.on("click", function(d,i) { alert("Clicked on the node " + d.name);}) ;
      .on("click", function(d) { window.location.href = d.browse_rabs_url; }) ;

  node.append("text")
      .attr("dx", function(d) { return d.children ? -8 : 8; })
      .attr("dy", 3)
      .attr("text-anchor", function(d) { return d.children ? "end" : "start"; })
      .text(function(d) { return d.is_leaf ? d.name : ""; });
});

d3.select(self.frameElement).style("height", height + "px");