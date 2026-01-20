<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 * (c) 2021 Siveo, http://siveo.net
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
 */
?>
<?php

global $conf;

ob_start();

require("includes/assert.inc.php");
require("includes/session.inc.php");
require("includes/config.inc.php");
require_once("includes/i18n.inc.php");
require("includes/acl.inc.php");
require_once("includes/utils.inc.php");
require("includes/PageGenerator.php");
require("modules/base/includes/edit.inc.php");

/**
  Lookup and load all MMC modules
 */
function autoInclude()
{
    global $redirArray;
    global $redirAjaxArray;
    global $conf;
    global $filter;

    $modules = fetchModulesList($conf["global"]["rootfsmodules"]);
    includeInfoPackage($modules);
    includePublicFunc($modules);

    if (isset($_GET["module"])) {
        $__module = $_GET["module"];
    } else {
        $__module = "default";
    }

    if (isset($_GET["submod"])) {
        $__submod = $_GET["submod"];
    } else {
        $__submod = "default";
    }

    if (isset($_GET["action"])) {
        $__action = $_GET["action"];
    } else {
        $__action = "default";
    }

    /* Check filter info */
    // we must be in a ajax call
    if (isset($_SERVER['HTTP_X_REQUESTED_WITH']) and
            $_SERVER['HTTP_X_REQUESTED_WITH'] == "XMLHttpRequest" and
            isset($_GET['filter'])) {
        // get the page who called us
        preg_match('/module=([^&]+)/', $_SERVER["HTTP_REFERER"], $matches);
        if (isset($matches[1])) {
            $module = $matches[1];
        } else {
            $module = "default";
        }
        preg_match('/submod=([^&]+)/', $_SERVER["HTTP_REFERER"], $matches);
        if (isset($matches[1])) {
            $submod = $matches[1];
        } else {
            $submod = "default";
        }
        preg_match('/action=([^&]+)/', $_SERVER["HTTP_REFERER"], $matches);
        if (isset($matches[1])) {
            $action = $matches[1];
        } else {
            $action = "default";
        }
        preg_match('/tab=([^&]+)/', $_SERVER["HTTP_REFERER"], $matches);
        if (isset($matches[1])) {
            $tab = $matches[1];
        } else {
            $tab = "default";
        }

        // extra arguments of the request so we don't cache filters for another
        // page
        $extra = "";
        foreach ($_GET as $key => $value) {
            if (!in_array($key, array('module', 'submod', 'tab', 'action', 'filter', 'start', 'end', 'maxperpage'))) {
                $extra .= $key . "_" . $value;
            }
        }
        // store the filter
        if (isset($_GET['filter'])) {
            $_SESSION[$module . "_" . $submod . "_" . $action . "_" . $tab . "_filter_" . $extra] = $_GET['filter'];
        }
        // store pagination info
        if (isset($_GET['maxperpage'])) {
            $_SESSION[$module . "_" . $submod . "_" . $action . "_" . $tab . "_max_" . $extra] = $_GET['maxperpage'];
        }
        if (isset($_GET['start'])) {
            $_SESSION[$module . "_" . $submod . "_" . $action . "_" . $tab . "_start_" . $extra] = $_GET['start'];
        }
        if (isset($_GET['end'])) {
            $_SESSION[$module . "_" . $submod . "_" . $action . "_" . $tab . "_end_" . $extra] = $_GET['end'];
        }

        unset($module);
        unset($submod);
        unset($action);
        unset($tab);
    }

    /* Redirect user to a default page. */
    if (!isset($redirArray[$__module][$__submod][$__action]) && !isset($redirAjaxArray[$__module][$__submod][$__action])
    ) {
        header("Location: " . getDefaultPage());
        exit;
    }

    if (!isNoHeader($__module, $__submod, $__action)) {
        require_once("graph/header.inc.php");
        /* Include specific module CSS if there is one */
        require("graph/dynamicCss.php");
    }

    /* ACL check */
    if (!hasCorrectAcl($__module, $__submod, $__action)) {
        header("Location: " . getDefaultPage());
        exit;
    }

    /* Warn user once at login if her account is expired. */
    if (in_array("ppolicy", $_SESSION["supportModList"])) {
        require_once("modules/ppolicy/default/warnuser.php");
    }

    if (!empty($redirArray[$__module][$__submod][$__action])) {
        require($redirArray[$__module][$__submod][$__action]);
    //debug($redirArray[$__module][$__submod][$__action]);
    } elseif (!empty($redirAjaxArray[$__module][$__submod][$__action])) {
        require($redirAjaxArray[$__module][$__submod][$__action]);
    }

    require_once("includes/check_notify.inc.php");

    if (!isNoHeader($__module, $__submod, $__action)) {
        require_once("graph/footer.inc.php");
    }
}

