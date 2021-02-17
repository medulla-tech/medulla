--
-- (c) 2021 Siveo, http://www.siveo.net/
--
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
USE xmppmaster;

DELIMITER //
CREATE OR REPLACE PROCEDURE countSuccessRateLastSixWeeks(
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
  set @partial = 0;

  select @total:=count(id) from deploy where startcmd >= (NOW()-INTERVAL 1 WEEK);
  select @partial:=count(id) from deploy where state="DEPLOYMENT SUCCESS" and startcmd >= (NOW()-INTERVAL 1 WEEK);
  select if(@total >0, (@partial/@total)*100, 0) into week1;

  -- week - 2
  set @total = 0;
  set @partial = 0;

  select @total:=count(id) from deploy where startcmd < (NOW()-INTERVAL 1 WEEK) and startcmd >= (NOW()-INTERVAL 2 WEEK);
  select @partial:=count(id) from deploy where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 1 WEEK) and startcmd >= (NOW()-INTERVAL 2 WEEK);
  select if(@total >0, (@partial/@total)*100, 0) into week2;

  -- week - 3
  set @total = 0;
  set @partial = 0;

  select @total:=count(id) from deploy where startcmd < (NOW()-INTERVAL 2 WEEK) and startcmd >= (NOW()-INTERVAL 3 WEEK);
  select @partial:=count(id) from deploy where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 2 WEEK) and startcmd >= (NOW()-INTERVAL 3 WEEK);
  select if(@total >0, (@partial/@total)*100, 0) into week3;

  -- week - 4
  set @total = 0;
  set @partial = 0;

  select @total:=count(id) from deploy where startcmd < (NOW()-INTERVAL 3 WEEK) and startcmd >= (NOW()-INTERVAL 4 WEEK);
  select @partial:=count(id) from deploy where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 3 WEEK) and startcmd >= (NOW()-INTERVAL 4 WEEK);
  select if(@total >0, (@partial/@total)*100, 0) into week4;

  -- week - 5
  set @total = 0;
  set @partial = 0;

  select @total:=count(id) from deploy where startcmd < (NOW()-INTERVAL 4 WEEK) and startcmd >= (NOW()-INTERVAL 5 WEEK);
  select @partial:=count(id) from deploy where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 4 WEEK) and startcmd >= (NOW()-INTERVAL 5 WEEK);
  select if(@total >0, (@partial/@total)*100, 0) into week5;

  -- week - 6
  set @total = 0;
  set @partial = 0;

  select @total:=count(id) from deploy where startcmd < (NOW()-INTERVAL 5 WEEK) and startcmd >= (NOW()-INTERVAL 6 WEEK);
  select @partial:=count(id) from deploy where state="DEPLOYMENT SUCCESS" and startcmd < (NOW()-INTERVAL 5 WEEK) and startcmd >= (NOW()-INTERVAL 6 WEEK);
  select if(@total >0, (@partial/@total)*100, 0) into week6;

end;
//

CREATE OR REPLACE PROCEDURE countDeployLastSixMonths()
begin
set @month1 = 0;
set @month2 = 0;
set @month3 = 0;
set @month4 = 0;
set @month5 = 0;
set @month6 = 0;

-- current month
set @date_end = NOW();
set @date_begin = convert(concat(YEAR(@date_end),'-',MONTH(@date_end),'-',1,' ', 0,':',0,':',0), datetime);
select @month1:=count(id) from deploy where startcmd >= @date_begin and startcmd <= @date_end;

set @date_end = DATE_SUB(@date_begin, INTERVAL 1 SECOND);
set @date_begin = convert(concat(YEAR(@date_end),'-',MONTH(@date_end),'-',1,' ', 0,':',0,':',0), datetime);
select @month2:=count(id) from deploy where startcmd >= @date_begin and startcmd <= @date_end;

set @date_end = DATE_SUB(@date_begin, INTERVAL 1 SECOND);
set @date_begin = convert(concat(YEAR(@date_end),'-',MONTH(@date_end),'-',1,' ', 0,':',0,':',0), datetime);
select @month3:=count(id) from deploy where startcmd >= @date_begin and startcmd <= @date_end;

set @date_end = DATE_SUB(@date_begin, INTERVAL 1 SECOND);
set @date_begin = convert(concat(YEAR(@date_end),'-',MONTH(@date_end),'-',1,' ', 0,':',0,':',0), datetime);
select @month4:=count(id) from deploy where startcmd >= @date_begin and startcmd <= @date_end;

set @date_end = DATE_SUB(@date_begin, INTERVAL 1 SECOND);
set @date_begin = convert(concat(YEAR(@date_end),'-',MONTH(@date_end),'-',1,' ', 0,':',0,':',0), datetime);
select @month5:=count(id) from deploy where startcmd >= @date_begin and startcmd <= @date_end;

set @date_end = DATE_SUB(@date_begin, INTERVAL 1 SECOND);
set @date_begin = convert(concat(YEAR(@date_end),'-',MONTH(@date_end),'-',1,' ', 0,':',0,':',0), datetime);
select @month6:=count(id) from deploy where startcmd >= @date_begin and startcmd <= @date_end;

end;
//
DELIMITER ;


UPDATE version SET Number = 57;

COMMIT;
