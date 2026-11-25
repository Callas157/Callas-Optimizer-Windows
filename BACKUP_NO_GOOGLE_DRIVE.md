# Backup antes de uma atualização

Antes de alterar o repositório para uma atualização, faça o backup da versão estável oferecida pelo atualizador do Callas Optima. Confirme a cópia no Drive antes de implementar ou publicar a nova versão.

1. Consulte a [Release estável do Callas Optima](https://api.github.com/repos/Callas157/Callas-Optimizer-Windows/releases/latest). Anote a tag e o SHA-256 do instalador em `assets[].digest`.
2. Na raiz de **Meu Drive**, localize ou crie a pasta **Callas Optima**. Dentro dela, use uma pasta **Callas Optima X.Y.Z** para a versão estável encontrada. Para `v8.9.30`, use **Callas Optima 8.9.30**.
3. Guarde o `Callas_Optimizer_Setup_x64.exe` e o `SHA256SUMS.txt` baixados da Release dessa tag. Guarde também um ZIP do código-fonte da mesma tag, por exemplo `Callas-Optima-8.9.30-codigo-fonte.zip`.
4. Compare o SHA-256 do instalador com o valor publicado no GitHub. Confira os três arquivos na pasta do Drive e verifique o conteúdo pela soma de verificação do Drive ou baixando a cópia e comparando com os arquivos de origem.
5. Se a pasta já existir e o backup estiver completo e conferido, reutilize-o. Se faltarem arquivos, complete a cópia e confira novamente. Preserve as cópias das outras versões. Se o Drive estiver indisponível ou a cópia falhar, informe o bloqueio antes de editar ou publicar a atualização.

Ao concluir uma atualização, registre a pasta da versão anterior na entrega e siga o [procedimento de publicação no GitHub](PUBLICAR_NO_GITHUB.md).
