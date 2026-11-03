/* /usr/share/mmc/modules/reflex/graph/js/reflex.js */
/* Fields driven by a select, for the reflex forms. No dependency. */

/*
 * Progressive enhancement only: every widget is rendered visible by the PHP
 * side and this script hides the ones that do not apply. A page where it does
 * not run stays complete and submittable, and the server revalidates.
 */

(function () {
  "use strict";

  var CATALOG_ID = "reflex-form-catalog";

  function readCatalog() {
    var node = document.getElementById(CATALOG_ID);
    if (!node) {
      return null;
    }
    try {
      return JSON.parse(node.textContent || node.innerText || "{}");
    } catch (e) {
      return null;
    }
  }

  var catalog = null;

  function operatorsFor(valueType) {
    if (catalog && catalog.operators && catalog.operators[valueType]) {
      return catalog.operators[valueType];
    }
    return null;
  }

  function isRangeOperator(operator) {
    var list = (catalog && catalog.rangeOperators) || ["between", "outside"];
    return list.indexOf(operator) !== -1;
  }

  function isThresholdlessOperator(operator) {
    var list = (catalog && catalog.thresholdlessOperators) || ["changed"];
    return list.indexOf(operator) !== -1;
  }

  function part(row, role) {
    return row.querySelector('[data-reflex-field="' + role + '"]');
  }

  function show(node, visible) {
    if (node) {
      node.classList.toggle("reflex-hidden", !visible);
    }
  }

  /* ------------------------------------------------------------------ *
   * Operator list of a row, narrowed to the value type
   * ------------------------------------------------------------------ */
  function applyOperators(row, valueType) {
    var select = part(row, "operator");
    if (!select) {
      return;
    }
    var allowed = operatorsFor(valueType);
    if (!allowed) {
      return;
    }

    var current = select.value;
    var stillAllowed = false;
    var i;

    for (i = 0; i < select.options.length; i++) {
      var option = select.options[i];
      if (option.value === "") {
        continue;
      }
      var ok = allowed.indexOf(option.value) !== -1;
      option.hidden = !ok;
      option.disabled = !ok;
      if (ok && option.value === current) {
        stillAllowed = true;
      }
    }

    /* An operator that the new value type does not accept is dropped rather
     * than silently kept: it would be refused by the server anyway. */
    if (current !== "" && !stillAllowed) {
      select.value = "";
    }
  }

  /* ------------------------------------------------------------------ *
   * Threshold widgets of a row
   * ------------------------------------------------------------------ */
  function applyThresholds(row, valueType, unit) {
    var operator = "";
    var operatorSelect = part(row, "operator");
    if (operatorSelect) {
      operator = operatorSelect.value;
    }

    var numeric = part(row, "threshold_numeric");
    var upper = part(row, "threshold_value2");
    var boolean_ = part(row, "threshold_boolean");
    var text = part(row, "threshold_text");

    var needsThreshold = operator !== "" && !isThresholdlessOperator(operator);

    show(numeric, needsThreshold && valueType === "numeric");
    show(upper, needsThreshold && valueType === "numeric" && isRangeOperator(operator));
    show(boolean_, needsThreshold && valueType === "boolean");
    show(text, needsThreshold && valueType === "text");

    var unitNode = row.querySelector('[data-reflex-field="unit"]');
    if (unitNode) {
      unitNode.textContent = unit || "";
    }
  }

  function refreshRow(row, valueType, unit) {
    applyOperators(row, valueType);
    applyThresholds(row, valueType, unit);
  }

  function refreshGroup(group) {
    if (!group) {
      return;
    }
    var valueType = group.getAttribute("data-reflex-value-type") || "numeric";
    var unit = group.getAttribute("data-reflex-unit") || "";
    var rows = group.querySelectorAll("[data-reflex-condition-row]");
    var i;
    for (i = 0; i < rows.length; i++) {
      refreshRow(rows[i], valueType, unit);
    }
  }

  /* ------------------------------------------------------------------ *
   * Repeatable rows
   * ------------------------------------------------------------------ */
  function resetRow(row) {
    var inputs = row.querySelectorAll("input");
    var selects = row.querySelectorAll("select");
    /* The mark of a field the server refused is an inline style posed on one
     * box of one row. A row cloned from that one would present itself as
     * refused before anything has been typed in it. */
    var styled = row.querySelectorAll("[style]");
    var i;

    if (row.hasAttribute("style")) {
      row.removeAttribute("style");
    }
    for (i = 0; i < styled.length; i++) {
      styled[i].removeAttribute("style");
    }

    for (i = 0; i < inputs.length; i++) {
      if (inputs[i].type === "button" || inputs[i].type === "submit") {
        continue;
      }
      if (inputs[i].type === "checkbox") {
        /* A condition being added is meant to alert; blanking the value of a
         * checkbox would make it submit an empty string instead. */
        inputs[i].checked = true;
        continue;
      }
      inputs[i].value = inputs[i].type === "number" ? "0" : "";
    }
    for (i = 0; i < selects.length; i++) {
      selects[i].selectedIndex = 0;
    }
  }

  /* An unchecked checkbox submits nothing, so it cannot use the implicit
   * name="x[]" of the other widgets: its index is written out and has to be
   * renumbered whenever a row appears or leaves. */
  function reindexGroup(group) {
    var rows = group.querySelectorAll("[data-reflex-condition-row]");
    var i, j, fields;
    for (i = 0; i < rows.length; i++) {
      fields = rows[i].querySelectorAll("[data-reflex-indexed]");
      for (j = 0; j < fields.length; j++) {
        fields[j].name = fields[j].getAttribute("data-reflex-indexed") + "[" + i + "]";
      }
    }
  }

  /* Blank row rendered by the server, the very one a form without any
   * condition starts with. */
  function templateOf(group) {
    if (!group.id) {
      return null;
    }
    var template = document.querySelector(
      'template[data-reflex-row-template="#' + group.id + '"]');
    if (!template || !template.content) {
      return null;
    }
    return template.content.querySelector("[data-reflex-condition-row]");
  }

  function addRow(group) {
    var copy;
    var blank = templateOf(group);
    if (blank) {
      copy = document.importNode(blank, true);
    } else {
      var rows = group.querySelectorAll("[data-reflex-condition-row]");
      if (!rows.length) {
        return;
      }
      copy = rows[rows.length - 1].cloneNode(true);
      resetRow(copy);
    }
    group.appendChild(copy);
    reindexGroup(group);
    refreshGroup(group);
  }

  function removeRow(row) {
    var group = row.closest("[data-reflex-conditions]");
    if (!group) {
      return;
    }
    var rows = group.querySelectorAll("[data-reflex-condition-row]");
    /* A probe may carry no condition at all, so the last row goes like the
     * others as long as a blank one can be added back. */
    if (rows.length <= 1 && !templateOf(group)) {
      resetRow(row);
    } else {
      group.removeChild(row);
    }
    reindexGroup(group);
    refreshGroup(group);
  }

  /* ------------------------------------------------------------------ *
   * Help lines following a select
   * ------------------------------------------------------------------ */
  function applyHints(select) {
    if (!select.id) {
      return;
    }
    var hints = document.querySelectorAll(
      '[data-reflex-hint-for="#' + select.id + '"]');
    var i;
    for (i = 0; i < hints.length; i++) {
      show(hints[i], hints[i].getAttribute("data-reflex-hint-value") === select.value);
    }
  }

  /* A field meant for a number is hidden for another comparison, unless it
   * holds something: a value is never hidden. */
  function applyNumericOnly(numeric) {
    var nodes = document.querySelectorAll("[data-reflex-numeric-only]");
    var i, j, filled, inputs;
    for (i = 0; i < nodes.length; i++) {
      filled = false;
      inputs = nodes[i].querySelectorAll("input, textarea, select");
      for (j = 0; j < inputs.length; j++) {
        if (inputs[j].value !== "") {
          filled = true;
        }
      }
      show(nodes[i], numeric || filled);
    }
  }

  /* The "Alert if" line: as many value boxes as the comparison takes. */
  function applyAlert(select) {
    var option = select.options[select.selectedIndex];
    if (!option) {
      return;
    }
    var count = parseInt(option.getAttribute("data-reflex-values") || "1", 10);
    show(document.querySelector("[data-reflex-alert-value]"), count >= 1);
    show(document.querySelector("[data-reflex-alert-value2]"), count >= 2);
    applyNumericOnly(option.getAttribute("data-reflex-numeric") === "1");
  }

  /* A template fills the form; the administrator adapts it afterwards. */
  function applyTemplate(form, data, index) {
    var template = data.templates && data.templates[index];
    if (!template) {
      return;
    }
    var fields = {
      label: template.name,
      command_unix: template.command_unix,
      command_windows: template.command_windows,
      alert_when: template.alert_when,
      alert_value: template.alert_value,
      alert_value2: "",
      category: template.category,
      unit: template.unit
    };
    Object.keys(fields).forEach(function (name) {
      var field = form.elements[name];
      if (field) {
        field.value = fields[name] || "";
      }
    });

    var alertSelect = form.querySelector("[data-reflex-alert]");
    if (alertSelect) {
      applyAlert(alertSelect);
    }
    var defaults = data.defaults || {};
    var options = form.querySelector(".reflex-options");
    if (options && ((template.category || "") !== (defaults.category || "") || template.unit)) {
      options.open = true;
    }
    if (form.elements.label) {
      form.elements.label.focus();
    }
  }

  /* ------------------------------------------------------------------ *
   * Recipients: address list imported from a file read in the browser
   * ------------------------------------------------------------------ */
  var ADDRESS = /[^@\s,;"']+@[^@\s,;"']+\.[^@\s,;"']+/g;
  var ADDRESS_WHOLE = /^[^@\s,;"']+@[^@\s,;"']+\.[^@\s,;"']+$/;

  function format(template, values) {
    var index = 0;
    return template.replace(/%(?:(\d+)\$)?[ds]/g, function (match, position) {
      var value = position ? values[parseInt(position, 10) - 1] : values[index++];
      return String(value);
    });
  }

  /* Addresses found in a text. */
  function scanAddresses(text) {
    var found = [];
    /* CSV quotes, and the brackets of a "Name <address>" form. */
    String(text).replace(/["'<>()]/g, " ").split(/[\s,;]+/).forEach(function (item) {
      var matches = item.match(ADDRESS);
      if (matches) {
        found = found.concat(matches);
      }
    });
    return found;
  }

  function initRecipients(block) {
    var field = document.getElementById(block.getAttribute("data-reflex-recipients"));
    var pick = block.querySelector("[data-reflex-recipients-pick]");
    var file = block.querySelector("[data-reflex-recipients-file]");
    var report = block.querySelector("[data-reflex-recipients-report]");
    if (!field || !pick || !file || !report || typeof FileReader === "undefined") {
      return;
    }

    function say(lines, warning) {
      report.textContent = lines.join(" ");
      report.classList.toggle("reflex-recipients-warning", !!warning);
    }

    pick.addEventListener("click", function () {
      file.click();
    });

    file.addEventListener("change", function () {
      if (!file.files || !file.files.length) {
        return;
      }
      say([], false);
      var reader = new FileReader();
      reader.onload = function () {
        var found = scanAddresses(reader.result);
        var known = {};
        scanAddresses(field.value).forEach(function (address) {
          known[address.toLowerCase()] = true;
        });
        var added = [];
        found.forEach(function (address) {
          var key = address.toLowerCase();
          if (!known[key]) {
            known[key] = true;
            added.push(address);
          }
        });
        if (added.length) {
          var current = field.value.replace(/\s+$/, "");
          field.value = (current === "" ? "" : current + "\n") + added.join("\n");
        }
        if (!found.length) {
          say([block.getAttribute("data-msg-none")], true);
        }
        file.value = "";
      };
      reader.readAsText(file.files[0]);
    });

    /* Said, never blocking: the server is the one that refuses. */
    field.addEventListener("blur", function () {
      var invalid = String(field.value).split(/[\s,;]+/).filter(function (item) {
        return item !== "" && !ADDRESS_WHOLE.test(item);
      });
      if (invalid.length) {
        var wording = (invalid.length === 1 && block.getAttribute("data-msg-invalid-one"))
          || block.getAttribute("data-msg-invalid");
        say([format(wording, [invalid.join(", ")])], true);
      } else if (report.classList.contains("reflex-recipients-warning")) {
        say([], false);
      }
    });
  }

  /* ------------------------------------------------------------------ *
   * Import of a script into a command box
   *
   * Typing comfort only: the file is read here, put in the box, and never
   * sent. The box is what the form submits, exactly as if it had been
   * pasted. A browser without FileReader keeps the box and loses only the
   * button.
   * ------------------------------------------------------------------ */
  function initCommandImport(block) {
    var field = document.getElementById(block.getAttribute("data-reflex-command"));
    var pick = block.querySelector("[data-reflex-command-pick]");
    var file = block.querySelector("[data-reflex-command-file]");
    var report = block.querySelector("[data-reflex-command-report]");
    if (!field || !pick || !file || !report) {
      return;
    }
    if (typeof FileReader === "undefined") {
      block.classList.add("reflex-hidden");
      return;
    }

    var max = parseInt(block.getAttribute("data-max"), 10);
    if (!(max > 0)) {
      max = 0;
    }

    function say(text, warning) {
      report.textContent = text || "";
      report.classList.toggle("reflex-command-warning", !!warning);
    }

    /* Read as the form will submit it: the CRLF a file carries is what PHP
       undoes on save, and a BOM would end up at the start of the command. */
    function normalise(text) {
      return String(text).replace(/^\uFEFF/, "").replace(/\r\n/g, "\n");
    }

    function done() {
      /* Cleared so picking the same file again is heard. */
      file.value = "";
    }

    pick.addEventListener("click", function () {
      file.click();
    });

    /* Cancelling the dialog raises no change: the box keeps what it holds. */
    file.addEventListener("change", function () {
      if (!file.files || !file.files.length) {
        return;
      }
      var chosen = file.files[0];
      say("", false);

      var reader = new FileReader();
      reader.onerror = function () {
        say(block.getAttribute("data-msg-unreadable"), true);
        done();
      };
      reader.onload = function () {
        var text = normalise(reader.result);
        if (text.replace(/\s+/g, "") === "") {
          say(block.getAttribute("data-msg-empty"), true);
          done();
          return;
        }
        if (max && text.length > max) {
          say(format(block.getAttribute("data-msg-too-long"),
                     [text.length, max]), true);
          done();
          return;
        }
        /* Replacement, never addition: what was written is overwritten only
           once its author has said so. */
        if (String(field.value).trim() !== ""
            && !window.confirm(block.getAttribute("data-msg-replace"))) {
          done();
          return;
        }
        field.value = text;
        say(format(block.getAttribute("data-msg-loaded"), [chosen.name]), false);
        done();
      };
      /* Named, so a script with accents does not arrive damaged. */
      reader.readAsText(chosen, "UTF-8");
    });
  }

  /* ------------------------------------------------------------------ *
   * Targets
   * ------------------------------------------------------------------ */
  function targetOf(node) {
    var selector = node.getAttribute("data-reflex-target");
    return selector ? document.querySelector(selector) : null;
  }

  /* The unit belongs to the probe, the thresholds show it: what is typed in
   * the one is read in the others without waiting for a save. */
  function spreadUnit(field) {
    var groups = document.querySelectorAll("[data-reflex-conditions]");
    var i;
    for (i = 0; i < groups.length; i++) {
      groups[i].setAttribute("data-reflex-unit", field.value || "");
      refreshGroup(groups[i]);
    }
  }

  /* ------------------------------------------------------------------ *
   * Wiring
   * ------------------------------------------------------------------ */
  function init() {
    catalog = readCatalog();

    var i;
    var unitFields = document.querySelectorAll("[data-reflex-unit-field]");
    for (i = 0; i < unitFields.length; i++) {
      (function (field) {
        field.addEventListener("input", function () {
          spreadUnit(field);
        });
      })(unitFields[i]);
    }

    var groups = document.querySelectorAll("[data-reflex-conditions]");
    for (i = 0; i < groups.length; i++) {
      (function (group) {
        group.addEventListener("change", function (event) {
          if (event.target && event.target.matches('[data-reflex-field="operator"]')) {
            var row = event.target.closest("[data-reflex-condition-row]");
            if (row) {
              applyThresholds(
                row,
                group.getAttribute("data-reflex-value-type") || "numeric",
                group.getAttribute("data-reflex-unit") || ""
              );
            }
          }
        });
        group.addEventListener("click", function (event) {
          if (event.target && event.target.hasAttribute("data-reflex-remove-row")) {
            event.preventDefault();
            var row = event.target.closest("[data-reflex-condition-row]");
            if (row) {
              removeRow(row);
            }
          }
        });
        refreshGroup(group);
      })(groups[i]);
    }

    var hinted = {};
    var hintNodes = document.querySelectorAll("[data-reflex-hint-for]");
    for (i = 0; i < hintNodes.length; i++) {
      hinted[hintNodes[i].getAttribute("data-reflex-hint-for")] = true;
    }
    Object.keys(hinted).forEach(function (selector) {
      var select = document.querySelector(selector);
      if (select) {
        select.addEventListener("change", function () {
          applyHints(select);
        });
        applyHints(select);
      }
    });

    var alertSelect = document.querySelector("[data-reflex-alert]");
    if (alertSelect) {
      alertSelect.addEventListener("change", function () {
        applyAlert(alertSelect);
      });
      applyAlert(alertSelect);
    }

    var templateNode = document.getElementById("reflex-probe-templates");
    var probeForm = document.querySelector(".reflex-probe-form");
    if (templateNode && probeForm) {
      var templateData = null;
      try {
        templateData = JSON.parse(templateNode.textContent || "{}");
      } catch (e) {
        templateData = null;
      }
      var templateButtons = document.querySelectorAll("[data-reflex-template]");
      for (i = 0; templateData && i < templateButtons.length; i++) {
        (function (button) {
          button.addEventListener("click", function () {
            applyTemplate(probeForm, templateData,
              parseInt(button.getAttribute("data-reflex-template"), 10));
          });
        })(templateButtons[i]);
      }
    }

    var recipientBlocks = document.querySelectorAll("[data-reflex-recipients]");
    for (i = 0; i < recipientBlocks.length; i++) {
      initRecipients(recipientBlocks[i]);
    }

    var commandBlocks = document.querySelectorAll("[data-reflex-command]");
    for (i = 0; i < commandBlocks.length; i++) {
      initCommandImport(commandBlocks[i]);
    }

    var adders = document.querySelectorAll("[data-reflex-add-row]");
    for (i = 0; i < adders.length; i++) {
      (function (button) {
        button.addEventListener("click", function (event) {
          event.preventDefault();
          var group = targetOf(button);
          if (group) {
            addRow(group);
          }
        });
      })(adders[i]);
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
