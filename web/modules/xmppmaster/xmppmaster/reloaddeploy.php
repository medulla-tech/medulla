<?php
// file /mmc/modules/xmppmaster/xmppmaster/reloaddeploy.php
/*
echo '<pre>';
echo '$_GET<br>';
print_r($_GET);
echo '$_POST<br>';
print_r($_POST);
echo '</pre>';*/
    // appelle la procedure stockee pour relancer les deployements.
    if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
        http_response_code(405);
        exit;
    }

    verifyCSRFToken($_POST);
    extract($_POST);

    if (isset($gr_cmd_id)){ $cmd_id=$gr_cmd_id;}else{unset($sessionid);}


    xmlrpc_reload_deploy(   $uuid,
                            $cmd_id,
                            $gid,
                            $sessionid,
                            $hostname,
                            $login,
                            $title,
                            $start,
                            $endcmd,
                            $startcmd,
                            $force_redeploy=isset($force)?1:0,
                            $rechedule=isset($reschedule)?1:0);

    header("location: ".urlStrRedirect($_GET['module'].'/'.$_GET['submod'].'/index'));
?>
