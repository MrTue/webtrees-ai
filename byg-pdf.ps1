# byg-pdf.ps1 - saetter hver SLAEGTSHISTORIEN*.md i projektroden som bog (titelblad, indhold,
# tavler, billedklip) til en PDF med samme basisnavn: SLAEGTSHISTORIEN-X.md -> SLAEGTSHISTORIEN-X.pdf.
# Billedklippene hentes fra mediemappen (miljoevariablen WEBTREES_MEDIA); er den vaek, kommer
# der en graa pladsholder og en advarsel, men PDF'en bliver bygget alligevel.
# Python findes som 'python' paa PATH; saet $env:PYTHON for at bruge en anden fortolker.
$py = if ($env:PYTHON) { $env:PYTHON } else { "python" }
Set-Location $PSScriptRoot
$filer = Get-ChildItem -Path $PSScriptRoot -Filter "SLAEGTSHISTORIEN*.md" -File | Where-Object { $_.Extension -eq ".md" } | Sort-Object Name
if (-not $filer) {
    Write-Host "Ingen SLAEGTSHISTORIEN*.md i $PSScriptRoot"
    exit 1
}
foreach ($f in $filer) {
    $ud = [IO.Path]::ChangeExtension($f.Name, ".pdf")
    & $py arkiv\mdpdf.py --bog $f.Name $ud
    if ($LASTEXITCODE -ne 0) { Write-Host "FEJL: $($f.Name) kunne ikke bygges"; exit $LASTEXITCODE }
}
