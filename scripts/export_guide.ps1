param(
    [string]$DocumentPath,
    [string]$PdfPath
)
$ErrorActionPreference = 'Stop'
$taskWord = New-Object -ComObject Word.Application
$taskWord.Visible = $false
$taskWord.DisplayAlerts = 0
$taskDocument = $null
try {
    $taskDocument = $taskWord.Documents.Open($DocumentPath, $false, $true)
    $taskDocument.Repaginate()
    $taskDocument.ExportAsFixedFormat($PdfPath, 17)
    Write-Output "Pages: $($taskDocument.ComputeStatistics(2))"
} finally {
    if ($null -ne $taskDocument) { $taskDocument.Close(0) }
    $taskWord.Quit()
    [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($taskWord)
}
