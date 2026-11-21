# Publicação no GitHub

Repositório oficial: https://github.com/Callas157/Callas-Optimizer-Windows

Este projeto é totalmente separado do Callas OS Linux.

## Primeira versão

O push inicial para `main` aciona o GitHub Actions para compilar e criar a Release `v8.9.0`, caso ainda não exista. Confira **Actions** e depois **Releases** para confirmar que o executável e o SHA-256 foram publicados.

## Próximas versões

1. Altere o código e os arquivos necessários na `main`.
2. Atualize a versão em `src/app.c` e as notas em `CHANGELOG.md`.
3. Após revisão e testes, crie a tag correspondente, por exemplo `v8.9.1`.
4. O workflow compila e publica a nova Release. Usuários receberão a oferta de atualização na próxima consulta ao GitHub Releases.

**Nota:** um push comum à `main` não deve substituir uma Release já publicada. A atualização automática só funciona depois de uma Release estável com asset EXE e `digest` SHA-256 confirmado pela API do GitHub.
