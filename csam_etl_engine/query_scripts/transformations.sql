select t1.fullName, count(distinct t1.assetId) as software_instance_count  
FROM Q_Asset_Inventory_Software_AssetId t1
inner join Q_Asset_Inventory t2  on  t1.assetId = t2.assetId
inner join Q_Asset_Inventory_Software_OS_Unique t3 on t1.fullName = t3.fullName	
group by t1.fullName;

INSERT INTO [dbo].[software_pre_eol_eos]
SELECT DISTINCT
    T1.fullName,
    T2.category,
    T2.gaDate,
    T2.eolDate,
    T2.eosDate,
    T2.stage as lifeCycleStage, 
    T2.lifeCycleConfidence,
    t2.eolSupportStage,
    T2.eosSupportStage,
    GETDATE() as reportDate,
    CASE WHEN T2.eolDate is not null and T2.eolDate <> 'Not Announced' and convert(datetime, T2.eolDate, 127) BETWEEN GETDATE() AND DATEADD(year, 1, GETDATE()) THEN 1 ELSE 0 END AS eol_future,
    CASE WHEN T2.eosDate is not null and T2.eosDate <> 'Not Announced' and convert(datetime, T2.eosDate, 127) BETWEEN GETDATE() AND DATEADD(year, 1, GETDATE()) THEN 1 ELSE 0 END AS eos_future
FROM  Q_Asset_Inventory_Software_AssetId T1
INNER JOIN Q_Asset_Inventory_Software_OS_Unique T2
    ON T1.fullName = T2.fullName;

INSERT INTO [dbo].[eol_eos_software]
SELECT distinct pre.*, count.software_instance_count
FROM software_pre_eol_eos as pre
INNER JOIN software_instance_count as count 
ON pre.fullName = count.fullName;

TRUNCATE TABLE software_pre_eol_eos;

TRUNCATE TABLE software_instance_count;

INSERT INTO [dbo].[Q_Asset_Inventory_Software_AssetId_History]
SELECT *, GETDATE() as report_date FROM [dbo].[Q_Asset_Inventory_Software_AssetId];

INSERT INTO [dbo].[Q_Asset_Inventory_Software_OS_Unique_History]
SELECT *, GETDATE() as report_date FROM [dbo].[Q_Asset_Inventory_Software_OS_Unique];

INSERT INTO [dbo].[Q_Asset_Inventory_History]
SELECT *, GETDATE() as report_date FROM [dbo].[Q_Asset_Inventory];