<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
 *
 * $Id$
 *
 */

$root = $conf["global"]["root"];
$css = $root."graph";

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Mandriva Management Console</title>
    <link href="<?php echo $css; ?>/master.css" rel="stylesheet" media="screen" type="text/css" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta http-equiv="imagetoolbar" content="false" />
    <meta name="Description" content="" />
    <meta name="Keywords" content="" />
    <link rel="icon" href="img/common/favicon.ico" />
    <script src="jsframework/lib/prototype.js" type="text/javascript"></script>
    <script src="jsframework/src/scriptaculous.js" type="text/javascript"></script>
    <script src="jsframework/common.js" type="text/javascript"></script>
<?php
unset($css);
?>
<script type="text/javascript">

<!--

var myglobalHandlers = {
    onCreate : function() {
        document.getElementById('loadimg').src = "<?php echo $root; ?>img/common/loader_p.gif"
    },
    onComplete: function() {
            if(Ajax.activeRequestCount== 0) {
                document.getElementById('loadimg').src = "<?php echo $root; ?>img/common/loader.gif"
            }
        }
    };

    Ajax.Responders.register(myglobalHandlers);



// pf="prefix" and ck="checked" (0|1)
function checkAll (pf,ck) {
cbox=document.getElementsByTagName('INPUT');
  for (i=0; i<cbox.length; i++){
    if (cbox[i].type=='checkbox'){
      if (cbox[i].name.indexOf(pf) > -1) {
        if (ck == "1") { cbox[i].checked = true; } else { cbox[i].checked = null; }
      }
    }
  }
}

// pf="prefix" and value can be (null, ro, rw)
function checkAllRadio (pf,value) {
    rbox=document.getElementsByTagName('INPUT');
    for (i=0; i<rbox.length; i++){
        if (rbox[i].type=='radio'){
            if (rbox[i].name.indexOf(pf) > -1) {
                if (value == rbox[i].value) { 
                    rbox[i].checked = true;
                } 
                else { 
                    rbox[i].checked = false;
                }
            }
        }
    }
}

// select all select with class 'list' options in the page
// usefull to run before post a form with
// selects in it.
function selectAll(formId) {
    $$("#" + formId + " select.list option").each(function(e) {
        e.selected = true;
    });
}

function getStyleObject(objectId) {
    // cross-browser function to get an object's style object given its id
    if(document.getElementById && document.getElementById(objectId)) {
    // W3C DOM
    return document.getElementById(objectId).style;
    } else if (document.all && document.all(objectId)) {
    // MSIE 4 DOM
    return document.all(objectId).style;
    } else if (document.layers && document.layers[objectId]) {
    // NN 4 DOM.. note: this won't find nested layers
    return document.layers[objectId];
    } else {
    return false;
    }
} // getStyleObject

function changeObjectDisplay(objectId, newVisibility) {
    // get a reference to the cross-browser style object and make sure the object exists
    var styleObject = getStyleObject(objectId);
    if(styleObject) {
    styleObject.display = newVisibility;
    return true;
    } else {
    // we couldn't find the object, so we can't change its visibility
    return false;
    }
} // changeObjectVisibility


function toggleVisibility(layer_ref)
{
    var state = getStyleObject(layer_ref).display;
    if (state == 'none') {
        state = 'inline';
    } else {
        state = 'none';
    }
    changeObjectDisplay(layer_ref, state)
}

function PopupWindow(evt, url, width) {
    $('popup').style.width = width + "px";
    if (!evt) evt = window.event;
    new Ajax.Updater('__popup_container', url, { onComplete: PopupWindowDisplay(evt, width), evalScripts:true});
}

function PopupWindowDisplay(evt, width) {
    obj = document.getElementById('popup');
    obj.style.left = parseInt(evt.clientX) + document.documentElement.scrollLeft - parseInt(width) + "px";
    obj.style.top = (parseInt(evt.clientY) + document.documentElement.scrollTop) + "px";
    getStyleObject('popup').display = 'inline';
}

function showPopup(evt, url) {
    $('popup').style.width = '300px';
    /*new Ajax.Updater('__popup_container', url, {onComplete: displayPopup(evt), evalScripts:true});*/
    new Ajax.Request(url, {
        onSuccess: function(t) {
            try {
                $('__popup_container').update(t.responseText);
            }
            catch(ex) {
                $('__popup_container').innerHTML = t.responseText;
            }
        },
        onComplete: displayPopup(evt)
    });
}

function showPopupFav(evt,url) {
    $('popup').style.width = '200px';
    /*new Ajax.Updater('__popup_container',url,{onComplete: displayPopupFav(evt), evalScripts:true});*/
    new Ajax.Request(url, {
        onSuccess: function(t) {
            try {
                $('__popup_container').update(t.responseText);
            }
            catch(ex) {
                $('__popup_container').innerHTML = t.responseText;
            }
        },
        onComplete: displayPopupFav(evt)
    });
}


function showPopupUp(evt,url) {
    $('popup').style.width = '300px';
    /*new Ajax.Updater('__popup_container',url,{onComplete: displayPopupUp(evt), evalScripts:true});*/
    new Ajax.Request(url, {
        onSuccess: function(t) {
            try {
                $('__popup_container').update(t.responseText);
            }
            catch(ex) {
                $('__popup_container').innerHTML = t.responseText;
            }
        },
        onComplete: displayPopupUp(evt)
    });
}

function showPopupCenter(url) {
    /*new Ajax.Updater('__popup_container',url,{onComplete: displayPopupCenter(), evalScripts:true});*/
    new Ajax.Request(url, {
        onSuccess: function(t) {
            try {
                $('__popup_container').update(t.responseText);
            }
            catch(ex) {
                $('__popup_container').innerHTML = t.responseText;
            }
        },
        onComplete: displayPopupCenter()
    });    
}

function displayPopupFav (evt) {
    if (!evt) evt = window.event;
    obj = document.getElementById('popup');
    obj.style.left = parseInt(evt.clientX)+document.documentElement.scrollLeft-100+"px";
    obj.style.top = (parseInt(evt.clientY)+document.documentElement.scrollTop)+"px";
    getStyleObject('popup').display='inline';
}

function displayPopup (evt) {
    if (!evt) evt = window.event;
    obj = document.getElementById('popup');
    obj.style.left = parseInt(evt.clientX)+document.documentElement.scrollLeft-300+"px";
    obj.style.top = (parseInt(evt.clientY)+document.documentElement.scrollTop)+"px";
    getStyleObject('popup').display='inline';
}

function displayPopupUp (evt) {
    if (!evt) evt = window.event;
    $('popup').style.left = parseInt(evt.clientX)+document.documentElement.scrollLeft+"px";
    $('popup').style.top = (parseInt(evt.clientY)+document.documentElement.scrollTop-350)+"px";
    $('popup').style.display = 'inline';
}

function displayPopupCenter () {
    $('popup').style.width = '50%';
    $('popup').style.left = '25%';
    $('popup').style.top  = '15%';
    $('popup').style.display = 'inline';
}

function validateForm(formId) {
    var resultok;
    resultok = 0;
    var resultbad;
    resultbad = 0;
    var inputlist;
    $$('#' + formId + ' input').each(
        function(input) {
            try {
                var result = input.validate()
                    if (result!=true) {
                        resultbad++;
                    } else {
                        resultok++;
                    }
            }
            catch (ex) {
                //do nothing... function not exist
            }
        }
    );
    if (resultbad!=0) {
        alert('<?php echo  _("Form cannot be submit. Input errors are highlighted in red.") ?>');
        return false;
    } else {
        return true;
    }
    return false;
}

-->

</script>