global $maxperpage;
$root = $conf["global"]["root"];
$maxperpage = $conf["global"]["maxperpage"];

autoInclude();

//debug(get_included_files());

if (strlen(ob_get_contents())) {
    ob_end_flush();
}
?>

<script>
// Timer global
let moduleActionTimer = null;
// Variables globales pour le timer
let urlGlobal = null;
let paramsGlobal = null;

let intervalId = null;
// Variables globales
let GLOBAL_PARAMS = null;
let GLOBAL_URL = null;

let GLOBAL_ON_FRAME = false;
// Timer global
let statepresence = null;
let ws = null;            // Connexion WebSocket globale
let isReading = false;    // Contrôle du switch ON/OFF
let readInterval = null;  // Intervalle pour lecture régulière
let currentAction = null; // Action actuelle
let currentCn = null;     // CN actuel

function getTimeStamp() {
    const now = new Date();
    return now.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

function getMachineInfo(param) {
    // Vérifie que les propriétés existent (même si elles sont falsy)
    if (param?.cn === undefined || param?.os === undefined || param?.entity === undefined) {
        return null;
    }
    return `${param.cn} ${param.os} (${param.entity})`;
}

function callModuleAction(url, param, messagepresence = 0) {
    // appel le script logview par ajax
    // 1. Extraire les paramètres de l'URL
    var queryString = url.split('?')[1];
    if (!queryString) {
        const timeStamp = getTimeStamp();
        console.error(`[${timeStamp}] URL invalide : aucun paramètre trouvé.`);
        return;
    }
    // console.log(param);

    var params = new URLSearchParams(queryString);
    var action = params.get('action');
    var module = params.get('module');
    var submod = params.get('submod');
    if (!action || !module || !submod) {
        const timeStamp = getTimeStamp();
        console.error(`[${timeStamp}] Paramètres manquants dans l'URL : action, module ou submod.`);
        return;
    }

    // 2. Construire le chemin du fichier PHP
    var phpFile = "./modules/" + module + "/" + submod + "/" + action + ".php";

    // 3. Appel AJAX avec jQuery
    jQuery.ajax({
        url: phpFile,
        type: 'GET',
        data: param,
        dataType: 'text',
        success: function(response) {
            // console.log("Résultat de l'appel AJAX :", response);
            // if (response === "1") {
            // startWebSocket("viewlog", param['cn']);
            // }
            // // --- SYSTÈME DE FRONT MONTANT ---
            // if (!messagepresence && response === statepresence) {
            //
            //      console.log("AJAX ne rien faire:");
            //      console.log("messagepresence", messagepresence);//0
            //      console.log("statepresence", statepresence);//1
            //     return; // On ne fait rien de plus
            // }
            // Mise à jour du cache
            statepresence = response;
            const timeStamp = getTimeStamp();
            const machineInfo = getMachineInfo(param);

            if (!machineInfo) {
                console.error(`[${timeStamp}] Variables manquantes : cn, os ou entity non définis.`);
                return response;
            }

            if (response === "0") {
                if (GLOBAL_ON_FRAME == false){
                    GLOBAL_ON_FRAME = true;
                    // console.log(`0 GLOBAL_ON_FRAME`, GLOBAL_ON_FRAME);
                    logTexteColorInIframe({
                            messagetext:`[${timeStamp}] La machine ${machineInfo} est offline. Impossible de récupérer les logs.[en attente]`,
                            className: "warning-message", // Appliquer la classe CSS créée
                        });
                    // console.log("Relance web socket historique");
                    startWebSocket("hist", param['cn']);
                }
            } else {
                // console.log(`0 GLOBAL_ON_FRAME`, GLOBAL_ON_FRAME);
                startWebSocket("viewlog", param['cn']);
                logTexteColorInIframe({ messagetext:`[${timeStamp}] Demande de logs pour la machine : ${machineInfo}`,
                                        className: "info-message", // Appliquer la classe CSS créée
                });
            }
            return response;
        },
        error: function(xhr, status, error) {
            const timeStamp = getTimeStamp();
            console.error(`[${timeStamp}] Erreur AJAX :`, status, error);
            console.error(`[${timeStamp}] Réponse du serveur :`, xhr.responseText);
        }
    });
}
function ensureIframeDiv(containerId, iframeId, iframePage) {
    let div = document.getElementById(containerId);
    if (!div) return null;

    let iframe = document.getElementById(iframeId);

    if (!iframe) {
        iframe = document.createElement("iframe");
        iframe.id = iframeId;
        iframe.style.width = "100%";
        iframe.style.height = "200px";
        iframe.style.border = "0";
        iframe.src = iframePage;
        div.appendChild(iframe);
    }
    return {div, iframe};
}

function sendToIframe1(params) {
    const iframe = document.getElementById("logIframe");

    if (!iframe) {
        console.error("Iframe introuvable !");
        return;
    }
    // Envoi immédiat si déjà chargée
    if (iframe.contentWindow && typeof iframe.contentWindow.receiveParams === "function") {
        iframe.contentWindow.receiveParams(params);
    } else {
        // Attendre que l’iframe soit chargée
        iframe.addEventListener("load", function onLoad() {
            iframe.removeEventListener("load", onLoad);
            iframe.contentWindow.receiveParams(params);
        });
    }
}


// Fonction pour appeler logTexteColor dans l'iframe
function logTexteColorInIframe({
    messagetext,
    color = "black",
    isBold = false,
    isItalic = false,
    isUnderline = false,
    margin = "0",
    border = "none",
    backgroundColor = "transparent",
    className = ""
}) {
    if (messagetext =="NOHIST") { return }
    if (messagetext =="PING") { return }
    console.error("Appel de logTexteColor avec message : " + messagetext);

    const params = {
        message: { messagetext: messagetext }, // Enveloppez dans un objet
        color,
        isBold,
        isItalic,
        isUnderline,
        margin,
        border,
        backgroundColor,
        className
    };

    const iframe = document.getElementById("logIframe");

    if (!iframe) {
        console.error("Erreur : Iframe 'logIframe' introuvable !");
        return;
    }

    const iframeContent = iframe.contentWindow;

    if (iframeContent && typeof iframeContent.logTexteColor === "function") {
        // Appel immédiat si la fonction est déjà chargée
        iframeContent.logTexteColor(params);
    } else {
        // Attendre que l’iframe soit totalement chargée
        const onLoad = function () {
            iframe.removeEventListener("load", onLoad);
            if (iframe.contentWindow && typeof iframe.contentWindow.logTexteColor === "function") {
                iframe.contentWindow.logTexteColor(params);
            } else {
                console.error("Erreur : La fonction logTexteColor est introuvable dans l'iframe.");
            }
        };
        iframe.addEventListener("load", onLoad);
    }
}


function startcallModuleAction(url, params) {
    // on appelle le script php en ajax pour faire genere des scripts par cet appel ajax.
    // si déjà lancé → on ne recrée pas un nouvel interval
    if (intervalId !== null) {
        // console.log("Déjà en cours !");
        return;
    }
    callModuleAction(url, params, 1);
    intervalId = setInterval(() => {
        callModuleAction(url, params);;
    }, 60000);

    // console.log("Interval démarré");
}

function stopcallModuleAction() {
    if (intervalId !== null) {
        clearInterval(intervalId);
        intervalId = null;
        // console.log("Interval arrêté");
    }
}
function deepEqual(a, b) {
    if (a === b) return true;

    if (typeof a !== "object" || typeof b !== "object" || a === null || b === null) {
        return false;
    }

    const keysA = Object.keys(a).sort();
    const keysB = Object.keys(b).sort();

    if (keysA.length !== keysB.length) return false;

    for (let i = 0; i < keysA.length; i++) {
        if (keysA[i] !== keysB[i]) return false;
        if (!deepEqual(a[keysA[i]], b[keysA[i]])) return false;
    }

    return true;
}


// Fonction pour démarrer ou maintenir la connexion
function startWebSocket(action, cn, firstlineyes=false) {
    // On stocke les valeurs actuelles pour pouvoir les réutiliser
    currentAction = action;
    currentCn = cn;
    currentFirstLineYes = firstlineyes;
    if (isReading) {
        // Si déjà en lecture, on renvoie juste le nouveau message
        // console.log("WebSocket déjà actif. Mise à jour des données...");
        sendMessage(action, cn, currentFirstLineYes);
        return;
    }

    isReading = true;

    // Si WebSocket non connecté ou fermée, on crée une nouvelle connexion
    if (!ws || ws.readyState === WebSocket.CLOSED) {
        ws = new WebSocket("wss://jfk.medulla-tech.io/ws/");

        ws.onopen = function() {
            // console.log("WebSocket connecté.");
            sendMessage(currentAction, currentCn, currentFirstLineYes);
            startReading();
        };

        ws.onmessage = handleMessage;

        ws.onclose = function() {
            // console.log("WebSocket fermé.");
            ws = null;
            isReading=false;
            stopReading();
        };

        ws.onerror = function(error) {
            console.error("Erreur WebSocket:", error);
        };
    } else if (ws.readyState === WebSocket.OPEN) {
        // WebSocket déjà ouverte, on envoie simplement le message
        sendMessage(currentAction, currentCn, currentFirstLineYes);
        startReading();
    }
}

// Fonction pour arrêter la connexion et la lecture
function stopWebSocket() {
    if (!isReading) return;

    isReading = false;
    stopReading();

    if (ws) {
        ws.close();
        ws = null;
    }

    // console.log("WebSocket arrêté.");
}

// Fonction pour envoyer un message
function sendMessage(action, cn, currentFirstLineYes) {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action, cn, currentFirstLineYes }));
        // console.log("Message envoyé :", { action, cn , currentFirstLineYes });
    }
}

