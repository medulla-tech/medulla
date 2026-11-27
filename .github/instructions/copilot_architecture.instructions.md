---
applyTo: "**"
---
# Repository architecture: medulla

A functional module usually spans three places that share the same module name: a Python server plugin, a PHP web module and SQL files.

| Path | Content |
|---|---|
| `services/mmc/plugins/<module>/` | Server plugins (Python), one per functional module |
| `services/pulse2/` | Shared server libraries (`database`, `apis`, `managers`, `inventoryserver`, `package_server`, `imaging`) |
| `services/contrib/<module>/` | Module resources, including SQL files |
| `services/bin/`, `services/conf/`, `services/systemd/`, `services/init.d/` | Server scripts, configuration and service files |
| `web/modules/<module>/` | Web interface modules (PHP) |
| `web/includes/`, `web/jsframework/`, `web/3rd_party/` | Shared web code and third-party libraries |
| `agent/` | Scripts, configuration and tools (`bin`, `conf`, `backup-tools`, `man`) |
| `debian/`, `debian13/`, `packaging/` | Packaging |
| `doc/`, `tools/` | Documentation and tools |

Rules:

- Keep module names identical across plugin, web module and SQL files.
- Put a change in the module it belongs to. Do not move code between modules unless asked.
- Never add data from a real infrastructure (host names, addresses, accounts) to the repository.
