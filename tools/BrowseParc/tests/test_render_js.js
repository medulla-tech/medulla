#!/usr/bin/env node
/*
 * Verifie la logique d'affichage de la colonne "Prise en main" de browseparc.js
 * sans navigateur : les fonctions sont extraites du fichier et evaluees.
 *
 *   node tests/test_render_js.js
 */
"use strict";

const fs = require("fs");
const path = require("path");

const SOURCE = path.join(__dirname, "..", "web", "browseparc.js");
let src;
try {
    src = fs.readFileSync(SOURCE, "utf8");
} catch (error) {
    console.error("cannot read %s: %s", SOURCE, error.message);
    process.exit(1);
}

// Extraire les fonctions testees du fichier (elles vivent dans une IIFE).
function extract(startMarker, endMarker, label) {
    const start = src.indexOf(startMarker);
    const end = src.indexOf(endMarker);
    if (start === -1 || end === -1 || end <= start) {
        console.error("cannot extract %s", label);
        process.exit(1);
    }
    return src.slice(start, end);
}

// escapeHtml est defini plus haut dans le fichier, les helpers de prise en main
// juste avant renderMachines : on assemble les deux blocs.
const escapeBlock = extract("function escapeHtml", "function call", "escapeHtml");
const helpers = extract("var SERVICE_PORTS", "function openSession", "helpers");

const factory = new Function(
    "t",
    escapeBlock + helpers +
    "\nreturn { remoteButtons: remoteButtons, servicesTags: servicesTags," +
    " servicePort: servicePort, escapeHtml: escapeHtml, methodFor: methodFor };");
const api = factory(function (key) { return key; });
const remoteButtons = api.remoteButtons;
const methodFor = api.methodFor;
const servicesTags = api.servicesTags;
const servicePort = api.servicePort;

let pass = 0;
let fail = 0;

function check(label, condition, detail) {
    if (condition) {
        pass += 1;
        console.log("  ok   %s", label);
    } else {
        fail += 1;
        console.log("  FAIL %s %s", label, detail === undefined ? "" : detail);
    }
}

function machine(services, ports) {
    return { target: "pc1", name: "pc1", services: services, ports: ports };
}

console.log("\n1. Machine Windows avec RDP et WinRM");
let html = remoteButtons(machine(["rdp", "winrm"], [3389, 5985]));
check("bouton RDP present", html.indexOf("bp-session") !== -1 && html.indexOf('data-protocol="rdp"') !== -1, html);
check("port RDP correct", html.indexOf('data-port="3389"') !== -1, html);
check("etiquette du service winrm affichee", html.indexOf("<span class=\"bp-tag\">winrm</span>") !== -1, html);
check("aucun bouton winrm", html.indexOf('data-protocol="winrm"') === -1, html);

console.log("\n2. Machine Windows avec WinRM seul (cas du controleur de domaine)");
html = remoteButtons(machine(["winrm"], [5985]));
check("aucun bouton de prise en main", html.indexOf("bp-session") === -1, html);
check("service affiche pour expliquer", html.indexOf("winrm") !== -1, html);
check("tiret affiche a la place des boutons", html.indexOf("<span class=\"bp-tag\">-</span>") !== -1, html);

console.log("\n3. Machine Linux avec SSH (VNC retire)");
html = remoteButtons(machine(["ssh"], [22]));
check("bouton SSH present", html.indexOf('data-protocol="ssh"') !== -1, html);
check("port SSH correct", html.indexOf('data-port="22"') !== -1, html);
html = remoteButtons(machine(["ssh", "vnc"], [22, 5900, 5901]));
check("aucun bouton VNC meme si le port est ouvert",
    html.indexOf('data-protocol="vnc"') === -1 && html.indexOf("VNC") === -1, html);

console.log("\n4. Machine sans service detecte");
html = remoteButtons(machine([], []));
check("tiret seul", html.indexOf("bp-session") === -1 && html.indexOf("<span class=\"bp-tag\">-</span>") !== -1, html);

console.log("\n5. Anciens resultats de decouverte (sans champ services)");
html = remoteButtons({ target: "pc-old", name: "pc-old" });
check("aucun plantage", typeof html === "string", html);
check("tiret affiche", html.indexOf("<span class=\"bp-tag\">-</span>") !== -1, html);

