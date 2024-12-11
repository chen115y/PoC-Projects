CREATE TABLE [dbo].[eol_eos_hardware](
      [assetId] [bigint] NULL,
      [hostId] [bigint] NULL,
      [assetName] [varchar](max) NULL,
      [assetType] [varchar](max) NULL,
      [address] [varchar](max) NULL,
      [operatingSystem] [varchar](max) NULL,
      [operatingSystem_eolDate] [varchar](max) NULL,
      [operatingSystem_eosDate] [varchar](max) NULL,
      [fullName] [varchar](max) NULL,
      [hardwareLifecycleObsoleteDate] [varchar](max) NULL,
      [hardwareLifecycleStage] [varchar](max) NULL,
      [hardwareLifecycleConfidence] [varchar](max) NULL,
      [Wyse_type] [bigint] NULL,
      [reportDate] [varchar](max) NULL,
      [eol_future] [bigint] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[eol_eos_operative_system](
      [assetId] [bigint] NULL,
      [hostId] [bigint] NULL,
      [assetName] [varchar](max) NULL,
      [assetType] [varchar](max) NULL,
      [address] [varchar](max) NULL,
      [timeZone] [varchar](max) NULL,
      [eolDate] [varchar](max) NULL,
      [eosDate] [varchar](max) NULL,
      [lifeCycleConfidence] [varchar](max) NULL,
      [lifeCycleStage] [varchar](max) NULL,
      [category] [varchar](max) NULL,
      [hardware] [varchar](max) NULL,
      [reportDate] [varchar](max) NULL,
      [eol_future] [bigint] NULL,
      [eos_future] [bigint] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[eol_eos_software](
      [fullName] [varchar](max) NULL,
      [category] [varchar](max) NULL,
      [gaDate] [varchar](max) NULL,
      [eolDate] [varchar](max) NULL,
      [eosDate] [varchar](max) NULL,
      [lifeCycleStage] [varchar](max) NULL,
      [lifeCycleConfidence] [varchar](max) NULL,
      [eolSupportStage] [varchar](max) NULL,
      [eosSupportStage] [varchar](max) NULL,
      [reportDate] [varchar](max) NULL,
      [eol_future] [bigint] NULL,
      [eos_future] [bigint] NULL,
      [software_instance_count] [bigint] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[software_instance_count](
      [fullName] [varchar](max) NULL,
      [software_instance_count] [bigint] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[software_pre_eol_eos](
      [fullName] [varchar](max) NULL,
      [category] [varchar](max) NULL,
      [gaDate] [varchar](max) NULL,
      [eolDate] [varchar](max) NULL,
      [eosDate] [varchar](max) NULL,
      [lifeCycleStage] [varchar](max) NULL,
      [lifeCycleConfidence] [varchar](max) NULL,
      [eolSupportStage] [varchar](max) NULL,
      [eosSupportStage] [varchar](max) NULL,
      [reportDate] [varchar](max) NULL,
      [eol_future] [bigint] NULL,
      [eos_future] [bigint] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[Q_Asset_Inventory](
      [assetId] [bigint] NULL,
      [assetUUID] [varchar](max) NULL,
      [hostId] [bigint] NULL,
      [lastModifiedDate] [varchar](max) NULL,
      [agentId] [varchar](max) NULL,
      [createdDate] [varchar](max) NULL,
      [sensorLastUpdatedDate] [varchar](max) NULL,
      [sensor_lastVMScanDate] [varchar](max) NULL,
      [sensor_lastComplianceScanDate] [varchar](max) NULL,
      [sensor_lastFullScanDate] [varchar](max) NULL,
      [sensor_lastPcScanDateAgent] [varchar](max) NULL,
      [sensor_lastPcScanDateScanner] [varchar](max) NULL,
      [sensor_lastVmScanDateAgent] [varchar](max) NULL,
      [sensor_lastVmScanDateScanner] [varchar](max) NULL,
      [inventory_createdDate] [varchar](max) NULL,
      [inventory_lastUpdatedDate] [varchar](max) NULL,
      [agent_lastActivityDate] [varchar](max) NULL,
      [agent_lastCheckedInDate] [varchar](max) NULL,
      [agent_lastInventoryDate] [varchar](max) NULL,
      [assetType] [varchar](max) NULL,
      [address] [varchar](max) NULL,
      [dnsName] [varchar](max) NULL,
      [assetName] [varchar](max) NULL,
      [netbiosName] [varchar](max) NULL,
      [timeZone] [varchar](max) NULL,
      [biosDescription] [varchar](max) NULL,
      [lastBoot] [varchar](max) NULL,
      [totalMemory] [varchar](max) NULL,
      [cpuCount] [varchar](max) NULL,
      [lastLoggedOnUser] [varchar](max) NULL,
      [domainRole] [varchar](max) NULL,
      [hwUUID] [varchar](max) NULL,
      [biosSerialNumber] [varchar](max) NULL,
      [biosAssetTag] [varchar](max) NULL,
      [isContainerHost] [varchar](max) NULL,
      [operatingSystem] [varchar](max) NULL,
      [hardware] [varchar](max) NULL,
      [userAccountListData] [varchar](max) NULL,
      [openPortListData] [varchar](max) NULL,
      [volumeListData] [varchar](max) NULL,
      [networkInterfaceListData] [varchar](max) NULL,
      [softwareListData] [varchar](max) NULL,
      [provider] [varchar](max) NULL,
      [cloudProvider] [varchar](max) NULL,
      [agent] [varchar](max) NULL,
      [sensor] [varchar](max) NULL,
      [container] [varchar](max) NULL,
      [inventory] [varchar](max) NULL,
      [activity] [varchar](max) NULL,
      [tagList] [varchar](max) NULL,
      [serviceList] [varchar](max) NULL,
      [lastLocation] [varchar](max) NULL,
      [criticality] [varchar](max) NULL,
      [businessInformation] [varchar](max) NULL,
      [assignedLocation] [varchar](max) NULL,
      [businessAppListData] [varchar](max) NULL,
      [riskScore] [varchar](max) NULL,
      [passiveSensor] [varchar](max) NULL,
      [domain] [varchar](max) NULL,
      [subdomain] [varchar](max) NULL,
      [whois] [varchar](max) NULL,
      [organizationName] [varchar](max) NULL,
      [isp] [varchar](max) NULL,
      [asn] [varchar](max) NULL,
      [easmTags] [varchar](max) NULL,
      [hostingCategory1] [varchar](max) NULL,
      [customAttributes] [varchar](max) NULL,
      [processor] [varchar](max) NULL,
      [missingSoftware] [varchar](max) NULL,
      [softwareComponent] [varchar](max) NULL,
      [BATCH_DATE] [varchar](max) NULL,
      [BATCH_NUMBER] [varchar](max) NULL,
      [Row_Last_Updated] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[Q_Asset_Inventory_Software_AssetId](
      [assetId] [bigint] NULL,
      [fullName] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[Q_Asset_Inventory_Software_OS_Unique](
      [fullName] [varchar](max) NULL,
      [osName] [varchar](max) NULL,
      [isIgnored] [varchar](max) NULL,
      [ignoredReason] [varchar](max) NULL,
      [category] [varchar](max) NULL,
      [gaDate] [varchar](max) NULL,
      [eolDate] [varchar](max) NULL,
      [eosDate] [varchar](max) NULL,
      [stage] [varchar](max) NULL,
      [lifeCycleConfidence] [varchar](max) NULL,
      [eolSupportStage] [varchar](max) NULL,
      [eosSupportStage] [varchar](max) NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[Q_Asset_Inventory_History](
      [assetId] [bigint] NULL,
      [assetUUID] [varchar](max) NULL,
      [hostId] [bigint] NULL,
      [lastModifiedDate] [varchar](max) NULL,
      [agentId] [varchar](max) NULL,
      [createdDate] [varchar](max) NULL,
      [sensorLastUpdatedDate] [varchar](max) NULL,
      [sensor_lastVMScanDate] [varchar](max) NULL,
      [sensor_lastComplianceScanDate] [varchar](max) NULL,
      [sensor_lastFullScanDate] [varchar](max) NULL,
      [sensor_lastPcScanDateAgent] [varchar](max) NULL,
      [sensor_lastPcScanDateScanner] [varchar](max) NULL,
      [sensor_lastVmScanDateAgent] [varchar](max) NULL,
      [sensor_lastVmScanDateScanner] [varchar](max) NULL,
      [inventory_createdDate] [varchar](max) NULL,
      [inventory_lastUpdatedDate] [varchar](max) NULL,
      [agent_lastActivityDate] [varchar](max) NULL,
      [agent_lastCheckedInDate] [varchar](max) NULL,
      [agent_lastInventoryDate] [varchar](max) NULL,
      [assetType] [varchar](max) NULL,
      [address] [varchar](max) NULL,
      [dnsName] [varchar](max) NULL,
      [assetName] [varchar](max) NULL,
      [netbiosName] [varchar](max) NULL,
      [timeZone] [varchar](max) NULL,
      [biosDescription] [varchar](max) NULL,
      [lastBoot] [varchar](max) NULL,
      [totalMemory] [varchar](max) NULL,
      [cpuCount] [varchar](max) NULL,
      [lastLoggedOnUser] [varchar](max) NULL,
      [domainRole] [varchar](max) NULL,
      [hwUUID] [varchar](max) NULL,
      [biosSerialNumber] [varchar](max) NULL,
      [biosAssetTag] [varchar](max) NULL,
      [isContainerHost] [varchar](max) NULL,
      [operatingSystem] [varchar](max) NULL,
      [hardware] [varchar](max) NULL,
      [userAccountListData] [varchar](max) NULL,
      [openPortListData] [varchar](max) NULL,
      [volumeListData] [varchar](max) NULL,
      [networkInterfaceListData] [varchar](max) NULL,
      [softwareListData] [varchar](max) NULL,
      [provider] [varchar](max) NULL,
      [cloudProvider] [varchar](max) NULL,
      [agent] [varchar](max) NULL,
      [sensor] [varchar](max) NULL,
      [container] [varchar](max) NULL,
      [inventory] [varchar](max) NULL,
      [activity] [varchar](max) NULL,
      [tagList] [varchar](max) NULL,
      [serviceList] [varchar](max) NULL,
      [lastLocation] [varchar](max) NULL,
      [criticality] [varchar](max) NULL,
      [businessInformation] [varchar](max) NULL,
      [assignedLocation] [varchar](max) NULL,
      [businessAppListData] [varchar](max) NULL,
      [riskScore] [varchar](max) NULL,
      [passiveSensor] [varchar](max) NULL,
      [domain] [varchar](max) NULL,
      [subdomain] [varchar](max) NULL,
      [whois] [varchar](max) NULL,
      [organizationName] [varchar](max) NULL,
      [isp] [varchar](max) NULL,
      [asn] [varchar](max) NULL,
      [easmTags] [varchar](max) NULL,
      [hostingCategory1] [varchar](max) NULL,
      [customAttributes] [varchar](max) NULL,
      [processor] [varchar](max) NULL,
      [missingSoftware] [varchar](max) NULL,
      [softwareComponent] [varchar](max) NULL,
      [BATCH_DATE] [varchar](max) NULL,
      [BATCH_NUMBER] [varchar](max) NULL,
      [Row_Last_Updated] [varchar](max) NULL,
      [report_date] [datetime] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[Q_Asset_Inventory_Software_AssetId_History](
      [assetId] [bigint] NULL,
      [fullName] [varchar](max) NULL,
      [report_date] [datetime] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[Q_Asset_Inventory_Software_OS_Unique_History](
      [fullName] [varchar](max) NULL,
      [osName] [varchar](max) NULL,
      [isIgnored] [varchar](max) NULL,
      [ignoredReason] [varchar](max) NULL,
      [category] [varchar](max) NULL,
      [gaDate] [varchar](max) NULL,
      [eolDate] [varchar](max) NULL,
      [eosDate] [varchar](max) NULL,
      [stage] [varchar](max) NULL,
      [lifeCycleConfidence] [varchar](max) NULL,
      [eolSupportStage] [varchar](max) NULL,
      [eosSupportStage] [varchar](max) NULL,
      [report_date] [datetime] NULL
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

CREATE TABLE [dbo].[report_01_eol_eos_apps_current](
      [report_date] [date] NOT NULL,
      [num_eol_apps] [int] NULL,
      [num_assets_affected] [int] NULL,
      [num_eos_apps] [int] NULL,
      [num_eos_assets] [int] NULL
) ON [PRIMARY]

CREATE TABLE [dbo].[report_02_eol_eos_apps_future](
      [report_date] [date] NOT NULL,
      [num_eol_apps] [int] NULL,
      [num_assets_affected] [int] NULL,
      [num_eos_apps] [int] NULL,
      [num_eos_assets] [int] NULL
) ON [PRIMARY]

CREATE TABLE [dbo].[report_03_eol_hardware](
      [report_date] [date] NOT NULL,
      [num_qualys_hw_reports] [int] NULL,
      [num_dell_wyse] [int] NULL,
      [num_total_eol_hw] [int] NULL
) ON [PRIMARY]

CREATE TABLE [dbo].[report_04_eol_hardware](
      [report_date] [date] NOT NULL,
      [num_eol_hardware] [int] NULL
) ON [PRIMARY]

CREATE TABLE [dbo].[report_05_eol_eos_operative_system_current](
      [report_date] [date] NOT NULL,
      [stage] [varchar](70) NULL,
      [os_name] [varchar](70) NULL,
      [num_eos_apps] [int] NULL
) ON [PRIMARY]

CREATE TABLE [dbo].[report_06_eol_eos_operative_system_future](
      [report_date] [date] NOT NULL,
      [stage] [varchar](70) NULL,
      [os_name] [varchar](70) NULL,
      [num_eos_apps] [int] NULL
) ON [PRIMARY]