# Install the required .NET libraries
# You can run these commands in PowerShell to install the libraries
# Install-Package HtmlAgilityPack -Version 1.11.36
# Install-Package ReverseMarkdown -Version 2.2.0

# Load the required .NET assemblies
Add-Type -Path "path\to\HtmlAgilityPack.dll"
Add-Type -Path "path\to\ReverseMarkdown.dll"

# Function to convert HTML to Markdown
function Convert-HtmlToMarkdown {
    param (
        [string]$htmlContent
    )

    # Create an instance of the ReverseMarkdown converter
    $converter = New-Object ReverseMarkdown.Converter

    # Convert the HTML content to Markdown
    $markdownContent = $converter.Convert($htmlContent)

    return $markdownContent
}

# Read the HTML content from a file
$htmlFilePath = "path\to\your\file.html"
$htmlContent = Get-Content -Path $htmlFilePath -Raw

# Convert the HTML content to Markdown
$markdownContent = Convert-HtmlToMarkdown -htmlContent $htmlContent

# Write the Markdown content to a file
$markdownFilePath = "path\to\your\file.md"
Set-Content -Path $markdownFilePath -Value $markdownContent

Write-Output "HTML content has been successfully converted to Markdown and saved to $markdownFilePath"
