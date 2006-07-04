<?

require("config.inc.php");

require("acl.inc.php");
require("session.inc.php");
require("PageGenerator.php");


function
print_mem_bar($title, $max, $used, $cache = 0, $width = 400)
{
  $wused = ($used / $max) * $width;

  if ($title != "")
    {
      echo $title." :";
    }
  echo "<div class=\"membarfree\" style=\"width: ".$width."px\">";
  if ($cache > 0)
    {
      printf("<div class=\"membarcache\" style=\"width: %.0fpx\">", $wused);
      $wused = (($used - $cache) / $max) * $width;
    }
  printf("<div class=\"membarused\" style=\"width: %.0fpx\"></div>", $wused);

  if ($cache > 0)
    {
      echo "</div>";
    }
  echo "</div>\n";
}

    function get_process()
    {
        return xmlCall("base.listProcess",null);
    }

    $arr = get_process();

    if (count($arr) == 0) { //if no job in background
        print '<div style="text-align: center;">'._T("No job.".'</div>');
        return;
    }

    foreach ($arr as $ps) {
        echo $ps[0]."<br/>";
        echo $ps[2]."<br/>";
        if ($ps[1] != "-1") {
            print_mem_bar("progress",100,$ps[1]);
        }
    }

?>