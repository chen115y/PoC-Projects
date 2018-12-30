
create database VMS_Analytics;

use VMS_Analytics;

Create Table kenya_log_csv (
  ID int not null,
  Date varchar(20) null,
  Country varchar(20) null,
  VehID int null,
  Destination varchar(255) null,
  KmInit int null,
  KmFinal int null,
  FuelBought double null,
  AmountFuel double null,
  CashFuel double null,
  AmountCash double null,
  FuelKm int null,
  DriverID int null,
  PRIMARY KEY (ID)
 );
 
Create Table madagascar_log_csv (
  ID int not null,
  Date varchar(20) null,
  Country varchar(20) null,
  VehID int null,
  Destination varchar(255) null,
  KmInit int null,
  KmFinal int null,
  FuelBought double null,
  AmountFuel double null,
  CashFuel double null,
  AmountCash double null,
  FuelKm int null,
  DriverID int null,
  PRIMARY KEY (ID)
 );
 
Create Table nigeria_log_csv (
  ID int not null,
  Date varchar(20) null,
  Country varchar(20) null,
  VehID int null,
  Destination varchar(255) null,
  KmInit int null,
  KmFinal int null,
  FuelBought double null,
  AmountFuel double null,
  CashFuel double null,
  AmountCash double null,
  FuelKm int null,
  DriverID int null,
  PRIMARY KEY (ID)
 );
 
load data local infile 'c:/github/VMS_Analytics/datasets/Kenya_Log.csv' 
  into table kenya_log_csv fields terminated by ','
  ignore 1 rows (ID, Date, Country, VehID, Destination, KmInit, KmFinal, FuelBought, AmountFuel,CashFuel, AmountCash, FuelKm, DriverID)
 ;

Commit;

load data local infile 'c:/github/VMS_Analytics/datasets/Madagascar_Log.csv' 
  into table madagascar_log_csv fields terminated by ','
  ignore 1 rows (ID, Date, Country, VehID, Destination, KmInit, KmFinal, FuelBought, AmountFuel,CashFuel, AmountCash, FuelKm, DriverID)
 ;

Commit;

load data local infile 'c:/github/VMS_Analytics/datasets/Nigeria_Log.csv' 
  into table nigeria_log_csv fields terminated by ','
  ignore 1 rows (ID, Date, Country, VehID, Destination, KmInit, KmFinal, FuelBought, AmountFuel,CashFuel, AmountCash, FuelKm, DriverID)
 ;

Commit;

select * from madagascar_log_csv;

--truncate table kenya_log_csv;
