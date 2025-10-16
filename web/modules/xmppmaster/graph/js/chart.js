/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file chart.js
 */
function chart(selector, datas) {
  var total = 0;
  for (let i = 0; i < datas.length; i++) total += +datas[i].value;

  var height = 200, width = 200;
  var innerRadius = 3, outerRadius = 80;

  var canvas = d3.select("#" + selector)
    .style("display", "flex")
    .append("svg")
    .attr("width", width)
    .attr("height", height);

  var group = canvas.append("g")
    .attr("transform", "translate(" + (width) / 2 + "," + height / 2 + ")");

  var dataset = d3.pie().value(d => d.value)(datas);

  var segments = d3.arc()
    .innerRadius(innerRadius)
    .outerRadius(outerRadius)
    .padAngle(.20)
    .padRadius(5);

  group.selectAll("path")
    .data(dataset)
    .enter()
    .append("path")
    .attr("d", segments)
    .attr("fill", (d, i) => d.data.color)

    .on("mouseover", function (event, d) {
      const idx = d.index;

      d3.select("#" + selector).select("ul").select('.' + selector + 'Label' + idx)
        .style("font-size", "2.3em")
        .style("line-height", "0.5em");

      d3.select("#" + selector).select("ul").select('.' + selector + 'Label' + idx).select("a")
        .style("font-size", "1.1em")
        .style("font-weight", "bold");

      canvas.append("g").attr("class", selector + "tooltip");

      const p = d3.pointer(event, this);
      canvas.select("." + selector + "tooltip")
        .append("text")
        .attr("y", p[1] + 80)
        .attr("text-anchor", "start")
        .text(d.data.label + " : " + d.data.value + " (" + ((d.data.value / total) * 100).toFixed(0) + "%)")
        .attr("fill", "white");

      var tooltiptextwidth = jQuery("#" + selector + " svg ." + selector + "tooltip text")[0].getComputedTextLength();
      var tooltipwidth = tooltiptextwidth + 5;

      var offsetRect = ((width - tooltipwidth) / 2 > 0) ? (width - tooltipwidth) / 2 : 2;
      canvas.select("." + selector + "tooltip")
        .append("rect")
        .attr("rx", 2).attr("ry", 2)
        .attr("width", tooltipwidth)
        .attr("height", 22)
        .attr("opacity", 0.6)
        .attr("fill", "black")
        .attr("x", offsetRect)
        .attr("y", p[1] + 80 - 15).lower();

      var offsetText = ((width - tooltiptextwidth) / 2 > 0) ? (width - tooltiptextwidth) / 2 : 5;
      canvas.select("." + selector + "tooltip").select("text").attr("x", offsetText);

      d3.select(this)
        .attr("cursor", "pointer")
        .attr("d", d3.arc()
          .innerRadius(innerRadius)
          .outerRadius(outerRadius + 5)
          .padAngle(.20)
          .padRadius(5)(d));
    })

    .on("mouseout", function (event, d) {
      const idx = d.index;

      d3.select("#" + selector).select("ul").select('.' + selector + 'Label' + idx)
        .style("font-size", "2em")
        .style("line-height", "0.5em");

      d3.select("#" + selector).select("ul").select('.' + selector + 'Label' + idx).select("a")
        .style("font-size", "1em")
        .style("line-height", "0.5em")
        .style("font-weight", "normal");

      canvas.select("." + selector + "tooltip").remove();
      d3.select(this).attr("d", segments(d));
    })

    .on("click", function (event, d) {
      if (typeof d.data.href !== "undefined" && d.data.href !== "") {
        window.location.replace(d.data.href);
      }
    });

  d3.select("#" + selector).append("ul")
    .selectAll("li")
    .data(dataset)
    .enter()
    .append("li")
    .style("font-size", "2em")
    .style("line-height", "0.5em")
    .attr("class", (d, i) => selector + 'Label' + i)
    .style("color", (d, i) => d.data.color)
    .style("display", d => d.data.value == 0 ? "none" : null)
    .append("span")
    .append('a')
    .style("color", "black")
    .style("font-weight", "normal")
    .attr("href", d => (typeof d.data.onclick === "undefined") ? d.data.href : null)
    .attr("onclick", d => (typeof d.data.onclick !== "undefined") ? (d.data.onclick + "('" + d.data.label + "')") : null)
    .text(d => d.data.label + " : " + d.data.value + " (" + ((d.data.value / total) * 100).toFixed(0) + "%)");
}