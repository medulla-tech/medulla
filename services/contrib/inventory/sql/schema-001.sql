--
-- (c) 2008 Mandriva, http://www.mandriva.com/
--
-- $Id$
--
-- This file is part of Pulse 2, http://pulse2.mandriva.org
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
-- Table structure for table `Bios`
--

CREATE TABLE Bios (
  id int(10) unsigned NOT NULL auto_increment,
  Serial varchar(64) default NULL,
  Chipset varchar(32) default NULL,
  BiosVersion varchar(64) default NULL,
  ChipSerial varchar(32) default NULL,
  ChipVendor varchar(32) default NULL,
  BiosVendor varchar(64) default NULL,
  TypeMachine varchar(32) default NULL,
  SmbManufacturer varchar(32) default NULL,
  SmbProduct varchar(32) default NULL,
  SmbVersion varchar(32) default NULL,
  SmbSerial varchar(32) default NULL,
  SmbUUID varchar(32) default NULL,
  SmbType varchar(32) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

CREATE INDEX bios_serial_idx ON `Bios` (Serial(64));

--
-- Table structure for table `Controller`
--

CREATE TABLE Controller (
  id int(10) unsigned NOT NULL auto_increment,
  Vendor varchar(128) default NULL,
  ExpandedType varchar(32) default NULL,
  HardwareVersion varchar(16) default NULL,
  StandardType varchar(16) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

CREATE INDEX controller_expandedType_idx ON `Controller` (ExpandedType(32));
CREATE INDEX controller_vendor_idx ON `Controller` (Vendor(128));
CREATE INDEX controller_hardwareVersion_idx ON `Controller` (HardwareVersion(16));
CREATE INDEX controller_standardType_idx ON `Controller` (StandardType(16));

--
-- Table structure for table `CustomField`
--

CREATE TABLE CustomField (
  id mediumint(9) unsigned NOT NULL auto_increment,
  machine mediumint(9) unsigned NOT NULL default '0',
  Field varchar(32) NOT NULL default '',
  Value varchar(255) NOT NULL default '',
  PRIMARY KEY  (id),
  KEY machine (machine),
  KEY Keyf (Field)
) ENGINE=MYISAM;

--
-- Table structure for table `Drive` (Logical drives)
--

CREATE TABLE Drive (
  id int(11) unsigned NOT NULL auto_increment,
  DriveLetter varchar(4) default NULL,
  DriveType varchar(32) default NULL,
  TotalSpace mediumint(16) default NULL,
  FreeSpace mediumint(16) default NULL,
  VolumeName varchar(16) default NULL,
  FileSystem varchar(16) default NULL,
  FileCount mediumint(16) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Hardware`
--

CREATE TABLE Hardware (
  id int(11) unsigned NOT NULL auto_increment,
  OperatingSystem varchar(64) default NULL,
  Version varchar(32) default NULL,
  Build varchar(64) default NULL,
  ProcessorType varchar(128) default NULL,
  ProcessorFrequency varchar(8) default NULL,
  ProcessorCount tinyint(2) default NULL,
  RamTotal varchar(8) default NULL,
  SwapSpace varchar(8) default NULL,
  IpAddress varchar(64) default NULL,
  Date date default NULL,
  User varchar(32) default NULL,
  Workgroup varchar(32) default NULL,
  RegisteredName varchar(32) default NULL,
  RegisteredCompany varchar(32) default NULL,
  OSSerialNumber varchar(32) default NULL,
  Description varchar(64) default NULL,
  Type varchar(32) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Input`
--

CREATE TABLE Input (
  id int(11) unsigned NOT NULL auto_increment,
  Type varchar(32) default NULL,
  StandardDescription varchar(128) default NULL,
  ExpandedDescription varchar(128) default NULL,
  Connector varchar(8) default NULL,
  Manufacturer varchar(64) default NULL,
  PointType varchar(64) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Inventory`
--

CREATE TABLE Inventory (
  id mediumint(8) unsigned NOT NULL auto_increment,
  Date date NOT NULL default '0000-00-00',
  Time time NOT NULL default '00:00:00',
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Machine`
--

CREATE TABLE Machine (
  id mediumint(9) unsigned NOT NULL auto_increment,
  Name varchar(32) default NULL,
  lastId mediumint(8) unsigned,
  lastBootId mediumint(8) unsigned,
  lastCustomId mediumint(8) unsigned,
  lastNmapId mediumint(8) unsigned,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Memory`
--

CREATE TABLE Memory (
  id int(11) unsigned NOT NULL auto_increment,
  ExtendedDescription varchar(32) default NULL,
  Size mediumint(8) default NULL,
  ChipsetType varchar(32) default NULL,
  Frequency varchar(8) default NULL,
  SlotCount varchar(16) default NULL,
  Description varchar(64) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Modem`
--

CREATE TABLE Modem (
  id int(11) unsigned NOT NULL auto_increment,
  Vendor varchar(32) default NULL,
  ExpandedDescription varchar(32) default NULL,
  Type varchar(32) default NULL,
  Model varchar(64) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Monitor`
--

CREATE TABLE Monitor (
  id int(11) unsigned NOT NULL auto_increment,
  Stamp varchar(64) default NULL,
  Description varchar(64) default NULL,
  Type varchar(64) default NULL,
  Serial varchar(32) default NULL,
  Manuf varchar(32) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Network`
--

CREATE TABLE Network (
  id int(11) unsigned NOT NULL auto_increment,
  CardType varchar(64) default NULL,
  NetworkType varchar(32) default NULL,
  MIB varchar(32) default NULL,
  Bandwidth varchar(16) default NULL,
  MACAddress varchar(64) default NULL,
  State varchar(16) default NULL,
  IP varchar(16) default NULL,
  SubnetMask varchar(16) default NULL,
  Gateway varchar(16) default NULL,
  DNS varchar(16) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Pci`
--

CREATE TABLE Pci (
  id int(11) unsigned NOT NULL auto_increment,
  Bus int(11) default NULL,
  Func varchar(8) default NULL,
  Vendor varchar(32) default NULL,
  Device varchar(128) default NULL,
  Class varchar(32) default NULL,
  Type varchar(32) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Port`
--

CREATE TABLE Port (
  id int(11) unsigned NOT NULL auto_increment,
  Stamp varchar(16) default NULL,
  Type varchar(32) default NULL,
  Caption varchar(32) default NULL,
  Description varchar(32) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Printer`
--

CREATE TABLE Printer (
  id int(11) unsigned NOT NULL auto_increment,
  Name varchar(32) default NULL,
  Driver varchar(64) default NULL,
  Port varchar(64) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Slot`
--

CREATE TABLE Slot (
  id int(11) unsigned NOT NULL auto_increment,
  Connector varchar(8) default NULL,
  PortType varchar(16) default NULL,
  Availability varchar(16) default NULL,
  State varchar(16) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Software`
--

CREATE TABLE Software (
  id int(11) unsigned NOT NULL auto_increment,
  ProductPath varchar(255) default NULL,
  ProductName varchar(64) default NULL,
  ExecutableSize int(10) unsigned default NULL,
  Company varchar(32) default NULL,
  Application varchar(32) default NULL,
  Type varchar(32) default NULL,
  ProductVersion varchar(32) default NULL,
  Comments varchar(255) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

CREATE INDEX soft_ProductPath_idx ON Software (ProductPath(255));
CREATE INDEX soft_ProductName_idx ON Software (ProductName(64));
CREATE INDEX soft_ExecutableSize_idx ON Software (ExecutableSize);
CREATE INDEX soft_Company_idx ON Software (Company(32));
CREATE INDEX soft_Application_idx ON Software (Application(32));
CREATE INDEX soft_Type_idx ON Software (Type(32));
CREATE INDEX soft_ProductVersion_idx ON Software (ProductVersion(32));
CREATE INDEX soft_Comments_idx ON Software (Comments(255));


--
-- Table structure for table `Sound`
--

CREATE TABLE Sound (
  id int(11) unsigned NOT NULL auto_increment,
  Name varchar(64) default NULL,
  Description varchar(128) default NULL,
  Manufacturer varchar(128) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

CREATE INDEX sound_name_idx ON Sound (Name(64));
CREATE INDEX sound_description_idx ON Sound (Description(128));
CREATE INDEX sound_manufacturer_idx ON Sound (Manufacturer(128));

--
-- Table structure for table `Storage`
--

CREATE TABLE Storage (
  id int(11) unsigned NOT NULL auto_increment,
  ExtendedType varchar(32) default NULL,
  Model varchar(32) default NULL,
  VolumeName varchar(32) default NULL,
  Media varchar(32) default NULL,
  StandardType varchar(32) default NULL,
  Manufacturer varchar(64) default NULL,
  DiskSize varchar(32) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `Version`
--

CREATE TABLE Version (
  Number tinyint(4) unsigned NOT NULL default '0'
) ENGINE=MYISAM;

--
-- Table structure for table `VideoCard`
--

CREATE TABLE VideoCard (
  id int(11) unsigned NOT NULL auto_increment,
  Model varchar(255) default NULL,
  Chipset varchar(255) default NULL,
  VRAMSize mediumint(8) default NULL,
  Resolution varchar(255) default NULL,
  PRIMARY KEY  (id)
) ENGINE=MYISAM;

--
-- Table structure for table `hasBios`
--

CREATE TABLE hasBios (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  bios int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,bios)
) ENGINE=MYISAM;

--
-- Table structure for table `hasController`
--

CREATE TABLE hasController (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  controller int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,controller)
) ENGINE=MYISAM;

--
-- Table structure for table `hasDrive`
--

CREATE TABLE hasDrive (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  drive int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,drive)
) ENGINE=MYISAM;

--
-- Table structure for table `hasHardware`
--

CREATE TABLE hasHardware (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  hardware int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,hardware)
) ENGINE=MYISAM;

--
-- Table structure for table `hasInput`
--

CREATE TABLE hasInput (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  input int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,input)
) ENGINE=MYISAM;

--
-- Table structure for table `hasMemory`
--

CREATE TABLE hasMemory (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  memory int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,memory)
) ENGINE=MYISAM;

--
-- Table structure for table `hasModem`
--

CREATE TABLE hasModem (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  modem int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,modem)
) ENGINE=MYISAM;

--
-- Table structure for table `hasMonitor`
--

CREATE TABLE hasMonitor (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  monitor int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,monitor)
) ENGINE=MYISAM;

--
-- Table structure for table `hasNetwork`
--

CREATE TABLE hasNetwork (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  network int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,network)
) ENGINE=MYISAM;

--
-- Table structure for table `hasPci`
--

CREATE TABLE hasPci (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  pci int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,pci)
) ENGINE=MYISAM;


--
-- Table structure for table `hasPort`
--

CREATE TABLE hasPort (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  port int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,port)
) ENGINE=MYISAM;

--
-- Table structure for table `hasPrinter`
--

CREATE TABLE hasPrinter (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  printer int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,printer)
) ENGINE=MYISAM;

--
-- Table structure for table `hasSlot`
--

CREATE TABLE hasSlot (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  slot int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,slot)
) ENGINE=MYISAM;

--
-- Table structure for table `hasSoftware`
--

CREATE TABLE hasSoftware (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  software int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,software)
) ENGINE=MYISAM;

CREATE INDEX hassoft_machine_idx ON hasSoftware (machine);
CREATE INDEX hassoft_inventory_idx ON hasSoftware (inventory);
CREATE INDEX hassoft_software_idx ON hasSoftware (software);

--
-- Table structure for table `hasSound`
--

CREATE TABLE hasSound (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  sound int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,sound)
) ENGINE=MYISAM;

--
-- Table structure for table `hasStorage`
--

CREATE TABLE hasStorage (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  storage int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,storage)
) ENGINE=MYISAM;

--
-- Table structure for table `hasVideoCard`
--

CREATE TABLE hasVideoCard (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  videocard int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,videocard)
) ENGINE=MYISAM;

--
--
--

CREATE TABLE IF NOT EXISTS BootGeneral (
  id int(10) unsigned NOT NULL auto_increment,
  MacAddr varchar(32) default NULL,
  LowMem INT default '0',
  HighMem BIGINT default '0',
  TotalMem BIGINT default '0',
  CpuVendor varchar(32) default NULL,
  Model varchar(64) default NULL,
  Freq varchar(32) default NULL,
  System varchar(255) default NULL,
  Bios varchar(255) default NULL,
  MiscSMB varchar(255) default NULL,
  MiscMem varchar(255) default NULL,
  CpuNum INT default '1',
  Chassis varchar(64) default NULL,
  PRIMARY KEY  (id)
);

CREATE TABLE IF NOT EXISTS hasBootGeneral (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  bootgeneral int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,bootgeneral)
);

CREATE TABLE IF NOT EXISTS BootPCI (
  id int(10) unsigned NOT NULL auto_increment,
  Num INT default NULL,
  Bus INT default '0',
  Func varchar(8) default NULL,
  Vendor varchar(64) default NULL,
  Device varchar(255) default NULL,
  Class varchar(64) default NULL,
  Type varchar(64) default NULL,
  PRIMARY KEY  (id)
);

CREATE TABLE IF NOT EXISTS hasBootPCI (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  bootpci int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,bootpci)
);

CREATE TABLE IF NOT EXISTS BootDisk (
  id int(10) unsigned NOT NULL auto_increment,
  Num INT default '-1',
  Name varchar(32) default NULL,
  Cyl INT default '0',
  Head INT default '0',
  Sector INT default '0',
  Capacity INT default '0',
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS hasBootDisk (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  bootdisk int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,bootdisk)
);

CREATE TABLE IF NOT EXISTS BootPart (
  id int(10) unsigned NOT NULL auto_increment,
  Disk INT default '-1',
  Num INT default '-1',
  Type varchar(32) default NULL,
  Length INT default '0',
  Flag varchar(32) default NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS hasBootPart (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  bootpart int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,bootpart)
);

CREATE TABLE IF NOT EXISTS BootMem (
  id int(10) unsigned NOT NULL auto_increment,
  Used INT default '0',
  Location varchar(32) default NULL,
  Form varchar(16) default NULL,
  Type varchar(32) default NULL,
  Speed INT default NULL,
  Capacity INT default NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS hasBootMem (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  bootmem int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,bootmem)
);


CREATE TABLE IF NOT EXISTS Custom (
  id int(10) unsigned NOT NULL auto_increment,
  BuyDate DATE default NULL,
  DeliveryDate DATE default NULL,
  WorkingDate DATE default NULL,
  WarrantyEnd DATE default NULL,
  SupportEnd DATE default NULL,
  Department varchar(32) default NULL,
  Location varchar(32) default NULL,
  Phone varchar(32) default NULL,
  Comments varchar(255) default NULL,
  BuyValue DOUBLE default NULL,
  ResidualValue DOUBLE default NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS hasCustom (
  machine mediumint(9) unsigned NOT NULL default '0',
  inventory mediumint(5) unsigned NOT NULL default '0',
  custom int(11) unsigned NOT NULL default '0',
  PRIMARY KEY  (machine,inventory,custom)
);

CREATE INDEX machine ON hasBios(machine);
CREATE INDEX machine ON hasBootDisk(machine);
CREATE INDEX machine ON hasBootGeneral(machine);
CREATE INDEX machine ON hasBootMem(machine);
CREATE INDEX machine ON hasBootPCI(machine);
CREATE INDEX machine ON hasBootPart(machine);
CREATE INDEX machine ON hasController(machine);
CREATE INDEX machine ON hasCustom(machine);
CREATE INDEX machine ON hasDrive(machine);
CREATE INDEX machine ON hasHardware(machine);
CREATE INDEX machine ON hasInput(machine);
CREATE INDEX machine ON hasMemory(machine);
CREATE INDEX machine ON hasModem(machine);
CREATE INDEX machine ON hasMonitor(machine);
CREATE INDEX machine ON hasNetwork(machine);
CREATE INDEX machine ON hasPort(machine);
CREATE INDEX machine ON hasPrinter(machine);
CREATE INDEX machine ON hasSlot(machine);
CREATE INDEX machine ON hasSoftware(machine);
CREATE INDEX machine ON hasSound(machine);
CREATE INDEX machine ON hasStorage(machine);
CREATE INDEX machine ON hasVideoCard(machine);

CREATE INDEX inventory ON hasBios(inventory);
CREATE INDEX inventory ON hasBootDisk(inventory);
CREATE INDEX inventory ON hasBootGeneral(inventory);
CREATE INDEX inventory ON hasBootMem(inventory);
CREATE INDEX inventory ON hasBootPCI(inventory);
CREATE INDEX inventory ON hasBootPart(inventory);
CREATE INDEX inventory ON hasController(inventory);
CREATE INDEX inventory ON hasCustom(inventory);
CREATE INDEX inventory ON hasDrive(inventory);
CREATE INDEX inventory ON hasHardware(inventory);
CREATE INDEX inventory ON hasInput(inventory);
CREATE INDEX inventory ON hasMemory(inventory);
CREATE INDEX inventory ON hasModem(inventory);
CREATE INDEX inventory ON hasMonitor(inventory);
CREATE INDEX inventory ON hasNetwork(inventory);
CREATE INDEX inventory ON hasPort(inventory);
CREATE INDEX inventory ON hasPrinter(inventory);
CREATE INDEX inventory ON hasSlot(inventory);
CREATE INDEX inventory ON hasSoftware(inventory);
CREATE INDEX inventory ON hasSound(inventory);
CREATE INDEX inventory ON hasStorage(inventory);
CREATE INDEX inventory ON hasVideoCard(inventory);

CREATE INDEX bios ON hasBios(bios);
CREATE INDEX bootdisk ON hasBootDisk(bootdisk);
CREATE INDEX bootgeneral ON hasBootGeneral(bootgeneral);
CREATE INDEX bootmem ON hasBootMem(bootmem);
CREATE INDEX bootpci ON hasBootPCI(bootpci);
CREATE INDEX bootpart ON hasBootPart(bootpart);
CREATE INDEX controller ON hasController(controller);
CREATE INDEX custom ON hasCustom(custom);
CREATE INDEX drive ON hasDrive(drive);
CREATE INDEX hardware ON hasHardware(hardware);
CREATE INDEX input ON hasInput(input);
CREATE INDEX memory ON hasMemory(memory);
CREATE INDEX modem ON hasModem(modem);
CREATE INDEX monitor ON hasMonitor(monitor);
CREATE INDEX network ON hasNetwork(network);
CREATE INDEX port ON hasPort(port);
CREATE INDEX printer ON hasPrinter(printer);
CREATE INDEX slot ON hasSlot(slot);
CREATE INDEX software ON hasSoftware(software);
CREATE INDEX sound ON hasSound(sound);
CREATE INDEX storage ON hasStorage(storage);
CREATE INDEX videocard ON hasVideoCard(videocard);


--
-- Database version
--
INSERT INTO Version VALUES( '1' );
