/* /usr/share/mmc/modules/reflex/graph/js/probeChart.js */
/* Time series renderers of the reflex module. Depends on d3 only: the curve of
   a numeric probe and the state timeline of a boolean one, sharing the frame,
   the margins and the date axis.
   No colour is set here: every element carries a class and the palette lives in
   graph/css/index.css, so the curve follows the theme.
   Timestamps arrive already shifted to the timezone of the server and are read
   back with the UTC formatters of d3. */

(function (global) {
  "use strict";

  var MARGIN = { top: 12, right: 26, bottom: 24, left: 48 };
  var PLOT_HEIGHT = 176;
  var MIN_WIDTH = 240;
  /* Horizontal room reserved per date label, wide enough for 07/09 or 14:32
     at the size of the axis font plus a gap. Fewer ticks is better than two
     labels touching, so the count follows the width of the card. */
  var TICK_SPACING = 62;
  var SEVERITIES = ["info", "medium", "high", "critical"];
  /* A hole in the measures is read on the cadence of the series itself: a
     probe reporting every five minutes and one reporting every hour are both
     regular, and no constant could judge either. Beyond this many times the
     median step, nothing was reported, and nothing is drawn across it: a line
     joining the two ends would show a descent the machine never made. */
  var GAP_STEPS = 3;
  /* Number of curve classes declared in graph/css/index.css. Beyond that the
     palette repeats: a machine carrying more than six volumes is served a
     legend, which is what tells the curves apart in the end. */
  var SERIES_CLASSES = 6;

  function d3lib() {
    return global.d3;
  }

  /* d3 v6 hands the event to the listener, v4 and v5 publish it as d3.event.
     The module is served with whichever d3 the base package installs. */
  function eventOf(candidate) {
    if (candidate && typeof candidate.clientX === "number") {
      return candidate;
    }
    var d3 = d3lib();
    return (d3 && d3.event) ? d3.event : null;
  }

  /* Decimal separator of the language the console is read in, handed over by
     the page: a curve must not write 43.6 next to a table that writes 43,6. */
  var decimalMark = ".";

  function numberText(value) {
    var text = String(value);
    return (decimalMark === ".") ? text : text.replace(".", decimalMark);
  }

  /* Two decimals at most: a load reported as 80.4213 is not measured that
     precisely, and the extra digits only push the cursor label wider. */
  function formatValue(value) {
    if (typeof value !== "number" || !isFinite(value)) {
      return "";
    }
    return numberText(Math.round(value * 100) / 100);
  }

  /* Axis labels stay short whatever the unit: a byte count would otherwise
     print eleven digits and eat half the card. */
  function formatTick(value) {
    var absolute = Math.abs(value);
    var scaled;
    var suffix = "";
    if (absolute >= 1e9) {
      scaled = value / 1e9;
      suffix = "G";
    } else if (absolute >= 1e6) {
      scaled = value / 1e6;
      suffix = "M";
    } else if (absolute >= 1e3) {
      scaled = value / 1e3;
      suffix = "k";
    } else {
      return numberText(Math.round(value * 100) / 100);
    }
    return numberText(Math.round(scaled * 10) / 10) + suffix;
  }

  /* Same shortening as the axis above a thousand, so the threshold caption
     and the graduation facing it read as the same number. */
  function formatCaption(value) {
    return (Math.abs(value) >= 1000) ? formatTick(value) : formatValue(value);
  }

  /* Hours over a day, dates beyond: an axis showing 07/09 six times says
     nothing, and one showing 14:32 over a month says no more. Read on what
     the frame actually spans, not on the period asked for. */
  function tickPatternFor(spanHours) {
    /* Under a quarter of an hour d3 may tick every thirty seconds, and two
       labels reading the same minute would say nothing. */
    if (spanHours <= 0.25) {
      return "%H:%M:%S";
    }
    if (spanHours <= 24) {
      return "%H:%M";
    }
    if (spanHours <= 72) {
      return "%d/%m %H:%M";
    }
    return "%d/%m";
  }

  /* Three labels at least: with one, nothing says what the frame spans. A
     date carrying its time needs roughly twice the room of a bare one, so the
     spacing follows the pattern rather than being fixed. */
  function tickCountFor(width, pattern) {
    var spacing = (pattern.length > 6) ? (TICK_SPACING * 1.7) : TICK_SPACING;
    return Math.max(3, Math.min(8, Math.floor(width / spacing)));
  }

  /* Steps the graduations are picked from: whole minutes, hours, days, weeks
     or months, so a label always falls on a round instant and two neighbours
     never read the same one. Left to a plain count, d3 may tick every twelve
     hours under a date only pattern, and the axis then prints 12/09 12/09
     13/09 13/09, which says nothing about where a peak sits. */
  var TICK_STEPS = [
    { ms: 1000, unit: "second", every: 1 },
    { ms: 5000, unit: "second", every: 5 },
    { ms: 15000, unit: "second", every: 15 },
    { ms: 30000, unit: "second", every: 30 },
    { ms: 60000, unit: "minute", every: 1 },
    { ms: 300000, unit: "minute", every: 5 },
    { ms: 600000, unit: "minute", every: 10 },
    { ms: 900000, unit: "minute", every: 15 },
    { ms: 1800000, unit: "minute", every: 30 },
    { ms: 3600000, unit: "hour", every: 1 },
    { ms: 7200000, unit: "hour", every: 2 },
    { ms: 10800000, unit: "hour", every: 3 },
    { ms: 21600000, unit: "hour", every: 6 },
    { ms: 43200000, unit: "hour", every: 12 },
    { ms: 86400000, unit: "day", every: 1 },
    { ms: 172800000, unit: "day", every: 2 },
    { ms: 604800000, unit: "week", every: 1 },
    { ms: 1209600000, unit: "week", every: 2 },
    { ms: 2592000000, unit: "month", every: 1 },
    { ms: 7776000000, unit: "month", every: 3 }
  ];

  /* The smallest step the frame holds no more labels of than there is room
     for: the finest graduation that still reads. */
  function stepIndexFor(spanMs, count) {
    var index;
    for (index = 0; index < TICK_STEPS.length; index++) {
      if ((spanMs / TICK_STEPS[index].ms) <= count) {
        return index;
      }
    }
    return TICK_STEPS.length - 1;
  }

  /* What a label has to carry to name its step: a graduation finer than a day
     needs the hour, or two of them read the same date. The day is dropped only
     where the frame spans a day at most, and 14:32 then names an instant on
     its own. */
  function patternForStep(step, spanHours) {
    if (step.unit === "second") {
      return "%H:%M:%S";
    }
    if (step.unit === "minute" || step.unit === "hour") {
      return (spanHours <= 24) ? "%H:%M" : "%d/%m %H:%M";
    }
    return "%d/%m";
  }

  /* The d3 interval a step is counted in, UTC or local to match the scale.
     Null where the d3 the base package installs does not publish it. */
  function intervalFor(utc, unit) {
    var d3 = d3lib();
    var names = {
      "second": "Second",
      "minute": "Minute",
      "hour": "Hour",
      "day": "Day",
      /* Weeks are counted from a Monday: a label every seven days on the day
         of the month would step over the end of a short month. */
      "week": "Monday",
      "month": "Month"
    };
    if (!d3 || !names[unit]) {
      return null;
    }
    var interval = utc ? d3[("utc" + names[unit])] : d3[("time" + names[unit])];
    return (interval && typeof interval.every === "function") ? interval : null;
  }

  /* The instants of one step inside the frame, or null where this d3 cannot
     count in that unit. */
  function ticksFor(scale, step, utc) {
    var interval = intervalFor(utc, step.unit);
    if (!interval) {
      return null;
    }
    var every = interval.every(step.every);
    return every ? scale.ticks(every) : null;
  }

  function repeats(values, format) {
    var seen = {};
    var index;
    for (index = 0; index < values.length; index++) {
      var label = format(values[index]);
      if (seen[label] === true) {
        return true;
      }
      seen[label] = true;
    }
    return false;
  }

  /* Graduations of the date axis, shared by the curve and the state timeline:
     two cards covering the same period have to carry the same dates in the
     same places, or nothing can be read from one against the other.
     Read on the frame and never on the measures, so a card holding two days of
     history inside a week is still graduated over the week. */
  function timeAxis(scale, from, to, width, utc) {
    var d3 = d3lib();
    var timeFormat = utc ? d3.utcFormat : d3.timeFormat;
    var spanMs = to - from;
    var spanHours = spanMs / 3600000;
    var pattern = tickPatternFor(spanHours);
    var index = 0;
    var guard;
    /* The room a label takes depends on what it carries, and what it carries
       depends on the step the room allowed: settled in a couple of passes,
       never looped on. The pattern always comes out of the step that was kept,
       so two neighbouring labels can never read the same instant. */
    for (guard = 0; guard < 3; guard++) {
      index = stepIndexFor(spanMs, tickCountFor(width, pattern));
      var wanted = patternForStep(TICK_STEPS[index], spanHours);
      if (wanted === pattern) {
        break;
      }
      pattern = wanted;
    }

    var values = ticksFor(scale, TICK_STEPS[index], utc);
    /* Two labels leave the middle of the frame unnamed: the next finer step is
       taken as long as its labels keep a reasonable share of the room they ask
       for. Distinct by construction, there again. */
    while (index > 0 && (!values || values.length < 3)) {
      var finer = TICK_STEPS[index - 1];
      var finerPattern = patternForStep(finer, spanHours);
      var finerValues = ticksFor(scale, finer, utc);
      if (!finerValues
          || finerValues.length > Math.ceil(tickCountFor(width, finerPattern) * 1.5)) {
        break;
      }
      index -= 1;
      pattern = finerPattern;
      values = finerValues;
    }
    /* Nothing usable out of the ladder: d3 picks the graduations, and the
       labels are told apart by adding the hour wherever they repeat. */
    if (!values || values.length < 2) {
      values = scale.ticks(tickCountFor(width, pattern));
      if (pattern === "%d/%m" && repeats(values, timeFormat(pattern))) {
        pattern = "%d/%m %H:%M";
        values = scale.ticks(tickCountFor(width, pattern));
      }
    }
    return { values: values, format: timeFormat(pattern) };
  }

  /* A stamp in seconds as the pages send them, null where nothing usable. */
  function stampOf(value) {
    if (value === null || value === "" || typeof value === "undefined"
        || typeof value === "boolean") {
      return null;
    }
    var number = Number(value);
    return isFinite(number) ? new Date(number * 1000) : null;
  }

  /* Bounds of the frame, out of the two dates the caller states and the extent
     of what it holds.

     The period asked for wins: every card of one period is then graduated the
     same way, and a curve that starts on the fourth day of a week is seen
     starting there instead of being stretched over the whole frame. The frame
     only widens to a measure falling outside the period, which is never drawn
     off it. */
  function boundsOf(spec, first, last) {
    var from = stampOf(spec ? spec.from : null);
    var to = stampOf(spec ? spec.to : null);
    if (from === null || (first !== null && first < from)) {
      from = first;
    }
    if (to === null || (last !== null && last > to)) {
      to = last;
    }
    if (from === null || to === null) {
      return null;
    }
    if (!(to > from)) {
      /* A window holding a single instant still needs a frame to draw it in. */
      to = new Date(from.getTime() + 60000);
    }
    return { from: from, to: to };
  }

  function severityClass(severity) {
    if (typeof severity !== "string") {
      return "";
    }
    var name = severity.toLowerCase();
    return (SEVERITIES.indexOf(name) === -1) ? "" : (" reflex-chart-threshold-" + name);
  }

  function readThreshold(spec) {
    var threshold = spec ? spec.threshold : null;
    if (!threshold || typeof threshold.value !== "number" || !isFinite(threshold.value)) {
      return null;
    }
    /* A threshold below zero has nothing to do on an axis anchored at zero. */
    if (threshold.value < 0) {
      return null;
    }
    return { value: threshold.value, severity: threshold.severity };
  }

  function textNode(parent, className) {
    var node = global.document.createElement("div");
    node.className = className;
    parent.appendChild(node);
    return node;
  }

  function seriesClass(index) {
    return "reflex-chart-serie-" + String(index % SERIES_CLASSES);
  }

  /* Cadence of a series, in milliseconds: the median of the steps between two
     measures. The median and not the mean, because the mean is moved by the
     very holes it is used to find. Zero when the series holds no usable step,
     which is how the caller knows it cannot judge a hole. */
  function medianStep(points) {
    var steps = [];
    var index;
    for (index = 1; index < points.length; index++) {
      var step = points[index].date - points[index - 1].date;
      if (step > 0) {
        steps.push(step);
      }
    }
    if (!steps.length) {
      return 0;
    }
    steps.sort(function (left, right) { return left - right; });
    var middle = Math.floor(steps.length / 2);
    return (steps.length % 2)
      ? steps[middle]
      : ((steps[middle - 1] + steps[middle]) / 2);
  }

  /* The extent a point stands for, its own value when it stands for itself:
     an unreduced measure is its own minimum and its own maximum. */
  function lowOf(point) {
    return (typeof point.low === "number") ? point.low : point.value;
  }

  function highOf(point) {
    return (typeof point.high === "number") ? point.high : point.value;
  }

  /* The points as the line is drawn from, a marker inserted wherever the
     measures stop. The marker carries the coordinates of its neighbour so no
     accessor can ever read it as a value, and the renderer skips it: the path
     ends before the hole and starts again after it. */
  function withHoles(points, cutoff) {
    if (!isFinite(cutoff)) {
      return points;
    }
    var drawn = [];
    var index;
    for (index = 0; index < points.length; index++) {
      if (index > 0 && (points[index].date - points[index - 1].date) > cutoff) {
        drawn.push({
          date: points[index - 1].date,
          value: points[index - 1].value,
          hole: true
        });
      }
      drawn.push(points[index]);
    }
    return drawn;
  }

  /* The curves to draw, whatever shape the caller holds them in. A probe
     reporting a single value hands one unnamed curve, one reporting a value
     per mount point hands one per volume. */
  function readCurves(spec) {
    var raw = (spec.series && spec.series.length)
      ? spec.series
      : [{ key: "", points: spec.points || [] }];
    var curves = [];
    var index;
    var position;
    for (index = 0; index < raw.length; index++) {
      var points = raw[index].points || [];
      var series = [];
      var banded = false;
      for (position = 0; position < points.length; position++) {
        var value = Number(points[position].v);
        if (!isFinite(value)) {
          continue;
        }
        var entry = {
          date: new Date(Number(points[position].t) * 1000),
          value: value
        };
        /* What the point stands for: on a reduced window it is an interval,
           its value is the average, and this is the extent the interval went
           through. Drawn behind the curve, because an average alone buries a
           minute at a hundred per cent in an hour of calm. */
        var low = Number(points[position].lo);
        var high = Number(points[position].hi);
        if (isFinite(low) && isFinite(high) && high >= low) {
          entry.low = low;
          entry.high = high;
          if (high > low) {
            banded = true;
          }
        }
        var samples = Number(points[position].n);
        if (isFinite(samples) && samples > 0) {
          entry.samples = samples;
        }
        series.push(entry);
      }
      /* A curve of one point draws no line. It is kept out rather than drawn
         as a dot nobody can read a trend from. */
      if (series.length >= 2) {
        var step = medianStep(series);
        /* Without a cadence nothing can be called a hole, and the curve is
           drawn as it always was. */
        var cutoff = (step > 0) ? (step * GAP_STEPS) : Infinity;
        curves.push({
          key: (typeof raw[index].key === "string") ? raw[index].key : "",
          series: series,
          banded: banded,
          cutoff: cutoff,
          /* How far from a measure the cursor still reads it: half a cadence,
             which is the distance the snapping already covered. Past that,
             inside a hole, there is no measure to read. */
          reach: (step > 0) ? (step / 2) : Infinity,
          drawn: withHoles(series, cutoff)
        });
      }
    }
    return curves;
  }

  /**
   * Draw the series of one probe into a container.
   *
   * @param node  DOM element receiving the chart, emptied first.
   * @param spec  {series: [{key, points: [{t, v, lo, hi, n}]}],
   *               from, to, unit, threshold: {value, severity}|null,
   *               labels: {threshold}}
   *              lo and hi are the extent a point stands for when it covers an
   *              interval, n the measures it was computed from. A single
   *              unnamed curve may also be handed as spec.points. from and to
   *              are the period asked for: the frame spans them, the curve
   *              only spans its measures.
   * @return true when a frame was drawn, measures or not.
   */
  function draw(node, spec) {
    var d3 = d3lib();
    if (!node || !d3 || !spec) {
      return false;
    }

    var curves = readCurves(spec);
    /* Spanned over every curve: two volumes that started reporting on
       different days must be drawn on the same axis, not each on its own. */
    var firstDate = curves.length
      ? d3.min(curves, function (curve) { return curve.series[0].date; }) : null;
    var lastDate = curves.length
      ? d3.max(curves, function (curve) {
        return curve.series[curve.series.length - 1].date;
      }) : null;
    /* The frame comes from the period the card was asked for, and is drawn
       even where the period holds no measure at all: a card that disappears
       says nothing, an empty frame on the right axis says the period went by
       without a measure. */
    var bounds = boundsOf(spec, firstDate, lastDate);
    if (!bounds) {
      return false;
    }

    decimalMark = (typeof spec.decimal === "string" && spec.decimal !== "")
      ? spec.decimal : ".";

    node.innerHTML = "";

    /* A single volume is named too: a machine carrying one must read like a
       machine carrying three, legend included. */
    var named = curves.length > 1 || (curves.length === 1 && curves[0].key !== "");
    var index;

    var outerWidth = Math.max(MIN_WIDTH, node.clientWidth || MIN_WIDTH);
    var width = outerWidth - MARGIN.left - MARGIN.right;
    var height = PLOT_HEIGHT - MARGIN.top - MARGIN.bottom;
    var unit = (typeof spec.unit === "string") ? spec.unit : "";

    /* Read on the top of the band: a bucket kept for its minimum can hold
       measures above the curve, which must stay inside the frame. */
    var maxValue = d3.max(curves, function (curve) {
      return d3.max(curve.series, function (d) { return highOf(d); });
    });
    var threshold = readThreshold(spec);
    /* No measure to read a top from: the threshold, where there is one, is
       what the axis is scaled on, so the line falls inside the frame. */
    var top = (typeof maxValue === "number" && isFinite(maxValue)) ? maxValue : 0;
    if (threshold && threshold.value > top) {
      top = threshold.value;
    }
    /* A flat series at zero still needs a readable axis. */
    if (!(top > 0)) {
      top = 1;
    }

    /* Anchored at zero: a load moving between 80 and 82 must not look like a
       cliff. The headroom keeps the curve and the threshold off the frame. */
    var domainTop = top * 1.1;
    /* A percentage cannot exceed 100, and an axis climbing to 120 suggests a
       range the machine can never reach. The cap is lifted only when a value
       or a threshold genuinely goes above it. */
    if (unit.replace(/\s+/g, "") === "%" && top <= 100) {
      domainTop = 100;
    }
    var y = d3.scaleLinear().domain([0, domainTop]).nice(4).range([height, 0]);
    /* An extent worth reading out: one twentieth of the frame, which is about
       where the band stops being a line under the curve. */
    var wideEnough = domainTop / 20;

    /* Scale and formatters have to agree on the timezone: the stamps are
       already shifted server side, so both read them as UTC. An older d3
       without the UTC pair falls back to the local one, which only shifts the
       labels of a console opened from another timezone. */
    var utc = !!(d3.scaleUtc && d3.utcFormat);
    var timeFormat = utc ? d3.utcFormat : d3.timeFormat;
    var x = (utc ? d3.scaleUtc() : d3.scaleTime())
      .domain([bounds.from, bounds.to])
      .range([0, width]);

    var svg = d3.select(node).append("svg")
      .attr("class", "reflex-chart-svg")
      .attr("width", outerWidth)
      .attr("height", PLOT_HEIGHT)
      .append("g")
      .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")");

    svg.append("g")
      .attr("class", "reflex-chart-grid")
      .call(d3.axisLeft(y).ticks(4).tickSize(-width)
        .tickFormat(function () { return ""; }));

    /* Read on the frame, which is the period asked for: the state timeline of
       the same machine is graduated the same way, and a break of the one falls
       under the hole of the other. */
    var spanHours = (bounds.to - bounds.from) / 3600000;
    var axis = timeAxis(x, bounds.from, bounds.to, width, utc);

    svg.append("g")
      .attr("class", "reflex-chart-axis reflex-chart-axis-x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x).tickValues(axis.values)
        .tickFormat(axis.format).tickSizeOuter(0));

    svg.append("g")
      .attr("class", "reflex-chart-axis reflex-chart-axis-y")
      .call(d3.axisLeft(y).ticks(4).tickFormat(formatTick).tickSizeOuter(0));

    /* Straight segments between measures, no spline: a monotone curve draws
       values between two points that were never measured, and over a hole it
       invents a whole descent. A segment at least says "the measure went from
       here to there" and nothing more.

       defined() is what cuts the line and the area on a hole: the path stops
       at the last measure before the silence and starts again at the first
       one after it. */
    function measured(d) {
      return !d.hole;
    }

    var area = d3.area()
      .defined(measured)
      .x(function (d) { return x(d.date); })
      .y0(height)
      .y1(function (d) { return y(d.value); })
      .curve(d3.curveLinear);

    var line = d3.line()
      .defined(measured)
      .x(function (d) { return x(d.date); })
      .y(function (d) { return y(d.value); })
      .curve(d3.curveLinear);

    /* Between the lowest and the highest the point stands for. Drawn behind
       the curve and only where a point covers an interval: on a window
       reduced to fit, the curve carries averages, and the peak that raised
       the alert only exists in this band. */
    var band = d3.area()
      .defined(measured)
      .x(function (d) { return x(d.date); })
      .y0(function (d) { return y(lowOf(d)); })
      .y1(function (d) { return y(highOf(d)); })
      .curve(d3.curveLinear);

    /* Filled under a single curve only: three shaded areas stacked on the
       same frame hide each other and the value read becomes a guess. */
    if (curves.length === 1) {
      svg.append("path").datum(curves[0].drawn).attr("class", "reflex-chart-area").attr("d", area);
    }

    for (index = 0; index < curves.length; index++) {
      if (curves[index].banded) {
        svg.append("path").datum(curves[index].drawn)
          .attr("class", "reflex-chart-range " + seriesClass(index))
          .attr("d", band);
      }
    }

    for (index = 0; index < curves.length; index++) {
      svg.append("path").datum(curves[index].drawn)
        .attr("class", "reflex-chart-line " + seriesClass(index))
        .attr("d", line);
    }

    if (threshold) {
      var thresholdY = y(threshold.value);
      var thresholdClass = severityClass(threshold.severity);
      svg.append("line")
        .attr("class", "reflex-chart-threshold" + thresholdClass)
        .attr("x1", 0).attr("x2", width)
        .attr("y1", thresholdY).attr("y2", thresholdY);
      var caption = (spec.labels && spec.labels.threshold) ? spec.labels.threshold + " " : "";
      svg.append("text")
        .attr("class", "reflex-chart-threshold-label" + thresholdClass)
        .attr("x", width)
        /* Above the line, except when the line hugs the top of the frame. */
        .attr("y", (thresholdY < 12) ? (thresholdY + 12) : (thresholdY - 4))
        .attr("text-anchor", "end")
        .text(caption + formatCaption(threshold.value) + unit);
    }

    /* ---------------------------------------------------------------- *
     * Cursor
     * ---------------------------------------------------------------- */
    var focus = svg.append("g").attr("class", "reflex-chart-focus").style("display", "none");
    focus.append("line").attr("class", "reflex-chart-cursor").attr("y1", 0).attr("y2", height);
    var cursorPoints = [];
    for (index = 0; index < curves.length; index++) {
      cursorPoints.push(focus.append("circle")
        .attr("class", "reflex-chart-cursor-point " + seriesClass(index))
        .attr("r", 4));
    }

    /* Read out as HTML rather than SVG text: the box wraps to its content on
       its own, no glyph measuring, and it inherits the fonts of the console. */
    var tip = global.document.createElement("div");
    tip.className = "reflex-chart-tip";
    tip.style.display = "none";
    node.appendChild(tip);
    /* One line per curve: on a probe reporting a value per volume, reading one
       of them under the cursor while the others are drawn would leave the
       reader comparing curves by eye. */
    var tipValues = [];
    for (index = 0; index < curves.length; index++) {
      /* Coloured only where there are curves to match: a single curve keeps
         the read out it always had. */
      tipValues.push(textNode(tip, "reflex-chart-tip-value"
        + (named ? (" " + seriesClass(index)) : "")));
    }
    var tipTime = textNode(tip, "reflex-chart-tip-time");

    /* Seconds on a short window, where neighbouring measures can share the
       same minute. */
    var stampFormat = timeFormat((spanHours <= 6) ? "%d/%m %H:%M:%S" : "%d/%m %H:%M");
    var bisect = d3.bisector(function (d) { return d.date; }).left;

    /* The measure of a curve closest to an instant, never an interpolation:
       the value read has to be one the agent actually reported.

       Nothing is handed back inside a hole. The cursor would otherwise read
       out a measure taken two days earlier as the value of the instant it
       points at, which is exactly the reading the cut line is there to stop.
       The measures bounding the hole stay readable within half a cadence of
       themselves, so pointing at one of them still answers. */
    function nearest(curve, wanted) {
      var points = curve.series;
      /* Before the first measure or after the last: the frame spans the period
         asked for, which the measures may only fill part of. Read within half
         a cadence of the nearest end, nothing beyond -- the cursor must not
         date the first measure of a curve to a day nothing was measured on. */
      if (wanted < points[0].date) {
        return ((points[0].date - wanted) <= curve.reach) ? points[0] : null;
      }
      var newest = points[points.length - 1];
      if (wanted > newest.date) {
        return ((wanted - newest.date) <= curve.reach) ? newest : null;
      }
      var position = bisect(points, wanted, 1);
      var before = points[position - 1];
      var after = points[position];
      if (!before) {
        return (after && (after.date - wanted) <= curve.reach) ? after : null;
      }
      if (!after) {
        return ((wanted - before.date) <= curve.reach) ? before : null;
      }
      if ((after.date - before.date) > curve.cutoff) {
        if ((wanted - before.date) <= curve.reach) {
          return before;
        }
        return ((after.date - wanted) <= curve.reach) ? after : null;
      }
      return ((wanted - before.date) > (after.date - wanted)) ? after : before;
    }

    var overlay = svg.append("rect")
      .attr("class", "reflex-chart-overlay")
      .attr("width", width)
      .attr("height", height);
    var overlayNode = overlay.node();

    function hide() {
      focus.style("display", "none");
      tip.style.display = "none";
    }

    function move(candidate) {
      var event = eventOf(candidate);
      if (!event || !overlayNode) {
        return;
      }
      var box = overlayNode.getBoundingClientRect();
      var pointer = event.clientX - box.left;
      if (pointer < 0) {
        pointer = 0;
      } else if (pointer > width) {
        pointer = width;
      }

      /* Snap to the measure, never to the pixel: the value read has to be one
         the agent actually reported. */
      var wanted = x.invert(pointer);
      var anchor = null;
      var closest = null;
      var position;
      for (position = 0; position < curves.length; position++) {
        var point = nearest(curves[position], wanted);
        if (!point) {
          cursorPoints[position].style("display", "none");
          tipValues[position].textContent = "";
          continue;
        }
        cursorPoints[position].style("display", null)
          .attr("cx", x(point.date)).attr("cy", y(point.value));
        /* The name of the curve travels with its value: two figures one under
           the other say nothing about which volume each belongs to.

           The extent follows the value only where it is wide enough to be
           worth reading: a point covering an interval that went from 12 to 88
           is not described by its average alone, while one that barely moved
           is, and printing two more figures there would only crowd the box. */
        var reading = formatValue(point.value) + unit;
        if ((highOf(point) - lowOf(point)) > wideEnough) {
          /* The unit is written once, on the value: repeating it inside the
             extent only makes the box wider. */
          reading += " (" + formatValue(lowOf(point))
            + " - " + formatValue(highOf(point)) + ")";
        }
        tipValues[position].textContent = named
          ? (curves[position].key + " " + reading) : reading;
        var gap = Math.abs(point.date - wanted);
        if (closest === null || gap < closest) {
          closest = gap;
          anchor = point;
        }
      }
      /* Every curve silent here: the pointer sits in a hole, and a read out
         left on screen from the last position would date a measure to an
         instant nothing was measured at. */
      if (!anchor) {
        hide();
        return;
      }

      /* The cursor line and the read out sit on the measure nearest the
         pointer, whichever curve carries it. */
      var px = x(anchor.date);
      var py = y(anchor.value);
      focus.style("display", null);
      focus.select(".reflex-chart-cursor").attr("x1", px).attr("x2", px);

      tipTime.textContent = stampFormat(anchor.date);
      tip.style.display = "block";

      /* Flips to the other side of the cursor near the right edge, so the box
         never leaves the card. */
      var left = MARGIN.left + px + 12;
      if (left + tip.offsetWidth > outerWidth) {
        left = MARGIN.left + px - 12 - tip.offsetWidth;
      }
      if (left < 0) {
        left = 0;
      }
      var topOffset = MARGIN.top + py - 34;
      /* A read out holding one line per curve is tall enough to run past the
         frame, where the card would clip it. */
      if (topOffset + tip.offsetHeight > PLOT_HEIGHT) {
        topOffset = PLOT_HEIGHT - tip.offsetHeight;
      }
      if (topOffset < 0) {
        topOffset = 0;
      }
      tip.style.left = left + "px";
      tip.style.top = topOffset + "px";
    }

    overlay
      .on("mouseenter", move)
      .on("mousemove", move)
      .on("mouseleave", hide);

    /* Legend, under the frame and only where the curves carry a name: on a
       probe reporting a single value there is nothing to tell apart, and a
       legend of one entry would only repeat the title of the card. */
    if (named) {
      var legend = global.document.createElement("div");
      legend.className = "reflex-chart-legend";
      for (index = 0; index < curves.length; index++) {
        var entry = textNode(legend, "reflex-chart-legend-item " + seriesClass(index));
        textNode(entry, "reflex-chart-legend-swatch");
        var label = textNode(entry, "reflex-chart-legend-label");
        /* The name comes from the machine: written as text, never as markup. */
        label.textContent = curves[index].key;
      }
      node.appendChild(legend);
    }

    return true;
  }

  /* ------------------------------------------------------------------ *
   * State timeline of a boolean probe. Plotted on an axis a boolean would be
   * a square wave nobody reads a level from: what is asked of it is since
   * when the state is the one it is. Same frame as a curve, only the plot
   * area differs.
   * ------------------------------------------------------------------ */
  var BAND_HEIGHT = 26;
  /* Room above a band for the name of what it was measured on, on a probe
     reporting one state per volume. */
  var BAND_LABEL = 14;
  var BAND_SPACING = 10;
  /* A run of a single measure has no duration and would be drawn as nothing:
     it is given the few pixels it takes to be seen and pointed at. */
  var BAND_MIN_WIDTH = 2;

  /* The band that alerts is coloured by the severity of the condition it
     breaks, exactly as the threshold line of a curve is: a probe raising a
     critical alert must not be read as an informative one. */
  function stateSeverityClass(severity) {
    if (typeof severity !== "string") {
      return "";
    }
    var name = severity.toLowerCase();
    return (SEVERITIES.indexOf(name) === -1) ? "" : (" reflex-state-" + name);
  }

  /* A stretch nothing is known over: neither of the two states, and a tint of
     its own, so it is never read as one of them. */
  var UNKNOWN_CLASS = "reflex-state-band-unknown";

  function stateClass(value, good, severity) {
    /* The probe carries no condition: nothing says which of the two states it
       is meant to be in, so two neutral tints told apart in the legend. */
    if (good === null) {
      return value ? "reflex-state-band-on" : "reflex-state-band-off";
    }
    if (value === good) {
      return "reflex-state-band-good";
    }
    return "reflex-state-band-bad" + stateSeverityClass(severity);
  }

  /* The cadence the states are measured at, in milliseconds, zero when the
     caller does not know it and the measures are the only thing left to read
     it from. What it serves is to tell a silence from a normal wait between
     two measures, and nothing else: a band never runs past the measure that
     ended it.

     On a reduced window a point stands for an interval rather than for an
     instant, and that interval is never shorter than the cadence: the wider
     of the two is what separates two points sent, and reading the closer one
     would cut a continuous band into silences. */
  function stateCadence(spec) {
    var declared = Number(spec.interval);
    if (!isFinite(declared) || declared <= 0) {
      return 0;
    }
    var bucket = Number(spec.bucket);
    if (isFinite(bucket) && bucket > declared) {
      declared = bucket;
    }
    return declared * 1000;
  }

  function readStateRows(spec) {
    var cadence = stateCadence(spec);
    var raw = (spec.series && spec.series.length)
      ? spec.series
      : [{ key: "", points: spec.points || [] }];
    var rows = [];
    var index;
    var position;
    for (index = 0; index < raw.length; index++) {
      var source = raw[index].points || [];
      var points = [];
      for (position = 0; position < source.length; position++) {
        var value = Number(source[position].v);
        if (!isFinite(value)) {
          continue;
        }
        points.push({
          date: new Date(Number(source[position].t) * 1000),
          value: value ? 1 : 0
        });
      }
      /* One measure is enough here: it says the state was that one at that
         date, which is more than an empty frame says. */
      if (points.length) {
        var step = (cadence > 0) ? cadence : medianStep(points);
        rows.push({
          key: (typeof raw[index].key === "string") ? raw[index].key : "",
          points: points,
          cutoff: (step > 0) ? (step * GAP_STEPS) : Infinity
        });
      }
    }
    return rows;
  }

  /**
   * The period cut into stretches of one state, the silences kept as such.
   *
   * A state holds until something else is measured. Where the measures stop
   * for more than a few cadences the stretch carries no state rather than the
   * last one seen: an agent quiet for two days said nothing about it. The
   * period before the first measure is one of those silences.
   */
  function stateSlots(row, from, to) {
    var runs = [];
    var current = null;
    var index;
    for (index = 0; index < row.points.length; index++) {
      var point = row.points[index];
      if (current && (point.date - current.to) <= row.cutoff) {
        if (point.value === current.value) {
          current.to = point.date;
          continue;
        }
        /* The change is dated on the first measure carrying the new state:
           it happened somewhere between the two, and that is the only end of
           the interval anything was actually observed at. */
        current.to = point.date;
        runs.push(current);
      } else if (current) {
        runs.push(current);
      }
      current = { value: point.value, from: point.date, to: point.date };
    }
    if (current) {
      runs.push(current);
    }

    var slots = [];
    var edge = from;
    for (index = 0; index < runs.length; index++) {
      if (runs[index].from > edge) {
        slots.push({ value: null, from: edge, to: runs[index].from });
      }
      slots.push(runs[index]);
      edge = runs[index].to;
    }
    if (to > edge) {
      slots.push({ value: null, from: edge, to: to });
    }
    return slots;
  }

  /**
   * One row out of stretches already cut, rather than out of measures.
   * Reading a cadence out of them would cut a week long connection into the
   * silence of a probe that had nothing to say.
   *
   * @param spec {spans: [{from, to, v: 0|1}]}
   */
  function readSpanRows(spec) {
    var raw = spec.spans || [];
    var slots = [];
    var index;
    for (index = 0; index < raw.length; index++) {
      var start = Number(raw[index].from);
      var end = Number(raw[index].to);
      if (!isFinite(start) || !isFinite(end) || end <= start) {
        continue;
      }
      slots.push({
        value: Number(raw[index].v) ? 1 : 0,
        from: new Date(start * 1000),
        to: new Date(end * 1000)
      });
    }
    if (!slots.length) {
      return [];
    }
    slots.sort(function (left, right) { return left.from - right.from; });
    return [{ key: "", points: [], slots: slots }];
  }

  /**
   * Stretches clipped to the frame, the gaps between them left as silences:
   * what no stretch covers carries no state rather than the one before it.
   */
  function padSlots(slots, from, to) {
    var padded = [];
    var edge = from;
    var index;
    for (index = 0; index < slots.length; index++) {
      if (slots[index].to <= edge) {
        continue;
      }
      if (slots[index].from >= to) {
        break;
      }
      var start = (slots[index].from > edge) ? slots[index].from : edge;
      if (start > edge) {
        padded.push({ value: null, from: edge, to: start });
      }
      var end = (slots[index].to > to) ? to : slots[index].to;
      padded.push({ value: slots[index].value, from: start, to: end });
      edge = end;
    }
    if (to > edge) {
      padded.push({ value: null, from: edge, to: to });
    }
    return padded;
  }

  /* Ends of what a row holds, whichever way it was read: measures dated one
     by one, or stretches carrying their own bounds. */
  function rowFirst(row) {
    return row.points.length ? row.points[0].date : row.slots[0].from;
  }

  function rowLast(row) {
    return row.points.length
      ? row.points[row.points.length - 1].date
      : row.slots[row.slots.length - 1].to;
  }

  /* Two dates into the sentence the page handed over, so the wording and the
     order of the two stamps belong to the catalog and not to this script. */
  function fillSpan(pattern, first, second) {
    var used = false;
    return String(pattern).replace(/%s/g, function () {
      if (used) {
        return second;
      }
      used = true;
      return first;
    });
  }

  /**
   * Draw a state timeline into a container.
   *
   * @param node  DOM element receiving the timeline, emptied first.
   * @param spec  {series: [{key, points: [{t, v: 0|1}]}],
   *               spans: [{from, to, v: 0|1}],
   *               from, to, interval, bucket,
   *               good: 0|1|null, severity, unknown,
   *               labels: {yes, no, none, span}}
   *              spans, when given, replaces series. good is the state that
   *              raises no alert, null when no condition tells one from the
   *              other. unknown paints and names the stretches nothing is
   *              known over.
   * @return true when a timeline was drawn.
   */
  function drawStates(node, spec) {
    var d3 = d3lib();
    if (!node || !d3 || !spec) {
      return false;
    }

    var rows = (spec.spans && spec.spans.length)
      ? readSpanRows(spec) : readStateRows(spec);
    /* The band spans the period that was asked for, not the history that
       happens to fill it: a machine that started reporting yesterday on a
       thirty day window must show the twenty nine days it says nothing
       about. */
    var frame = boundsOf(spec,
      rows.length ? d3.min(rows, rowFirst) : null,
      rows.length ? d3.max(rows, rowLast) : null);
    if (!frame) {
      return false;
    }
    if (!rows.length) {
      /* Nothing measured over the period: one silent row, so the frame and its
         axis are still drawn and the card reads as a period without a measure
         rather than as a card that was never there. */
      rows = [{ key: "", points: [], cutoff: Infinity }];
    }

    node.innerHTML = "";

    var labels = spec.labels || {};
    var good = (spec.good === 0 || spec.good === 1) ? spec.good : null;
    var severity = (typeof spec.severity === "string") ? spec.severity : "";
    var unknown = !!spec.unknown;
    var named = rows.length > 1 || rows[0].key !== "";
    var index;

    var outerWidth = Math.max(MIN_WIDTH, node.clientWidth || MIN_WIDTH);
    var width = outerWidth - MARGIN.left - MARGIN.right;

    var utc = !!(d3.scaleUtc && d3.utcFormat);
    var timeFormat = utc ? d3.utcFormat : d3.timeFormat;

    var from = frame.from;
    var to = frame.to;

    var rowHeight = BAND_HEIGHT + (named ? BAND_LABEL : 0);
    var stack = rows.length * rowHeight + (rows.length - 1) * BAND_SPACING;
    /* The card keeps the height of a curve card, so a machine carrying both
       reads as one block. It only grows past it when the bands no longer
       fit. */
    var height = Math.max(PLOT_HEIGHT - MARGIN.top - MARGIN.bottom, stack);
    var outerHeight = height + MARGIN.top + MARGIN.bottom;
    var top = Math.max(0, (height - stack) / 2);

    var x = (utc ? d3.scaleUtc() : d3.scaleTime())
      .domain([from, to])
      .range([0, width]);

    var svg = d3.select(node).append("svg")
      .attr("class", "reflex-chart-svg")
      .attr("width", outerWidth)
      .attr("height", outerHeight)
      .append("g")
      .attr("transform", "translate(" + MARGIN.left + "," + MARGIN.top + ")");

    /* Same graduations as the curves of the same period, read on the frame and
       drawn by the same code: the two cards are put side by side to be read
       against each other. */
    var axis = timeAxis(x, from, to, width, utc);

    svg.append("g")
      .attr("class", "reflex-chart-axis reflex-chart-axis-x")
      .attr("transform", "translate(0," + height + ")")
      .call(d3.axisBottom(x).tickValues(axis.values)
        .tickFormat(axis.format).tickSizeOuter(0));

    var seen = { 0: false, 1: false };
    var seenUnknown = false;
    for (index = 0; index < rows.length; index++) {
      var bandTop = top + index * (rowHeight + BAND_SPACING)
        + (named ? BAND_LABEL : 0);
      rows[index].top = bandTop;
      /* A row read out of stretches already holds them: it is clipped to the
         frame, never cut again on a cadence it never had. */
      rows[index].slots = rows[index].slots
        ? padSlots(rows[index].slots, from, to)
        : stateSlots(rows[index], from, to);

      if (named) {
        /* The name comes from the machine: written as text, never as
           markup. d3 sets the content of the node, it does not parse it. */
        svg.append("text")
          .attr("class", "reflex-state-label")
          .attr("x", 0)
          .attr("y", bandTop - 4)
          .text(rows[index].key);
      }

      /* Behind the states: what the period covers, so a band that only fills
         a corner of it is read as a band that stops, not as a short frame. */
      svg.append("rect")
        .attr("class", "reflex-state-track")
        .attr("x", 0).attr("y", bandTop)
        .attr("width", width).attr("height", BAND_HEIGHT);

      var slots = rows[index].slots;
      var position;
      for (position = 0; position < slots.length; position++) {
        var slot = slots[position];
        /* A silence is drawn as nothing at all: the track shows through, and
           nobody reads a colour where no measure was taken. Where the caller
           asks for it, it is painted and named instead, so a period nothing is
           known over is not read as the state around it. */
        if (slot.value === null && !unknown) {
          continue;
        }
        if (slot.value === null) {
          seenUnknown = true;
        } else {
          seen[slot.value] = true;
        }
        svg.append("rect")
          .attr("class", "reflex-state-band "
            + ((slot.value === null)
              ? UNKNOWN_CLASS : stateClass(slot.value, good, severity)))
          .attr("x", x(slot.from))
          .attr("y", bandTop)
          .attr("width", Math.max(BAND_MIN_WIDTH, x(slot.to) - x(slot.from)))
          .attr("height", BAND_HEIGHT);
      }
    }

    /* ---------------------------------------------------------------- *
     * Cursor
     * ---------------------------------------------------------------- */
    var focus = svg.append("g").attr("class", "reflex-chart-focus").style("display", "none");
    focus.append("line").attr("class", "reflex-chart-cursor")
      .attr("y1", 0).attr("y2", height);

    var tip = global.document.createElement("div");
    tip.className = "reflex-chart-tip";
    tip.style.display = "none";
    node.appendChild(tip);
    var tipState = textNode(tip, "reflex-chart-tip-value");
    var tipSpan = textNode(tip, "reflex-chart-tip-time");

    /* The date travels with the hour whatever the period: a stretch of state
       is read for when it started, and 08:00 alone does not say which day. */
    var stampFormat = timeFormat("%d/%m %H:%M");

    function stateText(value) {
      if (value === null) {
        return labels.none || "";
      }
      return (value ? labels.yes : labels.no) || "";
    }

    /* The row the pointer sits on, by the band nearest it: the gap between
       two bands belongs to one of them, not to nothing. */
    function rowAt(offset) {
      var best = 0;
      var closest = null;
      var position;
      for (position = 0; position < rows.length; position++) {
        var distance = Math.abs(offset - (rows[position].top + BAND_HEIGHT / 2));
        if (closest === null || distance < closest) {
          closest = distance;
          best = position;
        }
      }
      return rows[best];
    }

    function slotAt(row, wanted) {
      var position;
      for (position = 0; position < row.slots.length; position++) {
        if (wanted >= row.slots[position].from && wanted <= row.slots[position].to) {
          return row.slots[position];
        }
      }
      return null;
    }

    var overlay = svg.append("rect")
      .attr("class", "reflex-chart-overlay")
      .attr("width", width)
      .attr("height", height);
    var overlayNode = overlay.node();

    function hide() {
      focus.style("display", "none");
      tip.style.display = "none";
    }

    function move(candidate) {
      var event = eventOf(candidate);
      if (!event || !overlayNode) {
        return;
      }
      var box = overlayNode.getBoundingClientRect();
      var pointer = event.clientX - box.left;
      if (pointer < 0) {
        pointer = 0;
      } else if (pointer > width) {
        pointer = width;
      }

      var row = rowAt(event.clientY - box.top);
      var slot = slotAt(row, x.invert(pointer));
      if (!slot) {
        hide();
        return;
      }

      focus.style("display", null);
      focus.select(".reflex-chart-cursor").attr("x1", pointer).attr("x2", pointer);

      var state = stateText(slot.value);
      tipState.textContent = (named && row.key !== "")
        ? (row.key + " " + state) : state;
      tipSpan.textContent = fillSpan(labels.span || "%s %s",
        stampFormat(slot.from), stampFormat(slot.to));
      tip.style.display = "block";

      var left = MARGIN.left + pointer + 12;
      if (left + tip.offsetWidth > outerWidth) {
        left = MARGIN.left + pointer - 12 - tip.offsetWidth;
      }
      if (left < 0) {
        left = 0;
      }
      var topOffset = MARGIN.top + row.top - tip.offsetHeight - 6;
      if (topOffset < 0) {
        topOffset = MARGIN.top + row.top + BAND_HEIGHT + 6;
      }
      if (topOffset + tip.offsetHeight > outerHeight) {
        topOffset = outerHeight - tip.offsetHeight;
      }
      tip.style.left = left + "px";
      tip.style.top = topOffset + "px";
    }

    overlay
      .on("mouseenter", move)
      .on("mousemove", move)
      .on("mouseleave", hide);

    /* What the colours mean, and only for the states the period holds: a
       machine that never left the right state shows one entry, and nothing
       claims the other ever happened. */
    var legend = global.document.createElement("div");
    legend.className = "reflex-chart-legend";
    var order = (good === 0) ? [0, 1] : [1, 0];
    for (index = 0; index < order.length; index++) {
      if (!seen[order[index]]) {
        continue;
      }
      var entry = textNode(legend, "reflex-chart-legend-item");
      textNode(entry, "reflex-chart-legend-swatch reflex-state-swatch "
        + stateClass(order[index], good, severity));
      textNode(entry, "reflex-chart-legend-label").textContent =
        stateText(order[index]);
    }
    /* Named like the two others where it is drawn: without its own entry, the
       stretches nothing is known over read as one of the states. */
    if (unknown && seenUnknown) {
      var none = textNode(legend, "reflex-chart-legend-item");
      textNode(none, "reflex-chart-legend-swatch reflex-state-swatch "
        + UNKNOWN_CLASS);
      textNode(none, "reflex-chart-legend-label").textContent = stateText(null);
    }
    if (legend.childNodes.length) {
      node.appendChild(legend);
    }

    return true;
  }

  global.reflexProbeChart = draw;
  global.reflexProbeStates = drawStates;
})(window);
