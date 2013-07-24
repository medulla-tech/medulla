<?php

if ($_SESSION["login"]=='root') {
    print "<p>"._("Root user cannot have favorites")."</p>";
    exit(0);
}

if ($_GET['lmodule']) {
    $local_uri=$_GET['lmodule'].'/'.$_GET['lsubmod'].'/'.$_GET['laction'];
} else {
    $local_uri= "base/main/default";
}

function getPage($uri) {
    list($modname,$subname,$actname) = explode('/',$uri,3);
    $MMCApp =& MMCApp::getInstance();

    $mod = $MMCApp->getModule($modname);
    if (!$mod) return;
    $submod = $mod->getSubmod($subname);
    if (!$submod) return;
    $page = $submod->getPage($actname);
    if (!$page) return;
    return $page;
}

function getPrefs($login) {
  $res = xmlCall("base.getPrefs",array($login));
  if ($res) {
    return unserialize($res);
  } else {
    return array();
  }
}

function setPrefs($login,$pref) {
  return xmlCall("base.setPrefs",array($login,serialize($pref)));
}

function listFavorites() {
    $prefs = getPrefs($_SESSION["login"]);
    if ($prefs['favorites']) {
        return array_keys($prefs['favorites']);
    } else {
        return array();
    }
}

function addFavorite($uri) {
    $prefs = getPrefs($_SESSION["login"]);
    $prefs['favorites'][$uri] = 1;
    setPrefs($_SESSION["login"],$prefs);
}

function delFavorite($uri) {
    $prefs = getPrefs($_SESSION["login"]);
    unset($prefs['favorites'][$uri]);
    setPrefs($_SESSION["login"],$prefs);
}

function showFav($sort_a) {

$MMCApp =& MMCApp::getInstance();


foreach(getSorted($MMCApp->getModules()) as $mkey => $mod) {
    if (!$sort_a[$mod->getName()]) {
        continue;
    }
    if ($mod->getName()==$_GET['lmodule']) {
        $style="_select";
    } else {
        $style="";
    }
    print "<div class=\"modulefav$style\"><h3>".$mod->getDescription()."</h3>";
    foreach($sort_a[$mod->getName()] as $key => $al) {
        $submod = $mod->getSubmod($key);
        if ($mod->getName()==$_GET['lmodule']) {
            if ($submod->getName()==$_GET['lsubmod']) {
                $style="_sselect";
            } else {
                $style="_select";
            }
        } else {
            $style="";
        }


        print "<div class=\"submodfav$style\"><h4>".$submod->getDescription()."</h4>";
        foreach($al as $akey => $value) {
            $uri = $mod->getName().'/'.$key.'/'.$akey;

            $getrecop = $_GET;
            $getrecop['fav_action']='del';

            $getrecop['uri']=$uri;
            ?> <span class="redbutton"><a href="#" onClick="jQuery('#__popup_container').load('<?php echo  urlStr('base/main/favorites',$getrecop); ?>'); return false">X</a></span> <?php



            $page = getPage($uri);
            if ($page) {
                print '<a href="'.urlStr($uri).'">'.$page->getDescription().'</a>';
            } else {
                print $uri;
            }
            ?>
            <br/>

        <?php
        }
    print '</div>';
    }
    print '</div>';
}
}


if  ($_GET['fav_action']=='add') {
    addFavorite($_GET['uri']);
}

if  ($_GET['fav_action']=='del') {
    delFavorite($_GET['uri']);
}


$sort_a;
foreach (listFavorites() as $uri) {
    list($m,$s,$a) = explode('/',$uri,3);
    $sort_a[$m][$s][$a]=1;
}

showFav($sort_a);


//add favorites link

$local_page = getPage($local_uri);

if ($local_page->isVisible()) {

    $_GET['fav_action']='add';

    $_GET['uri']=$local_uri;

    ?>

    <p><a href="#" onClick="jQuery('__popup_container').load('<?php echo  urlStr('base/main/favorites',$_GET); ?>'); return false"><?php echo  _("Add this page to your favorite") ?></a></p>
    <?php
}

?>