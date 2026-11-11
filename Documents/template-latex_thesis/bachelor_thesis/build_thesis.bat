@echo off
rem ---------------------------------------------------------------------------
rem  Full build for the HAW thesis template - no Perl required.
rem
rem  Runs the complete chain in the right order:
rem      pdflatex -> glossaries -> bibtex -> pdflatex -> pdflatex
rem
rem  Usage:
rem      build_thesis.bat                 builds thesis.tex next to this file
rem      build_thesis.bat <file.tex>      builds the file given (TeXworks does
rem                                       this for you via $fullname)
rem ---------------------------------------------------------------------------

setlocal

rem Work out which document to build and switch to its folder.
if "%~1"=="" (
    cd /d "%~dp0"
    set "BASE=thesis"
) else (
    cd /d "%~dp1"
    set "BASE=%~n1"
)

set "PDFLATEX=pdflatex -synctex=1 -interaction=nonstopmode"

echo.
echo ===== 1/5  pdflatex (collect references, acronyms, citations) =====
%PDFLATEX% "%BASE%.tex"

echo.
echo ===== 2/5  glossaries (build the acronym / glossary / symbol lists) =====
rem Prefer makeglossaries-lite (Lua, no Perl). If it is not installed, call
rem makeindex directly - that is all makeglossaries does internally anyway.
where /q makeglossaries-lite
if errorlevel 1 (
    echo makeglossaries-lite not found, calling makeindex directly
    if exist "%BASE%.acn" makeindex -s "%BASE%.ist" -t "%BASE%.alg" -o "%BASE%.acr" "%BASE%.acn"
    if exist "%BASE%.glo" makeindex -s "%BASE%.ist" -t "%BASE%.glg" -o "%BASE%.gls" "%BASE%.glo"
    if exist "%BASE%.slo" makeindex -s "%BASE%.ist" -t "%BASE%.slg" -o "%BASE%.sls" "%BASE%.slo"
) else (
    makeglossaries-lite "%BASE%"
)

echo.
echo ===== 3/5  bibtex (build the bibliography) =====
bibtex "%BASE%"

echo.
echo ===== 4/5  pdflatex (pull in lists and bibliography) =====
%PDFLATEX% "%BASE%.tex"

echo.
echo ===== 5/5  pdflatex (settle page numbers and cross-references) =====
%PDFLATEX% "%BASE%.tex"

echo.
echo ===== build finished: %BASE%.pdf =====

endlocal
