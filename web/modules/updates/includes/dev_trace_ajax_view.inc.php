<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/includes/dev_trace_ajax_view.inc.php

if (function_exists('mmc_trace_ajax_view')) {
    mmc_trace_ajax_view('updates_dev_trace', 'UPDATES');
} elseif (function_exists('updates_dev_trace')) {
    $updatesTraceBacktrace = debug_backtrace(DEBUG_BACKTRACE_IGNORE_ARGS, 1);
    $updatesTraceCallerFile = isset($updatesTraceBacktrace[0]['file'])
        ? $updatesTraceBacktrace[0]['file']
        : __FILE__;

    updates_dev_trace('INFO', 'ajax-view', array('file' => $updatesTraceCallerFile));

    unset($updatesTraceBacktrace, $updatesTraceCallerFile);
}