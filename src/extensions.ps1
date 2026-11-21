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
  Log 'Configuracao das extensoes SteamDB e Bonjourr.'
  Add-CallasExtensions
  Log 'Verifique as extensoes apos reiniciar o Brave.'
} catch { Log ('FALHA: '+ $_.Exception.Message) }
Finish
