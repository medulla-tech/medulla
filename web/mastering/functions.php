<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 *
 */

function read_conf($conffile){
    $tmp = [];
    if (is_file($conffile)) {
        $content = file_get_contents($conffile);
        $content = str_replace("#", ";", $content);
        $tmp = parse_ini_string($content, false, INI_SCANNER_RAW);
    }
    return $tmp;
}

function get_groups($id, $name=""){
    global $db;

    $gids = [];
    // ----- static groups
    if($name == ""){
        $q1 = $db["dyngroup"]->prepare("SELECT g.id from Results r join Groups g on g.id=r.FK_groups join Machines m on m.id=r.FK_machines where m.uuid = ?");
        $q1->execute(["UUID".$id]);
    }
    else{
        $q1 = $db["dyngroup"]->prepare("SELECT g.id from Results r join Groups g on g.id=r.FK_groups join Machines m on m.id=r.FK_machines where m.uuid = ? and g.name = ?");
        $q1->execute(["UUID".$id, $name]);
    }

    $datas = $q1->fetchAll(\PDO::FETCH_ASSOC);
    // No static group for this machine
    if($datas == NULL){
        $gids = [];
    }
    else{
        foreach($datas as $row){
            $gids[] = $row["id"];
        }
    }

    // ----- dynamic groups
    if($name == ""){
        $q2 = $db["dyngroup"]->prepare("SELECT id, query, bool from Groups where query is not NULL and query != ''");
        $q2->execute([]);
    }
    else{
        $q2 = $db["dyngroup"]->prepare("SELECT id, query, bool from Groups where query is not NULL and query != '' and name = ?");
        $q2->execute([$name]);
    }
    $datas = $q2->fetchAll(\PDO::FETCH_ASSOC);
    $criterions = [];

    if($datas == NULL){
        return $gids;
    }

    // For each dynamic group
    foreach($datas as $row){
        
        // Do manipulation on bool and query
        // $row['bool'] = str_replace(" ", "", $row["bool"]);
        // $row["bool"] = strtoupper(($row["bool"]));

        $queries = explode("||", $row["query"]);
        $row["criterions"] = [];

        // Split the query to get each elements
        foreach($queries as $query){
            $matches = [];
            preg_match("#^([0-9]{1,})==([\w]+)::(.*)==(.*)$#", $query, $matches);
            if($matches != []){
                array_shift($matches);
                $criterion = [
                    "identifier"=>$matches[0],
                    "db"=>$matches[1],
                    "criterion"=>$matches[2],
                    "value"=>$matches[3],
                    "result"=>false
                ];

                $result = has_machine_criterion($id, $criterion);
                $criterion["result"] = $result;
                $row["criterions"][] = $criterion;
            }
        }
        if(bool_expr($row["bool"], $row["criterions"]) == true){
            if(!in_array($row["id"], $gids)){
                $gids[] = $row["id"];
            }
        }
    }

    return $gids;
}

function and_($a, $b){
    return ($a&&$b);
}

function or_($a, $b){
    return ($a||$b) == true ? 1 : 0;
}

function not_($a){
    return !$a == true ? 1 : 0;
}

function bool_expr($bool, $criterions){
    
    // Handle the case where the boolean is empty or null
    if($bool == "" || $bool == NULL){
        $count = count($criterions);
        if($count == 1){
            // At least use the first criterion
            $bool = "and_(1,1)";
        }
        else{
            $bool ="";
            for($i=1; $i<=$count; $i++){
                $bool .= $i.",";
            }
            $bool = rtrim($bool, ",");
            $bool = "and_(".$bool.")";
        }
    }
    else{
        $bool = strtoupper(str_replace(" ", "", $bool));
    }
    

    // Replace element from $bool with our function names.
    $bool = preg_replace(["#AND#", "#OR#", "#NOT#"], ["and_", "or_", "not_"], $bool);
    $bool = preg_replace_callback("#([0-9]{1,})#", function($data) use($criterions){
        array_shift($data);
        $id = $data[0]-1;
        return ($criterions[$id]["result"] == true) ? "1" : "0";
    },$bool);
    
    $result = false;
    eval('$result = '.$bool.';');
    
    return $result;
}

