START TRANSACTION;


drop table if exists profiles;
create table if not exists profiles(
    id int not null auto_increment, primary key(id),
    entity_id int not null,
    profile_uuid varchar(255) not null,
    profile_name varchar(255) not null
);


drop table if exists machines_profiles;
create table if not exists machines_profiles(
    id int not null auto_increment, primary key(id),
    machine_jid varchar(50) not null default "",
    profile_id int not null
);

alter table client_state change state state int not null default 0;
alter table client_state add column client_jid varchar(255) not null after client_id;

alter table all_logs add column loglevel int not null default -1 after id;
alter table all_logs change `time` `time` int not null;
alter table all_logs add column client_id int not null after id;

create or replace index idx_msg on all_logs(msg);
create or replace index idx_client_id on all_logs(client_id);
create or replace index idx_time on all_logs(`time`);

alter table machines_profiles
    add constraint fk_profiles_machines_profile
    FOREIGN KEY (`profile_id`)
    REFERENCES profiles(id) on delete cascade;

UPDATE version set Number = 2;

COMMIT;
