# Callas Optimizer - atualizacao de versoes estaveis via GitHub Releases.
# Nao instala nada sem confirmacao na interface grafica.
[CmdletBinding(DefaultParameterSetName = 'Check')]
param(
    [Parameter(Mandatory = $true, ParameterSetName = 'Check')][switch]$Check,
    [Parameter(Mandatory = $true, ParameterSetName = 'Install')][switch]$Install,
    [Parameter(Mandatory = $true)][string]$CurrentVersion,
    [Parameter(Mandatory = $true, ParameterSetName = 'Check')][string]$StatusFile,
    [Parameter(Mandatory = $true, ParameterSetName = 'Install')][string]$Target,
    [Parameter(Mandatory = $true, ParameterSetName = 'Install')][int]$WaitPid
)

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$Repository = 'Callas157/Callas-Optimizer-Windows'
$AssetName = 'Callas_Optimizer_Windows_x64.exe'
$ApiUrl = 'https://api.github.com/repos/' + $Repository + '/releases/latest'
$LogFolder = Join-Path $env:LOCALAPPDATA 'CallasTeck'
$LogPath = Join-Path $LogFolder 'atualizacoes.log'
New-Item -ItemType Directory -Path $LogFolder -Force | Out-Null
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Write-Log([string]$message) {
    try { Add-Content -LiteralPath $LogPath -Encoding UTF8 -Value ('[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $message) } catch {}
}
function Write-Status([string]$status) {
    if (-not $Check) { return }
    $dir = Split-Path -Parent $StatusFile
    New-Item -ItemType Directory -Path $dir -Force | Out-Null
    $tmp = $StatusFile + '.' + [guid]::NewGuid().ToString('N') + '.tmp'
    [System.IO.File]::WriteAllText($tmp, $status, [System.Text.Encoding]::ASCII)
    Move-Item -LiteralPath $tmp -Destination $StatusFile -Force
}
function Get-LatestVersion {
    $headers = @{ 'User-Agent' = 'CallasOptimizer-Updater'; 'Accept' = 'application/vnd.github+json' }
    $release = Invoke-RestMethod -Uri $ApiUrl -Headers $headers -TimeoutSec 15
    if ($release.draft -or $release.prerelease) { throw 'Release nao-estavel recusada.' }
    $tag = [string]$release.tag_name
    if ($tag -cnotmatch '^v[0-9]+\.[0-9]+\.[0-9]+$') { throw 'Tag de versao invalida.' }
    $version = [version]$tag.Substring(1)
    $asset = @($release.assets | Where-Object { $_.name -ceq $AssetName -and $_.state -eq 'uploaded' } | Select-Object -First 1)
    if ($asset.Count -ne 1) { throw 'EXE ausente na release.' }
    $expectedUrl = 'https://github.com/' + $Repository + '/releases/download/' + $tag + '/' + $AssetName
    if ([string]$asset[0].browser_download_url -cne $expectedUrl) { throw 'URL do executavel inesperada.' }
    $digest = [string]$asset[0].digest
    if ($digest -cnotmatch '^sha256:[0-9a-fA-F]{64}$') { throw 'Release sem SHA-256 confiavel. Atualizacao cancelada.' }
    return @{ Tag = $tag; Version = $version; Url = $expectedUrl; SHA256 = $digest.Substring(7).ToUpperInvariant() }
}
try {
    $latest = Get-LatestVersion
    if ($latest.Version -le [version]$CurrentVersion) {
        Write-Log ('Sem atualizacao: local ' + $CurrentVersion + ', GitHub ' + $latest.Tag)
        Write-Status 'CURRENT'
        if ($Install) { Write-Host 'Voce ja usa a versao mais recente.' }
        exit 0
    }
    if ($Check) {
        Write-Log ('Versao disponivel: ' + $latest.Tag)
        Write-Status ('AVAILABLE|' + $latest.Tag)
        exit 0
    }

    # Fluxo de instalacao iniciado somente apos clique do usuario no pop-up nativo.
    $fullTarget = [System.IO.Path]::GetFullPath($Target)
    if (-not (Test-Path -LiteralPath $fullTarget -PathType Leaf) -or [System.IO.Path]::GetExtension($fullTarget) -ine '.exe') {
        throw 'Executavel original nao localizado.'
    }
    $stageDir = Join-Path $LogFolder 'updates'
    New-Item -ItemType Directory -Path $stageDir -Force | Out-Null
    $staged = Join-Path $stageDir ($latest.Tag + '-' + $AssetName)
    Write-Host ('Baixando atualizacao ' + $latest.Tag + ' do repositorio oficial...') -ForegroundColor Cyan
    Invoke-WebRequest -Uri $latest.Url -Headers @{ 'User-Agent' = 'CallasOptimizer-Updater' } -UseBasicParsing -TimeoutSec 180 -OutFile $staged
    if ((Get-Item -LiteralPath $staged).Length -lt 10000) { throw 'Executavel incompleto.' }
    $actual = (Get-FileHash -LiteralPath $staged -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($actual -cne $latest.SHA256) { throw 'SHA-256 nao confere com o registro oficial do GitHub. Atualizacao bloqueada.' }
    Write-Log ('Hash SHA-256 validado: ' + $latest.Tag)
    Write-Host 'Download validado. Aguardando o aplicativo fechar...' -ForegroundColor Cyan

    $process = Get-Process -Id $WaitPid -ErrorAction SilentlyContinue
    if ($process) { Wait-Process -Id $WaitPid -Timeout 45 -ErrorAction Stop }
    Start-Sleep -Milliseconds 700
    $backup = $fullTarget + '.backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss')
    Move-Item -LiteralPath $fullTarget -Destination $backup -ErrorAction Stop
    try {
        Copy-Item -LiteralPath $staged -Destination $fullTarget -ErrorAction Stop
        Start-Process -FilePath $fullTarget -ErrorAction Stop
        Write-Log ('Atualizado de ' + $CurrentVersion + ' para ' + $latest.Tag + '. Backup: ' + $backup)
        Write-Host ('Atualizacao concluida: ' + $latest.Tag) -ForegroundColor Green
    } catch {
        if (Test-Path -LiteralPath $fullTarget) { Remove-Item -LiteralPath $fullTarget -Force -ErrorAction SilentlyContinue }
        Move-Item -LiteralPath $backup -Destination $fullTarget -Force -ErrorAction Stop
        Write-Log ('Falha apos download. Executavel antigo restaurado: ' + $_.Exception.Message)
        throw
    }
} catch {
    Write-Log ('ERRO: ' + $_.Exception.Message)
    if ($Check) {
        Write-Status 'ERROR'
        exit 1
    }
    Write-Host ('Falha na atualizacao: ' + $_.Exception.Message) -ForegroundColor Red
    Write-Host 'Nenhuma versao nao verificada foi instalada. Confira se o EXE esta em uma pasta com permissao de escrita.' -ForegroundColor Yellow
    Read-Host 'Pressione ENTER para fechar' | Out-Null
    exit 1
}
