$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$dir = Split-Path -Parent $MyInvocation.MyCommand.Path
$log = Join-Path $dir 'instalacoes.log'
function Log([string]$s) {
  $line = ('[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $s)
  Write-Host $line
  try { Add-Content -Path $log -Encoding UTF8 -Value $line } catch {}
}
function Check-Signature([string]$p,[string]$publisher) {
  $sig = Get-AuthenticodeSignature -LiteralPath $p
  if ($sig.Status -ne 'Valid' -or $sig.SignerCertificate.Subject -notmatch $publisher) {
    throw 'Assinatura digital invalida ou editor diferente do esperado. Instalacao bloqueada.'
  }
}
function Download-Official([string]$url,[string]$out) {
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  Log ('Baixando de ' + $url)
  Invoke-WebRequest -Uri $url -UseBasicParsing -MaximumRedirection 10 -OutFile $out
  if ((Get-Item -LiteralPath $out).Length -lt 100000) { throw 'Arquivo baixado pequeno demais.' }
}
function Finish {
  Write-Host ''
  Read-Host 'Pressione ENTER para fechar esta janela' | Out-Null
}
$ids = @('kdbmhfkmnlmbkgbabkdealhhbfhlmmon','dlnejlppicbjfcfcedcflplfjajinajd')
$key = 'HKCU:\Software\Policies\BraveSoftware\Brave\ExtensionInstallForcelist'
$mark = Join-Path $dir 'extensoes-gerenciadas-callas.txt'
function Add-CallasExtensions {
  if (-not (Test-Path $key)) { New-Item -Path $key -Force | Out-Null }
  $p = Get-ItemProperty $key
  $owned = @()
  if (Test-Path $mark) { $owned = @(Get-Content -Path $mark | Where-Object { $_ -match '^[0-9]+\|' }) }
  foreach ($id in $ids) {
    $present = $false
    $p.PSObject.Properties | Where-Object { $_.Name -match '^\d+$' } | ForEach-Object {
      if (($_.Value -as [string]) -match ('^' + $id + ';')) { $present = $true }
    }
    if ($present) { Log ('Politica existente mantida: ' + $id); continue }
    $n = 1
    while ($p.PSObject.Properties.Name -contains [string]$n) { $n++ }
    $value = $id + ';https://clients2.google.com/service/update2/crx'
    New-ItemProperty -Path $key -Name ([string]$n) -Value $value -PropertyType String -Force | Out-Null
    $owned += ('{0}|{1}' -f $n,$value)
    Log ('Extensao adicionada: ' + $id)
    $p = Get-ItemProperty $key
  }
  $owned | Select-Object -Unique | Set-Content -Path $mark -Encoding ASCII
  Log 'Politicas locais aplicadas. Reinicie o Brave para carregar as extensoes.'
  Log 'Aviso: Brave pode exibir "Gerenciado pela organizacao" enquanto estas politicas existirem.'
}
function Remove-CallasExtensions {
  if (-not (Test-Path $mark)) { Log 'Nenhuma politica criada pelo Callas foi encontrada.'; return }
  if (Test-Path $key) {
    foreach ($line in @(Get-Content $mark)) {
      if ($line -notmatch '^([0-9]+)\|(.+)$') { continue }
      $n=$Matches[1]; $v=$Matches[2]
      $current=(Get-ItemProperty -Path $key -Name $n -ErrorAction SilentlyContinue).$n
      if ($current -eq $v) {
        Remove-ItemProperty -Path $key -Name $n -ErrorAction Stop
        Log ('Politica Callas removida: '+$n)
      } else { Log ('Politica '+$n+' alterada por terceiro, preservada.') }
    }
  }
  Remove-Item $mark -Force
  Log 'Extensoes instaladas manualmente e outras politicas preservadas.'
  Log 'Reinicie o Brave. Remover a politica pode desinstalar extensoes antes forcadas.'
}

try {
  Log 'CALLAS OPTIMIZER V8.8 - Brave + SteamDB + Bonjourr'
  $candidates = @(
    (Join-Path $env:ProgramFiles 'BraveSoftware\Brave-Browser\Application\brave.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'BraveSoftware\Brave-Browser\Application\brave.exe'),
    (Join-Path $env:LOCALAPPDATA 'BraveSoftware\Brave-Browser\Application\brave.exe')
  ) | Where-Object { $_ -and (Test-Path $_) }
  if ($candidates.Count -eq 0) {
    if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { throw 'ARM64: use o instalador oficial em https://brave.com/download' }
    $dest = Join-Path $env:TEMP 'Callas_BraveBrowserSetup.exe'
    Download-Official 'https://laptop-updates.brave.com/latest/winx64' $dest
    Check-Signature $dest 'Brave Software'
    Log 'Assinatura Brave validada. Iniciando instalador oficial.'
    $proc = Start-Process -FilePath $dest -ArgumentList @('/silent','/install') -PassThru -Wait
    Log ('Instalador Brave finalizado, codigo: '+$proc.ExitCode)
    if ($proc.ExitCode -ne 0) { throw ('Instalador Brave retornou erro: '+$proc.ExitCode) }
  } else { Log 'Brave ja esta instalado; configurando extensoes.' }
  $braveExe = @(
    (Join-Path $env:ProgramFiles 'BraveSoftware\Brave-Browser\Application\brave.exe'),
    (Join-Path ${env:ProgramFiles(x86)} 'BraveSoftware\Brave-Browser\Application\brave.exe'),
    (Join-Path $env:LOCALAPPDATA 'BraveSoftware\Brave-Browser\Application\brave.exe')
  ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
  if (-not $braveExe) { throw 'Instalador finalizado, mas brave.exe nao foi localizado.' }
  Add-CallasExtensions
  Start-Process -FilePath $braveExe -ArgumentList 'brave://policy'
  Log 'Concluido. Se o Brave ja estava aberto, feche todas as janelas e abra novamente.'
} catch { Log ('FALHA: '+ $_.Exception.Message); Write-Host 'Nenhuma protecao de seguranca foi ignorada.' -ForegroundColor Yellow }
Finish
