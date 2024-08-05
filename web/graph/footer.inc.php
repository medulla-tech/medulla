<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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

$MMCApp =& MMCApp::getInstance();
$MMCApp->render();

$login = $_SESSION['login'];
$server = $conf['notification']['url'];
$port = $conf['notification']['port'];
$protocol = $conf['notification']['protocol'];
$jid = $conf['notification']['jid'];
$pwd = $conf['notification']['password'];
?>

<div class="clearer"></div>
</div><!-- section -->
</div><!-- content -->

<div id="footer">
    <a href="http://www.siveo.net" target="blank"><img src="graph/mandriva-logo.png" alt="[x]" /></a>
    &nbsp;|&nbsp;&nbsp;MMC Agent <a href="#" onclick="showPopupUp(event,'version.php'); return false;"><?php echo $_SESSION["modListVersion"]['ver'] ?></a>
    <img id="notificationBell" src="graph/actif.png" alt="[x]" onclick="toggleNotificationCenter()" />
</div>

<div id="notificationCenter" class="hidden">
    <div class="close-btn" onclick="toggleNotificationCenter()">&times;</div>
    <p id="time"></p>
    <div class="notification-buttons">
        <button onclick="filterNotifications('all')">All <span id="count-all">(0)</span></button>
        <button onclick="filterNotifications('INFO')">INFO <span id="count-info">(0)</span></button>
        <button onclick="filterNotifications('SUCCESS')">SUCCESS <span id="count-success">(0)</span></button>
        <button onclick="filterNotifications('WARNING')">WARNING <span id="count-warning">(0)</span></button>
        <button onclick="filterNotifications('CRITICAL')">CRITICAL <span id="count-critical">(0)</span></button>
    </div>
    <p id="noMessages" style="display: block;">Aucune notification</p>
    <div id="notifications" class="notifications-container"></div>
</div>

</div><!-- wrapper -->

</body>
<script type="text/javascript" src="jsframework/strophe/strophe.min.js"></script>
<script>
const PING_INTERVAL = 30000;
const CLOSE_POPUP_DELAY = 5000;

function toggleNotificationCenter() {
    const notificationCenter = document.getElementById("notificationCenter");
    if (notificationCenter.classList.contains("hidden")) {
        notificationCenter.classList.remove("hidden");
        setTimeout(() => notificationCenter.classList.add("visible"), 10);
    } else {
        notificationCenter.classList.remove("visible");
        setTimeout(() => notificationCenter.classList.add("hidden"), 800);
    }
    loadNotificationsFromLocalStorage();
    updateNoMessagesText();
}

function closeNotificationCenterAfterDelay() {
    setTimeout(() => {
        const notificationCenter = document.getElementById("notificationCenter");
        notificationCenter.classList.remove("visible");
        setTimeout(() => notificationCenter.classList.add("hidden"), 800);
    }, CLOSE_POPUP_DELAY);
}

function updateTime() {
    const now = new Date();
    document.getElementById("time").textContent = now.toTimeString().split(' ')[0];
}

updateTime();
setInterval(updateTime, 1000);

const connection = new Strophe.Connection('<?php echo $server . ':' . $port . '/' . $protocol; ?>');
let pingTimer;

const login = "<?php echo $login; ?>";
const resource = "<?php echo $jid . '/' . $login; ?>";

connection.connect(resource, "<?php echo $pwd ?>", handleConnectionStatus);

function handleConnectionStatus(status) {
    if (status === Strophe.Status.CONNECTED) {
        connection.addHandler(onMessage, null, 'message', null, null, null);
        connection.send($pres().tree());
        startPing();
    } else if (status === Strophe.Status.DISCONNECTED) {
        clearInterval(pingTimer);
    }
}

function startPing() {
    pingTimer = setInterval(() => {
        const ping = $iq({type: 'get'}).c('ping', {xmlns: 'urn:xmpp:ping'});
        connection.send(ping.tree());
    }, PING_INTERVAL);
}

function onMessage(msg) {
    const from = msg.getAttribute('from');
    const elems = msg.getElementsByTagName('body');
    if (elems.length > 0) {
        const body = elems[0];
        const encodedMessage = Strophe.getText(body);
        processMessage(encodedMessage, from);
    }
    return true;
}

function processMessage(encodedMessage, from) {
    try {
        const decodedMessage = atob(encodedMessage);
        const messageData = JSON.parse(decodedMessage.replace(/^"|"$/g, ''));

        const type = messageData.type.trim();
        const receivedAt = new Date().toISOString();

        const notificationData = {
            type: type,
            data: messageData,
            receivedAt: receivedAt
        };
        storeMessageInLocalStorage(notificationData);

        displayNotification(from, notificationData);
        if (document.getElementById("notificationCenter").classList.contains("hidden")) {
            toggleNotificationCenter();
        }
        closeNotificationCenterAfterDelay();
    } catch (e) {
        console.error('Error decoding or parsing message:', e);
    }
}

function storeMessageInLocalStorage(notificationData) {
    const notifications = JSON.parse(localStorage.getItem('notifications')) || [];

    notifications.push(notificationData);
    notifications.sort((a, b) => new Date(a.receivedAt) - new Date(b.receivedAt));

    localStorage.setItem('notifications', JSON.stringify(notifications));
    updateNoMessagesText();
}

