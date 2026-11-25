# Publicação no GitHub

O Callas Optima para Windows publica versões estáveis em [Callas157/Callas-Optimizer-Windows](https://github.com/Callas157/Callas-Optimizer-Windows/releases).

## Preparar e publicar

1. Antes de implementar a atualização, faça e confirme o [backup da versão estável no Google Drive](BACKUP_NO_GOOGLE_DRIVE.md). Anote a tag que a [API pública de releases](https://api.github.com/repos/Callas157/Callas-Optimizer-Windows/releases/latest) oferece para verificar a detecção depois da publicação.
2. Implemente a atualização e prepare a nova versão em `VERSION`, em `APP_VERSION` no arquivo `src/app.py` e em `CHANGELOG.md`.
3. Integre a mudança à `main` e publique no mesmo trabalho. O workflow **Testar e publicar Callas Optimizer Windows** compila, executa as verificações automáticas e cria a Release estável com a versão do arquivo `VERSION`. Uma tag `vX.Y.Z` no commit da atualização ou a execução manual do workflow na `main` também aciona a publicação. A avaliação do usuário acontece depois que a Release estiver disponível.
4. Acompanhe a execução até a publicação. A Release deve estar marcada como mais recente, com `draft=false` e `prerelease=false`. Ela deve incluir um único `Callas_Optimizer_Setup_x64.exe` com estado `uploaded`, digest `sha256:<64 dígitos hexadecimais>` e o `SHA256SUMS.txt` correspondente. Preserve os instaladores que já foram publicados.

## Destacar o instalador

- Mantenha o link direto do Setup estável no topo do README, antes da imagem. Use `https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest/download/Callas_Optimizer_Setup_x64.exe` para acompanhar a versão estável.
- O workflow usa `scripts/release_notes.py` para abrir as notas da Release com o link direto do Setup da própria tag. Em seguida, exibe a entrada da versão em `CHANGELOG.md` e um link para o histórico completo.
- Depois da publicação, confira os dois links sem login. O do README deve baixar a versão estável. O da Release deve baixar o Setup da tag exibida.

## Confirmar a detecção

1. Consulte a API pública `/releases/latest` sem autenticação. Confirme a nova tag, a estabilidade e os arquivos da Release que o atualizador vê.
2. Abra a versão estável anterior e clique em **Verificar atualização**. Ela deve oferecer a nova tag. Também é possível executar o script da versão anterior em modo de consulta, sem instalar nada. O exemplo abaixo verifica a atualização de 8.9.27 para 8.9.28.

   ```powershell
   $anterior = '8.9.27'
   $nova = 'v8.9.28'
   $script = Join-Path $env:TEMP "callas-updater-$anterior.ps1"
   $status = Join-Path $env:TEMP "callas-update-$([guid]::NewGuid().ToString('N')).status"
   git show "v${anterior}:src/updater.ps1" | Set-Content -LiteralPath $script -Encoding UTF8
   if ($LASTEXITCODE -ne 0) { throw "Não foi possível obter o atualizador da versão anterior." }
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File $script -Check -Installed -CurrentVersion $anterior -StatusFile $status
   if ($LASTEXITCODE -ne 0 -or (Get-Content -LiteralPath $status -Raw).Trim() -cne "AVAILABLE|$nova") {
       throw "A versão anterior ainda não confirmou a nova Release."
   }
   ```

3. Ao comunicar a entrega, inclua o link da Release estável e o resultado da consulta a partir da versão anterior. Para quem tem o Callas instalado, indique **Verificar atualização**. Após a confirmação, o próprio aplicativo baixa e abre o instalador. Se a API ainda mostrar a tag antiga ou o teste falhar, investigue a publicação antes de anunciar que a atualização chegou ao aplicativo.
