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

try {
  Log 'CALLAS OPTIMIZER V8.8 - NVIDIA App'
  if ($env:PROCESSOR_ARCHITECTURE -eq 'ARM64') { throw 'Arquitetura ARM64 requer download especifico no site da NVIDIA.' }
  $gpu = @(Get-CimInstance Win32_VideoController -ErrorAction SilentlyContinue | Where-Object { $_.Name -match 'NVIDIA' })
  if ($gpu.Count -eq 0) { throw 'Placa NVIDIA nao encontrada. Instalacao interrompida.' }
  Log ('GPU: ' + ($gpu | Select-Object -First 1 -ExpandProperty Name))
  $dest = Join-Path $env:TEMP 'Callas_NVIDIA_App_Setup.exe'
  # URL oficial verificavel pela pagina: https://www.nvidia.com/pt-br/software/nvidia-app/
  # Fallback versionado pode mudar futuramente: nesse caso use o site oficial.
  $url = 'https://us.download.nvidia.com/nvapp/client/11.0.9.585/x64/NVIDIA_app_v11.0.9.585_x64.exe'
  Download-Official $url $dest
  Check-Signature $dest 'NVIDIA'
  Log 'Assinatura NVIDIA validada. Abrindo instalador oficial.'
  $proc = Start-Process -FilePath $dest -PassThru -Wait
  Log ('Instalador NVIDIA finalizado, codigo: '+$proc.ExitCode)
  if ($proc.ExitCode -ne 0) { throw ('Instalacao nao concluiu corretamente. Codigo '+$proc.ExitCode) }
  Log 'Concluido. Drivers de video nao foram alterados automaticamente.'
} catch {
  Log ('FALHA: '+ $_.Exception.Message)
  Write-Host 'Pagina oficial: https://www.nvidia.com/pt-br/software/nvidia-app/' -ForegroundColor Yellow
  $answer = Read-Host 'Abrir pagina NVIDIA para download manual? [S/N]'
  if ($answer -match '^[Ss]') { Start-Process 'https://www.nvidia.com/pt-br/software/nvidia-app/' }
}
Finish
