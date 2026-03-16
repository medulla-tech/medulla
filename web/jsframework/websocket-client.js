/*
 * MedullaWebSocket — Reusable WebSocket client for Medulla
 *
 * Usage:
 *   var ws = new MedullaWebSocket('wss://hostname/wsl-server/', {
 *       onConnect: function() { ws.subscribe('group', 'file', 'tail20'); },
 *       onLog: function(data, mode) { console.log(data); },
 *       onError: function(err) { },
 *       onClose: function() { }
 *   });
 *   ws.connect();
 */
class MedullaWebSocket {
    constructor(url, options) {
        options = options || {};
        this.url = url;
        this.ws = null;
        this.onLog = options.onLog || function() {};
        this.onConnect = options.onConnect || function() {};
        this.onError = options.onError || function() {};
        this.onClose = options.onClose || function() {};
    }

    connect() {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = function() {
            this.onConnect();
        }.bind(this);

        this.ws.onmessage = function(event) {
            try {
                var message = JSON.parse(event.data);
                if (message.type === 'log') {
                    this.onLog(message.data, message.mode || null);
                }
            } catch (e) {
                console.error("MedullaWebSocket JSON error:", e);
            }
        }.bind(this);

        this.ws.onerror = function(error) {
            console.error("MedullaWebSocket error:", error);
            this.onError(error);
        }.bind(this);

        this.ws.onclose = function() {
            this.onClose();
        }.bind(this);
    }

    send(data) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify(data));
        }
    }

    subscribe(group, file, mode) {
        this.send({
            command: "subscribe",
            group: group,
            file: file,
            mode: mode || "tail10"
        });
    }

    unsubscribe() {
        this.send({ command: "unsubscribe" });
    }

    close() {
        if (this.ws) {
            this.ws.close();
        }
    }
}