function updateCounters() {
    const notifications = JSON.parse(localStorage.getItem('notifications')) || [];
    const counts = {
        all: notifications.length,
        INFO: 0,
        SUCCESS: 0,
        WARNING: 0,
        CRITICAL: 0
    };

    notifications.forEach(notification => {
        if (counts[notification.type] !== undefined) {
            counts[notification.type]++;
        }
    });

    document.getElementById('count-all').textContent = `(${counts.all})`;
    document.getElementById('count-info').textContent = `(${counts.INFO})`;
    document.getElementById('count-success').textContent = `(${counts.SUCCESS})`;
    document.getElementById('count-warning').textContent = `(${counts.WARNING})`;
    document.getElementById('count-critical').textContent = `(${counts.CRITICAL})`;
}

function filterNotifications(type) {
    const notifications = JSON.parse(localStorage.getItem('notifications')) || [];
    const filteredNotifications = type === 'all' ? notifications : notifications.filter(notification => notification.type === type);

    const container = document.getElementById("notifications");
    container.innerHTML = "";

    if (filteredNotifications.length > 0) {
        filteredNotifications.forEach(notification => displayNotification("Local", notification, true));
    }
    updateNoMessagesText();
}

function displayNotification(de, notificationData, fromLocalStorage = false) {
    const container = document.getElementById("notifications");
    const notificationDiv = document.createElement("div");
    notificationDiv.classList.add("notification");

    const typeLabel = notificationData.type || 'Undefined';
    const data = notificationData.data || {};
    let backgroundColor = "#f0f0f0";

    switch (notificationData.type) {
        case "INFO":
            backgroundColor = "#d9edf7";
            break;
        case "SUCCESS":
            backgroundColor = "#d4edda";
            break;
        case "WARNING":
            backgroundColor = "#fcf8e3";
            break;
        case "CRITICAL":
            backgroundColor = "#f8d7da";
            break;
        default:
            backgroundColor = "#f0f0f0";
            break;
    }

    notificationDiv.style.backgroundColor = backgroundColor;

    let contentHtml = `<div class='notification-detail'>`;
    contentHtml += `<span>${typeLabel}</span>`;

    if (data && typeof data === 'object') {
        for (const [key, value] of Object.entries(data)) {
            if (value !== undefined && value !== null && value !== '') {
                let keyLabel = key.charAt(0).toUpperCase() + key.slice(1);
                if (key === 'machine' && typeof value === 'string' && value.includes('@')) {
                    const jidParts = value.split('@')[0].split('.');
                    contentHtml += `<span>${keyLabel}: ${jidParts[0]}</span>`;
                } else if (key !== 'type') {
                    if (key === 'start_date') {
                        const formattedDate = new Date(value).toLocaleString();
                        contentHtml += `<span>Date de début: ${formattedDate}</span>`;
                    } else if (key === 'end_date') {
                        const formattedDate = new Date(value).toLocaleString();
                        contentHtml += `<span>Date de fin: ${formattedDate}</span>`;
                    } else {
                        contentHtml += `<span>${keyLabel}: ${value}</span>`;
                    }
                }
            }
        }
    }

    contentHtml += `</div>`;

    contentHtml += `
        <div class='notification-time'>${new Date(notificationData.receivedAt).toLocaleTimeString()}</div>
        <div class='notification-footer'>
            <span class='close-notification' onclick='removeNotification("${notificationData.receivedAt}")'>×</span>
        </div>
    `;

    notificationDiv.innerHTML = contentHtml;

    if (fromLocalStorage) {
        container.insertBefore(notificationDiv, container.firstChild);
    } else {
        if (container.children.length >= 3) {
            container.removeChild(container.children[0]);
        }
        container.appendChild(notificationDiv);
    }
    updateNoMessagesText();
}

function updateNoMessagesText() {
    const container = document.getElementById("notifications");
    const noMessagesText = document.getElementById("noMessages");
    const notificationCenter = document.getElementById("notificationCenter");
    if (container.children.length === 0) {
        noMessagesText.style.display = "block";
        notificationCenter.classList.add("no-notifications");
    } else {
        noMessagesText.style.display = "none";
        notificationCenter.classList.remove("no-notifications");
    }
    updateCounters();
}

function loadNotificationsFromLocalStorage() {
    const container = document.getElementById("notifications");
    container.innerHTML = "";
    const notifications = JSON.parse(localStorage.getItem('notifications')) || [];
    if (notifications.length > 0) {
        notifications.forEach(notification => displayNotification("Local", notification, true));
    }
    updateCounters();
    updateNoMessagesText();
}

function removeNotification(timestamp) {
    let notifications = JSON.parse(localStorage.getItem('notifications')) || [];
    notifications = notifications.filter(notification => notification.receivedAt !== timestamp);
    localStorage.setItem('notifications', JSON.stringify(notifications));
    loadNotificationsFromLocalStorage();
}

window.onload = function() {
    loadNotificationsFromLocalStorage();
}
</script>
</html>
