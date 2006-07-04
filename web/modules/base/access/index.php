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

require("modules/base/includes/groups.inc.php");
require("modules/base/includes/users.inc.php");
require("includes/conftool.inc.php");

function
sort_allowed($a, $b)
{
  $ag = preg_match("/^groupe = /", $a);
  $bg = preg_match("/^groupe = /", $b);

  if ($ag && !$bg)
    {
      return 1;
    }
  else if (!$ag && $bg)
    {
      return -1;
    }
  else
    {
      return strcmp($a, $b);
    }

}

?>

<style type="text/css">
<!--

<?php
require("modules/base/graph/access/index.css");
?>

#accesslist
{
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        padding: 10px 5px 5px 10px;
        margin: 0 5px 20px 0;
        width: 632px;
}

#accesslist div.list
{
        float: left;
}

select.list
{
        width: 300px;
}

#userlist
{
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        padding: 10px 10px 5px 10px;
        margin: 0 5px 20px 0;
        float: left;
        width: 300px;
}

#grouplist
{
        color: #666;
        background-color: #F0F4F7;
        border: solid 1px #CCC;
        padding: 10px 10px 5px 10px;
        margin: 0 5px 20px 0;
        float: left;
        width: 300px;
}

-->
</style>

<?php
$path = array(array("name" => "Accueil",
                    "link" => "main.php"),
              array("name" => "Droits d'acc�s",
                    "link" => "main.php?module=base&submod=access&action=index"),
              array("name" => "Gestion des droits d'acc�s"));

$sidebar = array("class" => "access",
                 "content" => array(array("id" => "global",
                                    "text" => "Gestion des droits d'acc�s",
                                    "link" => "main.php?module=base&submod=access&action=index")));

require("graph/navbar.inc.php");

$allowed = unserialize(base64_decode($_POST["allowed"]));
$denied = unserialize(base64_decode($_POST["denied"]));
$users = unserialize(base64_decode($_POST["lusers"]));
$groups = unserialize(base64_decode($_POST["lgroups"]));

if (isset($_POST["bdelallow"]))
{
  foreach ($_POST["allow"] as $user)
    {
      $idx = array_search($user, $allowed);
      if ($idx !== false)
	{
	  unset($allowed[$idx]);
	}
    }
}
else if (isset($_POST["bdeldeny"]))
{
  foreach ($_POST["deny"] as $user)
    {
      $idx = array_search($user, $denied);
      if ($idx !== false)
	{
	  unset($denied[$idx]);
	}
    }
}
else if (isset($_POST["ballowuser"]))
{
  foreach ($_POST["users"] as $user)
    {
      if (is_array($denied))
        {
          $idx = array_search($user, $denied);
          if ($idx !== false)
	    {
	      unset($denied[$idx]);
	    }
        }
      if (array_search($user, $allowed) === false)
	{
	  $allowed[] = $user;
	}
    }

  usort($allowed, "sort_allowed");
  reset($allowed);
}
else if (isset($_POST["bdenyuser"]))
{
  foreach ($_POST["users"] as $user)
    {
      $idx = array_search($user, $allowed);
      if ($idx !== false)
	{
	  unset($allowed[$idx]);
	}

      if ((array_search($user, $denied) === false) || !$denied)
	{
	  $denied[] = $user;
	}
    }

  sort($denied);
  reset($denied);
}
else if (isset($_POST["ballowgroup"]))
{
  foreach ($_POST["groups"] as $group)
    {
      if (array_search("groupe = ".$group, $allowed) === false)
	{
	  $allowed[] = "groupe = ".$group;
	}
    }

  usort($allowed, "sort_allowed");
  reset($allowed);
}
else if (isset($_POST["bconfirm"]))
{
  $conf["deny"] = $denied;
  $conf["allow"] = array();
  $conf["allow"] = array();

  foreach ($allowed as $item)
    {
      if (preg_match("/^groupe = (.+)/", $item, $match))
	{
	  $conf["allow"]["group"][] = $match[1];
	}
      else
	{
	  $conf["allow"]["user"][] = $item;
	}
    }

  $result = dump_conf_php();
  $result = dump_conf();
}
else // breset
{
    foreach ($conf["allow"] as $key=>$value) {
        $allowed[]=$key;
    }
    
  //$allowed = $conf["allow"];
    foreach ($conf["denied"] as $key=>$value) {
        $denied[]=$key;
    }
  
  $users = get_users($error);
  $groups = get_groups($error);
}

?>


<h2>Gestion des droits d&#039;acc�s</h2>

<div class="fixheight"></div>

<form action="<? echo $PHP_SELF; ?>" method="post">

<div id="accesslist">

  <div class="list">
    <h3>Accés autorisé</h3>
    <select multiple size="7" class="list" name="allow[]">
<?php
foreach ($allowed as $item)
{
  echo "<option value=\"".$item."\">".$item."</option>\n";
}
?>
    </select>
    <br>
    <input type="submit" class="btnPrimary" name="bdelallow" value="Supprimer" />
  </div>

  <div class="list" style="padding-left: 24px;">
    <h3>Accés interdit</h3>
    <select multiple size="7" class="list" name="deny[]">
<?php
foreach ($denied as $item)
{
  echo "<option value=\"".$item."\">".$item."</option>\n";
}
?>
    </select>
    <br>
    <input type="submit" class="btnPrimary" name="bdeldeny" value="Supprimer" />
  </div>

  <div class="clearer"></div>

</div>




<div id="userlist">
  <h3>Utilisateurs</h3>
  <select multiple size="7" class="list" name="users[]">
<?php
foreach ($users as $item)
{
  echo "<option value=\"".$item."\">".$item."</option>\n";
}
?>
  </select>
  <br>
  <input type="submit" class="btnPrimary" name="ballowuser" value="Autoriser" />
  <input type="submit" class="btnSecondary" name="bdenyuser" value="Interdire" onSubmit="return do_test('users')"/>
</div>

<div id="grouplist">
  <h3>Groupes</h3>
  <select multiple size="7" class="list" name="groups[]">
<?php
foreach ($groups as $item)
{
  echo "<option value=\"".$item."\">".$item."</option>\n";
}
?>
  </select>
  <br>
  <input type="submit" class="btnPrimary" name="ballowgroup" value="Autoriser" />
</div>

<div class="clearer"></div>

<input type="hidden" name="allowed" value="<?php echo base64_encode(serialize($allowed)); ?>" />
<input type="hidden" name="denied" value="<?php echo base64_encode(serialize($denied)); ?>" />
<input type="hidden" name="lusers" value="<?php echo base64_encode(serialize($users)); ?>" />
<input type="hidden" name="lgroups" value="<?php echo base64_encode(serialize($groups)); ?>" />

<input type="submit" class="btnPrimary" name="bconfirm" value="Valider" />
<input type="submit" class="btnSecondary" name="breset" value="Annuler" />
<?php
if (isset($_POST["bconfirm"]))
{
  if ($result)
  {
    echo "Configuration sauvegard�e";
  }
  else
  {
    echo "Erreur lors de la sauvegarde";
  }
}
?>
</form>
