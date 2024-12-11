SELECT 
    assetId,
    hostId,
    assetName,
    assetType,
    address,
    json_extract(operatingSystem, '$.osName') AS operatingSystem,
    json_extract(operatingSystem, '$.lifecycle.eolDate') AS operatingSystem_eolDate,
	json_extract(operatingSystem, '$.lifecycle.eosDate') AS operatingSystem_eosDate,
    json_extract(hardware, '$.fullName') AS fullName,
    json_extract(hardware, '$.lifecycle.obsoleteDate') AS hardwareLifecycleObsoleteDate,
    json_extract(hardware, '$.lifecycle.stage') AS hardwareLifecycleStage,
    json_extract(hardware, '$.lifecycle.lifeCycleConfidence') AS hardwareLifecycleConfidence,
    CASE 
        WHEN assetName LIKE '%wes%' THEN 1 -- update for wyse machines pattern
        ELSE 0
    END AS Wyse_type,
    datetime('now') AS reportDate,
    CASE WHEN DATE(json_extract(hardware, '$.lifecycle.obsoleteDate')) BETWEEN DATE('now') AND DATE('now', '+1 year') THEN 1 ELSE 0 END AS eol_future
FROM Q_Asset_Inventory