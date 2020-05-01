<?php
/*
 * (c) 2017 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 *
 * File xmppmaster/topology.php
 */

require("modules/base/computers/localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");

$response = xmlrpc_topology_pulse();
?>

<script src="jsframework/d3/d3.js"></script>
<style>
	.node {
		cursor: pointer;
		fill: steelblue;
	  stroke: none;
	}

	.node circle {
	  fill: #fff;
	  stroke: steelblue;
	  stroke-width: 5px;
	}

	.node text {
	  font: 12px sans-serif;
	}

	.link {
	  fill: none;
	  stroke: #ccc;
	  stroke-width: 2px;
	}
</style>

<?
    $p = new PageGenerator(sprintf (_T("Topology Pulse", 'xmppmaster')));
    $p->setSideMenu($sidemenu);
    $p->display();
    echo '<div id="body"></div>';
?>

<svg width="200" height="200">
</svg>

<script>
var widthscrollable = jQuery(window).width()-20;
var heightscrollable = jQuery(window).height()-20;

jQuery("svg").width(widthscrollable);
jQuery("svg").height(heightscrollable);

data = d3.json("datatopology/topology.json").then(function(json) {
	root = json;
	var root = d3.hierarchy(root)
	update(root);
});

var svg = d3.select("svg");

var help = svg.append("g")
	.classed("help", true)
	.attr("transform","translate(5,5)")

help.append("text").attr("y", "1em").text("Tip :")
help.append("text").attr("y", "2em").text("- Drag & drop : move the graph")
help.append("text").attr("y", "3em").text("- Zoom : wheel")

svg.append("rect")
		.attr("fill", "none")
		.attr("pointer-events", "all")
		.attr("width", widthscrollable)
		.attr("height", heightscrollable)
		.call(d3.zoom()
			.scaleExtent([0.3, 2])
			.on("zoom", zoom));

var g = svg.append("g").attr("transform", "translate(100,100)");

g.append("g").attr("class", "links");
g.append("g").attr("class", "nodes");

var width = 400;
var height = 200;
var cluster = d3.cluster()
	// Set the general space between
  .nodeSize([50, 350])

function update(source)
{
	var root = source;
	cluster(root)

	// Nodes
	var node = d3.select('svg g.nodes')
	  .selectAll('circle.node')
	  .data(root.descendants());


	var nodeEnter = node.enter()
		.append("g")
		.attr("class", function(d){
			return "node "+d.data.type;
		})
		.attr("data-number", function(d, i){
			d.data.datanumber = i
			return i})
		.on("click", click);

	nodeEnter.append('circle')
		.attr('cx', function(d) {return d.y;})
		.attr('cy', function(d) {return d.x;})
		.attr('r', 10);

	nodeEnter.append("text")
		.attr("x", function(d) {
			return d.children || d._children ? d.y-13 : d.y+13; })
		.attr("y", function(d){
			var ars = d3.selectAll(".ARS").enter()
			if(d.data.type == "ARS" && ars._groups[0].length == 1)
			return d.x-7
			else
				return d.x
		})
		.attr("dy", ".35em")
		.attr("text-anchor", function(d) { return d.data.children || d.data._children ? "end" : "start"; })
		.text(function(d) {
			if(d.data.display_name == "" || typeof(d.data.display_name) == "undefined")
				return d.data.name;
			else
				return d.data.display_name;
	 });

	// Links
	var link = d3.select('svg g.links')
	  .selectAll('line.link')
	  .data(root.links())
	  .enter()
	  .append('line')
	  .classed('link', true)
	  .attr('x1', function(d) {return d.source.y;})
	  .attr('y1', function(d) {return d.source.x;})
	  .attr('x2', function(d) {return d.target.y;})
	  .attr('y2', function(d) {return d.target.x;});
}

function zoom() {
	g.attr("transform", d3.event.transform);
}

function click(d) {
    if (d.data.type == "AM")
    {
        // redirect to xmpp detail
        document.location.href="main.php?module=xmppmaster&submod=xmppmaster&action=machine_xmpp_detail&machine=" + d.data.name
        return
    }
    // TODO :
    // if type is ARS def promise js. infos ARS in intern page <div id=ARS_info><div>

  // Toggle children on click.
	if(isNodeOpen(d))
	{
		collapse(d)
	}
	else {
		expand(d)
	}

	var current = d
	while (typeof(current.parent) != "undefined" && current.parent != null)
	{
		current = current.parent
	}
	d3.selectAll('.node').remove()
	d3.selectAll('.link').remove()
	update(current)

}
// Collapse nodes
function collapse(d) {
  if (d.children) {
      d._children = d.children;
      d._children.forEach(collapse);
      d.children = null;
    }
}

function expand(d){
	if (d._children) {
      d.children = d._children;
      d.children.forEach(expand);
      d._children = null;
    }
}

function isNodeOpen(d){
	if(d.children){return true;}
	return false;
}

  </script>
