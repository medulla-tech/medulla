<?php

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
 *
 * $Id$
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

class CommandOnHost {
    function CommandOnHost($coh) {
        $statusTable = getStatusTable();
        $this->db_coh = get_commands_on_host($coh);
        #$this->db_cmd = command_detail($this->db_coh['id_command']);
        $this->values = array(
            array(_T('Host', 'msc'), $this->db_coh['host'], 1),
            array(_T('current_state', 'msc'), $statusTable[$this->db_coh['current_state']], 1),
            array(_T('uploaded', 'msc'), _plusIcon($this->db_coh['uploaded']), 1),
            array(_T('executed', 'msc'), _plusIcon($this->db_coh['executed']), 1),
            array(_T('deleted', 'msc'), _plusIcon($this->db_coh['deleted']), 1)
        );
    }
    function display() {
        $name = array_map("_names", $this->values);
        $value = array_map("_values", $this->values);

        $n = new ListInfos($name, _T('Name', 'msc'));
        $n->addExtraInfo($value, _T('Value', 'msc'));
        $n->setRowsPerPage(count($this->values));

        $n->drawTable(0);
    }
    function quickDisplay($actions = array(), $params = array()) {
        $n = null;
        $params = array();
        foreach ($this->values as $col) {
            if ($col[2]) {
                if ($n) {
                    $n->addExtraInfo(array($col[1]), $col[0]);
                } else {
                    $n = new ListInfos(array($col[1]), $col[0]);
                }
            }
        }
        $n->setParamInfo(array($params));
        foreach ($actions as $a) {
            $n->addActionItem($a);
        }
        $n->drawTable(0);
    }
}
class Command {
    function Command($cmd) {
        $this->db_cmd = command_detail($cmd);
        $this->values = array(
            array(_T('Command name', 'msc'),$this->db_cmd['title'], 1),
            array(_T('Creation date', 'msc'),_toDate($this->db_cmd['date_created']), 1),
            array(_T('User command creator', 'msc'),$this->db_cmd['webmin_username'], 0),
            array(_T('Execute file', 'msc'),$this->db_cmd['start_file'], 0),
            array(_T('Execution arguments', 'msc'),$this->db_cmd['parameters'], 0),
            array(_T('Destination directory', 'msc'),$this->db_cmd['path_destination'], 0),
            array(_T('Source directory (repository)', 'msc'),$this->db_cmd['path_source'], 0),
            array(_T('Create destination directory', 'msc'),$this->db_cmd['create_directory'], 0),
            array(_T('Start execute file', 'msc'),$this->db_cmd['start_script'], 0),
            array(_T('Start inventory agent', 'msc'),$this->db_cmd['start_inventory'], 0),
            array(_T('Start "Wake On Lan" query if connection fails', 'msc'),$this->db_cmd['wake_on_lan'], 0),
            array(_T('Delay between two connections', 'msc'),$this->db_cmd['next_connection_delay'], 0),
            array(_T('Command start date', 'msc'),_toDate($this->db_cmd['start_date']), 0),
            array(_T('Command expiry date', 'msc'),_toDate($this->db_cmd['end_date']), 0),
        );
    }
    function display() {
        $name = array_map("_names", $this->values);
        $value = array_map("_values", $this->values);

        $n = new ListInfos($name, _T('Name', 'msc'));
        $n->addExtraInfo($value, _T('Value', 'msc'));
        $n->setRowsPerPage(count($this->values));

        $n->drawTable(0);
    }
    function quickDisplay($actions = array(), $params = array()) {
        $n = null;
        foreach ($this->values as $col) {
            if ($col[2]) {
                if ($n) {
                    $n->addExtraInfo(array($col[1]), $col[0]);
                } else {
                    $n = new ListInfos(array($col[1]), $col[0]);
                }
            }
        }
        $n->setParamInfo(array($params));
        foreach ($actions as $a) {
            $n->addActionItem($a);
        }
        $n->drawTable(0);
    }
}

