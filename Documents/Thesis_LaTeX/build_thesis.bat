@echo off
REM ---------------------------------------------------------------------------
REM  Build script for the HAW EMI thesis template (MiKTeX, no Perl required).
REM
REM  Runs the full chain:  pdflatex -> makeglossaries -> bibtex -> pdflatex x2
REM  Usage: double-click, or set as the build tool in TeXworks / TeXstudio.
REM ---------------------------------------------------------------------------

setlocal
cd /d "%~dp0"
set BASE=Thesis

echo [1/5] pdflatex (first pass)
pdflatex -interaction=nonstopmode -synctex=1 "%BASE%.tex"

echo [2/5] glossaries / acronyms
where /q makeglossaries-lite
if errorlevel 1 (
    if exist "%BASE%.acn" makeindex -s "%BASE%.ist" -t "%BASE%.alg" -o "%BASE%.acr" "%BASE%.acn"
    if exist "%BASE%.glo" makeindex -s "%BASE%.ist" -t "%BASE%.glg" -o "%BASE%.gls" "%BASE%.glo"
) else (
    makeglossaries-lite "%BASE%"
)

echo [3/5] bibtex
bibtex "%BASE%"

echo [4/5] pdflatex (second pass)
pdflatex -interaction=nonstopmode -synctex=1 "%BASE%.tex"

echo [5/5] pdflatex (third pass)
pdflatex -interaction=nonstopmode -synctex=1 "%BASE%.tex"

echo.
echo Done. Check %BASE%.pdf
endlocal