console.log("\n6. Echappement du nom de machine");
html = remoteButtons({ target: 'a"b<script>', services: ["ssh"], ports: [22] });
check("guillemets echappes", html.indexOf('data-target="a&quot;b&lt;script&gt;"') !== -1, html);

console.log("\n6 bis. Un bouton par protocole detecte, sans regle liee au systeme");
["Debian 12", "Windows", ""].forEach(function (osys) {
    const both = remoteButtons({ os: osys, services: ["ssh", "rdp"], ports: [22, 3389] });
    check("SSH + RDP detectes (" + (osys || "systeme inconnu") + ") -> les deux boutons",
        both.indexOf('data-protocol="ssh"') !== -1 && both.indexOf('data-protocol="rdp"') !== -1, both);
    const rdpOnly = remoteButtons({ os: osys, services: ["rdp"], ports: [3389] });
    check("RDP seul (" + (osys || "systeme inconnu") + ") -> RDP propose",
        rdpOnly.indexOf('data-protocol="rdp"') !== -1 && rdpOnly.indexOf('data-protocol="ssh"') === -1, rdpOnly);
});
check("plus de regle RDP/Linux dans le code", src.indexOf("rdpAllowed") === -1);

console.log("\n7. Methode d'installation annoncee");
check("Linux -> SSH", methodFor({ os: "Debian 13", ports: [22] }) === "SSH",
    methodFor({ os: "Debian 13", ports: [22] }));
check("Windows + WinRM -> WinRM",
    methodFor({ os: "Windows", ports: [5985] }) === "WinRM",
    methodFor({ os: "Windows", ports: [5985] }));
check("Windows joignable seulement en SSH -> SSH",
    methodFor({ os: "Windows", ports: [22] }) === "SSH",
    methodFor({ os: "Windows", ports: [22] }));
check("OS inconnu mais WinRM ouvert -> WinRM",
    methodFor({ os: "", ports: [5985] }) === "WinRM",
    methodFor({ os: "", ports: [5985] }));
check("OS inconnu mais SSH ouvert -> SSH",
    methodFor({ os: "", ports: [22] }) === "SSH",
    methodFor({ os: "", ports: [22] }));
check("Linux/Unix (assumed) -> SSH",
    methodFor({ os: "Linux/Unix (assumed)", ports: [22] }) === "SSH",
    methodFor({ os: "Linux/Unix (assumed)", ports: [22] }));
check("rien de connu -> ?", methodFor({ os: "", ports: [] }) === "?",
    methodFor({ os: "", ports: [] }));

console.log("\n7 bis. Les messages de succes sont affiches");
const notifyCode = src.slice(src.indexOf("function notify"), src.indexOf("function selectedMachines"));
check("notify n'ignore plus les messages de succes",
    notifyCode.indexOf("NotifyWidgetSuccess") === -1, notifyCode.slice(0, 90));
check("notify ecrit bien dans le panneau", notifyCode.indexOf("#bpJobLog") !== -1);

console.log("\n8. Le bouton Suivre ouvre le journal dans le tableau");
// Conception revue : le journal s'ouvre sous la ligne de la tache concernee.
// L'ancien comportement remontait la page vers le panneau du haut, ce qui
// faisait perdre le fil et eloignait l'information demandee.
check("handler Suivre present", src.indexOf('.bp-job-follow", function') !== -1);
check("le handler ouvre le journal en ligne",
    src.indexOf("toggleInlineLog($(this).data(\"job\")") !== -1);
check("plus de remontee en haut de page depuis Suivre",
    src.indexOf("panel.offset().top") === -1);
check("machinerie du journal en ligne", src.indexOf("function inlinePoll") !== -1
    && src.indexOf("function appendInlineLog") !== -1
    && src.indexOf("function closeInlineLog") !== -1);
check("le journal suit la tache, pas le panneau du haut",
    src.indexOf("scheduleInlinePoll") !== -1);
check("la ligne de tache porte son identifiant",
    src.indexOf("bp-job-row") !== -1 && src.indexOf('data-job="\' + escapeHtml(job.job)') !== -1);
check("le journal ouvert survit a un rafraichissement",
    src.indexOf("restoreInlineLog()") !== -1);
check("refreshJobs remet le journal ouvert sous sa ligne (tableau reconstruit)",
    extract("function refreshJobs(", "// -------------------------------------------------------- prerequisites", "refreshJobs")
        .split("restoreInlineLog()").length - 1 >= 2);
