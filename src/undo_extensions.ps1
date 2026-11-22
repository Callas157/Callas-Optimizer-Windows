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
function Remove-CallasExtensions {
  if (-not (Test-Path $mark)) { Log 'Nenhuma politica criada pelo Callas foi encontrada.'; return }
  if (Test-Path $key) {
    foreach ($line in @(Get-Content $mark)) {
      if ($line -notmatch '^([0-9]+)\|(.+)$') { continue }
      $n=$Matches[1]; $v=$Matches[2]
      $allowed = $ids | ForEach-Object { $_ + ';https://clients2.google.com/service/update2/crx' }
      if ($v -cnotin $allowed) { continue }
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

try { Remove-CallasExtensions } catch { Log ('FALHA: '+ $_.Exception.Message); exit 1 }
