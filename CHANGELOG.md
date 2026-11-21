# Histórico de versões — Callas Optimizer Windows

## v8.9.2 — Nova interface gráfica responsiva (Python + Qt)

- Interface inteiramente redesenhada em **Python e PySide6/Qt**: janela redimensionável, maximização nativa, barras de rolagem e layout adaptável.
- Barra lateral e páginas independentes: ao selecionar uma função, o painel central agora muda de conteúdo de verdade.
- **Ícones Brave e NVIDIA reais em SVG vetorial**, em vez de letras B/N; ícone Callas próprio na janela e no EXE.
- Instaladores do Brave, NVIDIA App e extensões SteamDB/Bonjourr reunidos exclusivamente na página **Programas**.
- **Limpeza Total nativa:** escolha do escopo, progresso sem travar a janela, cancelamento e log de resultados. Preserva arquivos de sistema e não segue links simbólicos.
- Página de atualizações integrada ao **GitHub Releases**, mantendo confirmação, SHA-256, backup, recuperação e o nome estável do executável para continuidade de atualizações.
- Logs acessíveis dentro do aplicativo.
- As demais funções continuam disponíveis via motor BAT 8.8 (em janela de console) durante a migração gradual para módulos nativos.
- Pipeline Windows x64 agora compila e testa a própria GUI Qt. A publicação é bloqueada se testes falharem ou o EXE ultrapassar 100 MiB (limite aceito pelo atualizador antigo).

**Limitação:** o teste automatizado da janela e da compilação não substitui teste de instalação, UAC e atualização ponta a ponta em um computador com Windows 11 real.

## v8.9.1 — Confiabilidade do atualizador

- Download concluído e validado antes de fechar a interface.
- Verificação SHA-256 e cabeçalho PE64, backup e tentativa de recuperação.
- Rotina de Releases vinculada à versão do projeto.

## v8.9.0 — Primeira Windows Edition

- Interface gráfica inicial e atualizações pelo GitHub Releases.
- Repositório Windows independente do Callas OS Linux.
