/**
 * (c) 2021 Siveo / http://siveo.net
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
 */

function barchart(selector, rawdatas){
  var config = {};
  var datas = {};
  if(typeof(rawdatas.config) == "undefined"){
    config = {
        top: 15,
        right: 45,
        bottom: 15,
        left: 30,
        width: 125,
        height: 200,
    };

  }
  else{
    config = rawdatas.config;
  }

  if(typeof(rawdatas.datas) == "undefined"){
    datas = rawdatas;
  }
  else{
    datas = rawdatas.datas;
  }

  var color1 = d3.scaleLinear()
    // Force constant color between 0 and 80%
    .domain([0, 80, 100])
    .range(['#e03c3c', '#e03c3c', '#52b749'])
    .interpolate(d3.interpolateHcl); //interpolateHsl interpolateHcl interpolateRgb";

  // Setup the svg canvas
  var svg = d3.select("#"+selector).append("svg")
      .attr("width", config.width + config.left + config.right)
      .attr("height", config.height + config.top + config.bottom)
      .append("g")
      .attr("transform", "translate(" + config.left + "," + config.top + ")");


  // Convert the max value to a linear scale of width (value = value*pixels)
  var x = d3.scaleLinear()
      .range([3, config.width])
      .domain([0, 100]);

  // Get the label for each lines
  // Manage the spacing between lines
  var y = d3.scaleBand()
      .range([0, config.height])
      .domain(datas.map(function(d){return d.label;}));

  var gy = svg.append("g")
      .attr("class", "y axis")
      .call(d3.axisLeft(y))
      .data(datas)
      .enter().append("g")

  var bars = svg.selectAll(".bar")
    .data(datas)
    .enter()
    .append("g")

  //append rects
  bars.append("rect")
    //.attr("class", "bar")
    .attr("style", function(d){
      color = color1(d.value)
      return "fill: "+color;
    })
    .attr("y", function (d,i) {
        return i*y.bandwidth();
    })
    .attr("height", y.bandwidth())
    .attr("width", function (d) {
        return x(d.value);
    });
  //add a value label to the right of each bar
  bars.append("text")
      .attr("class", "label")
      //y position of the label is halfway down the bar
      .attr("y", function (d,i) {
          return i*y.bandwidth() + 0.6*y.bandwidth();
      })
      //x position is 3 pixels to the right of the bar
      .attr("x", function (d) {
          return x(d.value) + 3;
      })
      .text(function (d) {
          return d.value+" %";
      });
}
