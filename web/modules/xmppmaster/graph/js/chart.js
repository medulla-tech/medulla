/*
 * (c) 2017 Siveo, http://http://www.siveo.net
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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
 */
function chart(selector, datas)
{
  var total = 0;
  for(i = 0; i < datas.length; i++)
  {
    total += datas[i].value;
  }

  var height = 200, width = 200;
  var innerRadius = 3;
  var outerRadius = 80;

  var canvas = d3.select("#"+selector)
    .attr("style", function(d){
      return d3.select("#"+selector).attr("style")+ "; display:flex;";
    })
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  var group = canvas.append("g")
    .attr("transform", "translate("+(width)/2+","+ height/2+")");

  var dataset = d3.pie()
    .value(function(d){return d.value; })(datas);

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
    .attr("fill", function(d,i){return d.data.color})
    // Actions executed when the mouse is over the section
    .on("mouseover", function(d,i){
      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i)
        .style("font-size", "2.3em")
        .style("line-height","0.5em");

      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i).select("a")
      .style("font-size", "1.1em")
      .style("font-weight","bold");
      // Add the tooltip text
      canvas.append("g")
        .attr("class", selector+"tooltip");

      canvas.select("."+selector+"tooltip")
        .append("text")
        .attr("y", d3.mouse(this)[1]+80)
        .attr("text-anchor", "start")
        .text(function(data,id){
            return d.data.label + " : " + d.data.value + " (" + ((d.data.value/total)*100).toFixed(0) + "%)";
          })
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
        .attr("y", d3.mouse(this)[1]+80-15).lower();

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
    .data(dataset, function(d,i){return d;})
    .enter()
    .append("li")
    .style("font-size", "2em")
    .style("line-height","0.5em")
    .attr("class",function(d,i){

      return selector+'Label'+i})
    .style("color",function(d,i){
      var tmp = segments(d);
      return d.data.color;
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
    .text(function(d,i){
        return d.data.label+" : "+d.data.value+ " ("+((d.data.value/total)*100).toFixed(0) + "%)"
      });
    }
