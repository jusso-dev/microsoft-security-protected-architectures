using './main.bicep'

param location = 'australiaeast'
param workspaceName = 'law-sentinel-protected-sample'
param retentionInDays = 90
param dailyQuotaGb = -1
param publicNetworkAccessForIngestion = 'Disabled'
param publicNetworkAccessForQuery = 'Disabled'
param deployPrivateLink = true
param enableDeleteLock = true
param enableDiagnosticSettings = true

// Replace placeholder GUIDs with Entra ID security group object IDs before deploying to a real environment.
// Leave empty ('') to skip an individual role assignment.
param sentinelReaderGroupObjectId = '00000000-0000-0000-0000-000000000001'
param sentinelResponderGroupObjectId = '00000000-0000-0000-0000-000000000002'
param sentinelContributorGroupObjectId = '00000000-0000-0000-0000-000000000003'
