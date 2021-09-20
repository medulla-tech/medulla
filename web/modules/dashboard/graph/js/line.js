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

function lineChart(selector, rawdatas){
  /*
  * The function lineChart create a line chart into the specified tag. The plot line
  * is generated from a serie of points contained in datas.
  *
  * @param selector : string, id of the tag used to create the chart.
  * param datas : dict, selection of points we want to display.
  * datas example :
  * [
  *   {"x": 0,"y":0.5},
  *   {"x": 1,"y":2},
  *   {"x": 2, "y": 1.3},
  * ]
  */

  var config = {
    top: 50,
    right: 50,
    bottom: 50,
    left: 50,
    width:125,
    height:70,
    delta:"absolute", // If the delta is absolute : the delta y is included between 0 and Ymax
    unit: " %"
  }
  if(typeof(rawdatas.config) !="undefined"){
    for(key in rawdatas.config){
      if(key != "delta")
        config[key] = rawdatas.config[key];
      else{
        if(["absolute", "relative"].includes(rawdatas.config[key])){
          config[key] = rawdatas.config[key];
        }
      }
    }
  }

  // Set the bottom border when labels are displayed
  if(config.xlabel == true){
    if(config.bottom < 75)
      config.bottom= 75;
  }


  if(typeof(rawdatas.datas) =="undefined"){
    datas = rawdatas;
  }
  else{
    datas = rawdatas.datas;
  }

  var total = 0;
  var load = datas.map(function(d){
    total += d.y;
    return d.y
  });

  n = load.length;
  min = Math.min.apply(null, load);


  var n = datas.length;
  for(i =0; i < n; i++)
  {
    total += datas[i].y;
  }

  if(config.delta == "absolute"){
    datas.unshift({"x":0,"y":0});
    datas.push({"x":n-1, "y":0});
  }
  else{
    datas.unshift({"x":0,"y":min});
    datas.push({"x":n-1, "y":min});
  }


  var xScale = d3.scaleLinear()
    .domain([0, n-1]) // input
    .range([0, config.width]); // output

  if(config.delta == "absolute"){
    var yScale = d3.scaleLinear()
      .domain([0, d3.max(load)]) // input
      .range([config.height, 0]); // output
  }
  else{
    var yScale = d3.scaleLinear()
      .domain([min, d3.max(load)]) // input
      .range([config.height, 0]); // output
  }

  var line = d3.line()
    .x(function(d, i) {return xScale(d.x); }) // set the x values for the line generator
    .y(function(d) { return yScale(d.y); }) // set the y values for the line generator
    .curve(d3.curveMonotoneX); // apply smoothing to the line

  var svg = d3.select("#"+selector).append("svg")
    .attr("width", config.width + config.left + config.right)
    .attr("height", config.height + config.top + config.bottom)
    .append("g")
    .attr("transform", "translate(" + config.left + "," + config.top + ")");

  xaxis = svg.append("g")
    .attr("class", "xaxis")
    .attr("transform", "translate(0," + config.height + ")")
    .call(d3.axisBottom(xScale).ticks(0)); // Create an axis component with d3.axisBottom

  yaxis = svg.append("g")
    .attr("class", "yaxis")
    .call(d3.axisLeft(yScale).ticks(3)); // Create an axis component with d3.axisLeft

  svg.append("path")
    .datum(datas) // 10. Binds data to the line
    .attr("class", "line") // Assign a class for styling
    .attr("d", line) // 11. Calls the line generator
    .attr("stroke","#ef2929")
    .attr("fill", "rgba(239, 41, 41,0.2)")
    .attr("stroke-width", "1px")

  svg.selectAll(".dot")
    .data(datas)
    .enter().append("circle") // Uses the enter().append() method
    .attr("class", "dot") // Assign a class for styling
    .attr("cx", function(d, i) {return xScale(d.x) })
    .attr("cy", function(d) { return yScale(d.y) })
    .attr("r", 4)
    .attr("display",function(d,i){
      if(i== 0 || i > n)
        return "none";
    })
    .attr("fill","#ef2929")
    .on("mouseover", function(d,i){
      svg.append("g")
        .attr("class", selector+"tooltip");

      svg.select("."+selector+"tooltip")
        .append("text")
        .attr("x", d3.mouse(this)[0]+2)
        .attr("y", d3.mouse(this)[1]-10)
        .attr("text-anchor", "start")
        .text(d.y+" "+config.unit)
        .attr("fill","white");

        var tooltiptextwidth = jQuery("#"+selector+" svg ."+selector+"tooltip text")[0].getComputedTextLength();
        var tooltipwidth = tooltiptextwidth +5;

        var offset = -2;
        svg.select("."+selector+"tooltip")
          .append("rect")
          .attr("rx", 2)
          .attr("ry", 2)
          .attr("width", tooltipwidth)
          .attr("height", 22)
          .attr("opacity", 0.6)
          .attr("fill", "black")
          .attr("x", d3.mouse(this)[0])
          .attr("y", d3.mouse(this)[1]-25).lower();

        svg.select("."+selector+"tooltip")
          .select("text");
    })
    .on("mouseout",function(){
      svg.select("."+selector+"tooltip").remove()
    });

    if(config.xlabel == true){
    svg.append("g")
    .attr("class", "xlabel")
    .attr("transform", "translate(0," + (config.height+15) + ") rotate(90)")
    .selectAll(".label")
    .data(datas)
    .enter().filter(function(d){
      if(typeof(d.label) != "undefined"){
        return d
      }
    })
    .append("text")
    .attr("y", function(d){return -1*xScale(d.x)})
    .text(function(d){return d.label;})
  }
}
