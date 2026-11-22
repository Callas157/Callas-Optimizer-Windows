## v8.9.19 — Atualização fecha o Callas automaticamente

- O Setup pede o fechamento das instâncias abertas da instalação de destino e aguarda saírem antes de substituir arquivos.
- Atualizações confirmadas exibem a janela de progresso e seguem com as configurações existentes. O atualizador reabre o Callas quando a instalação termina.
- O teste de atualização no Windows também usa um Callas em execução e verifica que o Setup fecha as janelas sem interação.

## v8.9.18 — Downloads da Central de Programas

- Validação HTTPS pela cadeia de confiança do Windows, com mensagem específica quando o certificado não é aceito.
- Identificação do novo editor Authenticode do Wise Program Uninstaller.
- ChatGPT e Codex compartilham o download e o progresso do instalador oficial, com detecção do pacote instalado.

## v8.9.17 — Painel Fênix e instalações na interface

- Painel inicial com métricas reais de CPU, RAM e armazenamento, além das seis rotas na mesma janela.
- Download e instalação de Brave, Discord, Steam, Epic Games Launcher, Wise Program Uninstaller, NVIDIA App, Medal, Logitech G HUB e Spotify com progresso no cartão. A Central permite abrir apps detectados e instalar atualizações que o WinGet identifica.
- Steam solicita UAC quando o Windows exige. Brave usa o instalador independente e informa quando outro processo de atualização do Brave impede o setup. SteamDB e Bonjourr têm configuração e reversão explícitas.
- O Setup iniciado pelo atualizador abre o assistente em primeiro plano. Os downloads usam arquivos isolados e verificação antes da execução. A restauração de configurações verifica destinos e tipos permitidos.

## v8.9.16 — Painel Fênix interativo e responsivo

- **Dashboard real, não apenas imagem:** destaque da Fênix, seis cartões clicáveis (Clean, Boost, Repair, Apps, Drivers e Atualizar), seção de saúde, programas de inicialização, armazenamento, modo jogo e ferramentas rápidas.
- **Navegação em uma janela:** os cartões levam às páginas existentes no `QStackedWidget`; não criam processos ou janelas paralelas.
- **Janela adaptável:** painel inicial reorganiza cartões em 1, 2 ou 3 colunas conforme a largura, mantendo o conteúdo acessível com rolagem.
- **Ações reais e confirmadas:** diagnósticos abrem Reparar; inicialização abre `ms-settings:startupapps`; armazenamento usa capacidade real do disco; modo jogo abre suas ações existentes.
- **Sem dados inventados:** a arte do README continua sendo uma prévia ilustrativa, não um monitor de CPU ou uma pontuação de saúde.
- **Compatibilidade preservada:** mesmo AppId, EXE, diretório, atualizador cumulativo, instaladores oficiais e ícone Fênix.

# Histórico de versões — Callas Optimizer Windows

## v8.9.15 — Arte Fênix aprovada
- A Fênix selecionada em imagem foi incorporada como recurso oficial da interface.
- Conversão automática da mesma imagem para ICO multirresolução do executável, Setup e atalhos.
- Prévia gráfica aprovada adicionada ao topo do README em substituição ao banner anterior.
- Mantidas as funções, rotas e compatibilidade de atualização acumulativa da versão anterior.


## v8.9.14 — Callas Optima, Fênix Edition
- Interface renovada com Fênix, tema gradiente roxo/azul e seis cartões de ação.
- Clean, Boost, Repair, Apps, Drivers e Atualizar navegam entre páginas reais dentro do mesmo QStackedWidget.
- Nova seção de drivers orienta o uso do NVIDIA App e do Windows Update, sem atualizar drivers arbitrariamente.
- Discord e Steam adicionados por HTTPS oficial com validação Authenticode; Epic Games Launcher e Wise Program Uninstaller usam seus sites de download oficiais.
- Nova iconografia SVG Fênix convertida em ICO multirresolução no build, inclusive para o instalador e atalhos.
- Prévia da interface no topo do README; identidades internas do Setup e compatibilidade de atualização mantidas.
- Sem métricas de saúde inventadas: o dashboard exibe informações de armazenamento lidas do sistema.


## v8.9.13 — Salto direto entre versões
- Formalizado o contrato de atualização cumulativa: apenas a última Release estável e seu Setup completo.
- Teste de migração de instalação 8.9.3 direto para a versão atual, sem intermediárias, com instalação e inicialização da GUI.
- Testes protegem AppId e caminhos de instalação para preservar a compatibilidade.
- Documentada a limitação irrecuperável do atualizador das antigas versões portáteis 8.9.0–8.9.2, que não têm mais assets correspondentes.
- Nenhum EXE portátil é redistribuído.



## v8.9.12 — ChatGPT e Codex em Programas
- ChatGPT e Codex adicionados à Central de Programas, total de sete cartões.
- Os dois cartões usam o mesmo canal oficial do ChatGPT para desktop, que já contém Codex.
- Guia de trabalho com arquivos locais, concedendo acesso somente a pastas/projetos escolhidos pelo usuário.
- Nenhum instalador não oficial, token de API, login automatizado ou acesso total ao sistema.
- Testes dos ícones e da navegação; distribuição exclusiva por Setup mantida.



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
