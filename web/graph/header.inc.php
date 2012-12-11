<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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
 */

$root = $conf["global"]["root"];

?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Mandriva Management Console</title>
    <link href="graph/master.css" rel="stylesheet" media="screen" type="text/css" />
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
        if ($('loadimg'))
            $('loadimg').src = "<?php echo $root; ?>img/common/loader_p.gif";
    },
    onComplete: function() {
        if(Ajax.activeRequestCount == 0 && $('loadimg')) {
            $('loadimg').src = "<?php echo $root; ?>img/common/loader.gif";
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
    $('overlay').show();
    $('overlay').observe("click", function () {
        closePopup();
    });
}

function displayConfirmationPopup(message, url_yes, url_no, klass) {
    if (!klass)
        var klass = '';
    var message = '<div style="padding: 10px"><div class="alert ' + klass + '">' + message + '</div>';
    message += '<div style="text-align: center"><a class="btn btn-primary" href="' + url_yes + '"><?=_('Yes')?></a>';

    if (url_no)
        message += ' <a class="btn" href="' + url_no + '"><?=_('No')?></a>';
    else
        message += ' <button class="btn" onclick="closePopup(); return false;"><?=_('No')?></button>';

    message += '</div></div>';

    try {
        $('__popup_container').update(message);
    }
    catch(ex) {
        $('__popup_container').innerHTML = message;
    }

    displayPopupCenter();
}

function closePopup() {
    $('popup').hide();
    $('overlay').hide();
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

<?php
if (isset($_SESSION['servicesInfos'])) {
?>
function restartServices() {

    services = JSON.parse('<?=$_SESSION['servicesInfos']?>');

    checkService = function(service) {
        new Ajax.Request(service.check, {
            onSuccess: function(r) {
                var statusElem = $(service.id + 'Status');
                if (r.responseJSON) {
                    var status = r.responseJSON[1];
                    if (status != "active" && status != "failed") {
                        setTimeout(function() {
                            checkService(service);
                        }, 800);
                    }
                    else {
                        if (status == "failed") {
                            statusElem.update(service.msg_fail);
                            statusElem.removeClassName("alert-info");
                            statusElem.addClassName("alert-error");
                        }
                        else {
                            statusElem.update(service.msg_success);
                            statusElem.removeClassName("alert-info");
                            statusElem.addClassName("alert-success");
                        }
                    }
                }
                else {
                    statusElem.update(service.msg_fail);
                    statusElem.removeClassName("alert-info");
                    statusElem.addClassName("alert-error");
                    r.responseText.evalScripts();
                }

            }
        });
    };

    services.each(function(service) {
        new Ajax.Request(service.restart, {
            onSuccess: function() {
                var message = $(service.id + 'Status');
                if (!message) {
                    message = new Element('p', {'id': service.id + 'Status',
                                                'class': 'alert alert-info'});
                    $('restartStatus').appendChild(message);
                }
                message.update(service.msg_exec);
                message.removeClassName("alert-success");
                message.removeClassName("alert-error");
                message.addClassName("alert-info");
                $('restartStatus').show();
                setTimeout(function() {
                    checkService(service);
                }, 1000);
            }
        });
    });
}
<?php
}
?>

-->
</script>
