param(
    [string]$Root = "."
)

$ErrorActionPreference = "Stop"
$markdownFiles = Get-ChildItem -Path $Root -Recurse -File -Filter "*.md"
$broken = @()

foreach ($file in $markdownFiles) {
    $content = Get-Content -Path $file.FullName -Raw
    $matches = [regex]::Matches($content, "\[[^\]]+\]\(([^)]+)\)")

    foreach ($m in $matches) {
        $link = $m.Groups[1].Value.Trim()
        if ($link -match "^(http|https|mailto):") { continue }
        if ($link.StartsWith("#")) { continue }

        $clean = $link.Split("#")[0]
        if ([string]::IsNullOrWhiteSpace($clean)) { continue }

        $target = Join-Path $file.DirectoryName $clean
        if (-not (Test-Path $target)) {
            $broken += [PSCustomObject]@{
                File = $file.FullName
                Link = $link
            }
        }
    }
}

if ($broken.Count -eq 0) {
    Write-Host "No broken relative links found."
    exit 0
}

Write-Host "Broken links found:"
$broken | Format-Table -AutoSize
exit 1
