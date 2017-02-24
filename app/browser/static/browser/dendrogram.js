function plotTaxonomy(container, callback) {
  d3.json(window.location.href + '?json', function(error, data) {
    if (error) throw error;

    const root = d3.hierarchy(data);

    const width = 700,
          widthTree = width - 400,
          height = root.leaves().length * 25;

    var figure;
    if (typeof container === 'string')
      figure = d3.select(container).append('svg');
    else figure = container.append('svg');
    figure.attr('width', width).attr('height', height);

    const plot = figure.append('g').attr('transform', 'translate(40,0)');

    const tree = d3.cluster()
      .size([height, widthTree])
      .separation(function(a, b) { return 1; });
    tree(root);

    const link = plot.selectAll('.link')
      .data(root.descendants().slice(1))
      .enter().append('polyline')
        .attr('class', 'link')
        .attr('points', function(d) {
          return [[d.parent.y, d.parent.x], [d.parent.y, d.x], [d.y, d.x]];
        });

    const node = plot.selectAll('.node')
      .data(root.descendants())
      .enter().append('g')
        .attr('class', function(d) {
          return 'node' + (d.children ? ' node-internal' : ' node-leaf');
        })
        .attr('transform', function(d) {
          return 'translate(' + d.y + ',' + d.x + ')';
        });

    node.append('circle')
      .attr('r', 4.5)
      .attr('class', 'internal')
      .on('mouseover', function(d) { d3.select(this).attr('r', 7); })
      .on('mouseout', function(d) { d3.select(this).attr('r', 4.5); })
      .on('click', function(d) { window.location.href = d.data.browse_rabs_url; }) ;

    node.append('text')
      .attr('dx', 8)
      .attr('dy', 3)
      .attr('text-anchor', 'start')
      .text(function(d) { return d.children ? '' : d.data.name; });

    node.append('title')
      .text(function(d) {return d.data.name; })

    if (typeof callback === 'function') callback();
  });
}
