start transaction;

CREATE TABLE if not exists `Profile` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fk_imagingserver` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE if not exists  `ProfileInMenu` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fk_menuitem` int(11) NOT NULL,
  `fk_profile` int(11) NOT NULL,
  PRIMARY KEY (`id`)
);
CREATE TABLE if not exists  `PostInstallInProfile` (
  `fk_profile` int(11) NOT NULL,
  `fk_post_install_script` int(11) NOT NULL,
  `order` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`fk_profile`,`fk_post_install_script`)
);

CREATE TABLE if not exists  `PostInstallInMenu` (
  `fk_menuitem` int(11) NOT NULL,
  `fk_post_install_script` int(11) NOT NULL,
  PRIMARY KEY (`fk_menuitem`,`fk_post_install_script`)
);

update version set Number=28 where Number=27;
commit;