// Fonction pour traiter les messages reçus
function handleMessage(event) {
    let message = event.data;

    try {
        // Si le message est du JSON, on le parse
        const data = JSON.parse(message);
        // console.log("Message reçu (JSON) :", data);
        message = JSON.stringify(data); // On garde la chaîne pour l'iframe
    } catch (e) {
        // Si ce n'est pas du JSON, on traite le texte brut
        console.error("Message reçu (texte brut) :", message);
        console.error("Pas Traite");
    }

    if (message.startsWith('[DEBUG]') ) {
        logTexteColorInIframe({
                                messagetext: message,
                                color: "#00FFFF",
                                isItalic: true
                            });
    } else if (message.startsWith('[INFO]')) {
        logTexteColorInIframe({
                                messagetext: message,
                                color: "#00FF00",
                                isBold: true
                            });
    } else if (message.startsWith('[ERROR]')) {
        logTexteColorInIframe({
                                messagetext: message,
                                color: "#FF4500",
                                isBold: true,
                                isItalic: true,
                                isUnderline: false,
                                margin: "10px",
                                border: "none",
                                backgroundColor: "transparent",
                                className: ""
                            });
    } else if (message.startsWith('[WARNING]')) {
        logTexteColorInIframe({
                                messagetext: message,
                                color: "#FFA500",
                                isBold: true });
    } else {
        // Si la ligne ne commence par aucun des préfixes attendus
        logTexteColorInIframe({
                                messagetext: message,
                                color: "#FFFFFF"
                            });
    }
}



