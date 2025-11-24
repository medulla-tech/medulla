--
-- (c) 2025, http://www.medulla-tech.io/
--
--
-- This file is part of Pulse 2, http://www.medulla-tech.io/
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
-- FILE contrib/xmppmaster/sql/schema-096.sql
-- =======================================
-- Database xmppmaster
-- =======================================

START TRANSACTION;
USE `xmppmaster`;

-- This is an update for the stored procedure countSuccessRateLastSixWeeks from schema-076. It takes a list of entities ids separated by comma
DELIMITER //
CREATE OR REPLACE PROCEDURE countSuccessRateLastSixWeeks(IN entities varchar(255),
  OUT week1 float,
  OUT week2 float,
  OUT week3 float,
  OUT week4 float,
  OUT week5 float,
  OUT week6 float
)
begin

  -- week - 1
  set @total = 0;
  set @notstarted = 0;
  set @success = 0;

  select @total:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where startcmd >= (NOW()-INTERVAL 1 WEEK) and glpi_entity.glpi_id in (entities);
  select @notstarted:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state in ("ABORT DEPLOYMENT CANCELLED BY USER", "ABORT INCONSISTENT GLPI INFORMATION", "ABORT MISSING AGENT", "ABORT ON TIMEOUT", "WAITING MACHINE ONLINE") and startcmd >= (NOW()-INTERVAL 1 WEEK) and glpi_entity.glpi_id in (entities);
  select @success:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state="DEPLOYMENT SUCCESS" and startcmd >= (NOW()-INTERVAL 1 WEEK) and glpi_entity.glpi_id in (entities);
  select if((@total-@notstarted) >0, (@success/(@total-@notstarted))*100, 0) into week1;

  -- week - 2
  set @total = 0;
  set @notstarted = 0;
  set @success = 0;

  select @total:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where startcmd < (NOW()-INTERVAL 1 WEEK) and startcmd >= (NOW()-INTERVAL 2 WEEK) and glpi_entity.glpi_id in (entities);
  select @notstarted:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state in ("ABORT DEPLOYMENT CANCELLED BY USER", "ABORT INCONSISTENT GLPI INFORMATION", "ABORT MISSING AGENT", "ABORT ON TIMEOUT", "WAITING MACHINE ONLINE") and startcmd < (NOW()-INTERVAL 1 WEEK) and startcmd >= (NOW()-INTERVAL 2 WEEK) and glpi_entity.glpi_id in (entities);
  select @success:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 1 WEEK) and startcmd >= (NOW()-INTERVAL 2 WEEK) and glpi_entity.glpi_id in (entities);
  select if((@total-@notstarted) >0, (@success/(@total-@notstarted))*100, 0) into week2;

  -- week - 3
  set @total = 0;
  set @notstarted = 0;
  set @success = 0;

  select @total:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where startcmd < (NOW()-INTERVAL 2 WEEK) and startcmd >= (NOW()-INTERVAL 3 WEEK) and glpi_entity.glpi_id in (entities);
  select @notstarted:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state in ("ABORT DEPLOYMENT CANCELLED BY USER", "ABORT INCONSISTENT GLPI INFORMATION", "ABORT MISSING AGENT", "ABORT ON TIMEOUT", "WAITING MACHINE ONLINE") and startcmd < (NOW()-INTERVAL 2 WEEK) and startcmd >= (NOW()-INTERVAL 3 WEEK) and glpi_entity.glpi_id in (entities);
  select @success:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 2 WEEK) and startcmd >= (NOW()-INTERVAL 3 WEEK) and glpi_entity.glpi_id in (entities);
  select if((@total-@notstarted) >0, (@success/(@total-@notstarted))*100, 0) into week3;

  -- week - 4
  set @total = 0;
  set @notstarted = 0;
  set @success = 0;

  select @total:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where startcmd < (NOW()-INTERVAL 3 WEEK) and startcmd >= (NOW()-INTERVAL 4 WEEK) and glpi_entity.glpi_id in (entities);
  select @notstarted:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state in ("ABORT DEPLOYMENT CANCELLED BY USER", "ABORT INCONSISTENT GLPI INFORMATION", "ABORT MISSING AGENT", "ABORT ON TIMEOUT", "WAITING MACHINE ONLINE") and startcmd < (NOW()-INTERVAL 3 WEEK) and startcmd >= (NOW()-INTERVAL 4 WEEK) and glpi_entity.glpi_id in (entities);
  select @success:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 3 WEEK) and startcmd >= (NOW()-INTERVAL 4 WEEK) and glpi_entity.glpi_id in (entities);
  select if((@total-@notstarted) >0, (@success/(@total-@notstarted))*100, 0) into week4;

  -- week - 5
  set @total = 0;
  set @notstarted = 0;
  set @success = 0;

  select @total:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where startcmd < (NOW()-INTERVAL 4 WEEK) and startcmd >= (NOW()-INTERVAL 5 WEEK) and glpi_entity.glpi_id in (entities);
  select @notstarted:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state in ("ABORT DEPLOYMENT CANCELLED BY USER", "ABORT INCONSISTENT GLPI INFORMATION", "ABORT MISSING AGENT", "ABORT ON TIMEOUT", "WAITING MACHINE ONLINE") and startcmd < (NOW()-INTERVAL 4 WEEK) and startcmd >= (NOW()-INTERVAL 5 WEEK) and glpi_entity.glpi_id in (entities);
  select @success:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 4 WEEK) and startcmd >= (NOW()-INTERVAL 5 WEEK) and glpi_entity.glpi_id in (entities);
  select if((@total-@notstarted) >0, (@success/(@total-@notstarted))*100, 0) into week5;
  -- week - 6
  set @total = 0;
  set @notstarted = 0;
  set @success = 0;

  select @total:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where startcmd < (NOW()-INTERVAL 5 WEEK) and startcmd >= (NOW()-INTERVAL 6 WEEK) and glpi_entity.glpi_id in (entities);
  select @notstarted:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state in ("ABORT DEPLOYMENT CANCELLED BY USER", "ABORT INCONSISTENT GLPI INFORMATION", "ABORT MISSING AGENT", "ABORT ON TIMEOUT", "WAITING MACHINE ONLINE") and startcmd < (NOW()-INTERVAL 5 WEEK) and startcmd >= (NOW()-INTERVAL 6 WEEK) and glpi_entity.glpi_id in (entities);
  select @success:=count(deploy.id) from deploy join machines on deploy.jidmachine=machines.jid join glpi_entity on machines.glpi_entity_id=glpi_entity.id where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 5 WEEK) and startcmd >= (NOW()-INTERVAL 6 WEEK) and glpi_entity.glpi_id in (entities);
  select if((@total-@notstarted) >0, (@success/(@total-@notstarted))*100, 0) into week6;

end;
//
DELIMITER ;


-- ----------------------------------------------------------------------
-- Database version
-- ----------------------------------------------------------------------
UPDATE version SET Number = 97;


commit;
