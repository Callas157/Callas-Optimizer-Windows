## v8.9.29 — Desligamento personalizado e navegação pelo mouse

- A aba Desligamento ganha um cartão para escolher os minutos em uma janela central, com atalhos de 15, 30 e 60 minutos. O cartão acompanha o prazo que o Windows mantém após fechar e reabrir o Callas.
- Cancelar desligamento também cancela o temporizador personalizado. Agendar um novo prazo substitui o anterior.
- Os botões laterais Voltar e Avançar percorrem o histórico das abas visitadas no Callas.

## v8.9.28 — Cartões compactos e reversão no mesmo botão

- Programas e ferramentas do Windows usam cartões retangulares em até três colunas, de acordo com a largura da janela. WinUtil e Ponto de restauração ficam alinhados à esquerda.
- Modo Gamer, Edge, Privacidade e Menu clássico usam o mesmo botão para aplicar e restaurar. O cartão mostra a animação durante a tarefa e o resultado ao terminar.
- Aplicativos instalados exibem Abrir e Atualizar lado a lado. A atualização usa WinGet, o instalador oficial ou a Microsoft Store, conforme o aplicativo.

## v8.9.27 — Progresso das tarefas no próprio aplicativo

- O botão Executar dá lugar a uma barra animada com a porcentagem no centro. O resultado fica no cartão e a saída detalhada fica em Registros.
- A barra acompanha o progresso do CHKDSK, DISM e SFC quando o Windows fornece uma porcentagem. O CHKDSK preserva os acentos na saída em português.
- Limpeza, Programas, extensões do Brave, VirtualBox e atualização do Callas mostram a atividade e o resultado na própria página. Falhas e cancelamentos preservam o último progresso informado.
- O verificador continua oferecendo novas versões do GitHub Releases quando a consulta termina.

## v8.9.26 — Correções nas ferramentas do Windows

- O CHKDSK examina o volume do Windows com o identificador correto. SFC e DISM podem terminar reparos longos, e a interface mostra os resultados e registra falhas.
- A manutenção preserva a inicialização atrasada de serviços, a configuração anterior de hibernação e backups que não puder ler. Avisos do Windows impedem confirmar um ponto de restauração que não foi criado.
- A Limpeza Total separa os temporários do usuário dos temporários do Windows, ignora caminhos com links e respeita o cancelamento na etapa final.
- A preparação de VMs é compatível com o comando de criação do VirtualBox 7.0. Falhas removem a VM incompleta e o disco recém-criado quando seus identificadores estão confirmados.
- A atualização consulta o Setup publicado e aguarda corretamente o fechamento do Callas. O atalho de drivers abre Atualizações opcionais nas Configurações do Windows.

## v8.9.25 — Limpeza Total e atalhos do Windows

- A Lixeira distingue estado vazio, sucesso, cancelamento e erro. Os temporários mostram o resultado por pasta.
- A Limpeza Total tem opções para os bancos de cache de ícones do perfil e para o NVIDIA DXCache em Local e LocalLow. Arquivos em uso são preservados.
- O Setup atualiza os atalhos do Menu Iniciar e da Área de Trabalho para um caminho de ícone versionado, preservando a seleção de atalhos da instalação anterior.

## v8.9.24 — 5 vCPUs e compartilhamento seguro de links

- VMs de Windows 11 Pro e IoT Enterprise LTSC recebem 5 vCPUs, com RAM 6 GB e disco de 80 GB preservados.
- Clipboard só host → guest; transferência de arquivos por clipboard e drag-and-drop desativados.
- Botão também ajusta VMs Callas existentes desligadas, alterando apenas CPU e clipboard sem apagar discos.
- VMs em execução ou suspensas são preservadas; Guest Additions necessário para colar links no Windows convidado.
- Testes de CPU, flags de compartilhamento, migração e proteção de máquinas ligadas.

## v8.9.23 — Preparação opcional de VMs Windows 11

- Laboratório VirtualBox na aba Programas, com criação confirmada de duas máquinas de teste, Pro e IoT Enterprise LTSC.
- Perfis de 6 GB RAM, 2 vCPU, VDI dinâmico 80 GB, TPM 2.0, UEFI, Secure Boot e NAT, via VBoxManage.
- Pasta escolhida pelo usuário e operações não destrutivas sobre VMs existentes. Sem ISOs e sem instalação automática de Windows.
- Criação em thread separada, com progresso na interface, sem console PowerShell.
- Testes automatizados de idempotência, criação, disco mínimo e ausência de comandos shell.

## v8.9.22 — Oracle VirtualBox (Windows)

- Incluído o Oracle VirtualBox na Central de aplicativos, sem mudanças nas outras ferramentas.
- A versão estável é resolvida no domínio oficial da Oracle, com verificação do SHA-256 publicado e assinatura digital Authenticode.
- Detecção da instalação, botão Abrir, integração com WinGet quando disponível e ícone vetorial como fallback.
- Interface responsiva e distribuição exclusiva via Callas Optimizer Setup preservadas.

## v8.9.21 — Ícones de aplicativos e abertura do WinUtil

- Steam, Discord, Epic Games, Medal, Logitech G HUB e Wise usam os ícones distribuídos pelos fabricantes. O Callas usa o executável instalado como fonte sempre que possível.
- O botão WinUtil abre a interface da versão estável 26.11.13 após a confirmação do UAC. O Callas obtém o script oficial e confere seu SHA-256 antes de iniciar.

## v8.9.20 — Detecção do Medal instalado

- O cartão do Medal reconhece o caminho do atalho atual e instalações anteriores. Quando encontrado, mostra **Abrir** e usa o executável instalado.

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
