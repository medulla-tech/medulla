<?php

//display the return of api for debug
function expand_arr($array) {
	foreach ($array as $key1) {
		foreach ($key1 as $key => $value) {
			if (is_array($value)) {
					echo "<i>".$key."</i>:<div style=\"margin-left: 20px;\" >";
					expand_arr($value);
					echo "</div>\n";
				} else {
					echo "<i>".$key."</i>: ".$value."<br>\n";
				}
			}
	}
	echo "<br>\n\n\n";
}

//return  an array in a one string to print it
function get_arr($array) {
	foreach ($array as $key1) {
		foreach ($key1 as $key => $value) {
			if (is_array($value)) {
					$arg =$arg."<i>".$key."</i>:<div style=\"margin-left: 20px;\" >";
					$arg = $arg.get_arr($value);
				} else {
					$arg = $arg."<i>".$key."</i>: ".$value."<br>";
				}
			}
	}
	return $arg;
}

//display the graph with his URL
function zabbixPrintGraph($url, $graphid, $width, $height, $time) {

$p = $url."/chart2.php?graphid=".$graphid."&width=".$width."&height=".$height."&period=".$time;
echo "<img src=".$p.">";
echo "</br></br>";
}

//calcul difference de temps entre 2 timestamp
function diffTime($date1, $date2) {
	$result = array();
	$diff = abs($date1 - $date2);
	$result['abs'] = $diff;
	$tmp = $diff;
	$result['second'] = $tmp % 60;
	$tmp = floor( ($tmp - $result['second']) / 60);
	$result['minute'] = $tmp % 60;
	$tmp = floor( ($tmp - $result['minute']) / 60);
	$result['hour'] = $tmp % 24;
	$tmp = floor( ($tmp - $result['hour']) / 24);
	$result['day'] = $tmp;
	
	$result2 = array();
	$result2['abs'] = $diff;
	$result2['time'] = $result['day']." Day(s) ".$result['hour']." Hour(s) ".$result['minute']." minute(s) ".$result['second']." second(s)";	

	return $result2;
}

class AjaxPrintGraph extends AjaxFilterLocation {
	

    function AjaxLocation($url, $divid = "container", $paramname = 'location', $params = array()) {
        $this->AjaxFilterLocation($url, $divid, $paramname, $params);
        $this->location = new SelectItem($paramname, 'pushSearchLocationGraph', 'searchfieldreal noborder');
    }

    function display($arrParam = array()) {
        global $conf;
        $root = $conf["global"]["root"];
        ?>

        <form name="FormLocationGraph" id="FormLocationGraph" action="#" onsubmit="return false;">
            <div id="Location">
                <span id="searchSpan" class="searchbox">
                    <img src="graph/search.gif"/>
                    <span class="locationtext">&nbsp;<?php echo _T("Select graph", "monitoring") ?>:&nbsp;</span>
                    <span class="locationfield">
                        <?php
                        $this->location->display();
                        ?>
                    </span>
                </span>
                <img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" />
            </div>

		<form name="FormLocationPeriod" id="FormLocationPeriod" action="#" onsubmit="return false;">
		    <div id="Location">
		        <span id="searchSpan" class="searchbox">
		            <img src="graph/search.gif"/>
		            <span class="locationtext">&nbsp;<?php echo _T("Select period", "monitoring") ?>:&nbsp;</span>
		            <span class="locationfield">
				<select id="period" class="searchfieldreal noborder" name="period" onchange="pushSearch(); return false;">
					<?php
					// time field creation
					$timeName = array(
						_T('1 hour', 'monitoring'),
						_T('1 week', 'monitoring'),
						_T('1 month', 'monitoring'),
						_T('1 year', 'monitoring'),
						_T('4 years', 'monitoring')
					);
					$timeValue = array('3600', '604800', '2419200', '29030400', '116121600');
					$count = count($timeName);
					for ($i = 0; $i < $count; $i++) {
						echo "<option value=\"$timeValue[$i]\" >";
						echo $timeName[$i];
						echo "</option>";
					}	
					?>
				</select>
		            </span>
		        </span>
		    </div>

            <script type="text/javascript">
                /**
                 * update div with user
                 */
		

                function updateSearchLocationGraph() {

			var div = document.getElementById('<?php echo $this->divid; ?>');
			var graphId = document.FormLocationGraph.<?php echo $this->paramname; ?>.value;
			var period = document.getElementById("period");
			var test = document.getElementById("graphId");
			if (test != null)
				document.getElementById("graphId").src = "http://192.168.0.105/zabbix/chart2.php?graphid=" + graphId +"&period=" + period.value;
			else {
				var image = document.createElement("img");
				image.id = "graphId";
				image.src = "http://192.168.0.105/zabbix/chart2.php?graphid=" + graphId +"&period=" + period.value;
				div.appendChild(image);
			}
                    
                }
                /**
                 * wait 500ms and update search
                 */

                function pushSearchLocationGraph() {

                    setTimeout("updateSearchLocationGraph()", 500);
                }
		
		var graph = document.getElementById("FormLocationGraph");
		graph.onchange = function() {
			pushSearchLocationGraph();
		};

                pushSearchLocationGraph();
            </script>

        </form></form>
        <?php
    }

}

