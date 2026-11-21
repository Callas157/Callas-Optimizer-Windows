# Callas Optimizer Windows — Historico de versoes

## v8.9.1 — Correcao de confiabilidade do atualizador

- O aplicativo permanece aberto durante o download e a verificacao de um update.
- O download so solicita fechar a interface apos comparar SHA-256, tamanho e formato PE64.
- A copia de atualizacao e preparada na pasta do executavel antes de fechar a GUI.
- Erro de download ou falta de permissao cancela a atualizacao sem fechar o aplicativo atual.
- O processo de atualizacao mantem backup, recuperacao em caso de falha e logs de diagnostico.
- O status de verificacao passa a ser isolado por processo para reduzir conflitos.
- A rotina de Releases utiliza VERSION e testes automatizados, sem fixar uma versao antiga.
- Mantidas as 13 funcoes e a Limpeza Total corrigida da linha 8.8.

**Testes:** compilacao Windows x64 e verificacoes estaticas realizadas; instalacao e atualizacao completa ainda exigem teste real em Windows 11.

## v8.9.0 — Interface Windows e atualizador inicial

- Interface grafica Win32 com 13 opcoes e instaladores Brave/NVIDIA.
- Confirmacao para updates via GitHub Releases e verificacao SHA-256.
