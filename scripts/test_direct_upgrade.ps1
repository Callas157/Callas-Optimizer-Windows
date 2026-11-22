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
$apiHeaders=$headers.Clone()
# O token temporário do GitHub Actions aumenta o limite da API no runner.
# Nunca é salvo em logs, artefatos ou no programa do usuário.
if ($env:GITHUB_TOKEN) {
    $apiHeaders['Authorization']="Bearer $env:GITHUB_TOKEN"
}
$api="https://api.github.com/repos/$Repository/releases/tags/$BaselineTag"
$release=Invoke-RestMethod -Uri $api -Headers $apiHeaders -TimeoutSec 30
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

# Testa o instalador com duas janelas reais, inclusive com os argumentos do
# atualizador interativo anterior. Desabilita o Restart Manager para que só
# passe se o próprio Setup solicitar e aguardar o fechamento.
$settingsKey = 'HKCU:\Software\Callas\OptimizerWindows'
if (!(Test-Path $settingsKey)) { New-Item -Path $settingsKey -Force | Out-Null }
Set-ItemProperty -Path $settingsKey -Name auto_update -Value 'false'
$env:QT_QPA_PLATFORM='windows'
$instances = @()
try {
    $instances += Start-Process -FilePath $app -PassThru
    $instances += Start-Process -FilePath $app -PassThru
    foreach ($instance in $instances) {
        $limit = [Diagnostics.Stopwatch]::StartNew()
        do {
            $instance.Refresh()
            if ($instance.HasExited) { throw 'O Callas de teste fechou antes de abrir a janela.' }
            if ($instance.MainWindowHandle) { break }
            Start-Sleep -Milliseconds 200
        } while ($limit.Elapsed.TotalSeconds -lt 20)
        if (!$instance.MainWindowHandle) { throw 'A janela do Callas de teste não abriu.' }
    }
    $setupLog = Join-Path $testRoot 'interactive-upgrade.log'
    $arguments = '/CALLASUPDATE /NORESTART /NOCLOSEAPPLICATIONS /SP- /DIR="' + $destination + '" /LOG="' + $setupLog + '"'
    $setup = Start-Process -FilePath $CurrentSetup -ArgumentList $arguments -PassThru
    if (!$setup.WaitForExit(90000)) {
        Stop-Process -Id $setup.Id -ErrorAction SilentlyContinue
        if (Test-Path -LiteralPath $setupLog) { Get-Content -LiteralPath $setupLog -Tail 70 }
        throw 'O Setup ficou esperando interação ou não conseguiu fechar o aplicativo.'
    }
    if ($setup.ExitCode -ne 0) {
        if (Test-Path -LiteralPath $setupLog) { Get-Content -LiteralPath $setupLog -Tail 70 }
        throw "Atualização com Callas aberto falhou: $($setup.ExitCode)"
    }
    foreach ($instance in $instances) {
        if (!$instance.HasExited) { throw 'Uma janela antiga permaneceu aberta após a instalação.' }
    }
    Write-Host 'Setup de atualização fechou duas instâncias sem intervenção.'
} finally {
    foreach ($instance in $instances) {
        if (!$instance.HasExited) { Stop-Process -Id $instance.Id -ErrorAction SilentlyContinue }
    }
}

# Desinstalar a versao de teste para nao interferir nos testes de instalacao normais.
$uninstaller=Join-Path $destination 'unins000.exe'
if (!(Test-Path -LiteralPath $uninstaller -PathType Leaf)) { throw 'Desinstalador nao encontrado' }
$exit=Start-Process -FilePath $uninstaller -ArgumentList '/VERYSILENT /NORESTART /SUPPRESSMSGBOXES' -Wait -PassThru
if ($exit.ExitCode -notin @(0,3010)) { throw "Desinstalacao de teste falhou: $($exit.ExitCode)" }
