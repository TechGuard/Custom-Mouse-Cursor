$files = Get-ChildItem -Include *.cur,*.ani,*.inf -Recurse

# create zip file
$zipFileName = 'package.zip'
Remove-Item $zipFileName
$zip = [System.IO.Compression.ZipFile]::Open($zipFileName, [System.IO.Compression.ZipArchiveMode]::Create)

# write entries with relative paths as names
foreach ($fname in $files) {
    $rname = $(Resolve-Path -Path $fname -Relative) -replace '\.\\',''
    Write-Output $rname
    $zentry = $zip.CreateEntry($rname)
    $zentryWriter = New-Object -TypeName System.IO.BinaryWriter $zentry.Open()
    $zentryWriter.Write([System.IO.File]::ReadAllBytes($fname))
    $zentryWriter.Flush()
    $zentryWriter.Close()
}

$zip.Dispose()