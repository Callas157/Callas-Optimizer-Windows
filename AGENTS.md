# Instruções para agentes

Antes de implementar uma atualização, faça e confirme o backup da versão estável atual no Google Drive seguindo [BACKUP_NO_GOOGLE_DRIVE.md](BACKUP_NO_GOOGLE_DRIVE.md).

Quando o usuário pedir uma atualização do aplicativo, implemente e publique a versão estável no mesmo trabalho. A avaliação do usuário acontece depois da publicação. Prepare uma prévia separada apenas quando ele pedir. Siga [PUBLICAR_NO_GITHUB.md](PUBLICAR_NO_GITHUB.md).

- Acione o workflow oficial de publicação pela `main` ou pela tag da versão. As verificações automáticas do workflow fazem parte da publicação.
- Ao entregar uma atualização publicada, confirme que a API pública `/releases/latest` retorna a nova tag e o Setup com digest SHA-256. Rode a consulta com o atualizador da versão estável anterior e registre o retorno `AVAILABLE|vX.Y.Z`.
- Mantenha o link direto do instalador estável no topo do README, antes da imagem. Toda Release começa com o link do Setup da própria tag e inclui apenas as notas daquela versão. O histórico completo fica em `CHANGELOG.md`.
- Entregue a atualização pelo canal estável do aplicativo. Oriente quem já instalou o Callas a usar **Verificar atualização** e confirmar. O aplicativo baixa o instalador oficial.
