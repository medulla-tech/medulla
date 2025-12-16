<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">

<!-- jQuery CDN -->
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script>jQuery.noConflict();</script>
<script>

// Variables globales
let globalUUID;
let globalType;
let globalJid;
let globalCn;
let globalOs ;
let globalobjectUUID;
let globalpresencemachinexmpp;
let globalentity;
let globalentityid;
let globaluser;
let globalvnctype;
let globalfrom;

function warningTexte(message) {
    const messagetext = message['messagetext'];
    // Ajoute le div à la fin de #mondivtext
    const div = document.createElement("div");
    div.className = "orangewarning";
    div.textContent = messagetext;
    document.getElementById("mondivtext").appendChild(div);
}

function erreurTexte(message) {
    const messagetext = message['messagetext'];
    // Ajoute le div à la fin de #mondivtext
    const div = document.createElement("div");
    div.className = "rouge";
    div.textContent = messagetext;
    document.getElementById("mondivtext").appendChild(div);
    }

function logTexte(message) {
    const messagetext = message['messagetext'];
    // Ajoute le div à la fin de #mondivtext
    const div = document.createElement("div");
    div.className = "vert";
    div.textContent = messagetext;
    document.getElementById("mondivtext").appendChild(div);
    }

function recois_parametre(param) {
    // console.log("receiveParams");
    for (const key in params) {
        console.log( params[key]);
        // rend chaque clé accessible globalement
    }
    // console.log("recois_parametre  Param reçu a dans l'iframe :", param);
    // document.body.innerHTML += "<p>recois_parametre : " + param + "</p>";
    }

function logTexteColor({
    message,
    color = "black",
    isBold = false,
    isItalic = false,
    isUnderline = false,
    margin = "0",
    border = "none",
    backgroundColor = "transparent",
    className = "",
    nombreEnfants = 500
}) {

    const messagetext = message["messagetext"];
    const parentDiv = document.getElementById("mondivtext");

    // 🔥 Commande spéciale pour nettoyer l'écran
    if (messagetext === "@COMMAND@:CLEANIFRAME") {

        let savedNode = null;

        // On récupère le premier vrai élément (div), ignore les TEXT_NODE vides
        const first = parentDiv.firstElementChild;

        if (first) {
            // On clone directement le premier div
            savedNode = first.cloneNode(true);
        }

        // 🚀 Nettoyage complet
        parentDiv.innerHTML = "";

        // ♻️ Restauration éventuelle du premier nœud
        if (savedNode) {
            parentDiv.appendChild(savedNode);
        }

        return;
    }

    // --- Ajout normal d’un message ---
    const div = document.createElement("div");

    if (className) {
        div.className = className;
    } else {
        div.style.color = color;
        div.style.fontWeight = isBold ? "bold" : "normal";
        div.style.fontStyle = isItalic ? "italic" : "normal";
        div.style.textDecoration = isUnderline ? "underline" : "none";
        div.style.margin = margin;
        div.style.border = border;
        div.style.backgroundColor = backgroundColor;
    }

    div.textContent = messagetext;
    parentDiv.appendChild(div);

    // 🔧 Limitation du nombre de messages
    while (parentDiv.children.length > nombreEnfants) {
        parentDiv.removeChild(parentDiv.firstElementChild);
    }
}


function receiveParams(params) {
    // console.log("receiveParams log iframe");
    for (const key in params) {
        window[key] = params[key];  // rend chaque clé accessible globalement
    }
    globalUUID = window.UUID;
    globalType = window.type;
    globalJid = window.jid;
    globalCn = window.cn;
    globalOs = window.os;
    globalobjectUUID = window.objectUUID;
    globalpresencemachinexmpp = window.presencemachinexmpp;
    globalentity = window.entity;
    globalentityid = window.entityid;
    globaluser = window.user;
    globalvnctype = window.vnctype;
    globalfrom = window.from;
}

</script>
 <style>
        body, html {
            margin: 0;
            padding: 3px;
            font-family: Arial, sans-serif;
            background: #000; /* Fond noir */
            color: white; /* Texte blanc par défaut */
            font-size: 10px;
            line-height: 1.5;
            height: 100%;
            width: 100%;
            overflow: auto;
            box-sizing: border-box;
        }
        .vert { color: #00ff00; }
        .rouge { color: #ff0000; }
        .blanche { color: #ff0000; }
        .orangewarning { color: #ffa500; } /* Orange standard */
        /* Classe CSS pour le message d'avertissement */

        /* MeEssage style infomartion page */
        .warning-message {
            background-color: #FFA500;  /* Orange clair */
            color: #FFFFFF;              /* Couleur du texte blanche */
            font-weight: bold;

            /* Relief renforcé */
            box-shadow:
                inset 0 0 8px rgba(255, 255, 255, 0.5),   /* Éclaircissement intérieur plus prononcé */
                0 0 12px rgba(0, 0, 0, 0.6);               /* Ombre externe plus forte */

            border-radius: 5px; /* Pour adoucir les coins, si souhaité */
            padding: 2px; /* Espacement interne pour un meilleur rendu */
        }
        /* Bordure orange foncé   border: 1px solid #FF8C00;*/
        .info-message {
            background-color: #3399FF;  /* Bleu clair */
            color: #FFFFFF;
            font-weight: bold;

            /* Relief renforcé */
            box-shadow:
                inset 0 0 8px rgba(255, 255, 255, 0.5),   /* Éclaircissement intérieur plus prononcé */
                0 0 12px rgba(0, 0, 0, 0.6);               /* Ombre externe plus forte */

            border-radius: 5px; /* Pour adoucir les coins, si souhaité */
            padding: 2px; /* Espacement interne pour un meilleur rendu */
        }

    </style>
</head>
<body>
    <div id="mondivtext">
    <?php

   ?>
    </div>
</body>
<!--<div id="infoContainer">-->

<!--</div>-->
</body>
</html>
