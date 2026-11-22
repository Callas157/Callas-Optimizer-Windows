# Testa migracao real de um Setup antigo para o atual em um runner Windows.
# Nao executa scripts remotos nem reintroduz downloads portateis.
param(
    [Parameter(Mandatory=$true)][string]$CurrentSetup,
    [string]$Repository='Callas157/Callas-Optimizer-Windows',
    [string]$BaselineTag='v8.9.3'
)
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$installerName='Callas_Optimizer_Setup_x64.exe'
if (!(Test-Path -LiteralPath $CurrentSetup -PathType Leaf)) { throw 'Setup novo nao encontrado' }
if ($Repository -cne 'Callas157/Callas-Optimizer-Windows') { throw 'Repositorio nao autorizado' }
if ($BaselineTag -cne 'v8.9.3') { throw 'Versao base nao permitida neste teste' }
$headers=@{'User-Agent'='CallasOptimizer-UpgradeSmoke'; 'Accept'='application/vnd.github+json'}
$api="https://api.github.com/repos/$Repository/releases/tags/$BaselineTag"
$release=Invoke-RestMethod -Uri $api -Headers $headers -TimeoutSec 30
if ($release.draft -or $release.prerelease -or $release.tag_name -cne $BaselineTag) {
    throw 'Release base inesperada'
}
$assets=@($release.assets | Where-Object { $_.name -ceq $installerName -and $_.state -eq 'uploaded' })
if ($assets.Count -ne 1) { throw 'Instalador base ausente ou duplicado' }
$asset=$assets[0]
$expected="https://github.com/$Repository/releases/download/$BaselineTag/$installerName"
if ([string]$asset.browser_download_url -cne $expected) { throw 'URL da versao base nao corresponde ao repositorio esperado' }
if ([string]$asset.digest -cnotmatch '^sha256:[a-fA-F0-9]{64}$') { throw 'Digest da versao base ausente' }
$sha=([string]$asset.digest).Substring(7).ToUpperInvariant()

$testRoot=Join-Path $env:RUNNER_TEMP 'CallasCumulativeUpgrade'
$oldSetup=Join-Path $testRoot 'LegacySetup893.exe'
$destination=Join-Path $testRoot 'Installed'
New-Item -ItemType Directory -Path $testRoot -Force | Out-Null
Invoke-WebRequest -Uri $expected -Headers $headers -OutFile $oldSetup -UseBasicParsing -TimeoutSec 120
if ((Get-Item -LiteralPath $oldSetup).Length -ne [long]$asset.size) { throw 'Tamanho do instalador base incorreto' }
if ((Get-FileHash -LiteralPath $oldSetup -Algorithm SHA256).Hash -cne $sha) { throw 'SHA-256 do instalador base incorreto' }
Write-Host 'Instalador 8.9.3 autenticado pelo SHA-256 publicado.'

function Install-Silent([string]$path,[string]$description) {
    $arguments='/VERYSILENT /SUPPRESSMSGBOXES /NORESTART /CLOSEAPPLICATIONS /DIR="' + $destination + '"'
    $process=Start-Process -FilePath $path -ArgumentList $arguments -Wait -PassThru
    if ($process.ExitCode -notin @(0, 3010)) { throw "$description falhou com codigo $($process.ExitCode)" }
}
Install-Silent $oldSetup 'Instalacao 8.9.3'
$app=Join-Path $destination 'Callas_Optimizer_Windows_x64.exe'
$marker=Join-Path $destination 'installed.marker'
if (!(Test-Path -LiteralPath $app -PathType Leaf) -or !(Test-Path -LiteralPath $marker -PathType Leaf)) {
    throw 'Setup 8.9.3 nao instalou no destino previsto'
}
# Nao chamar o app 8.9.3 no smoke: a versao antiga pode nao abrir em
# determinadas maquinas; o objetivo e testar o caminho de migracao por Setup.
Install-Silent $CurrentSetup 'Salto direto 8.9.3 para atual'
$runtime=Join-Path $destination '_internal/python312.dll'
$qt=Join-Path $destination '_internal/PySide6'
$icon=Join-Path $destination 'CallasOptimizer.ico'
foreach($p in @($app,$marker,$runtime,$qt,$icon)) {
    if (!(Test-Path -LiteralPath $p)) { throw "Componente ausente apos upgrade direto: $p" }
}
$env:QT_QPA_PLATFORM='offscreen'
$env:CALLAS_SMOKE='1'
$smoke=Start-Process -FilePath $app -ArgumentList '--self-test' -Wait -PassThru
if ($smoke.ExitCode -ne 0) { throw "O app atualizado nao abriu: $($smoke.ExitCode)" }
Write-Host 'Salto direto 8.9.3 -> Setup atual validado, incluindo abertura em Windows.'

# Desinstalar a versao de teste para nao interferir nos testes de instalacao normais.
$uninstaller=Join-Path $destination 'unins000.exe'
if (!(Test-Path -LiteralPath $uninstaller -PathType Leaf)) { throw 'Desinstalador nao encontrado' }
$exit=Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES' -Wait -PassThru
if ($exit.ExitCode -notin @(0,3010)) { throw "Desinstalacao de teste falhou: $($exit.ExitCode)" }
