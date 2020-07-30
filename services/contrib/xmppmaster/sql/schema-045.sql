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

START TRANSACTION;


-- qa_relay_command => QA LIST
drop table if exists qa_relay_command;
create table if not exists qa_relay_command(
  id int not null auto_increment, primary key(id),
  user varchar(45) not null, -- IF allusers : GENERIC COMMAND
  name varchar(45) not null,
  script text not null,
  description varchar(45)
);

-- DEFAULT QA FOR RELAYS
insert into qa_relay_command(user, name, script, description) VALUES
('allusers', 'ejabberd connected infos', 'ejabberdctl connected_users_info', 'Get the connected users infos'),
('allusers', 'ejabberd registered user pulse', 'ejabberdctl registered_users pulse', 'Get registered users in pulse'),
('allusers', 'ejabberd status', 'ejabberdctl status', 'Get ejabberd status'),
('allusers', 'ejabberd get_offline master', 'ejabberdctl get_offline_count master pulse', 'Get the count of offline in master'),
('allusers', 'ejabberd get_offline master_asse', 'ejabberdctl get_offline_count master_asse pulse', 'Get the count of offline in master_asse'),
('allusers', 'ejabberd get_offline master_depl', 'ejabberdctl get_offline_count master_depl pulse', 'Get the count of offline in master_depl'),
('allusers', 'ejabberd get_offline master_inv', 'ejabberdctl get_offline_count master_inv pulse', 'Get the count of offline in master_inv'),
('allusers', 'ejabberd get_offline master_log', 'ejabberdctl get_offline_count master_log pulse', 'Get the count of offline in master_log'),
('allusers', 'ejabberd get_offline master_reg', 'ejabberdctl get_offline_count master_reg pulse', 'Get the count of offline in master_reg'),
('allusers', 'ejabberd get_offline master_subs', 'ejabberdctl get_offline_count master_subs pulse', 'Get the count of offline in master_subs');

-- qa_relay_launched => QA LAUNCHED BY USERS
drop table if exists qa_relay_launched;
create table if not exists qa_relay_launched(
  id int not null auto_increment, primary key(id),
  id_command int NULL, -- Which command
  user_command varchar(45) NULL, -- Who launched
  command_start datetime default NOW(), -- when
  command_cluster varchar(45) NULL, -- on which cluster ...
  command_relay varchar(45) NULL -- ... or mahcine
);

-- command_action => Historique des qa
drop table if exists qa_relay_result;
create table if not exists qa_relay_result(
  id int not null auto_increment, primary key(id),
  id_command int not null, -- Quick get a ref to the initial command
  launched_id int not null, -- Reference to the specialized command (launched command)
  session_id varchar(45) not null, -- xmpp session id
  typemessage varchar(20) not null default 'log',
  command_result text,
  relay varchar(45) not null -- If uniq command : relay, if cluster command : jid of the cluster member
);

-- ----------------------------------------------------------------------
-- Database add colunms
--    - relayserver : syncthing_port = 23000 ARS port syncthing deployment
-- ----------------------------------------------------------------------
ALTER TABLE `xmppmaster`.`relayserver`
ADD COLUMN `syncthing_port` INT(11) NULL DEFAULT '23000' AFTER `keysyncthing`;

ALTER TABLE `xmppmaster`.`logs` CHANGE COLUMN `fromuser` `fromuser` VARCHAR(255) NULL DEFAULT '' ;

UPDATE version SET Number = 45;

COMMIT;
