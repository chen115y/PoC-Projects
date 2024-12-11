SELECT 
    assetId
	,hostId
	,assetName
	,assetType
	,address
	, timeZone
	, json_extract(operatingSystem, '$.lifecycle.eolDate') AS eolDate
	, json_extract(operatingSystem, '$.lifecycle.eosDate') AS eosDate
	, json_extract(operatingSystem, '$.lifecycle.lifeCycleConfidence') AS lifeCycleConfidence
	, json_extract(operatingSystem, '$.lifecycle.stage') AS lifeCycleStage
	, json_extract(operatingSystem, '$.category1') AS category
    , json_extract(hardware, '$.fullName') AS hardware 
    , datetime('now') AS reportDate
    , CASE WHEN DATE(json_extract(operatingSystem, '$.lifecycle.eolDate')) BETWEEN DATE('now') AND DATE('now', '+1 year') THEN 1 ELSE 0 END AS eol_future
    , CASE WHEN DATE(json_extract(operatingSystem, '$.lifecycle.eosDate')) BETWEEN DATE('now') AND DATE('now', '+1 year') THEN 1 ELSE 0 END AS eos_future
	FROM Q_Asset_Inventory