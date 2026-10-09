--
-- (c) 2026 Medulla, http://www.medulla-tech.io
--
-- SaaS Client-Admin profile for the first parallel onboarding entry.
-- The statements are idempotent and remain compatible with the legacy ACL
-- schema used by the current development instance.
--

SET NAMES utf8mb4;

USE admin;
START TRANSACTION;

CREATE TABLE IF NOT EXISTS acl_install_types (
    install_type VARCHAR(32) NOT NULL PRIMARY KEY,
    label VARCHAR(100) NOT NULL,
    display_order INT NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

INSERT INTO acl_install_types (install_type, label, display_order) VALUES
    ('onpremise', 'On-premise', 1),
    ('saas', 'SaaS', 2)
ON DUPLICATE KEY UPDATE label = VALUES(label), display_order = VALUES(display_order);

ALTER TABLE acl_feature_definitions
    ADD COLUMN IF NOT EXISTS install_types SET('onpremise','saas')
    NOT NULL DEFAULT 'onpremise,saas' AFTER access_type;

ALTER TABLE acl_profile_features
    ADD COLUMN IF NOT EXISTS install_type ENUM('onpremise','saas','both')
    NOT NULL DEFAULT 'both' AFTER access_level;

ALTER TABLE acl_profile_features DROP INDEX IF EXISTS uk_profile_feature;
ALTER TABLE acl_profile_features
    ADD UNIQUE KEY IF NOT EXISTS uk_profile_feature
    (profile_name, feature_key, install_type);

UPDATE acl_feature_definitions
     SET install_types = 'onpremise'
 WHERE feature_key = 'imaging_rw';

UPDATE acl_feature_definitions
     SET install_types = 'onpremise'
 WHERE feature_key = 'dashboard_superadmin_widgets';

UPDATE acl_feature_definitions
     SET install_types = 'onpremise'
 WHERE feature_key = 'inventory_machines'
     AND acl_entry IN ('base#computers#xmppMachinesList',
                                         'base#computers#ajaxXmppMachinesList');

UPDATE acl_feature_definitions
     SET install_types = 'onpremise'
 WHERE feature_key IN ('packaging_ro', 'packaging_rw',
                                             'package_deployment_admin', 'history');

UPDATE acl_feature_definitions
     SET install_types = 'onpremise'
 WHERE feature_key = 'admin_technician'
     AND acl_entry IN ('admin#admin#relaysList',
                                         'admin#admin#clustersList',
                                         'admin#admin#rules');

UPDATE acl_feature_definitions
     SET install_types = 'onpremise'
 WHERE feature_key = 'computer_management_rw'
     AND acl_entry IN ('security#security#settings',
                                         'security#security#settings#tabfilters',
                                         'security#security#settings#tabcves',
                                         'security#security#settings#tabsoftware',
                                         'security#security#settings#tabvendors',
                                         'security#security#settings#tabmachines',
                                         'security#security#settings#tabgroups');

DELETE FROM acl_profile_features WHERE feature_key LIKE 'imaging_onpremise_%';
DELETE FROM acl_feature_definitions WHERE feature_key LIKE 'imaging_onpremise_%';

INSERT INTO acl_feature_definitions
    (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types)
SELECT
    'admin_superadmin',
    'SaaS tenant management',
    'Manage SaaS tenants and their Client-Admin accounts.',
    'Administration',
    1,
    'admin#admin#itsmsync',
    'rw',
    'saas'
WHERE NOT EXISTS (
    SELECT 1 FROM acl_feature_definitions WHERE acl_entry = 'admin#admin#itsmsync'
);

INSERT INTO acl_feature_definitions
    (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types)
SELECT
    'admin_superadmin',
    'SaaS tenant management',
    'Manage SaaS tenants and their Client-Admin accounts.',
    'Administration',
    1,
    'admin#admin#editSaasClient',
    'rw',
    'saas'
WHERE NOT EXISTS (
    SELECT 1 FROM acl_feature_definitions WHERE acl_entry = 'admin#admin#editSaasClient'
);

INSERT INTO acl_feature_definitions
    (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types)
SELECT
    'admin_superadmin',
    'SaaS tenant management',
    'Edit the Client-Admin account of a SaaS tenant.',
    'Administration',
    1,
    'admin#admin#completeSaasClient',
    'rw',
    'saas'
WHERE NOT EXISTS (
    SELECT 1 FROM acl_feature_definitions WHERE acl_entry = 'admin#admin#completeSaasClient'
);

INSERT INTO acl_feature_definitions
    (feature_key, label, description, category, superadmin_only, acl_entry, access_type, install_types)
SELECT
    'admin_superadmin',
    'SaaS ITSM configuration',
    'Configure the external ITSM, API REST or LDAP connection of a SaaS tenant.',
    'Administration',
    1,
    'admin#admin#itsmformsync',
    'rw',
    'saas'
WHERE NOT EXISTS (
    SELECT 1 FROM acl_feature_definitions WHERE acl_entry = 'admin#admin#itsmformsync'
);

INSERT IGNORE INTO acl_profiles (profile_name, display_order)
SELECT 'Client-Admin', COALESCE(MAX(display_order), 0) + 1
FROM acl_profiles
WHERE NOT EXISTS (
    SELECT 1 FROM acl_profiles WHERE profile_name = 'Client-Admin'
);

INSERT IGNORE INTO acl_profile_features (profile_name, feature_key, access_level)
VALUES
    ('Client-Admin', 'dashboard_user_widgets', 'ro'),
    ('Client-Admin', 'inventory_machines', 'ro'),
    ('Client-Admin', 'groups_management_ro', 'ro'),
    ('Client-Admin', 'admin_admin', 'rw'),
    ('Client-Admin', 'computer_management_ro', 'ro'),
    ('Client-Admin', 'package_deployment_ro', 'ro'),
    ('Client-Admin', 'updates_ro', 'ro');

UPDATE version SET Number = 22 WHERE Number < 22;

COMMIT;

USE itsmlocal;
START TRANSACTION;

INSERT INTO glpi_profiles (
    name,
    interface,
    is_default,
    helpdesk_hardware,
    helpdesk_item_type,
    ticket_status,
    date_mod,
    comment,
    problem_status,
    create_ticket_on_login,
    tickettemplates_id,
    changetemplates_id,
    problemtemplates_id,
    change_status,
    managed_domainrecordtypes,
    date_creation
)
SELECT
    'Client-Admin',
    interface,
    is_default,
    helpdesk_hardware,
    helpdesk_item_type,
    ticket_status,
    date_mod,
    comment,
    problem_status,
    create_ticket_on_login,
    tickettemplates_id,
    changetemplates_id,
    problemtemplates_id,
    change_status,
    managed_domainrecordtypes,
    date_creation
FROM glpi_profiles
WHERE name = 'Observer'
  AND NOT EXISTS (
      SELECT 1 FROM glpi_profiles WHERE name = 'Client-Admin'
  )
LIMIT 1;

COMMIT;
