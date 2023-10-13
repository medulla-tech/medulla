DROP TABLE IF EXISTS machines;

CREATE TABLE IF NOT EXISTS machines(
   id_machines INT AUTO_INCREMENT,
   uuid_machine VARCHAR(100),
   nom VARCHAR(100),
   plateform VARCHAR(60)  NOT NULL,
   architecture VARCHAR(45),
   cpu INT,
   ram INT,
   state VARCHAR(50),
   persistent VARCHAR(50),
   PRIMARY KEY(id_machines)
);

CREATE TABLE IF NOT EXISTS has_guacamole(
   id_guac INT AUTO_INCREMENT,
   idguacamole VARCHAR(100),
   protocol VARCHAR(10),
   port INT,
   machine_name VARCHAR(50),
   id_machines INT NOT NULL,
   PRIMARY KEY(id_guac),
   UNIQUE(id_machines),
   UNIQUE(idguacamole),
   FOREIGN KEY (id_machines) REFERENCES machines(id_machines) ON DELETE CASCADE
);

UPDATE version SET Number = 2;
