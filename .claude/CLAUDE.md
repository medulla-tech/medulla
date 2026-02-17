# Medulla Web - Refactoring CSS

## Règles importantes

**Ne jamais commiter** - C'est l'utilisateur qui s'en charge. Proposer uniquement un message de commit.

---

## Objectif
Nettoyer et uniformiser les styles CSS de l'application Medulla.

## Architecture CSS cible

```
web/
├── graph/
│   ├── master.css          # Point d'entrée, importe global.css
│   └── global.css          # Styles généraux (variables, boutons, formulaires, tables, etc.)
│
└── modules/
    ├── dashboard/
    │   └── graph/css/dashboard.css    ✅ FAIT
    ├── admin/
    │   └── graph/css/admin.css        ⬜ À FAIRE
    ├── base/
    │   └── graph/css/base.css         ⬜ À FAIRE
    ├── glpi/
    │   └── graph/css/glpi.css         ⬜ À FAIRE
    ├── imaging/
    │   └── graph/css/imaging.css      ⬜ À FAIRE
    ├── inventory/
    │   └── graph/css/inventory.css    ⬜ À FAIRE
    ├── kiosk/
    │   └── graph/css/kiosk.css        ⬜ À FAIRE
    ├── msc/
    │   └── graph/css/msc.css          ⬜ À FAIRE (existe déjà, à nettoyer)
    ├── mobile/
    │   └── graph/css/mobile.css       ⬜ À FAIRE
    ├── pkgs/
    │   └── graph/css/pkgs.css         ⬜ À FAIRE
    ├── security/
    │   └── graph/css/security.css     ⬜ À FAIRE
    ├── updates/
    │   └── graph/css/updates.css      ⬜ À FAIRE (existe index.css, à renommer/nettoyer)
    ├── urbackup/
    │   └── graph/css/urbackup.css     ⬜ À FAIRE
    ├── xmppmaster/
    │   └── graph/css/xmppmaster.css   ⬜ À FAIRE
    └── dyngroup/
        └── graph/css/dyngroup.css     ⬜ À FAIRE
```

## Règles de nettoyage

### 1. Styles inline à retirer
- Chercher tous les `style="..."` dans les fichiers PHP
- Déplacer vers le fichier CSS du module concerné
- Utiliser des classes CSS à la place

### 2. Organisation des styles
- **global.css** : Variables CSS, reset, typography, boutons (.btn), formulaires, tables (.listinfos), searchbox, navbar, sidebar, layout général
- **module.css** : Styles spécifiques au module uniquement

### 3. Conventions de nommage
- Classes en kebab-case : `.my-class-name`
- Préfixer les classes spécifiques au module : `.dashboard-widget`, `.pkgs-form`, etc.
- Utiliser les variables CSS définies dans `:root` de global.css

### 4. Inclusion des CSS dans les pages
```php
// Dans le fichier PHP du module
echo '<link rel="stylesheet" href="modules/<module>/graph/css/<module>.css" type="text/css" media="screen" />';
```

## Progression

| Module | Status | Notes |
|--------|--------|-------|
| dashboard | ✅ Fait | dashboard.css créé, drawer widget |
| admin | ⬜ À faire | |
| base | ⬜ À faire | computers, users, groups |
| glpi | ⬜ À faire | machinesList styles |
| imaging | ⬜ À faire | Beaucoup de styles inline |
| inventory | ⬜ À faire | |
| kiosk | ⬜ À faire | |
| msc | ⬜ À faire | msc.css existe, à nettoyer |
| mobile | ⬜ À faire | configurationDetails a des styles inline |
| pkgs | ⬜ À faire | |
| security | ⬜ À faire | |
| updates | ⬜ À faire | index.css existe |
| urbackup | ⬜ À faire | |
| xmppmaster | ⬜ À faire | Beaucoup de styles inline |
| dyngroup | ⬜ À faire | |

## Commandes utiles

### Trouver les styles inline dans un module
```bash
grep -r 'style="' web/modules/<module>/ --include="*.php"
```

### Trouver les balises <style> dans un module
```bash
grep -r '<style' web/modules/<module>/ --include="*.php"
```
