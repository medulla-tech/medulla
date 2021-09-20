<?php
require_once("modules/pkgs/includes/xmlrpc.php");
//header("Content-type: ".$_GET['mime']);

$page = new PageGenerator(_T("Content for file ", "pkgs").'['.$_GET['name'].']');
//$page->setSideMenu($sidemenu);
$page->display();


$content = xmlrpc_get_files_infos($_GET['uuid'], $_GET['name']);
$content = htmlspecialchars(base64_decode($content['content']));

$match = preg_match_all("#\r?\n#", $content);
echo 'new line : '.$match.'<br>';
echo '<div style="display:flex">';
echo '<label for="nlmode">'._T("NL mode (unix)", "pkgs").'</label><input type="radio" id="nlmode" name="lfmode" value="ln" checked/>';
echo '<label for="crlfmode">'._T("CRLF mode (win)", "pkgs").'</label><input type="radio" id="crlfmode" name="lfmode" value="crln"/>';
echo '</div>';

echo '<pre style="max-height:40vh;overflow-y:scroll">';
echo '<object id="filecontainer">';
echo '</object>';
echo '</pre>';
?>

<script>
jQuery(function(){
  let phpcontent = <?php echo json_encode($content);?>;

  transform = function(mode, content=""){
    regex = new RegExp("\r?\n", 'gmi');
    //console.log(content.search(regex));
    if(mode == "ln"){
      phpcontent.replace(regex, '\n');
    }
    else if(mode == "crlf"){
      phpcontent.replace(regex, '\r\n');
    }

    jQuery("#filecontainer").html(phpcontent);
  }


  // When initialized : do 1 time the check with the selected value
  transform(jQuery("input[name='lfmode']").val(), phpcontent);

  jQuery("input[name='lfmode']").on("click change focus", function(){
    transform(jQuery(this).val(), phpcontent);
  })

})


</script>
