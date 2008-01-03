<?php

function return_icon($state)
{
    switch($state) {
        case "TODO":
            return "led_circle_grey.png";
            break;
        case "IGNORED":
            return "led_circle_black.png";
            break;
        case "DONE":
            return "led_circle_green.png";
            break;
        case "FAILED":
            return "led_circle_red.png";
            break;
        case "WORK_IN_PROGRESS":
            return "led_circle_orange.png";
            break;
    }
}

function state2icon($current_state) {
    switch ($current_state) {
        case "upload_in_progress" :
            return "led_circle_orange.png";
            break;
        case "upload_done" :
            return "led_circle_green.png";
            break;
        case "upload_failed" :
            return "led_circle_red.png";
            break;
        case "execution_in_progress":
            return "led_circle_orange.png";
            break;
        case "execution_done":
            return "led_circle_green.png";
            break;
        case "execution_failed":
            return "led_circle_red.png";
            break;
        case "delete_in_progress":
            return "led_circle_orange.png";
            break;
        case "delete_done":
            return "led_circle_green.png";
            break;
        case "delete_failed":
            return "led_circle_red.png";
            break;
        case "not_reachable":
            return "led_circle_red.png";
            break;
        case "done":
            return "led_circle_green.png";
            break;
        case "pause":
            return "led_circle_black.png";
            break;
        case "stop":
            return "led_circle_black.png";
            break;
        case "scheduled":
            return "led_circle_grey.png";
            break;
        default:
            return "led_circle_orange.png";
            break;
    }
}
function history_stat2icon($state) {
    switch ($state) {
        case "upload_in_progress" :
            return "led_circle_green.png";
            break;
        case "upload_done" :
            return "led_circle_green.png";
            break;
        case "upload_failed" :
            return "led_circle_red.png";
            break;
        case "execution_in_progress":
            return "led_circle_green.png";
            break;
        case "execution_done":
            return "led_circle_green.png";
            break;
        case "execution_failed":
            return "led_circle_red.png";
            break;
        case "delete_in_progress":
            return "led_circle_green.png";
            break;
        case "delete_done":
            return "led_circle_green.png";
            break;
        case "delete_failed":
            return "led_circle_red.png";
            break;
        case "not_reachable":
            return "led_circle_red.png";
            break;
        case "done":
            return "led_circle_green.png";
            break;
        case "pause":
            return "led_circle_black.png";
            break;
        case "stop":
            return "led_circle_black.png";
            break;
        case "scheduled":
            return "led_circle_gray.png";
            break;
    }
}

function state_tmpl($current_state) {
    $ret = array();
    if (
        ($current_state != "pause") &&
        ($current_state != "not_reachable") &&
        ($current_state != "upload_failed") &&
        ($current_state != "execution_failed") &&
        ($current_state != "delete_failed") &&
        ($current_state != "inventory_failed")

    ) {
        $ret['play'] = '';
    } else {
        $ret['play'] = 'BUTTON_PLAY';
    }

    if ( ($current_state != "scheduled")) {
        $ret['pause'] = '';
    } else {
        $ret['pause'] = 'BUTTON_PAUSE';
    }

    if (
        ($current_state != "scheduled") &&
        ($current_state != "not_reachable") &&
        ($current_state != "upload_failed") &&
        ($current_state != "execution_failed") &&
        ($current_state != "delete_failed") &&
        ($current_state != "inventory_failed") &&
        ($current_state != "upload_in_progress") &&
        ($current_state != "execution_in_progress") &&
        ($current_state != "delete_in_progress") &&
        ($current_state != "inventory_in_progress")
    ) {
        $ret['stop'] = '';
    } else {
        $ret['stop'] = 'BUTTON_STOP';
    }
    return $ret;
}

function template_set_cmd_by_page(&$template, $tmpl_name, $number_command_by_page) {

    /**
     * Number command by page display item selected
     */
    if ($number_command_by_page==10) {
        $template->set_block($tmpl_name, "NUMBER_BY_PAGE_10_SELECTED", "page_10_selected");
        $template->parse("page_10_selected", "NUMBER_BY_PAGE_10_SELECTED");
    } else {
        $template->set_block($tmpl_name, "NUMBER_BY_PAGE_10_SELECTED", "page_10_selected");
        $template->set_var("page_10_selected", "");
    }

    if ($number_command_by_page==20) {
        $template->set_block($tmpl_name, "NUMBER_BY_PAGE_20_SELECTED", "page_20_selected");
        $template->parse("page_20_selected", "NUMBER_BY_PAGE_20_SELECTED");
    } else {
        $template->set_block($tmpl_name, "NUMBER_BY_PAGE_20_SELECTED", "page_20_selected");
        $template->set_var("page_20_selected", "");
    }

    if ($number_command_by_page==50) {
        $template->set_block($tmpl_name, "NUMBER_BY_PAGE_50_SELECTED", "page_50_selected");
        $template->parse("page_50_selected", "NUMBER_BY_PAGE_50_SELECTED");
    } else {
        $template->set_block($tmpl_name, "NUMBER_BY_PAGE_50_SELECTED", "page_50_selected");
        $template->set_var("page_50_selected", "");
    }

    if ($number_command_by_page==100) {
        $template->set_block($tmpl_name, "NUMBER_BY_PAGE_100_SELECTED", "page_100_selected");
        $template->parse("page_100_selected", "NUMBER_BY_PAGE_100_SELECTED");
    } else {
        $template->set_block($tmpl_name, "NUMBER_BY_PAGE_100_SELECTED", "page_100_selected");
        $template->set_var("page_100_selected", "");
    }
}


?>
