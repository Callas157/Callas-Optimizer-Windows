# Callas Optimizer - GitHub Releases stable updater.
# A janela principal permanece aberta ate o download e a verificacao terminarem.
[CmdletBinding(DefaultParameterSetName='Check')]
param(
    [Parameter(Mandatory=$true, ParameterSetName='Check')][switch]$Check,
    [Parameter(Mandatory=$true, ParameterSetName='Install')][switch]$Install,
    [Parameter(Mandatory=$true)][string]$CurrentVersion,
    [Parameter(Mandatory=$true)][string]$StatusFile,
    [Parameter(Mandatory=$true, ParameterSetName='Install')][string]$Target,
    [Parameter(Mandatory=$true, ParameterSetName='Install')][ValidateRange(1,2147483647)][int]$WaitPid,
    [switch]$Installed
)

$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
$Repository='Callas157/Callas-Optimizer-Windows'
$AssetName = if ($Installed) { 'Callas_Optimizer_Setup_x64.exe' } else { 'Callas_Optimizer_Windows_x64.exe' }
$ApiUrl='https://api.github.com/repos/'+$Repository+'/releases/latest'
$HomeFolder=Join-Path $env:LOCALAPPDATA 'CallasTeck'
$LogPath=Join-Path $HomeFolder 'atualizacoes.log'
New-Item -ItemType Directory -Path $HomeFolder -Force | Out-Null
[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12

function Log([string]$message) {
    try { Add-Content -LiteralPath $LogPath -Encoding UTF8 -Value ('[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'),$message) } catch {}
}
function Status([string]$value) {
    $dir=Split-Path -Parent $StatusFile
    if (-not (Test-Path -LiteralPath $dir -PathType Container)) { throw 'Pasta do status indisponivel.' }
    $tmp=$StatusFile+'.'+[guid]::NewGuid().ToString('N')+'.tmp'
    [IO.File]::WriteAllText($tmp,$value,[Text.Encoding]::ASCII)
    Move-Item -LiteralPath $tmp -Destination $StatusFile -Force
}
function Get-Latest {
    $headers=@{'User-Agent'='CallasOptimizer-Updater'; 'Accept'='application/vnd.github+json'}
    $release=Invoke-RestMethod -Uri $ApiUrl -Headers $headers -TimeoutSec 20
    if ($release.draft -or $release.prerelease) { throw 'Release nao-estavel.' }
    $tag=[string]$release.tag_name
    if ($tag -cnotmatch '^v[0-9]+\.[0-9]+\.[0-9]+$') { throw 'Tag invalida.' }
    $asset=@($release.assets | Where-Object { $_.name -ceq $AssetName -and $_.state -eq 'uploaded' })
    if ($asset.Count -ne 1) { throw 'Release sem executavel unico.' }
    $expected='https://github.com/'+$Repository+'/releases/download/'+$tag+'/'+$AssetName
    if ([string]$asset[0].browser_download_url -cne $expected) { throw 'URL da release inesperada.' }
    if ([string]$asset[0].digest -cnotmatch '^sha256:[0-9a-fA-F]{64}$') { throw 'Release sem digest SHA-256.' }
    if ([long]$asset[0].size -lt 10000 -or [long]$asset[0].size -gt 250MB) { throw 'Tamanho de executavel inesperado.' }
    return @{Tag=$tag; Version=[version]$tag.Substring(1); Url=$expected; SHA256=([string]$asset[0].digest).Substring(7).ToUpperInvariant(); Size=[long]$asset[0].size}
}
function Confirm-WindowsExe([string]$path,[switch]$Installer) {
    $f=[IO.File]::OpenRead($path)
    try {
        if ($f.Length -lt 1024) { throw 'Executavel invalido.' }
        $r=New-Object IO.BinaryReader($f)
        if ($r.ReadUInt16() -ne 0x5A4D) { throw 'EXE sem cabecalho MZ.' }
        $f.Position=0x3C
        $offset=$r.ReadInt32()
        if ($offset -le 0 -or $offset -ge ($f.Length-24)) { throw 'Cabecalho PE invalido.' }
        $f.Position=$offset
        if ($r.ReadUInt32() -ne 0x00004550) { throw 'Assinatura PE invalida.' }
        $machine = $r.ReadUInt16()
        if ($Installer -and $machine -notin @(0x014c,0x8664)) { throw 'Instalador nao e Windows PE.' }
        if (-not $Installer -and $machine -ne 0x8664) { throw 'Aplicativo nao e Windows x64.' }
    } finally { $f.Dispose() }
}
function Move-Retry([string]$source,[string]$destination) {
    # PyInstaller onefile mantem um processo supervisor vivo por instantes
    # apos a janela fechar. Aguarda a liberacao do arquivo com limite.
    for($i=0; $i -lt 60; $i++) {
        try {
            Move-Item -LiteralPath $source -Destination $destination -ErrorAction Stop
            return
        } catch {
            if ($i -eq 59) { throw }
            Start-Sleep -Milliseconds 500
        }
    }
}
function Download-Verified([hashtable]$latest,[string]$staged) {
    for($attempt=1;$attempt -le 3;$attempt++) {
        try {
            if (Test-Path -LiteralPath $staged) { Remove-Item -LiteralPath $staged -Force }
            Invoke-WebRequest -Uri $latest.Url -Headers @{'User-Agent'='CallasOptimizer-Updater'} -UseBasicParsing -TimeoutSec 120 -OutFile $staged
            break
        } catch {
            Log ('Download tentativa '+$attempt+': '+$_.Exception.Message)
            if ($attempt -eq 3) { throw }
            Start-Sleep -Seconds (2*$attempt)
        }
    }
    $file=Get-Item -LiteralPath $staged
    if ($file.Length -ne $latest.Size) { throw 'Tamanho baixado diferente da Release.' }
    $hash=(Get-FileHash -LiteralPath $staged -Algorithm SHA256).Hash.ToUpperInvariant()
    if ($hash -cne $latest.SHA256) { throw 'Falha na validacao SHA-256.' }
    Confirm-WindowsExe $staged -Installer:$Installed
    Log ('Download e validacao PE64/SHA256 concluidos para '+$latest.Tag)
}
try {
    if ($CurrentVersion -cnotmatch '^[0-9]+\.[0-9]+\.[0-9]+$') { throw 'Versao local invalida.' }
    $latest=Get-Latest
    if ($latest.Version -le [version]$CurrentVersion) {
        Log ('Atualizado: '+$CurrentVersion+', ultima release '+$latest.Tag)
        Status 'CURRENT'
        exit 0
    }
    if ($Check) {
        Log ('Atualizacao disponivel: '+$latest.Tag)
        Status ('AVAILABLE|'+$latest.Tag)
        exit 0
    }
    $fullTarget=[IO.Path]::GetFullPath($Target)
    if (([IO.Path]::GetExtension($fullTarget) -ine '.exe') -or -not (Test-Path -LiteralPath $fullTarget -PathType Leaf)) { throw 'Executavel original nao encontrado.' }
    $targetDir=Split-Path -Parent $fullTarget
    $stageDir=Join-Path $HomeFolder 'updates'
    New-Item -ItemType Directory -Path $stageDir -Force | Out-Null
    $staged=Join-Path $stageDir ([guid]::NewGuid().ToString('N')+'.exe')
    if ($Installed) {
        try {
            if (-not (Test-Path -LiteralPath (Join-Path $targetDir 'installed.marker') -PathType Leaf)) {
                throw 'Instalacao nao reconhecida pelo Setup.'
            }
            Download-Verified $latest $staged
            Status 'READY'
            Log ('Setup validado; aguardando fechamento do PID '+$WaitPid)
            $process=Get-Process -Id $WaitPid -ErrorAction SilentlyContinue
            if ($process) { Wait-Process -Id $WaitPid -Timeout 60 -ErrorAction Stop }
            $setup=Start-Process -FilePath $staged -ArgumentList '/SILENT /NORESTART /CLOSEAPPLICATIONS /SUPPRESSMSGBOXES' -Verb RunAs -PassThru -Wait -ErrorAction Stop
            if ($setup.ExitCode -ne 0) { throw ('Setup devolveu codigo '+$setup.ExitCode) }
            if (-not (Test-Path -LiteralPath $fullTarget -PathType Leaf)) { throw 'Executavel ausente apos Setup.' }
            Log ('Setup aplicado: '+$latest.Tag)
            Start-Process -FilePath $fullTarget -ErrorAction Stop | Out-Null
            exit 0
        } catch {
            Log ('Falha no Setup instalado: '+$_.Exception.Message)
            try { if (Test-Path -LiteralPath $fullTarget) { Start-Process -FilePath $fullTarget -ErrorAction Stop | Out-Null } } catch {}
            throw
        } finally {
            Remove-Item -LiteralPath $staged -Force -ErrorAction SilentlyContinue
        }
    }
    $neighbor=Join-Path $targetDir ('.callas-update-'+[guid]::NewGuid().ToString('N')+'.exe')
    $backup=$fullTarget+'.backup-'+(Get-Date -Format 'yyyyMMdd-HHmmss')
    $originalMoved=$false
    $ready=$false
    try {
        Download-Verified $latest $staged
        # Copiar para a mesma unidade antes de solicitar o encerramento.
        # Se nao houver permissao de escrita, o programa antigo fica aberto.
        Copy-Item -LiteralPath $staged -Destination $neighbor -ErrorAction Stop
        Confirm-WindowsExe $neighbor
        Status 'READY'
        $ready=$true
        Log ('Arquivo pronto; aguardando fechamento do PID '+$WaitPid)
        $process=Get-Process -Id $WaitPid -ErrorAction SilentlyContinue
        if ($process) { Wait-Process -Id $WaitPid -Timeout 45 -ErrorAction Stop }
        Start-Sleep -Milliseconds 250
        Move-Retry $fullTarget $backup
        $originalMoved=$true
        Move-Retry $neighbor $fullTarget
        $new=Start-Process -FilePath $fullTarget -PassThru -ErrorAction Stop
        Start-Sleep -Seconds 2
        $new.Refresh()
        if ($new.HasExited) { throw 'Nova versao encerrou imediatamente; recuperando a anterior.' }
        Log ('Atualizacao '+$CurrentVersion+' -> '+$latest.Tag+' concluida. Backup: '+$backup)
        # Preservar os dois backups mais recentes desta instalacao.
        Get-ChildItem -LiteralPath $targetDir -Filter ([IO.Path]::GetFileName($fullTarget)+'.backup-*') -File -ErrorAction SilentlyContinue |
          Sort-Object LastWriteTime -Descending | Select-Object -Skip 2 |
          Remove-Item -Force -ErrorAction SilentlyContinue
    } catch {
        Log ('Falha na etapa de instalacao: '+$_.Exception.Message)
        if ($originalMoved) {
            try {
                if (Test-Path -LiteralPath $fullTarget) { Remove-Item -LiteralPath $fullTarget -Force -ErrorAction Stop }
                Move-Item -LiteralPath $backup -Destination $fullTarget -Force -ErrorAction Stop
                Start-Process -FilePath $fullTarget -ErrorAction Stop | Out-Null
                Log 'Rollback concluido; aplicativo anterior reaberto.'
            } catch { Log ('ERRO CRITICO no rollback: '+$_.Exception.Message+'; backup em '+$backup) }
        }
        throw
    } finally {
        Remove-Item -LiteralPath $staged -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $neighbor -Force -ErrorAction SilentlyContinue
    }
} catch {
    Log ('ERRO: '+$_.Exception.Message)
    if ($Install) { Write-Host ('Falha de atualizacao: '+$_.Exception.Message) -ForegroundColor Red }
    try { Status 'ERROR' } catch { Log ('Nao foi possivel gravar status: '+$_.Exception.Message) }
    exit 1
}
