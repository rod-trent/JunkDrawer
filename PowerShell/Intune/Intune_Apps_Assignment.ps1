# Requires the Microsoft.Graph.Intune and Microsoft.Graph.Authentication modules
# Install them using Install-Module if necessary

# Step 1: Authenticate and Connect to Microsoft Graph
Connect-MgGraph -Scopes "DeviceManagementApps.ReadWrite.All"

# Step 2: Define the List of App IDs
$appIds = @("app_id_1", "app_id_2") # Replace with actual app IDs

# Step 3: Define the Assignment Parameters
$targetGroupId = "your_target_group_id" # Replace with your target group ID
$assignmentType = "required" # Can be "required" or "available"

# Step 4: Loop Through Each App ID
foreach ($appId in $appIds) {
    # Construct the assignment object
    $assignment = @{
        "@odata.type" = "#microsoft.graph.mobileAppAssignment"
        "target" = @{
            "@odata.type" = "#microsoft.graph.groupAssignmentTarget"
            "groupId" = $targetGroupId
        }
        "intent" = $assignmentType # Installation type
    }

    # Step 5: Send the Request to Add the Assignment
    try {
        $assignmentJson = $assignment | ConvertTo-Json
        $url = "https://graph.microsoft.com/v1.0/deviceAppManagement/mobileApps/$appId/assignments"
        $response = Invoke-MgGraphRequest -Method POST -Uri $url -Body $assignmentJson -ContentType "application/json"
        Write-Host "Assignment added successfully for app ID: $appId"
    } catch {
        Write-Host "Failed to add assignment for app ID: $appId. Error: $_"
    }
}

# Disconnect from Microsoft Graph
Disconnect-MgGraph
