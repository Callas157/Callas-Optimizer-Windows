$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$dir = Join-Path $env:LOCALAPPDATA 'CallasTeck'
$log = Join-Path $dir 'instalacoes.log'
function Log([string]$s) {
  $line = ('[{0}] {1}' -f (Get-Date -Format 'yyyy-MM-dd HH:mm:ss'), $s)
  Write-Host $line
  try { Add-Content -Path $log -Encoding UTF8 -Value $line } catch {}
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
try {
  Log 'Configuracao das extensoes SteamDB e Bonjourr.'
  Add-CallasExtensions
  Log 'Verifique as extensoes apos reiniciar o Brave.'
} catch { Log ('FALHA: '+ $_.Exception.Message); exit 1 }
