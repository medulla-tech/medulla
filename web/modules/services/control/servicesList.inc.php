<?php
if ($service['active_state'] != "unavailable") {
    if ($service['active_state'] == "active") {
        $status = _T($service['active_state']);
        $actionsStart[] = $emptyAction;
        if ($service['can_stop']) {
            $actionsStop[] = $stopAction;
            $actionsRestart[] = $restartAction;
        }
        else {
            $actionsStop[] = $emptyAction;
            $actionsRestart[] = $emptyAction;
        }
        if ($service['can_reload'])
            $actionsReload[] = $reloadAction;
        else
            $actionsReload[] = $emptyAction;
        $actionsLog[] = $logAction;
    }
    else if ( ($service['active_state'] == "activating" ) ||
              ($service['active_state'] == "deactivating" ) ) {
            $status = _T($service['active_state']);
            $actionsStart[] = $emptyAction;
            $actionsStop[] = $emptyAction;
            $actionsRestart[] = $emptyAction;
            $actionsReload[] = $emptyAction;
            $actionsLog[] = $logAction;
    }
    else {
        $status = '<span class="error">' . _T($service['active_state']) . '</span>';
        if ($service['active_state'] != "unavailable") {
            if ($service['can_start'])
                $actionsStart[] = $startAction;
            $actionsStop[] = $emptyAction;
            $actionsRestart[] = $emptyAction;
            $actionsReload[] = $emptyAction;
            $actionsLog[] = $logAction;
        }
        else {
            $actionsStart[] = $emptyAction;
            $actionsStop[] = $emptyAction;
            $actionsRestart[] = $emptyAction;
            $actionsReload[] = $emptyAction;
            $actionsLog[] = $emptyAction;
        }
    }
    $name = substr($service['id'], 0, -8);
    if ($service['active_state'] != "active")
        $name = '<span class="error">' . $name . '</span>';
    $names[] = $name;
    $descs[] = $service['description'];
    $statuses[] = $status;
    $ids[] = array("service" => $service['id'], "parent" => $_GET['parent']);
}
?>
