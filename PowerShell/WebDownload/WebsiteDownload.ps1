# Define the base URL of the website to download
$baseUrl = "http://example.com"
# Define the output directory where the website will be saved
$outputDir = "C:\path\to\output\directory"

# Function to download a single URL
function Download-Url {
    param (
        [string]$url,
        [string]$outputPath
    )

    try {
        $response = Invoke-WebRequest -Uri $url -UseBasicParsing
        $content = $response.Content

        # Save the content to the output path
        $outputFile = Join-Path -Path $outputPath -ChildPath (Get-FileNameFromUrl -url $url)
        [System.IO.File]::WriteAllText($outputFile, $content)

        # Process links and assets
        $links = $response.Links | Where-Object { $_.href -like "http*" }
        foreach ($link in $links) {
            $linkUrl = $link.href
            $linkOutputPath = Join-Path -Path $outputPath -ChildPath (Get-FileNameFromUrl -url $linkUrl)
            Download-Url -url $linkUrl -outputPath $linkOutputPath
        }
    } catch {
        Write-Host ("Failed to download {0}: {1}" -f $url, $_.Exception.Message)
    }
}

# Function to get a file name from a URL
function Get-FileNameFromUrl {
    param (
        [string]$url
    )

    $uri = [System.Uri]::new($url)
    $fileName = [System.IO.Path]::GetFileName($uri.LocalPath)
    if ([string]::IsNullOrEmpty($fileName)) {
        $fileName = "index.html"
    }
    return $fileName
}

# Create the output directory if it doesn't exist
if (-not (Test-Path -Path $outputDir)) {
    New-Item -ItemType Directory -Path $outputDir
}

# Start downloading the website
Download-Url -url $baseUrl -outputPath $outputDir
