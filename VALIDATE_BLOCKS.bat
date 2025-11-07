@echo off
REM ========================================
REM IPB Block Validator - Quick Run Script
REM ========================================
REM 
REM This batch file runs the block validator
REM with your preset paths automatically.
REM
REM Simply double-click this file to run!
REM ========================================

echo.
echo ================================================================
echo IPB BLOCK VALIDATOR
echo ================================================================
echo.
echo Preset Configuration:
echo - CSV: J:\LIB\BR\xxBLOCKS\IPB-DescriptionKeys.csv
echo - Block Library: J:\LIB\BR (all subfolders)
echo.
echo Starting validation...
echo.

python block_validator_configured.py

echo.
echo ================================================================
echo Validation Complete!
echo ================================================================
echo.
echo Check these files for results:
echo - validation_report.txt
echo - IPB-DescriptionKeys-Validated.csv
echo.
pause
