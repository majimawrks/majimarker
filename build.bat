@echo off
REM MajiMarker - Nuitka Build Script
REM Builds a standalone Windows executable with maximum optimization
REM Uses local temp folder to avoid OneDrive sync issues

echo Building MajiMarker with Nuitka (optimized)...
echo.

cd /d "%~dp0"

REM Use local temp directory for build cache to avoid OneDrive locking issues
set NUITKA_CACHE_DIR=%TEMP%\nuitka_cache

python -m nuitka ^
    --standalone ^
    --onefile ^
    --windows-console-mode=disable ^
    --enable-plugin=tk-inter ^
    --include-module=PIL ^
    --include-module=PIL.Image ^
    --include-module=PIL.ImageDraw ^
    --include-module=PIL.ImageFont ^
    --windows-icon-from-ico=watermark.ico ^
    --include-data-files=watermark.ico=watermark.ico ^
    --output-filename=MajiMarker.exe ^
    --output-dir=dist ^
    --assume-yes-for-downloads ^
    --lto=yes ^
    --python-flag=no_docstrings ^
    --python-flag=-OO ^
    --nofollow-import-to=pytest ^
    --nofollow-import-to=unittest ^
    --nofollow-import-to=tkinter.test ^
    --nofollow-import-to=PIL.ImageQt ^
    --nofollow-import-to=PIL.ImageTk ^
    --nofollow-import-to=setuptools ^
    --nofollow-import-to=pip ^
    --nofollow-import-to=distutils ^
    src/main.py

echo.
if exist "dist\MajiMarker.exe" (
    echo Build successful!
    echo Output: dist\MajiMarker.exe
    for %%A in ("dist\MajiMarker.exe") do echo Size: %%~zA bytes
) else (
    echo Build may have failed. Check output above.
)

pause