check("le journal s'arrete quand la tache est finie",
    src.indexOf('if (status.status === "running") {\n                scheduleInlinePoll(INLINE_POLL_INTERVAL);') !== -1,
    "arret du suivi");
check("le bouton devient Masquer",
    src.indexOf('button.text(t("hide"))') !== -1);

console.log("\n9. Arbre des OU (domaine + branches contenant des machines)");
const treeSrc = extract("function buildOuTree(", "function renderOuTree(", "buildOuTree");
const buildOuTree = new Function(treeSrc + "; return buildOuTree;")();
const ous = [
    { name: "medulla", dn: "DC=medulla,DC=lan", canonical: "medulla.lan",
      machines: 1, total: 7, parent: "DC=lan" },
    { name: "Servers", dn: "OU=Servers,DC=medulla,DC=lan", canonical: "medulla.lan/Servers",
      machines: 3, total: 5, parent: "DC=medulla,DC=lan" },
    { name: "DMZ", dn: "OU=DMZ,OU=Servers,DC=medulla,DC=lan", canonical: "medulla.lan/Servers/DMZ",
      machines: 2, total: 2, parent: "OU=Servers,DC=medulla,DC=lan" },
    { name: "Workstations", dn: "OU=Workstations,DC=medulla,DC=lan", canonical: "medulla.lan/Workstations",
      machines: 3, total: 3, parent: "DC=medulla,DC=lan" }
];
const tree = buildOuTree(ous);
check("le domaine est la racine", tree.roots.length === 1
    && tree.roots[0].dn === "DC=medulla,DC=lan", "racines=" + tree.roots.length);
check("les OU sont rattachees a leur parent",
    (tree.children["DC=medulla,DC=lan"] || []).length === 2);
check("la sous-OU est rattachee a la sienne",
    (tree.children["OU=Servers,DC=medulla,DC=lan"] || []).length === 1
    && tree.children["OU=Servers,DC=medulla,DC=lan"][0].name === "DMZ");
check("le parent absent de la liste ne casse pas l'arbre",
    buildOuTree([{ name: "Orpheline", dn: "OU=X,DC=lan", parent: "OU=absente,DC=lan",
                   machines: 1, total: 1 }]).roots.length === 1);

console.log("\n10. Annulation : etat reel et retour visible");
check("l'etat vient du serveur, plus d'un binaire en cours/termine",
    src.indexOf('stateLabel(job.state)') !== -1);
check("chaque etat a son libelle", src.indexOf("function stateLabel") !== -1
    && src.indexOf('state === "cancelled"') !== -1
    && src.indexOf('state === "error"') !== -1);
check("le message va la ou l'utilisateur regarde",
    src.indexOf("#bpJobMessage") !== -1
    && src.indexOf('panel.hasClass("bp-hidden")') !== -1);
const cancelStart = src.indexOf('.bp-job-cancel", function');
const cancelBlock = src.slice(cancelStart, src.indexOf("refreshAgents();", cancelStart));
check("annuler ouvre le journal de la tache",
    cancelBlock.indexOf("openInlineLog(job, button)") !== -1);
check("le bouton est capture avant l'appel asynchrone",
    cancelBlock.indexOf("var button = $(this)") !== -1
    && cancelBlock.indexOf("openInlineLog($(this)") === -1);

console.log("\n11. Changement de mode : cases videes et tache annulee");
const switchSrc = extract("function switchMode(", "// The table must say", "switchMode");
check("passer en reseau vide les champs AD",
    switchSrc.indexOf('#bpServer, #bpOu, #bpDomain, #bpFilter') !== -1);
check("passer en AD vide le CIDR", switchSrc.indexOf('#bpTarget') !== -1);
check("l'arbre et la selection sont remis a zero",
    switchSrc.indexOf("state.ous = []") !== -1);
check("la tache en cours est annulee", switchSrc.indexOf("stopRunningJob(") !== -1);
const stopSrc = extract("function stopRunningJob(", "// The table must say", "stopRunningJob");
check("l'arret appelle bien l'endpoint cancel", stopSrc.indexOf('call("cancel"') !== -1);
check("le panneau de tache est masque", stopSrc.indexOf("bp-hidden") !== -1);
check("les identifiants sont conserves",
    switchSrc.indexOf("#bpUsername") === -1 && switchSrc.indexOf("#bpPassword") === -1);

