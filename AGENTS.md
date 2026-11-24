# Instruções para agentes

Para preparar ou publicar uma atualização do Callas Optima, siga [PUBLICAR_NO_GITHUB.md](PUBLICAR_NO_GITHUB.md).

- Use o workflow oficial para publicar a versão estável a partir da `main` ou de uma tag do commit aprovado.
- Ao entregar uma atualização publicada, confirme que a API pública `/releases/latest` retorna a nova tag e o Setup com digest SHA-256. Rode a consulta com o atualizador da versão estável anterior e registre o retorno `AVAILABLE|vX.Y.Z`.
- Mantenha o link direto do instalador estável no topo do README, antes da imagem. Toda Release começa com o link do Setup da própria tag e inclui apenas as notas daquela versão. O histórico completo fica em `CHANGELOG.md`.
- Informe o estado real da entrega. Um PR e um instalador de teste no GitHub Actions servem para revisão. O aplicativo encontra atualizações publicadas no GitHub Releases.
