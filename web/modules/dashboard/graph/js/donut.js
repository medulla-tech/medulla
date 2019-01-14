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

function donut(selector, datas, title, subtitle){

  var total = 0;
  for(i = 0; i < datas.length; i++)
  {
    total += datas[i].value;
  }

  var height = 200, width = 200;
  var outerRadius = 60;
  var innerRadius = 40;

  //var colors = d3.scaleOrdinal(d3.schemeCategory10);
  var colors = d3.scaleOrdinal()
    .range(["#509a4e","#c55252"]);

  var canvas = d3.select("#"+selector).append("svg")
    .attr("width", height)
    .attr("height", width);

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
    .innerRadius(40)
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
    .on("mouseover", function(d){
      // Add the tooltip text
      canvas.attr("width", 350);
      canvas.append("g")
        .attr("class", selector+"tooltip");

      canvas.select("."+selector+"tooltip")
        .append("text")
        //.attr("x", d3.mouse(this)[0]+1*outerRadius)
        .attr("y", d3.mouse(this)[1]+2*innerRadius)
        .attr("text-anchor", "start")
        .text(d.data.label+" "+ d.data.value+" ("+((d.data.value/total)*100).toFixed(0)+"%)")
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
        //.attr("x", d3.mouse(this)[0]+1*outerRadius)
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
    .on("mouseout", function(d){
      canvas.attr("width", width);
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
      window.location.replace(d.data.href)
    });

  //Add label text
  canvas.select("g")
    .append("g").selectAll("text")
    .data(dataset)
    .enter()
    .append("text")
    .attr("transform",function(d){
      return "translate(" + [segments.centroid(d)[0]*1.2, 1.2*segments.centroid(d)[1]] + ")";})
    .text(function(d){
      if(d.data.value > 0)
        return d.data.label+" "+ d.data.value
      else
        return ""
    })
    .on("mouseover",function(d){
      d3.select("#"+selector).select("svg").attr("width",width+100)
    })
    .on("mouseout",function(d){
      d3.select("#"+selector).select("svg").attr("width",width)
    });
}
