/* /usr/share/mmc/modules/reflex/graph/js/machineCharts.js */
/* Evolution charts of the machine sheet. Depends on jQuery, d3 and
   probeChart.js. */

/*
 * The sheet is served without any series: ten probes would mean ten XML-RPC
 * round trips at render time. Each card is filled afterwards by
 * modules/reflex/reflex/ajaxProbeChart.php.
 *
 * Requests are chained rather than fired together: PHP serialises those of one
 * session on the session lock anyway. Only the cards on screen are asked for.
 */

(function () {
  "use strict";

  var CATALOG_ID = "reflex-chart-catalog";
  var GRID_ID = "reflex-charts";
  var SELECT_ID = "reflex-chart-period";
  var TOGGLE_ID = "reflex-charts-toggle";
  var EXTRA_CLASS = "reflex-chart-extra";
  var HIDDEN_CLASS = "reflex-hidden";

  var catalog = {};
  var grid = null;
  /* Identifies the current period run: an answer from a previous period must
     not be drawn over the cards of the new one. */
  var run = 1;
  /* Run a card was asked for, by card: what has already been fetched for the
     period on screen is not fetched again when the cards are unfolded. */
  var asked = {};
  /* Last payload drawn per card. The renderer takes the width of the card at
     draw time, so a window resize has to redraw rather than refetch. */
  var drawn = {};
  var resizeTimer = null;

  function text(key) {
    return (catalog && typeof catalog[key] === "string") ? catalog[key] : "";
  }

  /* What a card is filed under. Probes are told apart by their identifier;
     the presence strip carries none, since it rests on no probe. */
  function cardKey(card) {
    return (card.getAttribute("data-kind") === "presence")
      ? "presence" : card.getAttribute("data-probe-id");
  }

  function note(card, message, isError) {
    var node = card.querySelector(".reflex-chart-note");
    if (!node) {
      return;
    }
    node.textContent = message;
    node.className = "reflex-chart-note" + (isError ? " reflex-chart-error" : "");
  }

  function plotOf(card) {
    return card.querySelector(".reflex-chart-plot");
  }

  function cards() {
    return grid ? grid.querySelectorAll(".reflex-chart-card") : [];
  }

  function folded(card) {
    return card.className.split(/\s+/).indexOf(HIDDEN_CLASS) !== -1;
  }

  /* Nearest ancestor carrying a class, the node itself included. */
  function closest(node, name) {
    while (node && typeof node.className === "string") {
      if ((" " + node.className + " ").indexOf(" " + name + " ") !== -1) {
        return node;
      }
      node = node.parentNode;
    }
    return null;
  }

  /* Takes a card off the page for good.
     Used where the answer says nothing is known rather than that nothing
     happened: an empty frame would be read as a fact, and it is the absence
     of the fact that is being reported. Left without a card, the grid keeps
     neither its period selector nor its unfold button, which would then
     apply to nothing. */
  function drop(card) {
    var id = cardKey(card);
    delete drawn[id];
    delete asked[id];
    if (card.parentNode) {
      card.parentNode.removeChild(card);
    }
    var button = document.getElementById(TOGGLE_ID);
    /* The button counts the cards it unfolds: with none left it would unfold
       nothing, and its count would name cards that are no longer there. */
    if (button && button.parentNode
        && !grid.querySelectorAll("." + EXTRA_CLASS).length) {
      button.parentNode.removeChild(button);
    }
    if (!cards().length) {
      var select = document.getElementById(SELECT_ID);
      var toolbar = select ? closest(select, "reflex-toolbar") : null;
      if (toolbar) {
        toolbar.style.display = "none";
      }
      grid.style.display = "none";
    }
  }

  /* Empties a card without touching what it is worth for the current run:
     used on the folded cards when the period changes, so an unfold never
     shows the curve of the period before. */
  function clear(card) {
    var plot = plotOf(card);
    if (plot) {
      plot.innerHTML = "";
    }
    delete drawn[cardKey(card)];
    note(card, "", false);
  }

  /* ------------------------------------------------------------------ *
   * One card
   * ------------------------------------------------------------------ */
  function draw(card, payload) {
    var plot = plotOf(card);
    if (!plot) {
      return;
    }
    /* Nothing of the payload is written as markup: the previous svg is
       dropped, the rest goes through textContent. */
    plot.innerHTML = "";
    delete drawn[cardKey(card)];

    // The cadence of the placement is written on the card by the sheet, which
    // already holds it: asking the server for it again would fetch the whole
    // machine detail to read one number.
    if (payload && payload.ok === true) {
        payload.interval_seconds = Number(card.getAttribute("data-interval")) || 0;
    }

    if (!payload || payload.ok !== true) {
      note(card, (payload && payload.message) ? payload.message : text("failed"), true);
      return;
    }

    /* The presence of the agent is stated by the server, not measured on the
       machine. Where the server could not read it, the card goes: a band left
       uncoloured over the whole period would be read as an agent that was
       never there, which is precisely what is not known. */
    if (payload.kind === "presence") {
      if (payload.unavailable) {
        drop(card);
        return;
      }
      if (!(payload.spans || []).length) {
        note(card, text("nopresence"));
        return;
      }
      if (!render(plot, payload)) {
        note(card, text("failed"), true);
        return;
      }
      drawn[cardKey(card)] = payload;
      note(card, payload.truncated ? text("trimmed") : "", false);
      return;
    }

    /* One entry per curve: a probe reporting a value per mount point answers
       with one series per volume, one reporting a single value with one
       unnamed series. */
    var series = payload.series || [];
    var total = 0;
    var longest = 0;
    for (var i = 0; i < series.length; i++) {
      var length = (series[i].points || []).length;
      total += length;
      longest = Math.max(longest, length);
    }
    /* A period without a single measure is still a period: the frame is drawn
       on its axis, empty, and the line under it says why it is empty. A card
       taken off the page would leave the reader with nothing to compare the
       other cards against. */
    if (total === 0) {
      if (render(plot, payload)) {
        drawn[cardKey(card)] = payload;
      }
      note(card, text("empty"));
      return;
    }
    /* Two measures make a curve. A window holding one, on every volume it
       holds, has nothing to draw whatever the number of volumes.

       A state timeline is not held to that: one measure already says which
       state was seen, and when. */
    if (longest < 2 && payload.kind !== "state") {
      /* A lone measure draws no curve, and the card keeps the frame of the
         period rather than the void: the axis is there to read the other
         cards against. */
      if (render(plot, payload)) {
        drawn[cardKey(card)] = payload;
      }
      note(card, text("single"));
      return;
    }

    if (!render(plot, payload)) {
      note(card, text("failed"), true);
      return;
    }
    drawn[cardKey(card)] = payload;

    /* A complete chart says nothing worth a line under it: only a window the
       data layer could not serve whole is written. A reduced window is not
       one of those, it covers the period from end to end with fewer points,
       so nothing is said about it. */
    note(card, (payload.truncated && !payload.aggregated) ? text("truncated") : "",
         false);
  }

  /* What the probe reports decides what is drawn: a number makes a curve, a
     state makes a band. The answer says which, so the page never has to
     guess it from the label of the probe. */
  function render(plot, payload) {
    if (payload.kind === "presence") {
      /* Same band as a boolean probe, fed with stretches instead of
         measures. Connected is the state expected of an agent, and the
         severity is fixed here rather than read off a condition: no probe
         backs this strip, and a machine switched off for the night is worth
         saying without being worth an alarm. */
      return reflexProbeStates(plot, {
        "spans": payload.spans || [],
        "from": payload.from,
        "to": payload.to,
        "good": 1,
        "severity": "medium",
        /* A stretch outside the spans is a stretch the server holds nothing
           about, never a machine that stayed off: it is drawn and named. */
        "unknown": true,
        "labels": {
          "yes": text("connected"),
          "no": text("disconnected"),
          "none": text("unknown"),
          "span": text("span")
        }
      });
    }
    if (payload.kind === "state") {
      return reflexProbeStates(plot, {
        "series": payload.series || [],
        /* Bounds of the period asked for: the band covers it whole, and the
           stretch before the first measure stays uncoloured. */
        "from": payload.from,
        "to": payload.to,
        /* Cadence of the placement: what separates two measures when all is
           well, which is what tells a normal wait from a silence. The band
           never runs past its last measure for all that. */
        "interval": payload.interval_seconds || 0,
        /* On a reduced window a point covers an interval of that width, so
           two points sent are that far apart and no closer cadence may be
           read as a silence between them. */
        "bucket": payload.bucket_seconds || 0,
        /* The state that raises no alert, null when nothing on the probe
           says which of the two that is. */
        "good": (payload.good === 0 || payload.good === 1) ? payload.good : null,
        "severity": payload.severity || "",
        "labels": {
          "yes": text("true"),
          "no": text("false"),
          "none": text("nomeasure"),
          "span": text("span")
        }
      });
    }
    return reflexProbeChart(plot, {
      "series": payload.series || [],
      /* Bounds of the period asked for, the same two the band is drawn on:
         every card of one period then carries the same date axis, and a curve
         that only starts on the fourth day starts there instead of being
         stretched over the frame. */
      "from": payload.from,
      "to": payload.to,
      "unit": payload.unit || "",
      "threshold": payload.threshold || null,
      "decimal": text("decimal"),
      "labels": { "threshold": text("threshold") }
    });
  }

  /* The cards are laid out on an auto-fit grid: their width changes with the
     window, and the curve is drawn for one width. Redrawn from the series
     already held, so resizing costs no request. */
  function redraw() {
    var list = cards();
    for (var i = 0; i < list.length; i++) {
      var payload = drawn[cardKey(list[i])];
      var plot = plotOf(list[i]);
      /* A folded card reports no width: drawing in it would freeze a curve
         to the minimum width for when it is unfolded. */
      if (payload && plot && !folded(list[i])) {
        plot.innerHTML = "";
        render(plot, payload);
      }
    }
  }

  function request(card, period, current, done) {
    var kind = card.getAttribute("data-kind") || "";
    note(card, text("loading"));

    var query = {
      "machines_id": grid.getAttribute("data-machines-id"),
      "period": period,
      /* What this card holds: empty for the measures of a probe, presence
         for the band the server states, which names no probe. */
      "kind": kind
    };
    if (kind !== "presence") {
      query.probe_id = card.getAttribute("data-probe-id");
    }

    jQuery.ajax({
      url: grid.getAttribute("data-url"),
      data: query,
      dataType: "json",
      cache: false
    }).done(function (payload) {
      if (current === run) {
        draw(card, payload);
      }
    }).fail(function () {
      if (current === run) {
        note(card, text("failed"), true);
      }
    }).always(function () {
      if (current === run) {
        done();
      }
    });
  }

  function period() {
    var select = document.getElementById(SELECT_ID);
    return (select && select.value) ? select.value : "7";
  }

  /* Fetches what is on screen and still missing for the current period. Called
     on load, on a period change and on an unfold: the folded cards are left
     out, so their measures are never asked for before they are shown. */
  function load() {
    var all = cards();
    var list = [];
    var i;
    for (i = 0; i < all.length; i++) {
      var id = cardKey(all[i]);
      if (folded(all[i]) || asked[id] === run) {
        continue;
      }
      asked[id] = run;
      list.push(all[i]);
    }
    if (!list.length) {
      return;
    }

    var current = run;
    var index = 0;
    var window_ = period();

    function next() {
      if (current !== run || index >= list.length) {
        return;
      }
      var card = list[index];
      index += 1;
      request(card, window_, current, next);
    }

    next();
  }

  /* The period applies to every card, the folded ones included: they are
     emptied and marked to fetch, and the fetch happens when they are shown. */
  function reload() {
    run += 1;
    asked = {};
    var list = cards();
    for (var i = 0; i < list.length; i++) {
      if (folded(list[i])) {
        clear(list[i]);
      }
    }
    load();
  }

  /* The chosen period travels in the address: a refresh reopens on it, and a
     sheet sent to somebody shows the window its sender was reading. Written
     without navigating, so the cards already fetched are not thrown away. */
  function remember(period) {
    if (!period || !window.history || !window.history.replaceState) {
      return;
    }
    var parts = window.location.search.replace(/^\?/, "").split("&");
    var kept = [];
    for (var i = 0; i < parts.length; i++) {
      if (parts[i] !== "" && parts[i].indexOf("period=") !== 0) {
        kept.push(parts[i]);
      }
    }
    kept.push("period=" + encodeURIComponent(period));
    window.history.replaceState(null, "",
      window.location.pathname + "?" + kept.join("&") + window.location.hash);
  }

  /* ------------------------------------------------------------------ *
   * Folded cards
   * ------------------------------------------------------------------ */
  function unfolded(card, show) {
    var parts = card.className.split(/\s+/);
    var kept = [];
    for (var i = 0; i < parts.length; i++) {
      if (parts[i] !== "" && parts[i] !== HIDDEN_CLASS) {
        kept.push(parts[i]);
      }
    }
    if (!show) {
      kept.push(HIDDEN_CLASS);
    }
    card.className = kept.join(" ");
  }

  function toggle() {
    var button = document.getElementById(TOGGLE_ID);
    if (!button || !grid) {
      return;
    }
    var show = button.getAttribute("aria-expanded") !== "true";
    var list = grid.querySelectorAll("." + EXTRA_CLASS);
    for (var i = 0; i < list.length; i++) {
      unfolded(list[i], show);
    }
    button.setAttribute("aria-expanded", show ? "true" : "false");
    /* An unreadable catalog would blank the button: the label it was served
       with is kept rather than emptied. */
    var label = show ? text("collapse") : text("expand");
    if (label !== "") {
      button.textContent = label;
    }

    if (show) {
      /* Cards already held from a previous unfold are only redrawn, at the
         width they now report; the others are fetched. */
      redraw();
      load();
    }
  }

  /* ------------------------------------------------------------------ *
   * Entry point
   * ------------------------------------------------------------------ */
  function start() {
    grid = document.getElementById(GRID_ID);
    if (!grid) {
      return;
    }

    var node = document.getElementById(CATALOG_ID);
    if (node) {
      try {
        catalog = JSON.parse(node.textContent || node.innerText || "{}");
      } catch (e) {
        catalog = {};
      }
    }

    /* d3 is a symlink posted by the base package. Missing it, saying so beats
       leaving empty frames on the page. */
    if (typeof reflexProbeChart !== "function"
        || typeof reflexProbeStates !== "function"
        || typeof window.d3 === "undefined") {
      var list = cards();
      for (var i = 0; i < list.length; i++) {
        /* Nothing left to fold: the button would only unfold error lines. */
        unfolded(list[i], true);
        note(list[i], text("nolibrary"), true);
      }
      var dead = document.getElementById(TOGGLE_ID);
      if (dead && dead.parentNode) {
        dead.parentNode.removeChild(dead);
      }
      return;
    }

    var select = document.getElementById(SELECT_ID);
    if (select) {
      select.addEventListener("change", function () {
        remember(select.value);
        reload();
      });
    }

    var button = document.getElementById(TOGGLE_ID);
    if (button) {
      button.addEventListener("click", toggle);
    }

    window.addEventListener("resize", function () {
      if (resizeTimer) {
        window.clearTimeout(resizeTimer);
      }
      resizeTimer = window.setTimeout(redraw, 200);
    });

    load();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }
})();
