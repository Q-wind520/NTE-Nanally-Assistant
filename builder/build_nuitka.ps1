# Nuitka 编译脚本 — NanallyAssistant v1.0.0
# 用法: powershell -ExecutionPolicy Bypass -File builder\build_nuitka.ps1
# 要求: 从项目根目录执行

$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

$NuitkaArgs = @(
    '--assume-yes-for-downloads'
    '--standalone'
    '--enable-plugin=pyside6'
    '--windows-uac-admin'
    '--include-data-dir=assets=assets'
    '--include-data-dir=scripts=scripts'
    '--include-data-dir=docs/img=docs/img'
    '--include-data-file=pyproject.toml=pyproject.toml'
    '--windows-icon-from-ico=docs/img/icon.ico'
    '--windows-console-mode=disable'
    '--output-dir=dist/nuitka'
    'src/main.py'
)

Write-Host "==> Nuitka 编译开始..." -ForegroundColor Cyan
$start = Get-Date

python -m nuitka @NuitkaArgs

if ($LASTEXITCODE -eq 0) {
    # 重命名产物
    Rename-Item -Path "dist/nuitka/main.dist/main.exe" -NewName "NanallyAssistant.exe" -Force
    Rename-Item -Path "dist/nuitka/main.dist" -NewName "NanallyAssistant" -Force

    $elapsed = [math]::Round(((Get-Date) - $start).TotalSeconds, 0)
    Write-Host "==> 编译成功！耗时 ${elapsed}s" -ForegroundColor Green
    Write-Host "    产物: dist/nuitka/NanallyAssistant/NanallyAssistant.exe" -ForegroundColor Green
} else {
    Write-Host "==> 编译失败 (exit code: $LASTEXITCODE)" -ForegroundColor Red
    exit $LASTEXITCODE
}
