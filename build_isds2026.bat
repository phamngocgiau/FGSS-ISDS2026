@echo off
REM Build the ISDS 2026 submission PDF (LNCS/CCIS one-column).
REM Double-click this file, or run it from a terminal in this folder.

setlocal
cd /d "%~dp0"

set MAIN=ISDS2026_FGSS_compact
if not "%~1"=="" set MAIN=%~1

echo ============================================================
echo Building %MAIN%.tex
echo ============================================================

pdflatex -interaction=nonstopmode "%MAIN%.tex"
if errorlevel 1 goto failed
pdflatex -interaction=nonstopmode "%MAIN%.tex"
if errorlevel 1 goto failed

echo.
echo ============================================================
echo BUILD OK
echo ============================================================

where pdfinfo >nul 2>&1
if %errorlevel%==0 (
    echo --- PDF info ---
    pdfinfo "%MAIN%.pdf" | findstr /R "Pages Page.size File.size PDF.version"
)

echo.
echo --- Warnings worth checking in %MAIN%.log ---
findstr /N /R /C:"Overfull" /C:"Underfull" /C:"undefined" /C:"Citation" /C:"multiply-defined" /C:"LaTeX Warning" "%MAIN%.log"

echo.
echo Reminder: ISDS 2026 long paper limit is 12-15 pages.
goto end

:failed
echo.
echo ============================================================
echo BUILD FAILED - open %MAIN%.log and search for the first "!"
echo ============================================================

:end
echo.
pause
endlocal