console.log("\n12. Une recherche sans compte ne part pas");
const credSrc = extract("function credentialProblem(", "function showFormMessage(", "credentialProblem");
const showSrc = extract("function showFormMessage(", "function clearFormMessage(", "showFormMessage");
check("le controle des identifiants existe", credSrc.indexOf("adAccountRequired") !== -1);
check("Active Directory exige identifiant et mot de passe",
    credSrc.indexOf('currentMode() === "ad"') !== -1
    && credSrc.indexOf("(user && pass) ? null : t(\"adAccountRequired\")") !== -1);
check("le reseau accepte une cle SSH a la place du mot de passe",
    credSrc.indexOf("if (key)") !== -1 && credSrc.indexOf("usernameRequired") !== -1);
check("sans cle, identifiant et mot de passe sont exiges",
    credSrc.indexOf('t("accountRequired")') !== -1);
check("le message s'affiche dans le formulaire",
    showSrc.indexOf("#bpDiscoverMessage") !== -1);
const discoverSrc = src.slice(src.indexOf("function doDiscover("), src.indexOf("function doListOus("));
check("la decouverte est bloquee avant de lancer la tache",
    discoverSrc.indexOf("credentialProblem()") !== -1
    && discoverSrc.indexOf("showFormMessage(problem)") !== -1
    && discoverSrc.indexOf("return;") !== -1);
const ousSrc = src.slice(src.indexOf("function doListOus("), src.indexOf("function doInstall("));
check("le listage des OU aussi", ousSrc.indexOf("credentialProblem()") !== -1);
const installSrc = src.slice(src.indexOf("function doInstall("), src.indexOf("function groupExists("));
check("l'installation aussi", installSrc.indexOf("credentialProblem()") !== -1);

console.log("\n13. Robustesse de l'interface (relecture)");
check("le groupe Medulla standard est retire",
    src.indexOf("pushGroup") === -1 && src.indexOf("group_push") === -1 && src.indexOf("bpPushGroup") === -1);
const sessionSrc = extract("function openSession(", "function switchMode(", "openSession");
check("la fenetre de session s'ouvre dans le clic",
    sessionSrc.indexOf('window.open("", "_blank")') !== -1
    && sessionSrc.indexOf("popup.location = response.url") !== -1);
check("la fenetre est fermee sur erreur", sessionSrc.indexOf("popup.close()") !== -1);
check("pop-up bloque: message", sessionSrc.indexOf("popupBlocked") !== -1);
const appendSrc = extract("var LOG_MAX_CHARS", "// ------------------------------------------------------------ selection", "appendLog");
check("le journal est ajoute comme texte, pas comme HTML",
    appendSrc.indexOf("createTextNode") !== -1 && appendSrc.indexOf(".append(") === -1);
check("le journal est plafonne", appendSrc.indexOf("LOG_MAX_CHARS") !== -1 && appendSrc.indexOf("slice(") !== -1);
check("plus de journal en HTML brut",
    src.indexOf("escapeHtml(status.log.join") === -1 && src.indexOf("escapeHtml(lines.join") === -1);
const applySrc = extract("function applyStatus(", "function poll(", "applyStatus");
check("relance rapide quand il reste du journal", applySrc.indexOf("log_more") !== -1);
check("le bouton des prerequis est traduit", src.indexOf("Installer les prerequis") === -1);
check("le libelle de l'agent generique est traduit", src.indexOf('t("genericAgent")') !== -1);
check("le suivi en ligne se met en pause onglet masque",
    extract("function inlinePoll(", "function appendInlineLog(", "inlinePoll").indexOf("document.hidden") !== -1);
check("plus de selecteur construit par concatenation avec un id de tache",
    src.indexOf('[data-job="\' + ') === -1);
check("code mort retire de doDiscover", src.slice(src.indexOf("function doDiscover("), src.indexOf("function doListOus(")).indexOf("!params.mode") === -1);

