START TRANSACTION;

-- Schema 003: Retirer les filtres d'age et d'annee par defaut
-- Le filtrage se fait a l'affichage, pas au scan
-- 0 = pas de filtre (recuperer toutes les CVEs)

UPDATE `policies_defaults` SET `value` = '0' WHERE `category` = 'display' AND `key` = 'max_age_days';
UPDATE `policies_defaults` SET `value` = '0' WHERE `category` = 'display' AND `key` = 'min_published_year';

UPDATE `policies` SET `value` = '0', `updated_by` = 'system' WHERE `category` = 'display' AND `key` = 'max_age_days';
UPDATE `policies` SET `value` = '0', `updated_by` = 'system' WHERE `category` = 'display' AND `key` = 'min_published_year';

UPDATE `version` SET `Number` = 3;

COMMIT;