function has_machine_criterion($id, $query){
    global $db;
    $sql = "select unique(c.id) from glpi_computers_pulse c";
    $join = "";
    $where = "";
    $bind = [$id, $query["value"]];
    $result = [];

    $like="=";
    $query["value"] = preg_replace_callback("#\*#", function($data) use (&$like){
        $like = "like";
        return '%';
    }, $query["value"]);

    switch($query["criterion"]){
        case "Computer name":
            $where = "c.id = ? and c.name $like ?";
            break;
        
        case "Description":
            $where = "c.id = ? and c.comment $like ?";
            break;
            
        case "Inventory number":
            $where = "c.id = ? and c.otherserial $like ?";
            break;

        case "Group":
            $join = "join glpi_groups g on g.id = c.groups_id";
            $where = "c.id = ? and g.completename $like ?";
            break;
        
        case "Peripheral name":
            $join = "join glpi_computers_items ci on ci.computers_id = c.id join glpi_peripherals p on p.id = ci.items_id and ci.itemtype=\"Peripheral\"";
            $where = "p.name $like ?";
            break;
        
        case "Peripheral serial":
            $join = "join glpi_computers_items ci on ci.computers_id = c.id join glpi_peripherals p on p.id = ci.items_id and ci.itemtype=\"Peripheral\"";
            $where = "p.serial $like ?";
            break;

        case "System type":
            $join = "join glpi_computertypes t on t.id = c.computertypes_id";
            $where = "c.id = ? and t.name $like ?";
            break;

        case "System manufacturer":
            $join = "join glpi_manufacturers m on m.id = c.manufacturers_id";
            $where = "c.id = ? and m.name $like ?";
            break;

        case "System model":
            $join = "join glpi_computermodels m on m.id = c.computermodels_id";
            $where = "c.id = ? and m.name $like ?";
            break;

        case "Owner of the machine":
            $join = "join glpi_users u on u.id = c.users_id";
            $where = "c.id = ? and u.name $like ?";
            break;

        case "Last Logged User":
            $where = "c.id = ? and c.contact $like ?";
            break;

        case "User location":
            $join = "join glpi_users u on u.id = c.users_id join glpi_locations l on l.id = u.locations_id";
            $where = "c.id = ? and l.completename $like ?";
            break;

        case "Location":
            $join = "join glpi_locations l on l.id = c.locations_id";
            $where = "c.id = ? and l.completename $like ?";
            break;

        case "State":
            $join = "join glpi_states s on c.states_id = s.id";
            $where = "c.id = ? and s.name $like ?";
            break;

        case "Entity":
            $join = "join glpi_entities e on e.id=c.entities_id";
            $where = "c.id = ? and e.name $like ?";
            break;

        case "Operating system":
            $join = "join glpi_operatingsystems o on o.id = c.operatingsystems_id";
            $where = "c.id = ? and o.name $like ?";
            break;

        case "Installed software":
            $join = "join glpi_items_softwareversions gis on gis.items_id = c.id join glpi_softwareversions gsv on gsv.id = gis.softwareversions_id join glpi_softwares gs on gs.id = gsv.softwares_id";
            $where = "c.id = ? and gs.name $like ?";
            break;

        case "Installed software (specific version)":
            $join = "join glpi_items_softwareversions gis on gis.items_id = c.id join glpi_softwareversions gsv on gsv.id = gis.softwareversions_id join glpi_softwares gs on gs.id = gsv.softwares_id";
            $where = "c.id = ? and gs.name = ? and gsv.name $like ?";
            list($value, $version) = explode(", ", $query["value"]);
            $bind = [$id, substr($value, 1), substr($version, 0, -1)];
            break;

        case "OS Version":
            $join = "join glpi_operatingsystemversions v on ov.id = c.operatingsystemversions_id";
            $where = "c.id = ? and v.name $like ?";
            break;

        case "Architecture":
            $join = "join glpi_operatingsystemarchitectures a on a.id = c.operatingsystemarchitectures_id";
            $where = "c.id = ? and a.name $like ?";
            break;

        case "Register key":
            break;

        case "Register key value":
            break;

        case "Online computer":
            $query["db"] = "xmppmaster";
            $sql = "SELECT substr(m.uuid_inventorymachine, 5) as id from machines m";
            $where = "m.uuid_inventorymachine = ? and m.enabled = ?";
            $bind = ["UUID".$id, ($query["value"] == "True") ? 1 : 0];
            break;

        case "OU user":
            // Explicit xmppmaster
            $query["db"] = "xmppmaster";
            $sql = "SELECT substr(m.uuid_inventorymachine, 5) as id from machines m";
            $where = "m.uuid_inventorymachine = ? and m.ad_ou_user REGEXP ?";
            $bind = ["UUID".$id, $query["value"]];
            break;

        case "OU Machine":
            $query["db"] = "xmppmaster";
            $sql = "SELECT substr(m.uuid_inventorymachine, 5) as id from machines m";
            $where = "m.uuid_inventorymachine = ? and m.ad_ou_user REGEXP ?";
            $bind = ["UUID".$id, $query["value"]];

            break;

        case "groupname":
            $result = get_groups($id, $query["value"]);
            return ($result == []) ? false : true;
            break;
    }

    $sql = $sql." ".$join." WHERE ".$where;
    $q = $db[$query["db"]]->prepare($sql);
    $q->execute($bind);
    $datas = $q->fetch(\PDO::FETCH_ASSOC);

    return ($datas != []) ? true : false;
}
