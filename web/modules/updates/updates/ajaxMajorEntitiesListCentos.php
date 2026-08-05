<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxMajorEntitiesListCentos.php

/*
 * Onglet "CentOS" de la page "Montees de version".
 *
 * Le code est commun a toutes les distributions : il vit dans
 * ajaxMajorEntitiesListDistribution.php. Ce fichier ne porte que les deux
 * parametres qui distinguent cet onglet.
 */
$distribution      = "centos";
$distributionLabel = "CentOS";

require("modules/updates/updates/ajaxMajorEntitiesListDistribution.php");
