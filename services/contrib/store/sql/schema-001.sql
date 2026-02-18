-- =============================================
-- Medulla Store Module - Schema local minimal
--
-- Note: Ce module se connecte à une base store DISTANTE (centralisée).
-- Les tables software, subscriptions, etc. sont sur le serveur Store.
-- Ce schema sert uniquement à la vérification de version locale.
-- =============================================

CREATE DATABASE IF NOT EXISTS store
  DEFAULT CHARACTER SET utf8mb4
  DEFAULT COLLATE utf8mb4_unicode_ci;

USE store;

-- Table de versioning (requise par le module pour le check de version)
CREATE TABLE IF NOT EXISTS version (
    Number TINYINT UNSIGNED NOT NULL DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO version (Number)
SELECT 1 WHERE NOT EXISTS (SELECT 1 FROM version);
