<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php
/* $Id$ */

ob_start();

require("includes/config.inc.php");

require("modules/base/includes/users.inc.php");
require("modules/base/includes/edit.inc.php");
require("modules/base/includes/groups.inc.php");
require("includes/i18n.inc.php");
require("includes/PageGenerator.php");


$root = $conf["global"]["root"];

function auth_user ($login, $pass, $error)
{
  global $conf;
  global $error;

  if (($login == "") || (!preg_match("/^[a-zA-Z][.a-zA-Z0-9]*$/", $login)) || ($pass == ""))
    {
      return false;
    }

  $param[]=$login;
  $param[]=$pass;

  //put server selected in $_SESSION
  $urlArr=parse_url($_POST["server"]);
  $_SESSION["XMLRPC_agent"] = $urlArr;

  $ret= xmlCall("base.ldapAuth",$param);

  if ($ret!="1") // erreur
    {
          if (!isXMLRPCError()) {
	       $error = _T("Invalid login");
          }
	  return false;
    }

  return true;
}


if (isset($_POST["bConnect"]))
{
  $login = $_POST["username"];
  $pass = $_POST["password"];

  /* Suivre le goto si existant ... */
  if (isset($_POST["goto"]))
  {
    $goto = $_POST["goto"];
  }
  else
  {
    $goto = $root."main.php";
  }

  if (auth_user($login, $pass, $error))
    {
      /* créer la session */
      $ip = ereg_replace('\.','',$_SERVER["REMOTE_ADDR"]);
      $sessionid = md5 (time() . $ip . mt_rand());

      session_id($sessionid);
      session_start();
      $_SESSION["ip_addr"] = $_SERVER["REMOTE_ADDR"];
      $_SESSION["login"] = $login;
      /* stock� pour les opérations à venir... */
      $_SESSION["pass"] = $pass;
      /* expiration de la session : 90 minutes */
      $_SESSION["expire"] = time() + 90 * 60;

      $_SESSION['lang']=$_POST['lang'];
      setcookie('lang',$_POST['lang'],time()+3600*24*30);


      $urlArr=parse_url($_POST["server"]);
      $_SESSION["XMLRPC_agent"] = $urlArr;
      $tmp = createAclArray(getAcl($login));
      /*print "<pre>";
      print_r($tmp);
      print "</pre>";*/
      $_SESSION["acl"] = $tmp["acl"];
      $_SESSION["aclattr"] = $tmp["aclattr"];
      $_SESSION["supportModList"] = xmlCall("base.getModList",null);


      //register version
      $_SESSION["modListVersion"]['rev'] =  xmlCall("getRevision",null);
      $_SESSION["modListVersion"]['ver'] =  xmlCall("getVersion",null);

      /* Redirection vers $goto */


      header("Location: ".$goto);
      exit;
    }
  else
    {
      if (!isXMLRPCError()) {
        $error = _("incorrect ID");
      }
    }

}

if ($_GET['error']) {
    $error= urldecode($_GET['error'])."<br/>".$error;
}

?>

<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">

<html>
<head>
	<title>Linbox-Free&ALter Soft</title>
	<link href="<?php echo $root; ?>graph/login/index.css" rel="stylesheet" media="screen" type="text/css" />
	<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1" />
	<meta http-equiv="imagetoolbar" content="false" />
	<meta name="Description" content="" />
	<meta name="Keywords" content="" />

</head>
<body>

<table width="100%" height="100%" border="0" cellpadding="0" cellspacing="0">
  <tr>
    <td align="center">
	<table width="467" border="0" cellpadding="0" cellspacing="0">
      <tr>
        <td align="center" valign="middle">

        <div id="header">
        <div id="headerLeft"><div id="headerRight">

<!-- Contenu du header ici (mettre dans un <p>) -->

        <p class="lock"></p>

        </div></div></div>

        <div id="interface">
        <div id="content">

<?php


$n = new NotifyWidget();
//


if (isset($_SESSION['__notify'])) {
    foreach ($_SESSION['__notify'] as $err){ //add notify widget error
        $error = $error . $err.'<br/>';
    }

    $n->flush();
}


if (isset($error))
{
  echo "<div id=\"alert\">".$error."</div>\n";
}
?>

        <div id="login">

<!-- Contenu login -->

        <img src="<?php echo $root; ?>img/login/logo_linboxfas_small.gif" alt="" width="131" height="32">

		<form action="<?php echo $root; ?>index.php" method="post" name="loginForm" target="_self">

<?php
/* Transmission du goto en POST */
if (isset($_GET["goto"]))
{
  $goto = $_GET["goto"];
}

/* peut-�tre d�j� initalis�, si pass� en POST */
if (isset($goto))
{
  echo "<input name=\"goto\" type=\"hidden\" value=\"$goto\" />\n";
}

?>
			<p><?= _("Login");?> :<br>
			<input name="username" type="text" class="textfield" id="username" size="18"
<?php
			echo "value=\"$login\"";
?>
			/>
			</p>

			<p><?= _("Password");?><br>
			<input name="password" type="password" class="textfield" id="password" size="18">
			</p>

                        <p> <?= _("Server");?> : <br>
			<?php

                        global $conf;


                        $servList = array();

                        foreach ($conf as $key => $value) {
                          if (strstr($key,"server")) {
                            $descList[$key]=$conf[$key]["description"];
                            $urlList[$key]=$conf[$key]["url"];
                          }
                        }

                        $listbox = new SelectItem("server");

                        $listbox->setElements($descList);
                        $listbox->setElementsVal($urlList);
                        $listbox->setSelected($descList[0]);
                        $listbox->display();

                        ?>
                        <br/>
                        <?= _("Language");?>: <br />

                        <?php

                        $langList = list_system_locales(realpath("modules/base/locale/"));

                        $descList = array();
                        $urlList = array();

                        $langDesc = getArrLocale();

                        foreach ($langList as $value) {
                            if ($langDesc[$value]) {
                                $descList[]=$langDesc[$value];
                            } else {
                                $descList[]=$value;
                            }
                            $urlList[]=$value;
                        }

                        $listbox = new SelectItem("lang");

                        $listbox->setElements($descList);
                        $listbox->setElementsVal($urlList);
                        $listbox->setSelected($descList[0]);
                        if ($_COOKIE['lang']) {
                            $listbox->setSelected($langDesc[$_COOKIE['lang']]);
                        }
                        $listbox->display();

                        ?>

			<input name="bConnect" type="submit" class="btnPrimary" value="<?= _("Connect");?>" /></p>

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
</table>

</div>
</body>
</html>
<?
ob_end_flush();
?>
