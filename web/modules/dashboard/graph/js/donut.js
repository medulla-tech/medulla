/*
 * (c) 2019-2023 siveo, http://www.siveo.net/
 *
 * This file is part of Management Console (MMC).
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
 */

function getDivWidth (div) {
  var width = d3.select(div)
    // get the width of div element
    .style('width')
    // take of 'px'
    .slice(0, -2)
  // return as an integer
  return Math.round(Number(width))
}

function donut(selector, datas, title, subtitle){
  /*
  * the donut function creates a donut with the datas provided and print it inside the specified selector
  * @param: selector string of the id name. For example "myDiv" will select #myDiv
  * @param: datas dict of the datas we want print.
  * datas structure :
  * [
  *   {"label":"myLabel", "value":5, href:"http://mywebsite.com", "unit":"GB"},
  *   {"label":"myLabel-2", "value":15, href:"http://siveo.net"},
  *]
  * Here the "unit" key is optional and is set to "" if it doesn't exist.
  * The "href" key is also optional. If no href is specified, no location is executed on section click
  *
  * @param: title string of the title which is printed inside the donut
  * @param: subtitle string of the subtitle which is printed below the title
  */
  var total = 0;
  for(i = 0; i < datas.length; i++)
  {
    if(typeof(datas[i].unit) == "undefined" )
      datas[i].unit = "";
    total += datas[i].value;
  }
  var height = 130, width = 130;
  var outerRadius = 56;
  var innerRadius = 38;
  var widgetWidth = d3.select("#"+selector).node().getBoundingClientRect().width;

  //var colors = d3.scaleOrdinal(d3.schemeCategory10);
  // 0:gris 1:bleu 2:vert 3:orange 4:rouge 5:gris-foncé 6:gris-clair
  var colors = ["#b5c7cc", "#3a8fa8", "#8CB63C", "#f48f42", "#e03c3c", "#7a8a8f", "#d0d8db"];

  // Make the selector container a flex column, aligned to top
  d3.select("#"+selector)
    .style("display", "flex")
    .style("flex-direction", "column")
    .style("align-items", "center")
    .style("justify-content", "flex-start")
    .style("flex", "1");

  var container = d3.select("#"+selector);

  var svgContainer = container.append("div")
    .style("display", "flex")
    .style("justify-content", "center")
    .style("height", height + "px")
    .style("margin-top", "20px");

  var canvas = svgContainer.append("svg")
    .attr("width", width)
    .attr("height", height);

  var group = canvas.append("g")
    .attr("transform", "translate("+width/2+","+ height/2+")");

  // Create a group for the text in the center of the donut chart
  canvas.append("g")
    .attr("class", "center")
    .attr("transform","translate("+width/2+","+ height/2+")");

  canvas.select(".center")
    .append("text")
    .attr("font-size",13)
    .append("tspan")
    .attr("text-anchor", "middle")
    .attr("x", 0)
    .attr("dy", 0)
    .text(title);

  canvas.select(".center").select("text")
    .append("tspan")
    .attr("x", 0)
    .attr("dy", 14)
    .attr("text-anchor", "middle")
    .attr("font-size",13)
    .attr("font-weight", "normal")
    .text(subtitle);

  var dataset = d3.pie()
    .value(function(d){ return d.value; })(datas);

  var segments = d3.arc()
    .innerRadius(innerRadius)
    .outerRadius(outerRadius)
    .padAngle(.20)
    .padRadius(5);

  var sections = group.selectAll("path")
    .data(dataset)
    .enter()
    .append("path")
    .attr("d", segments)
    .attr("fill", function(d, i){return colors[i]})

    // Actions executed when the mouse is over the section
    .on("mouseover", function(d,i){
      d3.select(this).attr("cursor","pointer");
      // Highlight the label
      d3.select("#"+selector).select('.'+selector+'Label'+i.index)
        .style("font-weight","bold");
      // Expand the arc slightly
      var s = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius+5)
        .padAngle(.20)
        .padRadius(5);
      d3.select(this).attr("d", s(i));
    })

    // Action executed when the mouse leaves the section
    .on("mouseout", function(d,i){
      // Remove label highlight
      d3.select("#"+selector).select('.'+selector+'Label'+i.index)
        .style("font-weight","normal");
      // Reset arc size
      var s = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius)
        .padAngle(.20)
        .padRadius(5);
      d3.select(this).attr("d", s(i));
    })
    .on("click", function(i, d){
      if(typeof(d.data.href) != "undefined" && d.data.href != "")
        window.location.replace(d.data.href)
    });

  //Add label text below (stacked vertically)
    d3.select("#"+selector).append("div")
    .style("display", "flex")
    .style("flex-direction", "column")
    .style("align-items", "center")
    .style("gap", "8px")
    .style("font-size", "17px")
    .style("margin-top", "12px")
    .selectAll("div")
    .data(dataset)
    .enter()
    .append("div")
    .style("display", function(d,i){
      if(d.data.value == 0)
        return "none";
      else
        return "flex";
    })
    .style("align-items", "center")
    .attr("class",function(d){return selector+'Label'+d.index})
    .html(function(d, i){
      return '<span style="display:inline-block;width:12px;height:12px;border-radius:50%;background:'+colors[i]+';margin-right:8px;"></span>' +
        '<span style="color:#333;font-size:13px;">' + d.data.label + ' (' + d.data.value + d.data.unit + ')</span>';
    });

    if(dataset.length == 3)
    {
      d3.select("#"+selector).select("."+selector+'Label1').raise();
    }
}
