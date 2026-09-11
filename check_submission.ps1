# =====================================================================
#  ISDS 2026 submission check - one command, all verification.
#
#  Usage (PowerShell, in this folder):
#      .\check_submission.ps1
#
#  If PowerShell blocks the script:
#      powershell -ExecutionPolicy Bypass -File .\check_submission.ps1
#
#  Does: compile x2 -> page count -> PDF size -> LaTeX warnings ->
#        figure check -> parameter verification -> PASS/FAIL summary.
# =====================================================================

$ErrorActionPreference = "Continue"
Set-Location -Path $PSScriptRoot

$Main       = "ISDS2026_FGSS_compact"
$MinPages   = 12
$MaxPages   = 15
$MaxSizeMB  = 10

function Head($t) {
    Write-Host ""
    Write-Host ("=" * 68) -ForegroundColor Cyan
    Write-Host "  $t" -ForegroundColor Cyan
    Write-Host ("=" * 68) -ForegroundColor Cyan
}
function Pass($m) { Write-Host "  [PASS] $m" -ForegroundColor Green }
function Fail($m) { Write-Host "  [FAIL] $m" -ForegroundColor Red }
function Warn($m) { Write-Host "  [WARN] $m" -ForegroundColor Yellow }
function Info($m) { Write-Host "         $m" -ForegroundColor Gray }

$results = @()

# ---------------------------------------------------------------- pdflatex
Head "1. Locating pdflatex"

$pdflatex = $null
if (Get-Command pdflatex -ErrorAction SilentlyContinue) {
    $pdflatex = "pdflatex"
    Pass "found on PATH"
} else {
    $guesses = @(
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe",
        "$env:LOCALAPPDATA\Programs\MiKTeX\miktex\bin\pdflatex.exe",
        "C:\Program Files\MiKTeX\miktex\bin\x64\pdflatex.exe",
        "C:\texlive\2025\bin\windows\pdflatex.exe",
        "C:\texlive\2024\bin\windows\pdflatex.exe"
    )
    foreach ($g in $guesses) {
        if (Test-Path $g) { $pdflatex = $g; Pass "found at $g"; break }
    }
}
if (-not $pdflatex) {
    Fail "pdflatex not found. Install MiKTeX or add it to PATH, then re-run."
    exit 1
}

# ---------------------------------------------------------------- compile
Head "2. Compiling $Main.tex (two passes)"

for ($i = 1; $i -le 2; $i++) {
    Write-Host "  pass $i of 2 ..." -NoNewline
    & $pdflatex -interaction=nonstopmode -halt-on-error "$Main.tex" > "_pass$i.txt" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ok" -ForegroundColor Green
    } else {
        Write-Host " FAILED" -ForegroundColor Red
        Fail "compile error on pass $i"
        Info "First error from the log:"
        $err = Select-String -Path "$Main.log" -Pattern '^!' | Select-Object -First 5
        if ($err) { $err | ForEach-Object { Write-Host "         $($_.Line)" -ForegroundColor Red } }
        Info "Full log: $Main.log   (search for the first '!')"
        exit 1
    }
}
Remove-Item "_pass1.txt","_pass2.txt" -ErrorAction SilentlyContinue
$results += "compile:OK"

# ---------------------------------------------------------------- pages
Head "3. Page count (ISDS limit: $MinPages-$MaxPages for a long paper)"

$pages = $null
$m = Select-String -Path "$Main.log" -Pattern 'Output written on .*\((\d+) pages?' |
     Select-Object -Last 1
if ($m) { $pages = [int]$m.Matches[0].Groups[1].Value }

if ($null -eq $pages) {
    Warn "could not read the page count from the log"
} elseif ($pages -ge $MinPages -and $pages -le $MaxPages) {
    Pass "$pages pages - within the limit"
    $results += "pages:OK($pages)"
} elseif ($pages -gt $MaxPages) {
    Fail "$pages pages - OVER the $MaxPages-page limit by $($pages - $MaxPages)"
    Info "Tell Claude the number; there is more that can be cut in the Method section."
    $results += "pages:OVER($pages)"
} else {
    Warn "$pages pages - UNDER the $MinPages-page minimum for a long paper"
    $results += "pages:UNDER($pages)"
}

# ---------------------------------------------------------------- size
Head "4. PDF size (EasyChair often caps uploads at $MaxSizeMB MB)"

if (Test-Path "$Main.pdf") {
    $mb = [math]::Round((Get-Item "$Main.pdf").Length / 1MB, 2)
    if ($mb -le $MaxSizeMB) {
        Pass "$mb MB"
        $results += "size:OK($mb MB)"
    } else {
        Fail "$mb MB - likely too large to upload"
        Info "Fix it with:   python shrink_assets.py"
        Info "then re-run this script. Originals are backed up, nothing is lost."
        $results += "size:OVER($mb MB)"
    }
} else {
    Fail "$Main.pdf was not produced"
}

