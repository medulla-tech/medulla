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


UPDATE version set Number = 2;

COMMIT;