class CommandHistory {
    function CommandHistory($coh_id) {
        // TODO : ch is a list, we have to chose the good one (ie : the most recent date)
        $this->db_ch = get_command_history($coh_id);
        $this->db_coh = get_commands_on_host($coh_id);
        $this->db_cmd = command_detail($this->db_coh['id_command']);
    }
    function display() {
        // display parameters
        $values = array(
            array(_T('Command name', 'msc'),$this->db_cmd['title']),
            array(_T('Creation date', 'msc'),_toDate($this->db_cmd['date_created'])),
            array(_T('User command creator', 'msc'),$this->db_cmd['webmin_username']),
            array(_T('Execute file', 'msc'),$this->db_cmd['start_file']),
            array(_T('Execution arguments', 'msc'),$this->db_cmd['parameters']),
            array(_T('Destination directory', 'msc'),$this->db_cmd['path_destination']),
            array(_T('Source directory (repository)', 'msc'),$this->db_cmd['path_source']),
            array(_T('Create destination directory', 'msc'),$this->db_cmd['create_directory']),
            array(_T('Start execute file', 'msc'),$this->db_cmd['start_script']),
            array(_T('Start inventory agent', 'msc'),$this->db_cmd['start_inventory']),
            array(_T('Start "Wake On Lan" query if connection fails', 'msc'),$this->db_cmd['wake_on_lan']),
            array(_T('Remaining attempts', 'msc'),$this->db_coh['number_attempt_connection_remains']),
            array(_T('Delay between two connections', 'msc'),$this->db_cmd['next_connection_delay']),
            array(_T('Command start date', 'msc'),_toDate($this->db_cmd['start_date'])),
            array(_T('Command expiry date', 'msc'),_toDate($this->db_cmd['end_date'])),
            array(_T('Command next run date', 'msc'),_toDate($this->db_coh['next_launch_date']))
        );

        $name = array_map("_names", $values);
        $value = array_map("_values", $values);

        $n = new ListInfos($name, _T('Name', 'msc'));
        $n->addExtraInfo($value, _T('Value', 'msc'));
        $n->setRowsPerPage(count($values));

        $n->drawTable(0);

        // display files
        $files = array('Transferred files list empty.');
        if ($this->db_cmd["files"]!="" && $this->db_cmd["files"]!=array()) {
            if (gettype($command["files"]) != 'array') {
                $files = explode("\n", $this->db_cmd["files"]);
            } else {
                $files = $this->db_cmd["files"];
            }
        }
        $n = new ListInfos($files, _T('Transferred files list', 'msc'));
        print "<hr/><br/>";
        $n->drawTable(0);

        # display command history
        # display log files
        foreach ($this->db_ch as $hist) {
            $history = '<img style="vertical-align: middle;" alt="'.$hist['state'].'" src="modules/msc/graph/images/'.history_stat2icon($hist['state']).'"/> '.date("Y-m-d H:i:s", $hist['date']).': <b>'.$hist['state'].'</b>';
            if (gettype($hist["stdout"]) != 'array')
                $hist["stdout"] = split("\n", $hist["stdout"]);
            if (gettype($hist["stderr"]) != 'array')
                $hist["stderr"] = split("\n", $hist["stderr"]);
            if (count($hist["stdout"]) > 0 &&
                !(count($hist["stdout"]) == 1 && $hist["stdout"][0] == '')
               ) {
                   $hist["stderr"] = array_merge($hist["stderr"], $hist["stdout"]);
            }
            $n = new ListInfos(array_map('_colorise', $hist["stderr"]), $history);
            if (count($hist["stderr"]) > 0  &&
                !(count($hist["stderr"]) == 1 && $hist["stderr"][0] == '')
               ) {
                $n->drawTable(0);
            }
        }
    }
}
function _values($a) { return $a[1]; }
function _names($a) { return $a[0]; }
function _colorise($line) {
    if (preg_match_all("|^(.*) ([ECOX]): (.*)$|", $line, $matches)) {
        $out .= '<font color=grey>' . $matches[1][0] . '</font>&nbsp;';
        if ($matches[2][0] == "E") {
            $out .= '<font color=red>';
        } elseif ($matches[2][0] == "C") {
            $out .= '<font color=blue>';
        } elseif ($matches[2][0] == "O") {
            $out .= '<font color=green>';
        } elseif ($matches[2][0] == "X") {
            $out .= '<font color=blue>';
        }
        $out .= $matches[3][0];
        $out .= '</font><br/>';
    } else $out .=  "<font>$line</font>\n";
    return $out;
}
function _toDate($a) {
    if (is_array($a) && count($a) == 6) {
        return $a[0]."/".$a[1].'/'.$a[2]." ".$a[3].":".$a[4].":".$a[5];
    } elseif (is_array($a) && count($a) == 9) {
        return $a[0]."/".$a[1].'/'.$a[2]." ".$a[3].":".$a[4].":".$a[5];
    } else {
        return $a;
    }
}
function _plusIcon($a) {
    return '<img alt="'.$a.'" src="modules/msc/graph/images/'.return_icon($a).'"/> '.$a;
}

# CH :
#Array ( [0] => Array ( [date] => 05-10-2007 23:34:47 [id_command_history] => 9 [state] => execution_in_progress [stderr] => [stdout] => ) [1] => Array ( [date] => 05-10-2007 23:34:47 [id_command_history] => 10 [state] => execution_failed [stderr] => /bin/sh: line 1: bin/annotate_output: No such file or directory *** Exit code: 127 *** [stdout] => ) )

# COH :
#Array ( [uploaded] => IGNORED [executed] => FAILED [next_launch_date] => 00-00-0000 00:00:00 [deleted] => TODO [id_command] => 3 [current_state] => execution_failed [host] => belial [number_attempt_connection_remains] => 3 )

# CMD :
#Array ( [files] => [next_connection_delay] => 60 [path_source] => [end_date] => [parameters] => [title] => list [max_connection_attempt] => 3 [webmin_username] => root@192.168.100. [start_script] => enable [start_file] => /bin/ls /tmp [create_directory] => disable [start_inventory] => disable [path_destination] => none [date_created] => 2007-10-05 23:34:42 [wake_on_lan] => disable [start_date] => [target] => belial )