# ---------------------------------------------------------------- warnings
Head "5. LaTeX warnings"

$undef = Select-String -Path "$Main.log" -Pattern 'Reference .* undefined|Citation .* undefined|multiply-defined'
if ($undef) {
    Fail "$($undef.Count) undefined reference/citation warning(s) - these must be fixed"
    $undef | Select-Object -First 8 | ForEach-Object {
        Write-Host "         line $($_.LineNumber): $($_.Line.Trim())" -ForegroundColor Red
    }
    $results += "refs:BROKEN"
} else {
    Pass "no undefined references or citations"
    $results += "refs:OK"
}

$over = Select-String -Path "$Main.log" -Pattern 'Overfull \\hbox \((\d+\.?\d*)pt'
$bad = @()
foreach ($o in $over) {
    $pt = [double]$o.Matches[0].Groups[1].Value
    if ($pt -gt 5) { $bad += [pscustomobject]@{ Pt = $pt; Line = $o.LineNumber } }
}
if ($bad.Count -eq 0) {
    Pass "no Overfull hbox over 5 pt"
    $results += "overfull:OK"
} else {
    $worst = ($bad | Sort-Object Pt -Descending | Select-Object -First 1).Pt
    Warn "$($bad.Count) Overfull hbox over 5 pt (worst ${worst}pt = $([math]::Round($worst/28.45,2)) cm into the margin)"
    $bad | Sort-Object Pt -Descending | Select-Object -First 6 | ForEach-Object {
        Write-Host "         $($_.Pt) pt  (log line $($_.Line))" -ForegroundColor Yellow
    }
    Info "Anything under ~20pt is usually acceptable; report the worst ones to Claude."
    $results += "overfull:$($bad.Count)"
}

# ---------------------------------------------------------------- figures
Head "6. Figure files referenced by the .tex"

$tex = Get-Content "$Main.tex" -Raw
$figs = [regex]::Matches($tex, '\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}') |
        ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique
$missing = 0
foreach ($f in $figs) {
    if (Test-Path $f) {
        $kb = [math]::Round((Get-Item $f).Length / 1KB)
        Info ("{0,-46} {1,8} KB" -f $f, $kb)
    } else {
        Fail "MISSING: $f"
        $missing++
    }
}
if ($missing -eq 0) {
    Pass "all $($figs.Count) figure files present"
    $results += "figures:OK"
} else {
    $results += "figures:MISSING($missing)"
}

# ---------------------------------------------------------------- params
Head "7. Parameter-count verification"

$py = $null
foreach ($c in @("python","py","python3")) {
    if (Get-Command $c -ErrorAction SilentlyContinue) { $py = $c; break }
}
if (-not $py) {
    Warn "Python not found - skipping. The paper states 10,677,395 trainable parameters."
    $results += "params:SKIPPED"
} elseif (-not (Test-Path "verify_params.py")) {
    Warn "verify_params.py not found - skipping"
    $results += "params:SKIPPED"
} else {
    Push-Location $PSScriptRoot
    if (Test-Path "source_data\model_definition.py") {
        $env:PYTHONPATH = if ($env:PYTHONPATH) {
            "$PSScriptRoot\source_data;$env:PYTHONPATH"
        } else {
            "$PSScriptRoot\source_data"
        }
    }
    & $py "verify_params.py"
    Pop-Location
    $results += "params:RAN"
}

# ---------------------------------------------------------------- summary
Head "SUMMARY"

foreach ($r in $results) {
    if     ($r -match ':(OK|RAN)')              { Pass $r }
    elseif ($r -match ':(OVER|BROKEN|MISSING)') { Fail $r }
    else                                        { Warn $r }
}

Write-Host ""
Write-Host "  Send Claude these three numbers:" -ForegroundColor White
$pagesTxt = if ($null -eq $pages) { "unknown (check the log)" } else { $pages }
Write-Host "    pages    = $pagesTxt" -ForegroundColor White
if (Test-Path "$Main.pdf") {
    Write-Host "    pdf size = $([math]::Round((Get-Item "$Main.pdf").Length/1MB,2)) MB" -ForegroundColor White
}
Write-Host "    overfull > 5pt = $($bad.Count)" -ForegroundColor White
Write-Host ""
Write-Host "  Then submit at https://easychair.org/conferences/?conf=isds2026" -ForegroundColor White
Write-Host "  Track 3 - Image Processing & Pattern Recognition" -ForegroundColor White
Write-Host ""
