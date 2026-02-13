
-- Define template for possibles actions.
-- The template is copied, not linked
drop table if exists actionTemplates;
create table if not exists actionTemplates(
    id int not null auto_increment, primary key(id),
    name varchar(50) not null,
    description varchar(255) null default "",
    content text default ""
);

insert into actionTemplates (name, content, description) VALUES("Continue", "exit", "Normal boot");

insert into actionTemplates(name, content, description) VALUES("Mastering", "set url_path http://${next-server}/downloads/davos/
set kernel_args boot=live config noswap edd=on nomodeset raid=noautodetect fetch=${url_path}fs.squashfs davos_action=XMPP davos_subaction=CREATE_MASTER mac=${mac}  timereboot=2 initrd=initrd.img
kernel ${url_path}vmlinuz ${kernel_args}
initrd ${url_path}initrd.img
boot || exit", "Create Master");

insert into actionTemplates(name, content, description) values("Deploy Master", "set url_path http://\${next-server}/downloads/davos/
set kernel_args boot=live config noswap edd=on nomodeset nosplash noprompt vga=788 fetch=${url_path}fs.squashfs mac=${mac} davos_action=XMPP davos_subaction=RESTORE_IMAGE image_uuid=###MASTER_UUID### initrd=initrd.img
kernel ${url_path}vmlinuz ${kernel_args}
initrd ${url_path}initrd.img
boot || exit", "Restore a master", "Deploy Master");

drop table if exists os;
create table if not exists os(
    id int not null auto_increment, primary key(id),
    name varchar(100) not null,
);

insert into os (name, type) VALUES("Unknown");
insert into os (name, type) VALUES("Windows 10 Pro");
insert into os (name, type) VALUES("Windows 10 OEM");
insert into os (name, type) VALUES("Windows 11 Pro");
insert into os (name, type) VALUES("Windows 11 OEM");
insert into os (name, type) VALUES("Debian 12");
insert into os (name, type) VALUES("Debian 13");

drop table if exists masters;
create table if not exists masters(
    id int not null auto_increment, primary key(id),
    name varchar(100) not null default "",
    description varchar(255) null default "",
    uuid varchar(50) not null,
    path varchar(255) not null,
    size bigint default 0,
    creation_date datetime default NOW(),
    modification_date datetime NULL
);

drop table if exists mastersEntities;
create table if not exists mastersEntities(
    id_master int not null,
    id_entity int not null
);


drop table if exists scripts;
create table if not exists scripts(
    id int not null auto_increment, primary key(id),
    name varchar(50) not null,
    content text default "",
    creation_date datetime default NOW(),
    modification_date datetime NULL
);

drop table if exists scriptsEntities;
create table if not exists scriptsEntities(
    id int not null auto_increment, primary key(id),
    id_script int not null,
    id_entity varchar(50) not NULL
);



drop table if exists actionMachines;
create table if not exists actionMachines(
    id int not null auto_increment, primary key(id),
    uuid varchar(50) not null COMMENT "The Machine uuid",
    session_id varchar(30) not null default "" COMMENT "Use this sessionid to find xmpp related logs and actions",
    name varchar(50) not null,
    content text default "" COMMENT "Store the action to do as json",
    result text default "",
    status varchar(50) default "TODO",
    date_creation datetime default NOW(),
    date_start datetime default NOW(),
    date_end datetime default NULL
);

drop table if exists actionGroups;
create table if not exists actionGroups(
    id int not null auto_increment, primary key(id),
    gid varchar(50) not null,
    session_id varchar(30) not null default "" COMMENT "Use this sessionid to find xmpp related logs and actions",
    name varchar(50) not null,
    content text default "" COMMENT "Store the action to do as json",
    result text default "",
    status varchar(50) default "TODO",
    date_creation datetime default NOW(),
    date_start datetime default NOW(),
    date_end datetime default NULL
);
