CREATE DATABASE dyngroup;
USE dyngroup;

CREATE TABLE SqlDatumSave (id INT NOT NULL AUTO_INCREMENT, k TEXT NOT NULL, value TEXT, PRIMARY KEY(id));

alter table SqlDatumSave add column user Text;

insert into SqlDatumSave (k, value) values ('id', 1);

