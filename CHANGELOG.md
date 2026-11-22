# Histórico de versões — Callas Optimizer Windows

## v8.9.11 — Menu sem números
- Removidos os números de todos os 13 itens da navegação, mantendo nomes e ícones.
- Preservadas rotas, funcionalidades e agrupamento Início / Programas / Manutenção / Central.
- Teste automático confirma que nenhum item aparece com prefixo numérico.



## v8.9.10 — Validação de identidade antes de solicitar UAC
- Verifica nome e metadados de produto do Setup validado antes da elevação.
- Mantém nome legível no arquivo baixado, com diagnóstico no log e checagem no Windows Actions.
- Explica a migração de edições com atualizador antigo, que pode exibir GUID na primeira atualização.
- Não altera o comportamento das ferramentas de manutenção ou a exigência de assinatura digital.



## v8.9.9 — Nome do atualizador no UAC e navegação
- Programas reposicionado imediatamente abaixo de Início, antes de Manutenção.
- Nome do Setup temporário alterado de GUID para `Callas Optimizer.exe` durante o update.
- Metadados de descrição e produto do Setup identificam Callas Optimizer.
- Testes automatizados para navegação e nome do executável que solicita elevação.
- Sem mudanças nas funções de manutenção ou instalações existentes.
- Sem certificado digital, Windows ainda pode exibir Fornecedor desconhecido.



## v8.9.8 — Correções dos instaladores extras
- Verificação digital sobre o executável temporário (.exe), não um arquivo de extensão desconhecida.
- Thread de download reaproveitável para instalar Medal, Logitech G HUB e Spotify na mesma sessão.
- Teste de restrição HTTPS e domínios dos fornecedores.
- Publicação protege contra commits ultrapassados quando novas versões surgem durante o build.



## v8.9.7 — Novos instaladores de aplicativos
- Medal (clipes de jogos), Logitech G HUB e Spotify adicionados à Central de aplicativos.
- Download direto por HTTPS oficial, assinatura digital do fornecedor obrigatória, sem WinGet.
- Ícones vetoriais para os novos programas, layout adaptativo e fallback para sites oficiais.
- Apenas instalador Setup no GitHub Releases, com verificação de SHA-256 e mecanismo de atualização preservado.


## v8.9.6 — Manutenção em Python e correção do carregamento

- Motor de manutenção migrado para **Python/PySide6**, com ações individuais nas 13 funções. Não executa mais o BAT antigo.
- As operações administrativas usam os próprios utilitários do Windows (PowerShell, PowerCfg, DISM, SFC, SC, Registro), com confirmação, logs e backups dos ajustes suportados.
- Instalador **PyInstaller onedir**: os componentes Python/Qt são instalados em Program Files, sem extração temporária `_MEI` a cada inicialização.
- O build do Windows é interrompido se o executável instalado não abrir nos testes.
- Confirmações em **português** (Sim/Não), menu lateral maior e ícones SVG.
- Apenas **Setup.exe** nas Releases. Sem edição portátil.
- Quem está com a 8.9.4 que não abre deve **instalar o novo Setup manualmente por cima**.
- Importante: compatibilidade com uma instalação específica do Windows 11 IoT LTSC, UAC e todas as ações de manutenção ainda requerem validação prática. O SmartScreen pode continuar mostrando alerta até haver uma assinatura digital confiável.



## v8.9.5 — Correção da DLL Python e interface em português
- Corrigido empacotamento para PyInstaller `--onedir` instalado com Python/Qt e dependências permanentes em `Program Files` (evita extração `_MEI` a cada abertura).
- Instalador inclui a pasta `_internal`, e testes falham se `python312.dll` ou PySide6 estiverem ausentes.
- Teste automatizado executa **o aplicativo instalado** no Windows antes de publicar a Release.
- Perguntas de atualização e manutenção usam botões explícitos **Sim / Não** em PT-BR.
- Barra lateral ampliada e com ícones SVG uniformes, em vez de caracteres pequenos.
- Executor de manutenção reescrito em Python com ações por função, UAC, backups e registros; BAT não é mais chamado.
- Mantida somente a versão Setup para download.
- O alerta de SmartScreen ainda pode aparecer sem assinatura digital.


## v8.9.4 — Ícone e atalhos do Windows
- Instalador passa a instalar o arquivo de ícone `CallasOptimizer.ico` no diretório do programa.
- Área de Trabalho e menu Iniciar apontam explicitamente para o ícone instalado.
- AppUserModelID sincronizado entre os atalhos e a interface Qt, para integração com a barra de tarefas.
- Nova validação no GitHub Actions instala o Setup num runner Windows e verifica os atalhos e o arquivo ICO.
- Mantida a distribuição apenas por Setup (sem versão portátil).
- A assinatura digital segue pendente; o alerta do SmartScreen pode persistir.


## v8.9.3 — Windows Setup (distribuição corrigida)
- Removidos os downloads portáteis das Releases e o hash associado a eles.
- Publicações futuras oferecem somente o Setup e o arquivo de integridade.
- Ícone Callas no EXE e na janela; instalador Inno para Program Files e menu Iniciar.
- Desinstalador, entrada em Aplicativos Instalados, atalho opcional na área de trabalho.
- Updater com canal Setup instalado, validação SHA-256 e solicitação UAC.
- Release somente com instalador; ainda sem assinatura digital.
- Motor BAT 8.8 segue nas 11 opções avançadas.

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
