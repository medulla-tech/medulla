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

function customPie(selector, datas){
  /*
  * the customPie function creates a pie with the datas provided and print it inside the specified selector
  * @param: selector string of the id name. For example "myDiv" will select #myDiv
  * @param: datas dict of the datas we want print.
  * datas structure :
  * [
  *   {"label":"myLabel", "value":5, href:"http://mywebsite.com"},
  *   {"label":"myLabel-2", "value":15, href:"http://siveo.net"},
  *]
  * The "href" key is also optional. If no href is specified, no location is executed on section click
  *
  */
  var total = 0;
  for(i = 0; i < datas.length; i++)
  {
    if(datas[i].version == false)
      datas[i].version = "";
    total += datas[i].value;
  }

  var height = 200, width = 200;
  var outerRadius = 70;
  var innerRadius = 2;
  var widgetWidth = d3.select("#"+selector).node().getBoundingClientRect().width;

  var colors = d3.scaleOrdinal()
    .range([
        "#2484c1", "#65a620", "#7b6888", "#a05d56", "#961a1a", "#e98125", "#d8d23a", "#d0743c", "#635222", "#6ada6a",
				"#0c6197", "#7d9058", "#207f33", "#44b9b0", "#bca44a", "#e4a14b", "#a3acb2", "#8cc3e9", "#69a6f9", "#5b388f",
				"#546e91", "#8bde95", "#d2ab58", "#273c71", "#98bf6e", "#4daa4b", "#98abc5", "#cc1010", "#31383b", "#006391",
				"#c2643f", "#b0a474", "#a5a39c", "#a9c2bc", "#22af8c", "#7fcecf", "#987ac6", "#3d3b87", "#b77b1c", "#c9c2b6",
				"#807ece", "#8db27c", "#be66a2", "#9ed3c6", "#00644b", "#005064", "#77979f", "#77e079", "#9c73ab", "#1f79a7",
        "#1b81c1", "#4ea61f", "#886883", "#a06e56", "#963a1a", "#f98125", "#d8d2da", "#00743c", "#635242", "#dada3a",
      ]);

  var canvas = d3.select("#"+selector).append("svg")
    .attr("width", width)
    .attr("height", height);

  var group = canvas.append("g")
    .attr("transform", "translate("+(width)/2+","+ height/2+")");

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
    .attr("fill", function(d,i){return colors(i)})

    // Actions executed when the mouse is over the section
    .on("mouseover", function(d,i){
      canvas.attr("width", 2*width);
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
          if(d.data.version != "")
            return d.data.label + " (" + d.data.version + ") : " + d.data.value + " (" + ((d.data.value/total)*100).toFixed(0) + "%)";
          else
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
    .data(dataset, function(d,i){return d;})
    .enter()
    .append("li")
    .style("font-size", "2em")
    .style("line-height","0.5em")
    .attr("class",function(d,i){

      return selector+'Label'+i})
    .style("color",function(d,i){
      var tmp = segments(d);
      return colors(i);
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
      if(d.data.version != "")
        return d.data.label+" v."+ d.data.version+" : "+d.data.value
      else
        return d.data.label+ d.data.version+" : "+d.data.value
      });
}