// Lecture régulière des logs
function startReading() {
    if (readInterval) return;

    readInterval = setInterval(() => {
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ action: "get_logs" }));
        }
    }, 5000);
}

// Arrêt de la lecture
function stopReading() {
    isReading=false;
    if (readInterval) {
        clearInterval(readInterval);
        readInterval = null;
    }
}

// Fonction pour afficher l'iframe
function showIframe() {
    document.body.classList.add("iframe-visible");
    document.getElementById("iframeContainer").classList.add("visible");
}

// Fonction pour masquer l'iframe
function hideIframe() {
    document.body.classList.remove("iframe-visible");
    document.getElementById("iframeContainer").classList.remove("visible");
}


function toggleIframeAndSendParams(containerId, iframeId, params, url) {
    // console.log(containerId);
    // console.log(iframeId);
    // console.log("Params globaux :", GLOBAL_PARAMS);
    // console.log("URL globale :", GLOBAL_URL);
    // console.log("Params local :", params);
    // console.log("URL globale :", url);
    // console.log("jfk");
    const container = document.getElementById(containerId);
    const iframeEl = document.getElementById(iframeId);

    // Construction URL iframe
    const paramsString = new URLSearchParams(params).toString();
    const iframeUrl = `${url}?${paramsString}`;

    if (!deepEqual(params, GLOBAL_PARAMS) || url !== GLOBAL_URL) {
        stopcallModuleAction();
    }

    // Mettre params et url dans des variables globales
    GLOBAL_PARAMS = params;
    GLOBAL_URL = url;

    let block = ensureIframeDiv(containerId, iframeId, "logs_iframeb.php");
    if (!block) return;
    let div = block.div;
    let iframe = block.iframe;

    if (div.style.display === "block") {
        div.style.display = "none";
        div.classList.remove("visible");
         hideIframe();
        // document.body.classList.remove("iframe-visible");
        stopcallModuleAction();
        stopWebSocket();
        iframe.contentWindow.location.reload();
        GLOBAL_ON_FRAME = false
        // console.log("Ferme log");
    } else {
        div.style.display = "block";
        div.classList.add("visible");
        showIframe();
        // document.body.classList.add("iframe-visible");
        startcallModuleAction(url, params);
        // startWebSocket("viewlog", params['cn']);
        // console.log("Ouvre log");
    }
    sendToIframe1(params);
}

document.getElementById('copier').addEventListener('click', () => {
  // Récupérer l'iframe
  const iframe = document.getElementById('logIframe');

  try {
    // Accéder au document de l'iframe
    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;

    // Récupérer le texte de tout le corps de l'iframe
    const texte = iframeDoc.body.innerText;

    // Copier dans le presse-papier
    navigator.clipboard.writeText(texte)
      .then(() => {
        console.log('Texte copié dans le presse-papier !');
      })
      .catch(err => {
        console.error('Erreur lors de la copie : ', err);
      });
  } catch (e) {
    console.error("Impossible d'accéder au contenu de l'iframe : ", e);
  }
});

</script>

