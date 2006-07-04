/**
 * local var to know how keys pressed (prevend ajax request on each keydown)
 */
var launch = 0;

   function url_encode(str) {
        var hex_chars = "0123456789ABCDEF";
        var noEncode = /^([a-zA-Z0-9\_\-\.])$/;
        var n, strCode, hex1, hex2, strEncode = "";

        for(n = 0; n < str.length; n++) {
            if (noEncode.test(str.charAt(n))) {
                strEncode += str.charAt(n);
            } else {
                strCode = str.charCodeAt(n);
                hex1 = hex_chars.charAt(Math.floor(strCode / 16));
                hex2 = hex_chars.charAt(strCode % 16);
                strEncode += "%" + (hex1 + hex2);
            }
        }
        return strEncode;
    }


/**
 * update group div via ajax request
 */
function updateSearchGroup() {
    launch--;

        if (launch==0) {
            new Ajax.Updater('groupContainer','main.php?module=base&submod=groups&action=ajaxFilter&filter='+document.groupForm.param.value, { asynchronous:true, evalScripts: true});
        }
    }


/**
 * provide navigation in ajax for group
 */

function updateSearchGroupParam(filter, start, end) {
       new Ajax.Updater('groupContainer','main.php?module=base&submod=groups&action=ajaxFilter&filter='+filter+'&start='+start+'&end='+end, { asynchronous:true, evalScripts: true});
    }


/**
 * wait 500ms and update search
 * prevent ajax request on each keydown
 */
function pushSearchGroup() {
    launch++;
    setTimeout("updateSearchGroup()",500);
}


/**
 * update div with user
 */
function updateSearchUser() {
    launch--;

        if (launch==0) {
            new Ajax.Updater('userContainer','main.php?module=base&submod=users&action=ajaxFilter&filter='+document.userForm.param.value, { asynchronous:true, evalScripts: true});
        }
    }

/**
 * provide navigation in ajax for user
 */

function updateSearchUserParam(filter, start, end) {
       new Ajax.Updater('userContainer','main.php?module=base&submod=users&action=ajaxFilter&filter='+filter+'&start='+start+'&end='+end, { asynchronous:true, evalScripts: true});
    }

/**
 * wait 500ms and update search
 */

function pushSearchUser() {
    launch++;
    setTimeout("updateSearchUser()",500);
}