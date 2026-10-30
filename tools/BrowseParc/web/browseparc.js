/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
 *
 * Client side logic of the "Browse my fleet" page.
 * Every exchange with the server is JSON, the MMC page dispatcher is used as
 * the endpoint (see BROWSE_PARC.url).
 */
(function ($) {
    "use strict";

    var state = {
        job: null,
        jobAction: null,
        poll: null,
        logOffset: 0,
        machines: [],
        ous: [],
        selected: {},
        groups: [],
        onComplete: null
    };

    // The server runs php-fpm with pm.max_children = 5 and the mmc-agent with
    // a 20 thread pool: polling too fast saturates them and PHP kills the
    // request after max_execution_time (30s), which shows up as an empty
    // answer. Keep one single poll in flight, slowly, and only when visible.
    var POLL_INTERVAL = 2500;
    var POLL_ERRORS_MAX = 3;

    function t(key) {
        return (window.BROWSE_PARC && BROWSE_PARC.i18n && BROWSE_PARC.i18n[key]) || key;
    }

    function escapeHtml(value) {
        return String(value === null || value === undefined ? "" : value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#39;");
    }

    // Read-only commands travel as GET so a page load never needs the CSRF
    // token. They stay below the php-fpm 30s limit (max_execution_time) so a
    // slow answer is reported instead of leaving the interface waiting.
    var READ_COMMANDS = ["status", "jobs", "groups", "group_get", "agents", "prereq", "machine_log"];
    var CALL_TIMEOUT = 25000;

    function callFailed(xhr, textStatus) {
        if (textStatus === "timeout") {
            return { ok: false, error: t("timeout") };
        }
        // A redirect towards the login page is followed by jQuery: the answer is
        // HTML and the final status is 200, which only shows as a parse error.
        if (textStatus === "parsererror" ||
            (xhr && xhr.status === 200 && !xhr.responseJSON)) {
            return { ok: false, expired: true, error: t("sessionExpired") };
        }
        if (!xhr || !xhr.status) {
            return { ok: false, error: t("agentUnreachable") };
        }
        return { ok: false, error: "HTTP " + xhr.status };
    }

    function call(method, data, done) {
        var payload = $.extend({}, data || {});
        payload.cmd = method;
        var options = {
            url: BROWSE_PARC.url,
            dataType: "json",
            data: payload,
            timeout: CALL_TIMEOUT
        };
        if (READ_COMMANDS.indexOf(method) !== -1) {
            options.type = "GET";
        } else {
            options.type = "POST";
            payload.auth_token = BROWSE_PARC.token;
        }
        $.ajax(options)
            .done(function (response) {
                done(response || { ok: false, error: t("emptyAnswer") });
            })
            .fail(function (xhr, textStatus) { done(callFailed(xhr, textStatus)); });
    }

    // In-page dialog, in place of window.prompt / window.confirm: those native
    // browser boxes carry the browser look instead of Medulla's, and a
    // browser can mute them. options: title, message, input (bool), value,
    // inputLabel, input2Label/value2 (optional second field), validate(value)
    // returning an error text, confirmLabel, danger. onConfirm receives the
    // typed text(s) (input dialogs) or true.
    function openDialog(options, onConfirm) {
        $(".bp-dialog-overlay").remove();
        $(document).off("keydown.bpDialog");
        var previous = document.activeElement;
        var overlay = $('<div class="bp-dialog-overlay"></div>');
        var box = $('<div class="bp-dialog" role="dialog" aria-modal="true"></div>');
        var titleId = "bpDialogTitle";
        var body = $('<div class="bp-dialog-body"></div>');
        var input = null;
        var input2 = null;
        var error = $('<div class="bp-dialog-error bp-hidden" role="alert"></div>');

        box.append($('<h4 class="bp-dialog-title"></h4>').attr("id", titleId).text(options.title || ""));
        box.attr("aria-labelledby", titleId);
        if (options.message) {
            body.append($('<p class="bp-dialog-message"></p>').text(options.message));
        }
        if (options.input) {
            var field = $('<label class="bp-dialog-label"></label>').text(options.inputLabel || "");
            input = $('<input type="text" class="bp-dialog-input" maxlength="128" autocomplete="off">')
                .val(options.value || "");
            body.append(field.append(input));
            if (options.input2Label) {
                input2 = $('<input type="text" class="bp-dialog-input" maxlength="500" autocomplete="off">')
                    .val(options.value2 || "");
                body.append($('<label class="bp-dialog-label bp-dialog-label2"></label>')
                    .text(options.input2Label).append(input2));
            }
            body.append(error);
        }

        var cancel = $('<button type="button" class="btnSecondary bp-dialog-cancel"></button>')
            .text(t("dialogCancel"));
        var confirm = $('<button type="button" class="btnPrimary bp-dialog-confirm"></button>')
            .text(options.confirmLabel || t("dialogConfirm"));
        if (options.danger) {
            confirm.addClass("bp-dialog-danger");
        }
        box.append(body).append($('<div class="bp-dialog-actions"></div>').append(cancel).append(confirm));
        overlay.append(box);

        function close() {
            $(document).off("keydown.bpDialog");
            overlay.remove();
            if (previous && previous.focus) {
                previous.focus();
            }
        }
        function accept() {
            var value = true;
            if (input) {
                value = $.trim(input.val());
                var problem = !value ? t("groupNameRequired")
                    : (options.validate ? options.validate(value) : "");
                if (problem) {
                    error.text(problem).removeClass("bp-hidden");
                    input.focus();
                    return;
                }
            }
            close();
            onConfirm(value, input2 ? $.trim(input2.val()) : "");
        }

        cancel.on("click", close);
        confirm.on("click", accept);
        overlay.on("mousedown", function (event) {
            if (event.target === overlay[0]) {
                close();
            }
        });
        $(document).on("keydown.bpDialog", function (event) {
            if (event.key === "Escape") {
                event.preventDefault();
                close();
            } else if (event.key === "Enter" && input && event.target === input[0]) {
                event.preventDefault();
                accept();
            } else if (event.key === "Tab") {
                var items = box.find("input, button");
                var first = items.first()[0];
                var last = items.last()[0];
                if (event.shiftKey && document.activeElement === first) {
                    event.preventDefault();
                    last.focus();
                } else if (!event.shiftKey && document.activeElement === last) {
                    event.preventDefault();
                    first.focus();
                }
            }
        });

        ($("#browseParc").length ? $("#browseParc") : $("body")).append(overlay);
        if (input) {
            input.focus();
            input[0].select();
        } else {
            confirm.focus();
        }
    }

    // Short-lived message pinned to the corner of the screen, so that an
    // answer is seen wherever the user is on this long page (the job log sits
    // at the very top, the buttons far below).
    var TOAST_MAX = 3;

    function toast(message, isError) {
        var root = $("#browseParc").length ? $("#browseParc") : $("body");
        var zone = root.children(".bp-toasts");
        if (!zone.length) {
            zone = $('<div class="bp-toasts"></div>').appendTo(root);
        }
        var item = $('<div class="bp-toast"></div>')
            .addClass(isError ? "bp-toast-error" : "bp-toast-info")
            .attr("role", isError ? "alert" : "status")
            .text(message);
        item.on("click", function () { item.remove(); });
        zone.append(item);
        while (zone.children().length > TOAST_MAX) {
            zone.children().first().remove();
        }
        setTimeout(function () { item.remove(); }, isError ? 12000 : 6000);
    }

    // The page has its own feedback area (#bpJobLog). Medulla defines its own
    // "NotifyWidgetSuccess" helper, but nothing here calls it: skipping the
    // message because it merely exists silently swallowed every success
    // message ("remote session opened", "job followed"...), which made the
    // interface look unresponsive.
    function notify(message, isError) {
        var line = (isError ? "[error] " : "[info] ") + message;
        toast(message, isError);
        // Write where the user is actually looking: the job panel sits at the
        // top of the page and the jobs table at the bottom. A message about a
        // job started from the table used to land in the hidden top panel,
        // which made the buttons look like they did nothing.
        var panel = $("#bpJob");
        if (panel.length && !panel.hasClass("bp-hidden") && $("#bpJobLog").length) {
            appendLog($("#bpJobLog"), line + "\n");
            return;
        }
        var zone = $("#bpJobMessage");
        if (zone.length) {
            zone.removeClass("bp-hidden");
            zone.append($("<div></div>")
                .addClass(isError ? "bp-msg-error" : "bp-msg-info")
                .text(line));
            zone.scrollTop(zone[0].scrollHeight);
        }
    }

    // A long job can produce a lot of output: the pane keeps the tail only,
    // so the page does not grow without limit. Text goes in as a text node,
    // never as HTML.
    var LOG_MAX_CHARS = 200000;

    function appendLog(pre, text) {
        var node = pre && pre[0];
        if (!node || !text) {
            return;
        }
        node.appendChild(document.createTextNode(text));
        if (node.textContent.length > LOG_MAX_CHARS) {
            node.textContent = t("logTruncated") + "\n" +
                node.textContent.slice(-Math.floor(LOG_MAX_CHARS / 2));
        }
        node.scrollTop = node.scrollHeight;
    }

    // ------------------------------------------------------------ selection

    function selectedMachines() {
        var result = [];
        for (var i = 0; i < state.machines.length; i += 1) {
            var machine = state.machines[i];
            if (state.selected[machine.target]) {
                result.push(machine);
            }
        }
        return result;
    }

    function refreshSelectionCounter() {
        var machines = selectedMachines();
        var methods = { SSH: 0, WinRM: 0 };
        for (var i = 0; i < machines.length; i += 1) {
            var method = methodFor(machines[i]);
            if (methods[method] !== undefined) {
                methods[method] += 1;
            }
        }
        var text = machines.length + " " + t("selected");
        var parts = [];
        if (methods.SSH) { parts.push(methods.SSH + " SSH"); }
        if (methods.WinRM) { parts.push(methods.WinRM + " WinRM"); }
        if (parts.length) {
            text += " (" + parts.join(", ") + ")";
        }
        $("#bpSelectionCount").text(text);
    }

    // Ports carrying a remote control service, in the order we prefer them.
    var SERVICE_PORTS = { rdp: [3389], ssh: [22] };
    var SERVICE_LABELS = { rdp: "RDP", ssh: "SSH" };

    function servicePort(machine, service) {
        var want = SERVICE_PORTS[service] || [];
        var ports = machine.ports || [];
        for (var i = 0; i < want.length; i += 1) {
            if (ports.indexOf(want[i]) !== -1) {
                return want[i];
            }
        }
        return want.length ? want[0] : null;
    }

    // Which transport the installation will use for this machine. It mirrors
    // the rule applied by the deployment script (server side), so the interface
    // announces what will really happen.
    var LINUX_OS = /macos|mac os|darwin|os x|debian|ubuntu|linux|centos|rocky|alma|alpine|fedora|raspbian|red ?hat|rhel|suse|bsd/i;

    function methodFor(machine) {
        var osys = machine.os || "";
        var ports = machine.ports || [];
        var winrm = ports.indexOf(5985) !== -1;
        var ssh = ports.indexOf(22) !== -1;
        var smb = ports.indexOf(445) !== -1;
        if (/windows/i.test(osys)) {
            if (ssh && !winrm) {
                return "SSH";
            }
            return (smb && !winrm && !ssh) ? "SMB" : "WinRM";
        }
        if (LINUX_OS.test(osys)) {
            return "SSH";
        }
        if (winrm && !ssh) {
            return "WinRM";
        }
        if (ssh && !winrm) {
            return "SSH";
        }
        if (smb && !winrm && !ssh) {
            return "SMB";
        }
        return "?";
    }

    // Small tags listing every service found on the machine, so a machine
    // without any remote control protocol is not just showing a dash.
    function servicesTags(machine) {
        var services = machine.services || [];
        if (!services.length) {
            return "";
        }
        var html = [];
        for (var i = 0; i < services.length; i += 1) {
            html.push('<span class="bp-tag">' + escapeHtml(services[i]) + "</span>");
        }
        return html.join(" ") + " ";
    }

    function remoteButtons(machine) {
        var services = machine.services || [];
        var html = [];
        for (var service in SERVICE_LABELS) {
            if (!SERVICE_LABELS.hasOwnProperty(service)) {
                continue;
            }
            if (services.indexOf(service) === -1) {
                continue;
            }
            html.push('<button type="button" class="btnSecondary bp-session" data-target="' +
                escapeHtml(machine.target) + '" data-protocol="' + service +
                '" data-port="' + (servicePort(machine, service) || "") + '">' +
                SERVICE_LABELS[service] + "</button>");
        }
        return servicesTags(machine) +
            (html.length ? html.join(" ") : '<span class="bp-tag">-</span>');
    }

    function openSession(target, protocol, port) {
        // The window must be opened synchronously inside the click: opened in
        // the asynchronous answer, the browser takes it for a pop-up and
        // blocks it. It is pointed at the session once the server answers.
        var popup = window.open("", "_blank");
        call("session", {
            target: target,
            protocol: protocol,
            port: port,
            username: $("#bpUsername").val(),
            password: $("#bpPassword").val(),
            // SSH: a private key is what hardened machines expect. Without one
            // the server falls back to the key Medulla uses for its relay.
            sshkey: protocol === "ssh" ? $("#bpSshkey").val() : ""
        }, function (response) {
            if (!response.ok) {
                if (popup) {
                    popup.close();
                }
                notify((response.error || t("sessionError")) + " (" + target + ")", true);
                return;
            }
            if (response.warning) {
                notify(response.warning, true);
            }
            if (!popup || popup.closed) {
                notify(t("popupBlocked") + " (" + target + ")", true);
                return;
            }
            popup.opener = null;
            popup.location = response.url;
            notify(t("sessionOpened") + " : " + protocol.toUpperCase() + " " + target, false);
        });
    }

    // Switching between Active Directory and a network sweep means changing the
    // kind of search: the previous mode's fields are cleared (they belong to the
    // other search and would be sent by mistake) and the job still running -
    // which belongs to the previous mode - is stopped.
    function switchMode(mode) {
        if (mode === "ad") {
            $(".bp-ad").removeClass("bp-hidden");
            $(".bp-network").addClass("bp-hidden");
            $("#bpTarget").val("");
        } else {
            $(".bp-ad").addClass("bp-hidden");
            $(".bp-network").removeClass("bp-hidden");
            $("#bpServer, #bpOu, #bpDomain, #bpFilter").val("");
            state.ous = [];
            $("#bpOuSelection").text(t("allDirectory"));
            $("#bpOuTree").empty().append($("<div></div>")
                .addClass("bp-ou-hint").text(t("listOuHint")));
        }
        stopRunningJob(t("modeChanged"));
    }

    // Stop whatever job is attached to the top panel. The credentials are left
    // alone: both modes use them.
    function stopRunningJob(reason) {
        var job = state.job;
        if (job) {
            call("cancel", { job: job }, function (response) {
                if (response.ok && response.cancelled !== false) {
                    notify(reason || t("cancelRequested"), false);
                }
            });
        }
        stopPolling();
        state.job = null;
        state.jobAction = null;
        state.logOffset = 0;
        state.onComplete = null;
        $("#bpJob").addClass("bp-hidden");
        if (job) {
            refreshJobs();
        }
    }

    // The table must say what really happened: a cancelled job used to read
    // "done", as if the installation had gone through.
    function stateLabel(state) {
        if (state === "running") {
            return t("running");
        }
        if (state === "cancelled") {
            return t("cancelled");
        }
        if (state === "error") {
            return t("error");
        }
        return t("done");
    }

    // --------------------------------------------------- Active Directory tree
    //
    // The agent only sends the branches that really hold machines (an empty
    // organizational unit has no interest here), and gives each node its parent
    // so the hierarchy can be rebuilt. Clicking a node picks that branch; the
    // domain node itself means "the whole directory".
    function ouLine(node, depth) {
        var line = $("<div></div>").addClass("bp-ou-line")
            .css("padding-left", (depth * 14) + "px");
        line.append($("<span></span>").addClass("bp-ou-name")
            .attr("data-dn", node.dn)
            .text(node.name));
        // CN=Computers is a plain container, not an organizational unit: say so,
        // it still works as a search base.
        if (node.kind === "container") {
            line.addClass("bp-ou-is-container");
            line.append($("<span></span>").addClass("bp-ou-kind").text(t("container")));
        }
        line.append($("<span></span>").addClass("bp-ou-count")
            .text(node.total + " " + t("machines")));
        return line;
    }

    function ouBranch(node, children, depth) {
        var box = $("<div></div>").addClass("bp-ou-branch");
        box.append(ouLine(node, depth));
        var kids = children[node.dn] || [];
        for (var i = 0; i < kids.length; i += 1) {
            box.append(ouBranch(kids[i], children, depth + 1));
        }
        return box;
    }

    // Rebuild the hierarchy from the flat list sent by the agent: a node whose
    // parent was filtered out (or the domain itself) starts a branch. Pure
    // computation, kept apart from the rendering so it can be tested.
    function buildOuTree(ous) {
        var byDn = {};
        var children = {};
        var roots = [];
        var i;
        for (i = 0; i < ous.length; i += 1) {
            byDn[ous[i].dn] = ous[i];
        }
        for (i = 0; i < ous.length; i += 1) {
            if (ous[i].parent && byDn[ous[i].parent]) {
                if (!children[ous[i].parent]) {
                    children[ous[i].parent] = [];
                }
                children[ous[i].parent].push(ous[i]);
            } else {
                roots.push(ous[i]);
            }
        }
        return { roots: roots, children: children };
    }

    function renderOuTree(ous) {
        var container = $("#bpOuTree");
        if (!container.length) {
            return;
        }
        var tree = buildOuTree(ous);
        var roots = tree.roots;
        var children = tree.children;
        var i;
        container.empty();
        if (!roots.length) {
            container.append($("<div></div>").addClass("bp-ou-hint")
                .text(t("noOuWithMachines")));
            return;
        }
        for (i = 0; i < roots.length; i += 1) {
            container.append(ouBranch(roots[i], children, 0));
        }
        if (!$("#bpOu").val() || !byDnHas(ous, $("#bpOu").val())) {
            $("#bpOu").val(roots[0].dn);
            setOuSelection(roots[0]);
        }
        markOuSelection();
    }

    function byDnHas(ous, dn) {
        for (var i = 0; i < ous.length; i += 1) {
            if (ous[i].dn === dn) {
                return true;
            }
        }
        return false;
    }

    function setOuSelection(node) {
        $("#bpOuSelection").text(node ? (node.canonical || node.name) : t("allDirectory"));
    }

    function markOuSelection() {
        var selected = $("#bpOu").val();
        $("#bpOuTree .bp-ou-line").removeClass("bp-ou-selected");
        $("#bpOuTree .bp-ou-name").filter(function () {
            return $(this).attr("data-dn") === selected;
        }).closest(".bp-ou-line").addClass("bp-ou-selected");
    }

    function selectOu(dn) {
        var node = null;
        for (var i = 0; i < state.ous.length; i += 1) {
            if (state.ous[i].dn === dn) {
                node = state.ous[i];
            }
        }
        $("#bpOu").val(dn || "");
        setOuSelection(node);
        markOuSelection();
    }

    function renderMachines() {
        var filter = ($("#bpResultFilter").val() || "").toLowerCase();
        var body = $("#bpMachinesBody");
        var visible = 0;
        var html = [];

        for (var i = 0; i < state.machines.length; i += 1) {
            var machine = state.machines[i];
            var haystack = (machine.name + " " + machine.ip + " " + machine.ou + " " + machine.os).toLowerCase();
            if (filter && haystack.indexOf(filter) === -1) {
                continue;
            }
            visible += 1;
            var checked = state.selected[machine.target] ? " checked" : "";
            html.push(
                "<tr>" +
                '<td class="bp-col-check"><input type="checkbox" class="bp-machine-check" data-target="' +
                    escapeHtml(machine.target) + '"' + checked + " /></td>" +
                "<td>" + escapeHtml(machine.name) + "</td>" +
                "<td>" + escapeHtml(machine.ip) + "</td>" +
                "<td>" + escapeHtml(machine.source) + "</td>" +
                "<td>" + escapeHtml(machine.ou) + "</td>" +
                "<td>" + escapeHtml(machine.os) + "</td>" +
                '<td><span class="bp-tag">' + methodFor(machine) + "</span></td>" +
                "<td>" + (machine.installed
                    ? '<span class="bp-tag bp-tag-ok">' + t("installed") + "</span>"
                    : '<span class="bp-tag">-</span>') + "</td>" +
                '<td class="bp-col-actions">' + remoteButtons(machine) + "</td>" +
                "</tr>"
            );
        }

        if (visible === 0) {
            body.html('<tr class="bp-empty"><td colspan="9">' +
                (state.machines.length ? t("noFilterResult") : t("noMachine")) + "</td></tr>");
        } else {
            body.html(html.join(""));
        }
        refreshSelectionCounter();
    }

    // ---------------------------------------------------------------- jobs

    function progressBar(status) {
        var total = (status.progress && status.progress.total) || 0;
        var done = (status.progress && status.progress.done) || 0;
        if (total > 0) {
            return Math.round((done * 100) / total) + "%";
        }
        return status.status === "running" ? "5%" : "0%";
    }

    function renderJob(status) {
        $("#bpJob").removeClass("bp-hidden");
        $("#bpProgressBar").css("width", progressBar(status));
        // Name the job: several jobs of the same type can be listed, and
        // "network 41/41 - done" alone does not say which one is displayed.
        var label = status.job ? status.job + " - " : "";
        label += status.mode ? status.mode : "";
        if (status.progress && status.progress.total) {
            label += " " + status.progress.done + "/" + status.progress.total;
        }
        label += " - " + (status.status === "running" ? t("running") :
            (status.status === "error" ? t("error") :
                (status.status === "cancelled" ? t("cancelled") : t("done"))));
        $("#bpJobLabel").text(label);

        if (status.log && status.log.length) {
            appendLog($("#bpJobLog"), status.log.join("\n") + "\n");
        }
        if (status.log_truncated) {
            appendLog($("#bpJobLog"), t("logTruncated") + "\n");
        }
        if (typeof status.log_offset === "number") {
            state.logOffset = status.log_offset;
        }
    }

    // Report of an installation: the machines that failed, with the step where
    // it went wrong and why. The full log of the machine is one click away.
    function renderInstallResults(status) {
        var box = $("#bpJobResults");
        var results = (status.summary && status.summary.results) || [];
        box.empty().addClass("bp-hidden");
        if (status.mode !== "install" || !results.length) {
            return;
        }
        var failed = [];
        for (var i = 0; i < results.length; i += 1) {
            if (results[i].status !== "ok") {
                failed.push(results[i]);
            }
        }
        var ok = results.length - failed.length;
        box.append($("<div>").addClass("bp-results-head")
            .text(t("installReport").replace("%d", ok).replace("%d", failed.length)));
        if (failed.length) {
            var table = $('<table class="bp-table bp-fail-table"></table>');
            table.append("<thead><tr><th>" + escapeHtml(t("failColMachine")) + "</th><th>" +
                escapeHtml(t("failColStep")) + "</th><th>" + escapeHtml(t("failColCause")) +
                "</th><th>" + escapeHtml(t("failColDetail")) + "</th><th></th></tr></thead>");
            var body = $("<tbody>");
            for (var j = 0; j < failed.length; j += 1) {
                body.append(failRow(status.job, failed[j]));
            }
            table.append(body);
            box.append(table);
        }
        box.removeClass("bp-hidden");
    }

    function failRow(job, item) {
        var stepKey = "failStep_" + (item.step || "unknown");
        var codeKey = "failCode_" + (item.code || "unknown");
        var step = t(stepKey) === stepKey ? t("failStep_unknown") : t(stepKey);
        var cause = t(codeKey) === codeKey ? t("failCode_unknown") : t(codeKey);
        var row = $("<tr>").addClass("bp-fail-row");
        row.append($("<td>").text(item.name || item.target));
        row.append($("<td>").text(step));
        row.append($("<td>").text(cause));
        row.append($("<td>").addClass("bp-fail-detail").text(item.reason || ""));
        var button = $('<button type="button" class="btnSecondary bp-machine-log"></button>')
            .text(t("showMachineLog"));
        button.on("click", function () {
            toggleMachineLog(job, item.target, button);
        });
        row.append($("<td>").append(button));
        if (!item.manual) {
            return row;
        }
        var manual = $('<tr class="bp-manual-row"><td colspan="5"></td></tr>');
        manual.find("td").append($("<span>").addClass("bp-manual-label").text(t("failManual") + " "))
            .append($("<code>").addClass("bp-manual-command").text(item.manual));
        return row.add(manual);
    }

    function toggleMachineLog(job, target, button) {
        var row = button.closest("tr");
        var next = row.next(".bp-machine-log-row");
        if (next.length) {
            next.remove();
            button.text(t("showMachineLog"));
            return;
        }
        var panel = $('<tr class="bp-machine-log-row"><td colspan="5"><pre class="bp-log"></pre></td></tr>');
        row.after(panel);
        button.text(t("hideMachineLog"));
        call("machine_log", { job: job, target: target }, function (response) {
            panel.find("pre").text(response.ok ? response.log : (response.error || t("machineLogUnavailable")));
        });
    }

    function stopPolling() {
        if (state.poll) {
            clearTimeout(state.poll);
            state.poll = null;
        }
    }

    function scheduleNextPoll(delay) {
        stopPolling();
        state.poll = setTimeout(poll, delay === undefined ? POLL_INTERVAL : delay);
    }

    function applyStatus(status) {
        renderJob(status);

        if (status.machines && status.machines.length) {
            state.machines = status.machines;
            // keep the previous selection when a machine is still there
            var kept = {};
            for (var i = 0; i < state.machines.length; i += 1) {
                if (state.selected[state.machines[i].target]) {
                    kept[state.machines[i].target] = true;
                }
            }
            state.selected = kept;
            renderMachines();
        }

        if (status.ous && status.ous.length) {
            state.ous = status.ous;
            renderOuTree(status.ous);
        }

        if (status.status === "running" || status.log_more) {
            // More log is waiting on the server: fetch it right away instead
            // of one slice per interval.
            state.pollErrors = 0;
            scheduleNextPoll(status.log_more ? 100 : POLL_INTERVAL);
        } else {
            stopPolling();
            state.job = null;
            var done = state.onComplete;
            state.onComplete = null;
            $("#bpJobLabel").append(
                status.status === "error" && status.error ? " - " + escapeHtml(status.error) : "");
            if (status.status === "error") {
                notify(status.error || "error", true);
                maybeShowPrereqBanner(status.error);
            }
            renderInstallResults(status);
            refreshGroups();
            refreshJobs();
            if (done) {
                done(status);
            }
        }
    }

    function poll() {
        if (!state.job) {
            return;
        }
        // One single request in flight: a slow answer must not stack up.
        if (state.polling) {
            scheduleNextPoll();
            return;
        }
        // A hidden tab has no reason to keep asking the server.
        if (document.hidden) {
            scheduleNextPoll(POLL_INTERVAL * 4);
            return;
        }
        state.polling = true;
        call("status", { job: state.job, log_offset: state.logOffset }, function (status) {
            state.polling = false;
            if (!status.ok) {
                // A killed request is transient: retry a few times before
                // giving up, with a growing delay.
                state.pollErrors = (state.pollErrors || 0) + 1;
                if (state.pollErrors <= POLL_ERRORS_MAX) {
                    scheduleNextPoll(POLL_INTERVAL * state.pollErrors * 2);
                    return;
                }
                stopPolling();
                notify(status.error || t("statusError"), true);
                return;
            }
            state.pollErrors = 0;
            applyStatus(status);
        });
    }

    function startJob(action, extra, label, onComplete) {
        state.onComplete = onComplete || null;
        stopPolling();
        state.logOffset = 0;
        $("#bpJobLog").text("");
        $("#bpJobResults").empty().addClass("bp-hidden");
        $("#bpJob").removeClass("bp-hidden");
        $("#bpJobLabel").text((label || action) + "...");
        $("#bpProgressBar").css("width", "5%");

        var payload = { action: action };
        $.extend(payload, extra || {});
        call("start", payload, function (response) {
            if (!response.ok) {
                notify(response.error || t("cannotStartJob"), true);
                $("#bpJobLabel").text(t("error") + ": " + (response.error || ""));
                maybeShowPrereqBanner(response.error);
                return;
            }
            state.job = response.job;
            state.jobAction = action;
            poll();
        });
    }

    // Attach the top progress panel to a job that is already running or done.
    function followJob(job, label) {
        state.onComplete = null;
        stopPolling();
        state.logOffset = 0;
        $("#bpJobLog").text("");
        $("#bpJobResults").empty().addClass("bp-hidden");
        $("#bpJob").removeClass("bp-hidden");
        $("#bpJobLabel").text(label + "...");
        $("#bpProgressBar").css("width", "5%");
        state.job = job;
        state.jobAction = "install";
        poll();
        scrollToJob();
    }

    function scrollToJob() {
        $("html, body").animate({ scrollTop: $("#bpJob").offset().top - 120 }, 300);
    }

    // Agents the server can deploy (entity agents generated by Medulla plus
    // the generic one).
    function refreshAgents() {
        call("agents", {}, function (response) {
            var select = $("#bpAgent");
            if (!response.ok || !response.agents || !response.agents.length) {
                select.html('<option value="generic">' + escapeHtml(t("noAgent")) + "</option>");
                return;
            }
            var html = [];
            for (var i = 0; i < response.agents.length; i += 1) {
                var agent = response.agents[i];
                var systems = [];
                if (agent.windows) { systems.push("Windows"); }
                if (agent.linux) { systems.push("Linux"); }
                if (agent.mac) { systems.push("macOS"); }
                var label = agent.kind === "generic" ? t("genericAgent") : agent.label;
                if (systems.length) { label += " [" + systems.join("/") + "]"; }
                if (agent.date) { label += " - " + agent.date; }
                html.push('<option value="' + escapeHtml(agent.id) + '">' +
                          escapeHtml(label) + "</option>");
            }
            select.html(html.join(""));
        });
    }

    function credentials() {
        return {
            username: $("#bpUsername").val(),
            password: $("#bpPassword").val(),
            port: $("#bpPort").val() || 5985,
            namefilter: $("#bpFilter").val(),
            sshkey: $("#bpSshkey").val()
        };
    }

    // ----------------------------------------------------------- discovery

    function currentMode() {
        return $('input[name="bpMode"]:checked').val() || "network";
    }

    // Every search needs an account: the agent refuses to start without one, so
    // it is checked here first - and the message is shown next to the button
    // instead of in the job panel, which is hidden at this point.
    function credentialProblem() {
        var user = ($("#bpUsername").val() || "").replace(/^\s+|\s+$/g, "");
        var pass = $("#bpPassword").val() || "";
        var key = ($("#bpSshkey").val() || "").replace(/^\s+|\s+$/g, "");
        if (currentMode() === "ad") {
            // An SSH key is no help against a directory.
            return (user && pass) ? null : t("adAccountRequired");
        }
        if (key) {
            // The key replaces the password; a user name is still needed.
            return user ? null : t("usernameRequired");
        }
        return (user && pass) ? null : t("accountRequired");
    }

    function showFormMessage(message) {
        var zone = $("#bpDiscoverMessage");
        if (!zone.length) {
            notify(message, true);
            return;
        }
        zone.removeClass("bp-hidden").text(message);
    }

    function clearFormMessage() {
        $("#bpDiscoverMessage").addClass("bp-hidden").text("");
    }

    function doDiscover() {
        var params = credentials();
        params.mode = currentMode();
        if (params.mode === "ad") {
            params.server = $("#bpServer").val();
            params.ou = $("#bpOu").val();
            params.domain = $("#bpDomain").val();
        } else {
            params.target = $("#bpTarget").val();
        }
        var problem = credentialProblem();
        if (problem) {
            showFormMessage(problem);
            return;
        }
        clearFormMessage();
        startJob("discover", params, t("jobDiscovery"));
    }

    function doListOus() {
        var params = credentials();
        params.mode = "ad";
        params.server = $("#bpServer").val();
        params.domain = $("#bpDomain").val();
        if (!params.server) {
            showFormMessage(t("adServerRequired"));
            return;
        }
        var problem = credentialProblem();
        if (problem) {
            showFormMessage(problem);
            return;
        }
        clearFormMessage();
        startJob("list_ous", params, t("jobListOus"));
    }

    function doInstall(machines, groupName) {
        var list = machines || selectedMachines();
        if (!list.length) {
            notify(t("noMachine"), true);
            return;
        }
        var problem = credentialProblem();
        if (problem) {
            showFormMessage(problem);
            return;
        }
        clearFormMessage();
        var params = credentials();
        params.targets = JSON.stringify(list);
        params.agent_id = $("#bpAgent").val() || "generic";
        if ($("#bpAgentInsecure").is(":checked")) {
            params.agent_insecure = "1";
        }
        if ($("#bpReinstall").is(":checked")) {
            params.reinstall = "1";
        }
        if (groupName) {
            params.group = groupName;
        }
        startJob("install", params, t("jobInstall").replace("%d", list.length));
        scrollToJob();
    }

    // An agent installation group is this page's own list of machines to
    // deploy to: the machines do not need the agent yet.
    function groupExists(name) {
        var wanted = String(name).toLowerCase();
        for (var i = 0; i < state.groups.length; i += 1) {
            if (String(state.groups[i].name).toLowerCase() === wanted) {
                return true;
            }
        }
        return false;
    }

    function saveInstallGroup(name, description, machines) {
        call("group_save", {
            name: name,
            description: description,
            machines: JSON.stringify(machines)
        }, function (response) {
            if (!response.ok) {
                notify(response.error || t("groupSaveFailed"), true);
                return;
            }
            notify(t("groupSaved").replace("%s", response.group).replace("%d", response.count), false);
            refreshGroups();
        });
    }

    function doCreateInstallGroup() {
        var list = selectedMachines();
        if (!list.length) {
            notify(t("noMachine"), true);
            return;
        }
        openDialog({
            title: t("createInstallGroup"),
            message: t("installGroupInfo").replace("%d", list.length),
            inputLabel: t("groupName"),
            value: t("defaultGroupPrefix") + " " + new Date().toISOString().slice(0, 10),
            input: true,
            input2Label: t("descriptionLabel"),
            validate: function (name) { return groupExists(name) ? t("groupExists") : ""; },
            confirmLabel: t("dialogCreate")
        }, function (name, description) {
            saveInstallGroup(name, description, list);
        });
    }

    // -------------------------------------------------------------- groups

    function refreshGroups() {
        call("groups", {}, function (response) {
            var body = $("#bpGroupsBody");
            if (!response.ok || !response.groups || !response.groups.length) {
                body.html('<tr class="bp-empty"><td colspan="5">' + t("noGroup") + "</td></tr>");
                state.groups = [];
                return;
            }
            state.groups = response.groups;
            var html = [];
            for (var i = 0; i < response.groups.length; i += 1) {
                var group = response.groups[i];
                html.push(
                    "<tr>" +
                    "<td>" + escapeHtml(group.name) + "</td>" +
                    "<td>" + escapeHtml(group.count) + "</td>" +
                    "<td>" + escapeHtml(group.description) + "</td>" +
                    "<td>" + escapeHtml(group.updated) + "</td>" +
                    '<td class="bp-col-actions">' +
                    '<button type="button" class="btnSecondary bp-group-install" data-name="' + escapeHtml(group.name) + '">' + t("install") + "</button> " +
                    '<button type="button" class="btnSecondary bp-group-follow" data-name="' + escapeHtml(group.name) + '">' + t("follow") + "</button> " +
                    '<button type="button" class="btnDanger bp-group-delete" data-name="' + escapeHtml(group.name) + '">' + t("delete") + "</button>" +
                    "</td></tr>"
                );
            }
            body.html(html.join(""));
            // The table is rebuilt on every refresh: put the open log back under
            // its row instead of closing it under the reader's eyes.
            restoreInlineLog();
        });
    }

    // ------------------------------------------------------------- job logs
    //
    // "Follow" opens the job log inside the table, right below its own row.
    // The previous behaviour scrolled the page back to the top panel: the user
    // lost their place and the log they asked for was somewhere else.
    var INLINE_POLL_INTERVAL = 3000;

    function inlineState() {
        if (!state.inline) {
            state.inline = { job: null, offset: 0, timer: null, busy: false,
                             errors: 0, panel: null };
        }
        return state.inline;
    }

    function closeInlineLog() {
        var inline = inlineState();
        if (inline.timer) {
            clearTimeout(inline.timer);
            inline.timer = null;
        }
        if (inline.panel) {
            inline.panel.remove();
        }
        var previous = inline.job;
        inline.job = null;
        inline.panel = null;
        inline.offset = 0;
        inline.busy = false;
        inline.errors = 0;
        if (previous) {
            $(".bp-job-follow").filter(function () {
                return $(this).attr("data-job") === previous;
            }).text(t("follow"));
        }
    }

    function toggleInlineLog(job, button) {
        var inline = inlineState();
        if (inline.job === job) {
            closeInlineLog();
            return;
        }
        openInlineLog(job, button);
    }

    function openInlineLog(job, button) {
        var inline = inlineState();
        if (inline.job === job) {
            return;
        }
        closeInlineLog();
        var panel = $('<tr class="bp-job-log-row"><td colspan="6">' +
            '<div class="bp-job-log-head"></div>' +
            '<pre class="bp-log bp-job-log"></pre></td></tr>');
        button.closest("tr").after(panel);
        panel.find(".bp-job-log-head").text(t("loading"));
        inline.job = job;
        inline.panel = panel;
        inline.offset = 0;
        inline.errors = 0;
        button.text(t("hide"));
        scheduleInlinePoll(0);
    }

    function restoreInlineLog() {
        var inline = inlineState();
        if (!inline.job || !inline.panel) {
            return;
        }
        var row = $("#bpJobsBody tr.bp-job-row").filter(function () {
            return $(this).attr("data-job") === inline.job;
        });
        if (!row.length) {
            closeInlineLog();
            return;
        }
        row.after(inline.panel);
        row.find(".bp-job-follow").text(t("hide"));
    }

    function scheduleInlinePoll(delay) {
        var inline = inlineState();
        if (!inline.job) {
            return;
        }
        if (inline.timer) {
            clearTimeout(inline.timer);
        }
        inline.timer = setTimeout(inlinePoll, delay);
    }

    function inlinePoll() {
        var inline = inlineState();
        if (!inline.job || inline.busy) {
            return;
        }
        // A hidden tab has no reason to keep asking the server.
        if (document.hidden) {
            scheduleInlinePoll(INLINE_POLL_INTERVAL * 4);
            return;
        }
        inline.busy = true;
        call("status", { job: inline.job, log_offset: inline.offset }, function (status) {
            inline.busy = false;
            if (!inline.job || !inline.panel) {
                return;
            }
            if (!status.ok) {
                inline.errors += 1;
                if (inline.errors <= 3) {
                    scheduleInlinePoll(INLINE_POLL_INTERVAL * inline.errors);
                    return;
                }
                inline.panel.find(".bp-job-log-head").text(status.error || t("statusError"));
                return;
            }
            inline.errors = 0;
            appendInlineLog(status);
            if (status.log_more) {
                scheduleInlinePoll(100);
            } else if (status.status === "running") {
                scheduleInlinePoll(INLINE_POLL_INTERVAL);
            }
        });
    }

    function appendInlineLog(status) {
        var inline = inlineState();
        var lines = status.log || [];
        if (lines.length) {
            appendLog(inline.panel.find(".bp-job-log"), lines.join("\n") + "\n");
        }
        if (status.log_truncated) {
            appendLog(inline.panel.find(".bp-job-log"), t("logTruncated") + "\n");
        }
        if (typeof status.log_offset === "number") {
            inline.offset = status.log_offset;
        }
        var parts = [status.job || inline.job];
        if (status.mode) {
            parts.push(status.mode);
        }
        if (status.progress && status.progress.total) {
            parts.push(status.progress.done + "/" + status.progress.total);
        }
        parts.push(status.status === "running" ? t("running")
            : (status.status === "error" ? t("error")
            : (status.status === "cancelled" ? t("cancelled") : t("done"))));
        if (status.machines && status.machines.length) {
            parts.push(status.machines.length + " " + t("machines"));
        }
        if (status.error) {
            parts.push(status.error);
        }
        inline.panel.find(".bp-job-log-head").text(parts.join(" - "));
    }

    function groupMachines(name, done) {
        call("group_get", { name: name }, function (response) {
            if (!response.ok) {
                notify(response.error || t("groupUnreadable"), true);
                return;
            }
            done(response.machines || []);
        });
    }

    // ---------------------------------------------------------------- jobs

    function refreshJobs() {
        call("jobs", {}, function (response) {
            var body = $("#bpJobsBody");
            if (!response.ok || !response.jobs || !response.jobs.length) {
                body.html('<tr class="bp-empty"><td colspan="6">' + t("noJob") + "</td></tr>");
                restoreInlineLog();
                return;
            }
            var html = [];
            for (var i = 0; i < response.jobs.length; i += 1) {
                var job = response.jobs[i];
                html.push(
                    '<tr class="bp-job-row" data-job="' + escapeHtml(job.job) + '">' +
                    "<td>" + escapeHtml(job.job) + "</td>" +
                    "<td>" + escapeHtml(job.action) + "</td>" +
                    "<td>" + escapeHtml(job.target) + "</td>" +
                    '<td><span class="bp-state bp-state-' + escapeHtml(job.state || "finished") +
                        '">' + escapeHtml(stateLabel(job.state)) + "</span></td>" +
                    "<td>" + escapeHtml(job.total) + "</td>" +
                    '<td class="bp-col-actions">' +
                    '<button type="button" class="btnSecondary bp-job-follow" data-job="' +
                        escapeHtml(job.job) + '">' + t("follow") + "</button>" +
                    // Cancelling a finished job means nothing: the button is
                    // only offered while the job is really running.
                    (job.state === "running"
                        ? ' <button type="button" class="btnSecondary bp-job-cancel" data-job="' +
                          escapeHtml(job.job) + '">' + t("cancel") + "</button>"
                        : "") +
                    "</td></tr>"
                );
            }
            body.html(html.join(""));
            // The rows were rebuilt: put the open log back under its row.
            restoreInlineLog();
        });
    }

    // -------------------------------------------------------- prerequisites

    // The banner is not shown while everything works: it only appears when an
    // action really fails because a prerequisite is missing.
    function maybeShowPrereqBanner(message) {
        if (!message) {
            return;
        }
        if (!/WSMan|PSWSMan|PowerShell|pr[ée]requis/i.test(message)) {
            return;
        }
        var banner = $("#bpPrereq");
        banner.removeClass("bp-hidden").addClass("bp-banner-error").html(
            "<strong>" + escapeHtml(message) + "</strong>" +
            ' <button type="button" class="btnSecondary" id="bpInstallPrereq">' +
            escapeHtml(t("installPrereq")) + "</button>"
        );
    }

    function checkPrereq(showWhenOk, retry) {
        call("prereq", {}, function (response) {
            var banner = $("#bpPrereq");
            if (response.ok && response.refreshing && !retry) {
                // The report is being refreshed in the background, ask again.
                setTimeout(function () { checkPrereq(showWhenOk, true); }, 4000);
            }
            if (!response.ok) {
                banner.removeClass("bp-hidden").addClass("bp-banner-error")
                    .html(t("prereqUnreadable") + " " + escapeHtml(response.error || ""));
                return;
            }
            var prereq = response.prerequisites || {};
            var known = false;
            for (var probe in prereq) {
                if (prereq.hasOwnProperty(probe)) { known = true; break; }
            }
            if (!known) {
                // Nothing cached yet, the background refresh is on its way.
                return;
            }
            var missing = [];
            var labels = {
                pwsh: "PowerShell (pwsh)",
                wsman: t("prereqWsmanClient"),
                nmap: "nmap",
                python3: "python3",
                mysql: t("prereqMysqlClient"),
                dig: "dig"
            };
            for (var key in labels) {
                if (labels.hasOwnProperty(key) && !response.prerequisites[key]) {
                    missing.push(labels[key]);
                }
            }
            if (!missing.length) {
                banner.addClass("bp-hidden").removeClass("bp-banner-error");
                if (showWhenOk) {
                    notify(t("prereqAllPresent"), false);
                }
                return;
            }
            banner.removeClass("bp-hidden").addClass("bp-banner-error").html(
                "<strong>" + t("prereqMissing") + "</strong> " + escapeHtml(missing.join(", ")) +
                ' <button type="button" class="btnSecondary" id="bpInstallPrereq">' +
                escapeHtml(t("installPrereq")) + "</button>"
            );
        });
    }

    // ---------------------------------------------------------------- init

    $(function () {
        $('input[name="bpMode"]').on("change", function () {
            switchMode(currentMode());
        });

        $("#bpDiscover").on("click", doDiscover);
        $("#bpListOus").on("click", doListOus);
        // Clicking a branch of the tree targets it for the next search.
        $(document).on("click", "#bpOuTree .bp-ou-name", function () {
            selectOu($(this).attr("data-dn"));
            return false;
        });
        $("#bpCancel").on("click", function () {
            if (!state.job) {
                return;
            }
            call("cancel", { job: state.job }, function (response) {
                if (!response.ok) {
                    notify(response.error || t("cancelFailed"), true);
                } else if (response.cancelled === false) {
                    notify(t("jobAlreadyFinished"), false);
                } else {
                    notify(t("cancelRequested"), false);
                }
            });
        });

        $("#bpPrereqButton").on("click", function () { checkPrereq(true); });
        $(document).on("click", "#bpInstallPrereq", function () {
            startJob("ps_setup", {}, t("jobPrereqSetup"));
        });

        $("#bpResultFilter").on("input", renderMachines);
        $("#bpSelectAll").on("change", function () {
            var checked = $(this).is(":checked");
            $("#bpMachinesBody .bp-machine-check").each(function () {
                state.selected[$(this).data("target")] = checked;
            });
            renderMachines();
        });
        $(document).on("visibilitychange", function () {
            if (!document.hidden && state.job) {
                scheduleNextPoll(300);
            }
        });

        $(document).on("click", ".bp-session", function () {
            openSession($(this).data("target"), $(this).data("protocol"), $(this).data("port"));
        });

        $(document).on("change", ".bp-machine-check", function () {
            state.selected[$(this).data("target")] = $(this).is(":checked");
            refreshSelectionCounter();
        });

        $("#bpInstall").on("click", function () { doInstall(null); });
        $("#bpCreateGroup").on("click", doCreateInstallGroup);

        $("#bpGroupSave").on("click", function () {
            var machines = selectedMachines();
            var name = $("#bpGroupName").val();
            if (!name) {
                notify(t("groupNameRequired"), true);
                return;
            }
            if (!machines.length) {
                notify(t("noMachine"), true);
                return;
            }
            saveInstallGroup(name, $("#bpGroupDescription").val(), machines);
        });

        $(document).on("click", ".bp-group-install", function () {
            var name = $(this).data("name");
            groupMachines(name, function (machines) { doInstall(machines, name); });
        });
        $(document).on("click", ".bp-group-follow", function () {
            var name = $(this).data("name");
            call("jobs", { group: name }, function (response) {
                var latest = response.ok && response.jobs && response.jobs.length ? response.jobs[0] : null;
                if (!latest) {
                    notify(t("noGroupJob"), false);
                    return;
                }
                followJob(latest.job, t("groupJobLabel").replace("%s", name));
            });
        });
        $(document).on("click", ".bp-group-delete", function () {
            var name = $(this).data("name");
            openDialog({
                title: t("delete"),
                message: t("confirmDelete") + " (" + name + ")",
                confirmLabel: t("delete"),
                danger: true
            }, function () {
                call("group_delete", { name: name }, function (response) {
                    notify(response.ok ? t("groupDeleted") : (response.error || t("groupDeleteFailed")), !response.ok);
                    refreshGroups();
                });
            });
        });

        // "Follow" opens the log of that job just below its own row.
        $(document).on("click", ".bp-job-follow", function () {
            toggleInlineLog($(this).data("job"), $(this));
        });
        // Stopping a job interrupts what it was doing (an installation, a
        // discovery): ask first.
        $(document).on("click", ".bp-job-cancel", function () {
            var button = $(this);
            var job = button.data("job");
            openDialog({
                title: t("stopJob"),
                message: t("confirmCancel"),
                confirmLabel: t("stopJob"),
                danger: true
            }, function () {
                call("cancel", { job: job }, function (response) {
                    if (!response.ok) {
                        notify(response.error || t("cancelFailed"), true);
                    } else if (response.cancelled === false) {
                        // Already finished: say it instead of pretending that
                        // something was stopped.
                        notify(t("jobAlreadyFinished"), false);
                    } else {
                        notify(t("cancelRequested"), false);
                        // Open the log of that very job: its header shows the
                        // cancelled state, right where the button was clicked.
                        openInlineLog(job, button);
                    }
                    refreshJobs();
                });
            });
        });

        refreshAgents();
        refreshGroups();
        refreshJobs();
    });
}(jQuery));
