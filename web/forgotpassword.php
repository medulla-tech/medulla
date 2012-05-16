<?php

session_start();
require("includes/config.inc.php");
require("modules/base/includes/users.inc.php");
require("includes/PageGenerator.php");

global $conf;
$root = $conf["global"]["root"];
$server = $_GET["server"];
$lang = $_GET["lang"];

$_SESSION["XMLRPC_agent"] = parse_url($conf[$server]["url"]);
$_SESSION["agent"] = $server;
$_SESSION["XMLRPC_server_description"] = $conf[$server]["description"];

if (isset($_POST['bBack']))
    header("Location: " . $root);

if (isset($_POST['bReset']) && isset($_POST['user'])) {
    if (xmlCall("base.createAuthToken", array($_POST['user'], $server, $lang)))
        $info = _("A password reset link has been sent.");
    else
        $error = _("Can't reset your password. Please contact your administrator.");
}

?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
<head>
	<title>Mandriva Linux / Mandriva Management Console / Reset Password</title>
	<link href="<?php echo $root; ?>graph/login/index.css" rel="stylesheet" media="screen" type="text/css" />
	<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
	<meta http-equiv="imagetoolbar" content="false" />
	<meta name="Description" content="" />
	<meta name="Keywords" content="" />
	<link rel="icon" href="img/common/favicon.ico" />
        <script src="jsframework/lib/prototype.js" type="text/javascript"></script>
        <script src="jsframework/src/scriptaculous.js" type="text/javascript"></script>
</head>
<body onload="Form.focusFirstElement('lostPasswordForm')">

<table width="100%" height="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td align="center">
	<table width="467" border="0" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center" valign="middle">

        <div id="header">
        <div id="headerLeft"><div id="headerRight">
            <p class="lock"></p>
        </div></div></div>

        <div id="interface">
        <div id="content">
        <?php
        if (isset($error)) {
            echo '<div id="alert">' . $error . '</div>';
        }
        if (isset($info)) {
            echo '<div id="info">' . $info . '</div>';
        }
        ?>
        <div id="login">

            <img src="<?php echo $root; ?>img/login/logo_mandriva_small.png" alt="">

            <form action="<?php echo $root; ?>forgotpassword.php?server=<?=$server?>&lang=<?=$lang?>" method="post" name="lostPasswordForm" id="lostPasswordForm" target="_self">

                <p><strong><?= _("Password reset") ?></strong></p>

                <p><?php echo  _("Login or mail"); ?> :<br>
                    <input name="user" type="text" class="textfield" id="username" size="18" />
                </p>
                <p>
                    <input name="bReset" type="submit" class="btnPrimary" value="<?php echo  _("Password reset"); ?>" />
                    <input name="bBack" type="submit" class="btnSecondary" value="<?php echo  _("Back"); ?>" />
                </p>

            </form>

        </div> <!-- login -->
        </div> <!-- content -->
        </div> <!-- interface -->
        <div id="footer">
        <div id="footerLeft"><div id="footerRight">
        </div></div></div>
  		</td>
      </tr>
    </table>
	</td>
  </tr>
<?php

if (isCommunityVersion() && is_file("license.php")) {
    require("license.php");
}

?>
</table>
</div>

</body>
</html>
