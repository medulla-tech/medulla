<?php
$sidemenu = new SideMenu();
$sidemenu->setClass('security');

$sidemenu->addSideMenuItem(
    new SideMenuItem(_T('Synthèse CVE', 'security'), 'security', 'security', 'index')
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T('Résultats (liste)', 'security'), 'security', 'security', 'list')
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T('Résultats par machine', 'security'), 'security', 'security', 'by_machine')
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T('Paramètres', 'security'), 'security', 'security', 'settings')
);