class AjaxFilterLocationFormid extends AjaxFilterLocation {

    function AjaxFilterLocation($url, $divid = "container", $paramname = 'location', $params = array(), $formid = "") {
        $this->AjaxFilter($url, $divid, $params, $formid);
        $this->location = new SelectItem($paramname, 'pushSearch', 'searchfieldreal noborder');
        $this->paramname = $paramname;
    }
}

// TO ERASE

//request the api and return the result
function json_request($uri, $data) {
	$json_data = json_encode($data);
	$c = curl_init();
	curl_setopt($c, CURLOPT_URL, $uri);
	curl_setopt($c, CURLOPT_CUSTOMREQUEST, "POST");
	curl_setopt($c, CURLOPT_RETURNTRANSFER, true);
	curl_setopt($c, CURLOPT_POST, $json_data);
	curl_setopt($c, CURLOPT_POSTFIELDS, $json_data);
	curl_setopt($c, CURLOPT_HTTPHEADER, array(
		'Content-Type: application/json',
		'Content-Length: ' . strlen($json_data))
	);
	curl_setopt($c, CURLOPT_SSL_VERIFYPEER, false);
	$result = curl_exec($c);

	/* Uncomment to see some debug info
	echo "<b>JSON Request:</b><br>\n";
	echo $json_data."<br><br>\n";

	echo "<b>JSON Answer:</b><br>\n";
	echo $result."<br><br>\n";

	echo "<b>CURL Debug Info:</b><br>\n";
	$debug = curl_getinfo($c);
	echo expand_arr($debug)."<br><hr>\n";
	*/

	return json_decode($result, true);
}

//return the token
function zabbix_auth($uri, $username, $password) {
	$data = array(
		'jsonrpc' => "2.0",
		'method' => "user.authenticate",
		'params' => array(
			'user' => $username,
			'password' => $password
		),
		'id' => "1"
	);
	$response = json_request($uri, $data);
	return $response['result'];
}

//return all the hosts' informations
function zabbix_get_host($uri, $authtoken) {
        $data = array(
                'jsonrpc' => "2.0",
                'method' => "host.get",
                'params' => array(
                        'output' => "extend",
                        'sortfield' => "name",
			'with_triggers' => "1"
                ),
                'id' => "2",
                'auth' => $authtoken
        );
        $response = json_request($uri, $data);
        return $response['result'];
}

//return all the group
function zabbix_get_hostgroups($uri, $authtoken) {
	$data = array(
		'jsonrpc' => "2.0",
		'method' => "hostgroup.get",
		'params' => array(
			'output' => "extend",
			'sortfield' => "name",
			'filter' => array('name' => "Zabbix servers")
		),
		'id' => "2",
		'auth' => $authtoken
	);
	$response = json_request($uri, $data);
	return $response['result'];
}

//return all the graph by id
function zabbix_get_graph_by_id($uri, $authtoken, $id) {
        $data = array(
                'jsonrpc' => "2.0",
                'method' => "graph.get",
                'params' => array(
                        'output' => "extend",
			'hostids' => $id,
                        'sortfield' => "name"
                ),
                'id' => "2",
                'auth' => $authtoken
        );
        $response = json_request($uri, $data);
        return $response['result'];
}

//return alert
function zabbix_get_event($uri, $authtoken) {
        $data = array(
                'jsonrpc' => "2.0",
                'method' => "event.get",
                'params' => array(
                        'output' => "extend"
                ),
                'id' => "2",
                'auth' => $authtoken
        );
        $response = json_request($uri, $data);
        return $response['result'];
}

//return trigger
function zabbix_get_trigger($uri, $authtoken) {
        $data = array(
                'jsonrpc' => "2.0",
                'method' => "trigger.get",
                'params' => array(
                        'output' => "extend"
                ),
                'id' => "2",
                'auth' => $authtoken
        );
        $response = json_request($uri, $data);
        return $response['result'];
}


//display all the graph
function zabbix_print_all_graph($url, $result, $time) {
	foreach ($result as $item) {
        	$graphid =  $item['graphid'];
        	$width = $item['width'];
        	$height = $item['height'];
        	$p = $url."/chart2.php?graphid=".$graphid."&width=".$width."&height=".$height."&period=".$time;
        	echo "<img src=".$p.">";
	}
}

//display only a select graph
/**function zabbix_print_graph($url, $result, $graph, $time) {
        foreach ($result as $item) {
		if ($item['name'] == $graph) {
                	$graphid =  $item['graphid'];
                	$width = $item['width'];
                	$height = $item['height'];
                	$p = $url."/chart2.php?graphid=".$graphid."&width=".$width."&height=".$height."&period=".$time;
                	echo "<img src=".$p.">";
		}
        }
}**/


//count event number
function count_event($uri, $authtoken) {
	$result = zabbix_get_event($uri, $authtoken);
	$nb = 0;
	$total = 0;
	foreach ($result as $item) {
		$nb += (int)$item['value'];
		$total += 1;
	}
	echo "event : ".$nb."/".$total."<br>";
}





?>