console.log("\n14. Fenetres integrees a la place de prompt/confirm");
const codeOnly = src.split("\n").filter(l => !/^\s*(\/\/|\*)/.test(l)).join("\n");
check("plus aucun window.prompt", codeOnly.indexOf("window.prompt") === -1);
check("plus aucun window.confirm", codeOnly.indexOf("window.confirm") === -1);
check("plus aucun alert natif", /(^|[^.\w])alert\(/.test(codeOnly) === false);
check("creation de groupe via la fenetre integree",
    src.slice(src.indexOf("function doCreateInstallGroup("), src.indexOf("// ---", src.indexOf("function doCreateInstallGroup("))).indexOf("openDialog(") !== -1);
check("suppression de groupe confirmee par la fenetre integree",
    src.slice(src.indexOf("bp-group-delete\", function"), src.indexOf("bp-job-follow\", function")).indexOf("openDialog(") !== -1);
check("arret de tache confirme par la fenetre integree",
    src.slice(src.indexOf("bp-job-cancel\", function")).indexOf("openDialog(") !== -1);
check("la fenetre se ferme avec Echap", src.indexOf('event.key === "Escape"') !== -1);
check("la fenetre insere les textes comme texte (pas de .html)",
    extract("function openDialog(", "function notify", "openDialog").indexOf(".html(") === -1);
check("notify affiche aussi une notification visible", notifyCode.indexOf("toast(") !== -1);
const phpSource = fs.readFileSync(path.join(__dirname, "..", "web", "browseparc.php"), "utf8");
["dialogCancel", "dialogConfirm", "dialogCreate", "stopJob", "createInstallGroup", "installGroupInfo"].forEach(function (key) {
    check("cle i18n declaree cote PHP : " + key, phpSource.indexOf("'" + key + "' =>") !== -1);
});

check("l'installation depuis un groupe transmet son nom", src.indexOf("doInstall(machines, name)") !== -1 && src.indexOf("params.group = groupName") !== -1);
check("Suivre un groupe ouvre la derniere installation du groupe",
    src.slice(src.indexOf('".bp-group-follow"'), src.indexOf('".bp-group-delete"')).indexOf("followJob(latest.job") !== -1);
["noGroupJob", "groupJobLabel"].forEach(function (key) {
    check("cle i18n declaree cote PHP : " + key, phpSource.indexOf("'" + key + "' =>") !== -1);
});

console.log("\n15. macOS et rapport d'installation");
check("macOS: installation annoncee en SSH", methodFor({ os: "macOS 14", ports: [22] }) === "SSH");
check("Darwin: installation annoncee en SSH", methodFor({ os: "Darwin", ports: [] }) === "SSH");
check("rapport d'installation affiche", src.indexOf("function renderInstallResults") !== -1 &&
    src.indexOf("renderInstallResults(status)") !== -1);
check("etape et cause traduites", src.indexOf('"failStep_"') !== -1 && src.indexOf('"failCode_"') !== -1);
check("journal de la machine lu en GET", src.indexOf('"machine_log"]') !== -1 || src.indexOf('"machine_log"') !== -1);
check("l'agent macOS est annonce dans la liste", src.indexOf('systems.push("macOS")') !== -1);

console.log("\n16. Installation manuelle et SMB");
check("Windows avec seulement 445: SMB", methodFor({ os: "Windows 10", ports: [445] }) === "SMB");
check("Windows avec WinRM: WinRM", methodFor({ os: "Windows 10", ports: [445, 5985] }) === "WinRM");
check("Installer remonte sur le journal (groupes compris)",
    /startJob\("install"[^;]*;\s*scrollToJob\(\);/.test(src) && src.indexOf("function scrollToJob") !== -1);
check("aucun champ mot de passe (Chrome proposerait de l'enregistrer)",
    phpSource.indexOf('type="password"') === -1 && phpSource.indexOf('id="bpPassword" class="bp-secret"') !== -1);
check("le mot de passe reste masque par CSS",
    fs.readFileSync(path.join(__dirname, "..", "web", "browseparc.css"), "utf8").indexOf("-webkit-text-security: disc") !== -1);
check("commande manuelle affichee en texte (pas en HTML)",
    src.indexOf('.addClass("bp-manual-command").text(item.manual)') !== -1);
["failManual", "failCode_smb_unavailable", "failCode_admin_required", "failCode_smb_client_missing"].forEach(function (key) {
    check("cle i18n declaree cote PHP : " + key, phpSource.indexOf("'" + key + "' =>") !== -1);
});

console.log("\n=====================================");
console.log("%d verifications, %d echec(s)", pass, fail);
process.exit(fail ? 1 : 0);
