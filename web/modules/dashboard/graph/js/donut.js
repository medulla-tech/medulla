/*
 * (c) 2019 siveo, http://www.siveo.net/
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

  var height = 135, width = 125;
  var outerRadius = 45;
  var innerRadius = 30;
  var widgetWidth = d3.select("#"+selector).node().getBoundingClientRect().width;

  //var colors = d3.scaleOrdinal(d3.schemeCategory10);
  var colors = d3.scaleOrdinal()
    .range(["#52b749","#e03c3c", "#f48f42"]);

  var canvas = d3.select("#"+selector).append("svg")
    .attr("width", width)
    .attr("height", height)
    .style("margin-left",(getDivWidth("#"+selector)-width)/2+"px");

  var group = canvas.append("g")
    .attr("transform", "translate("+width/2+","+ height/2+")");

  // Create a group for the text in the center of the donut chart
  canvas.append("g")
    .attr("class", "center")
    .attr("transform","translate("+width/2+","+ height/2+")");

  canvas.select(".center")
    .append("text")
    .attr("font-size",11)
    .append("tspan")
    .attr("text-anchor", "middle")
    .attr("x", 0)
    .attr("dy", 0)
    .text(title);

  canvas.select(".center").select("text")
    .append("tspan")
    .attr("x", 0)
    .attr("dy", 11)
    .attr("text-anchor", "middle")
    .attr("font-size",11)
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
    .attr("fill", function(d){return colors(d.data.value)})

    // Actions executed when the mouse is over the section
    .on("mouseover", function(d,i){
      canvas.attr("width", 300);
      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i)
        .style("font-weight","bold");
      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i).select("a")
      .style("font-weight","bold");
      // Add the tooltip text
      canvas.append("g")
        .attr("class", selector+"tooltip");

      canvas.select("."+selector+"tooltip")
        .append("text")
        //.attr("x", d3.mouse(this)[0]+1*outerRadius)
        .attr("y", d3.mouse(this)[1]+2*innerRadius)
        .attr("text-anchor", "start")
        .text(d.data.label+" "+ d.data.value+d.data.unit+" ("+((d.data.value/total)*100).toFixed(0)+"%)")
        .attr("fill","white");

      var tooltiptextwidth = jQuery("#"+selector+" svg ."+selector+"tooltip text")[0].getComputedTextLength();
      var tooltipwidth = tooltiptextwidth +5;

      var offset = ((width-tooltipwidth)/2 >0) ? (width-tooltipwidth)/2 : 2;
      canvas.select("."+selector+"tooltip")
        .append("rect")
        .attr("rx", 2)
        .attr("ry", 2)
        .attr("width", tooltipwidth)
        .attr("height", 22)
        .attr("opacity", 0.6)
        .attr("fill", "black")
        .attr("x", offset)
        .attr("y", d3.mouse(this)[1]+2*innerRadius-15).lower();

      var offset = ((width-tooltiptextwidth)/2 >0) ? (width-tooltiptextwidth)/2 : 5;
      canvas.select("."+selector+"tooltip")
        .select("text")
        .attr("x", offset);

      d3.select(this).attr("cursor","pointer")

      // Create a new arc path to replace the old
      var s = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius+5)
        .padAngle(.20)
        .padRadius(5);

      d3.select(this).attr("d", s(d));
      return segments(d);
    })

    // Action executed when the mouse is over the section
    .on("mouseout", function(d,i){
      canvas.attr("width", width);

      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i)
      .style("font-size", "2em")
      .style("line-height","0.5em");
      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i).select("a")
      .style("font-size", "1em")
      .style("line-height","0.5em")
      .style("font-weight", "normal");
      // Define the div for the tooltip
      canvas.select("."+selector+"tooltip").remove();

      var s = d3.arc()
        .innerRadius(innerRadius)
        .outerRadius(outerRadius)
        .padAngle(.20)
        .padRadius(5);
      d3.select(this).attr("d", s(d));
      return segments(d);
    })
    .on("click", function(d){
      if(typeof(d.data.href) != "undefined")
        window.location.replace(d.data.href)
    });

  //Add label text
    d3.select("#"+selector).append("ul")
    .selectAll("li")
    .data(dataset)
    .enter()
    .append("li")
    .style("font-size", "2em")
    .style("line-height","0.5em")
    .attr("class",function(d,i){return selector+'Label'+i})
    .style("color",function(d){
      var tmp = segments(d);
      return colors(d.data.value);
    })
    .style("display", function(d,i){
      if(d.data.value == 0)
        return "none";
      else
        return "reset";
    })
    .append("span")
    .append('a')
    .style("color","black")
    .attr("href", function(d){return d.data.href})
    .text(function(d,i){return d.data.label+" ("+d.data.value+d.data.unit+")"});

    if(dataset.length == 3)
    {
      d3.select("#"+selector).select("."+selector+'Label1').raise();
    }
}
