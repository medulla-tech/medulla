--
-- (c) 2020 Siveo, http://www.siveo.net/
--
-- $Id$
--
-- This file is part of Pulse 2, http://www.siveo.net/
--
-- Pulse 2 is free software; you can redistribute it and/or modify
-- it under the terms of the GNU General Public License as published by
-- the Free Software Foundation; either version 2 of the License, or
-- (at your option) any later version.
--
-- Pulse 2 is distributed in the hope that it will be useful,
-- but WITHOUT ANY WARRANTY; without even the implied warranty of
-- MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
-- GNU General Public License for more details.
--
-- You should have received a copy of the GNU General Public License
-- along with Pulse 2; if not, write to the Free Software
-- Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
-- MA 02110-1301, USA.

--

START TRANSACTION;


DROP EVENT IF EXISTS purgelogs;
CREATE EVENT IF NOT EXISTS purgelogs
    ON SCHEDULE
        EVERY 1 DAY
        STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 5 HOUR
        COMMENT 'Clean each day at 4 hours olds records of 30 days on table logs. Si 1 deploy n est pas encore terminer, il n est pas supprimer'
    DO
        DELETE FROM xmppmaster.logs
        WHERE
            xmppmaster.logs.date < DATE_SUB(NOW(), INTERVAL 30 DAY)
            AND xmppmaster.logs.sessionname NOT IN (SELECT
                xmppmaster.deploy.sessionid
            FROM
                xmppmaster.deploy
            WHERE
                xmppmaster.deploy.endcmd > NOW());

DROP EVENT IF EXISTS purgehistorylogs;
CREATE EVENT IF NOT EXISTS purgehistorylogs
    ON SCHEDULE
        EVERY 1 DAY
        STARTS CURRENT_DATE + INTERVAL 1 DAY + INTERVAL 6 HOUR
    DO
        DELETE FROM historylogs WHERE date < DATE_SUB(NOW(), INTERVAL 60 DAY);

-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 76;

COMMIT;
