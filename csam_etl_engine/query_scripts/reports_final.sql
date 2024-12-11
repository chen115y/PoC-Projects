------------------------------------
-- Report 1 Insert new row on reporting table
------------------------------------
with
report_1_eol_data as (
	select 
		max(sw.reportDate) reportDate,
		count(*) as total_eol_apps ,
		sum(sw.software_instance_count) as total_eol_assetss_affected
	from  [dbo].[eol_eos_software]  as sw 
	where 
		sw.lifeCycleStage <> 'GA' -- Filter on pivot table
		and sw.eol_future = 0 -- 0 means current software
		and sw.eosDate is not null  -- have a date available
		and sw.eosDate <> 'Not Announced'

	group by sw.reportDate
),
report_1_eos_data as (
	select 
		max(sw.reportDate) reportDate,
		count(*) as total_eos_apps ,
		sum(sw.software_instance_count) as total_eos_assetss_affected
	from [eol_eos_software] as sw 
	where 
		1 = 1 
		and sw.lifeCycleStage = 'EOL/EOS' 
		and sw.eol_future = 0 -- 0 means current software
		and sw.eolDate is not null -- have a date available
		and sw.eolDate <> 'Not Announced'
	group by sw.reportDate
	)

Insert into report_01_eol_eos_apps_current

select 
	cast(t1.reportDate as date) as report_date,
	t1.total_eol_apps,
	t1.total_eol_assetss_affected,
	t2.total_eos_apps,
	t2.total_eos_assetss_affected
from 
	report_1_eol_data t1
inner join  report_1_eos_data t2
	on t1.reportDate = t2.reportDate;

------------------------------------
-- Report 2 Insert new row on reporting table
------------------------------------
-- EOL Future
with
report_02_eol_data as (
	select 
		max(sw.reportDate) as reportDate,   
		count(*) as total_eol_apps ,
		sum(sw.software_instance_count) as total_eol_assetss_affected
	from  [dbo].[eol_eos_software]  as sw 
	where 
		sw.eolDate is not null 
		and sw.eolDate <> 'Not Announced'
		and sw.eol_future = 1 -- this means is future eos  = true (within next calendar year from running the report)
	group by sw.reportDate
),
report_02_eos_data as (
	select 
		max(sw.reportDate) as reportDate,   
		count(*) as total_eos_apps ,
		sum(sw.software_instance_count) as total_eos_assetss_affected
	from  [dbo].[eol_eos_software]  as sw 
	where 
		sw.eosDate is not null 
		and sw.eosDate <> 'Not Announced'
		and sw.eos_future = 1 -- this means is future eos  = true (within next calendar year from running the report)
	group by sw.reportDate
	)

Insert into report_02_eol_eos_apps_future

select 
	cast(t1.reportDate as date) as report_date,
	t1.total_eol_apps,
	t1.total_eol_assetss_affected,
	t2.total_eos_apps,
	t2.total_eos_assetss_affected
from 
	report_02_eol_data t1
inner join  report_02_eos_data t2
	on t1.reportDate = t2.reportDate;

------------------------------------
-- Report 3 Insert new row on reporting table
------------------------------------
with
report_03_qualys_hw as (
	SELECT
	count(*) as total_from_qualys_hw,
	max(reportDate) as reportDate
	FROM  eol_eos_hardware
	where 
		hardwareLifecycleObsoleteDate is not null 
		and hardwareLifecycleObsoleteDate <> 'Not Announced' 
		and eol_future = 0 
		and Wyse_type = 0
	group by reportDate 
	),
report_03_dell_wyse as (
	SELECT
	count(*) as total_dell_wyse,
	max(reportDate) as reportDate
	FROM  eol_eos_hardware
	where 
		hardwareLifecycleObsoleteDate is not null 
		and hardwareLifecycleObsoleteDate <> 'Not Announced' 
		and eol_future = 0 
		and Wyse_type = 1
	group by reportDate 
	union all
	-- if there is no rows on above querey still create a record with 
	-- date and 0 as count
	select 
		0 as total_dell_wyse,
		max(reportDate) reportDate
	from eol_eos_hardware
	where 
		not exists (select assetId where 
		hardwareLifecycleObsoleteDate is not null 
		and hardwareLifecycleObsoleteDate <> 'Not Announced' 
		and eol_future = 0 
		and Wyse_type = 0)
)

insert into report_03_eol_hardware

select 
	cast(t1.reportDate as date) as report_date,
	t1.total_from_qualys_hw,
	t2.total_dell_wyse,
	t1.total_from_qualys_hw + t2.total_dell_wyse as total
from 
	report_03_qualys_hw t1
inner join  report_03_dell_wyse t2
	on t1.reportDate = t2.reportDate;

------------------------------------
-- Report 4 Insert new row on reporting table
------------------------------------

Insert into report_04_eol_hardware

	select 
	cast(max(t1.reportDate) as date) as report_date,
	count(*) num_eol_hardware
	from eol_eos_hardware t1
	where eol_future = 1
	group by reportDate ;


------------------------------------
-- Report 5 Insert new row on reporting table
------------------------------------
-- EOL Current
-------------------------------
with report_5 as(
select 
	substring(max(reportDate),1, 10) as report_date, 
	'EOL' as stage, 
	case 
		when category = 'Virtualization' then 'VMWare' 
		when category = 'Network Operating System' then 'Cisco' 
		else category 
	end as os_name,
	count(*) count
from 
	[dbo].[eol_eos_operative_system] 
where eolDate is not null 
	and eolDate <> 'Not Announced' 
	and eol_future = 0
	and lifeCycleStage like 'EOL%' 
group by reportDate, category

union 
-------------------------------
-- EOS Current
-------------------------------
select 
	substring(max(reportDate),1, 10) as report_date, 
	'EOS' as stage, 
	case 
		when category = 'Virtualization' then 'VMWare'
		when category = 'Network Operating System' then 'Cisco' 
		else category 
	end as os_name,
	count(*) count
from 
	[dbo].[eol_eos_operative_system] 
where eosDate is not null 
	and eosDate <> 'Not Announced' 
	--and eos_future = 0
	and lifeCycleStage like 'EOL%' 
	and eosDate < reportDate
group by reportDate, category
)

Insert into report_05_eol_eos_operative_system_current

select 
	cast(t1.report_date as date) as report_date,
	t1.stage,
	t1.os_name,
	t1.count
from report_5 t1;


------------------------------------
-- Report 6 Insert new row on reporting table
------------------------------------
-- EOL Future
-------------------------------
with report_6 as(
select 
	substring(max(reportDate),1, 10) as report_date, 
	'EOL' as stage, 
	case when category = 'Virtualization' then 'VMWare' 
		when category = 'Network Operating System' then 'Cisco' 
		else category 
	end as os_name,
	count(*) count
from 
	[dbo].[eol_eos_operative_system] 
where eolDate is not null 
	and eolDate <> 'Not Announced' 
	and eol_future = 1
group by reportDate, category

union 
-------------------------------
-- EOS Future
-------------------------------
select 
	substring(max(reportDate),1, 10) as report_date, 
	'EOS' as stage, 
	case when category = 'Virtualization' then 'VMWare'
		when category = 'Network Operating System' then 'Cisco' 
	else category 
	end as os_name,
	count(*) count
from 
	[dbo].[eol_eos_operative_system] 
where eosDate is not null 
	and eosDate <> 'Not Announced' 
	and eos_future = 1
group by reportDate, category
)

Insert into report_06_eol_eos_operative_system_future

select 
	cast(t1.report_date as date) as report_date,
	t1.stage,
	t1.os_name,
	t1.count
from report_6 t1;