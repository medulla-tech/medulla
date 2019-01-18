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

  var height = 180, width = 200;
  var outerRadius = 60;
  var innerRadius = 40;
  var widgetWidth = d3.select("#backup").node().getBoundingClientRect().width;

  //var colors = d3.scaleOrdinal(d3.schemeCategory10);
  var colors = d3.scaleOrdinal()
    .range(["#509a4e","#c55252", "#dd794b"]);

  var canvas = d3.select("#"+selector).append("svg")
    .attr("width", width)
    .attr("height", height)

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
      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i)
      .style("font-size", "1.1em");
      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i).select("a")
      .style("font-size", "1.1em")
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
      .style("font-size", "1em");
      d3.select("#"+selector).select("ul").select('.'+selector+'Label'+i).select("a")
      .style("font-size", "1em")
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
  canvas.select("g")
    .append("g").selectAll("text")
    .data(dataset)
    .enter()
    .append("text")
    .attr("transform",function(d){
      return "translate(" + [segments.centroid(d)[0]*1.2, 1.2*segments.centroid(d)[1]] + ")";})
    .text(function(d){
      if(d.data.value > 0)
        return d.data.label+" "+ d.data.value+d.data.unit
      else
        return ""
    })
    .attr("text-anchor",function(data,i){
      var length = this.getComputedTextLength();
      var translate = d3.select(this).attr("transform");
      var translate = translate.substring(10, translate.length-1).split(",")[0];
      translate = parseFloat(translate);

      //Positionning the text to limit the overflow
      if(translate < 0)
        return "start";
      else
        return (width/2 + 5 >translate+length > width/2) ? "end" : "middle";
    })
    .on("mouseover",function(d){
      d3.select("#"+selector).select("svg").attr("width",width+100)
    })
    .on("mouseout",function(d){
      d3.select("#"+selector).select("svg").attr("width",width)
    });
    d3.select("#"+selector).append("ul")
    .selectAll("li")
    .data(dataset)
    .enter().filter(function(d, i){
      if(d.data.value > 0)
        return d;
    })
    .append("li")
    .attr("class",function(d,i){return selector+'Label'+i})
    .style("color",function(d){
      var tmp = segments(d);
      return colors(d.data.value);
    })

    .append("span")
    .append('a')
    .style("color","black")
    .attr("href", function(d){return d.data.href})
    .text(function(d,i){return d.data.label+" ("+d.data.value+d.data.unit+")"});

}
