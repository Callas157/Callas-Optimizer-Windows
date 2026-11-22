param(
    [Parameter(Mandatory=$true)][string]$Target
)

$ErrorActionPreference = 'Stop'
$env:PSModulePath = Join-Path $PSHOME 'Modules'
$path = [IO.Path]::GetFullPath($Target)
$processName = [IO.Path]::GetFileNameWithoutExtension($path)
$session = [Diagnostics.Process]::GetCurrentProcess().SessionId
$deadline = [Diagnostics.Stopwatch]::StartNew()
$requested = [Collections.Generic.HashSet[int]]::new()

do {
    $running = @(Get-Process -Name $processName -ErrorAction SilentlyContinue | Where-Object {
        $_.SessionId -eq $session -and [StringComparer]::OrdinalIgnoreCase.Equals($_.Path, $path)
    })
    if ($running.Count -eq 0) { exit 0 }

    foreach ($app in $running) {
        try {
            if (!$app.HasExited -and !$requested.Contains($app.Id) -and $app.CloseMainWindow()) {
                [void]$requested.Add($app.Id)
            }
        } catch [System.InvalidOperationException] {
            # O processo pode encerrar entre a consulta e o pedido de fechamento.
        }
    }
    Start-Sleep -Milliseconds 200
} while ($deadline.Elapsed.TotalSeconds -lt 15)

exit 1
