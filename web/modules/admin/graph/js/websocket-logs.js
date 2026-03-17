/* /usr/share/mmc/modules/admin/graph/js/websocket-logs.js */
/* Depends on: /mmc/jsframework/websocket-client.js (MedullaWebSocket) */

  class UIController {
    static init() {
      this.logContainer = document.getElementById("logOutputContainer");
      this.logOutput = document.getElementById("logOutput");
      this.lastConfig = null;

    // File change: reset controls and configuration
      document.getElementById("fileSelect").addEventListener("change", () => {
        UIController.clearLogPanel();
        UIController.resetControls();
        UIController.lastConfig = null;
        wsClient.close();
        initWebSocket();
      });

      // Change of display mode (Complete/Partial)
      document.querySelectorAll('input[name="displayMode"]').forEach((elem) => {
        elem.addEventListener("change", () => {
          UIController.clearLogPanel();
          UIController.handleDisplayModeChange();
          UIController.lastConfig = null;
          UIController.sendLogSettings();
        });
      });

      document.getElementById("lineCount").addEventListener("change", () => {
        UIController.lastConfig = null;
        UIController.sendLogSettings();
      });

    // Change of the state of the live mode
      document.getElementById("liveMode").addEventListener("change", () => {
        UIController.clearLogPanel();
        UIController.lastConfig = null;
        if (!document.getElementById("liveMode").checked) {
          wsClient.close();
          initWebSocket();
        } else {
          UIController.sendLogSettings();
        }
      });

      document.getElementById("serverSelect").addEventListener("change", function() {
        UIController.clearLogPanel();
        UIController.lastConfig = null;
        updateFileSelect(this.value);
        wsClient.close();
        initWebSocket();
      });
    }

    static resetControls() {
      document.getElementById("lineCount").value = 1;
    }

    static handleDisplayModeChange() {
      UIController.clearLogPanel();
      const displayMode = document.querySelector('input[name="displayMode"]:checked').value;
      const partialOptions = document.getElementById("partialOptions");
      partialOptions.style.display = (displayMode === "partial") ? "flex" : "none";
    }

    static sendLogSettings() {
      const fileSelectValue = document.getElementById("fileSelect").value;
      const [group, fileChoice] = fileSelectValue.split('|');
      const displayMode = document.querySelector('input[name="displayMode"]:checked').value;
      const lineCount = document.getElementById("lineCount").value;
      const liveChecked = document.getElementById("liveMode").checked;

      let mode = "";
      if (displayMode === "complete") {
        mode = "complete";
      } else {
        mode = liveChecked ? `tail${lineCount}` : `partial${lineCount}`;
      }

      const newConfig = { group, fileChoice, mode };
      if (JSON.stringify(newConfig) !== JSON.stringify(UIController.lastConfig)) {
        UIController.clearLogPanel();
        UIController.lastConfig = newConfig;
      }

      wsClient.send({
        command: "subscribe",
        group: group,
        file: fileChoice,
        mode: mode
      });

      setTimeout(() => {
        if (UIController.logOutput.innerHTML.trim() === "") {
          if (!liveChecked) {
            UIController.logMessage("Fichier vide.", "server");
          } else {
            UIController.logMessage("Connecté en mode live. En attente de logs...", "server");
          }
        }
      }, 500);
    }

    static clearLogPanel() {
      this.logOutput.innerHTML = "";
      this.logContainer.scrollTop = 0;
    }

    static logMessage(message, sender) {
      const p = document.createElement("p");
      p.textContent = message;
      p.className = sender === "client" ? "message-client" : "message-server";
      this.logOutput.appendChild(p);
      this.logContainer.scrollTop = this.logContainer.scrollHeight;
    }

    static setLogContent(content) {
      this.logOutput.textContent = content;
      this.logContainer.scrollTop = this.logContainer.scrollHeight;
    }
  }

  function updateFileSelect(selectedServer) {
    const fileSelect = document.getElementById("fileSelect");
    fileSelect.innerHTML = "";
    if (wsLogsConfig[selectedServer]) {
      for (const group in wsLogsConfig[selectedServer]) {
        const optgroup = document.createElement("optgroup");
        optgroup.label = group.toUpperCase();
        const files = wsLogsConfig[selectedServer][group];
        for (const fileKey in files) {
           const option = document.createElement("option");
           option.value = group + '|' + fileKey;
           const filePath = files[fileKey];
           const fileName = filePath.split('/').pop();
           option.textContent = `${group.toUpperCase()} - ${fileName}`;
           optgroup.appendChild(option);
        }
        fileSelect.appendChild(optgroup);
      }
    }
  }

  let wsClient;
  function initWebSocket() {
    const serverSelect = document.getElementById("serverSelect");
    const selectedServer = serverSelect ? serverSelect.value : "";
    const wsPath = wsPaths[selectedServer] || "";
    const wsProto = (location.protocol === 'https:') ? 'wss://' : 'ws://';
    const wsUrl = wsProto + hostname + wsPath;

    wsClient = new MedullaWebSocket(wsUrl, {
      onConnect: function() {
        UIController.logMessage("WebSocket " + selectedServer + " connected.", "server");
        UIController.sendLogSettings();
      },
      onLog: function(data, mode) {
        if (data.trim() === "") {
          UIController.logMessage("Fichier vide.", "server");
        } else if (mode === "complete") {
          UIController.setLogContent(data);
        } else {
          UIController.logMessage(data, "server");
        }
      },
      onError: function() {
        UIController.logMessage("WebSocket error.", "server");
      }
    });
    wsClient.connect();
  }

  document.addEventListener("DOMContentLoaded", function() {
    UIController.init();
    const serverSelect = document.getElementById("serverSelect");
    updateFileSelect(serverSelect ? serverSelect.value : "");
    initWebSocket();
  });
