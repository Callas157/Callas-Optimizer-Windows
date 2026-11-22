<div align="center">

# Callas Optima — Fênix Edition

**Interface redesenhada para Windows 11: desempenho e renovação em uma única janela, com cores azul, roxo e ciano.**

<img src="assets/optima-interface.png" alt="Interface do Callas Optima em execução, com a Fênix, métricas do Windows e atalhos para as seções" width="100%" />

<sub>Captura da interface em execução no Windows 11. O círculo mostra a porcentagem de RAM em uso.</sub>

[![Release](https://img.shields.io/github/v/release/Callas157/Callas-Optimizer-Windows?logo=github)](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest)
[![Windows 11](https://img.shields.io/badge/Windows-11%20x64-1976FF?logo=windows11&logoColor=white)](#compatibilidade)
[![Python + Qt](https://img.shields.io/badge/GUI-Python%20%2B%20Qt-2868b2)](#desenvolvimento)

**[Baixar a versão estável mais recente](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest)**
</div>

## v8.9.18 — Downloads da Central de Programas

- Os downloads HTTPS usam a cadeia de confiança nativa do Windows. O Callas continua conferindo o domínio, o arquivo e a assinatura Authenticode antes de abrir o instalador.
- Spotify mantém a fonte oficial. Wise Program Uninstaller aceita o certificado atual do fabricante.
- ChatGPT e Codex baixam na Central o mesmo instalador oficial para Windows, com progresso nos dois cartões e detecção do aplicativo instalado. O instalador da Microsoft pode usar componentes da Store.

## v8.9.17 — Interface Fênix, instalações e atualização do Callas

- **Painel Fênix:** acompanhe CPU, RAM e espaço livre. Clean, Boost, Repair, Apps, Drivers e Atualizar abrem suas seções na mesma janela, com cartões que se reorganizam conforme a largura disponível.
- **Programas:** instale Brave, Discord, Steam, Epic Games Launcher, Wise Program Uninstaller, NVIDIA App, Medal, Logitech G HUB e Spotify com progresso no cartão. O botão **Abrir** aparece quando o aplicativo instalado é localizado. **Atualizar** aparece para versões reconhecidas pelo WinGet quando ele está disponível no Windows.
- **Brave:** usa o instalador independente oficial. SteamDB e Bonjourr ficam em **Extensões do Brave**, com confirmação e opção de desfazer as políticas locais.
- **Drivers:** abra o NVIDIA App ou consulte drivers opcionais pelo Windows Update. O Callas deixa a escolha da instalação na ferramenta oficial.
- **Atualização do Callas:** o instalador mostra sua janela após a confirmação do UAC. Uma atualização iniciada pela v8.9.16 ou anterior ainda usa o fluxo da versão que está instalada.
- **Segurança:** downloads diretos verificam o editor Authenticode e a origem HTTPS. As operações administrativas usam utilitários do sistema e a restauração aceita somente configurações contempladas no Callas. A atualização do Callas confere o SHA-256 divulgado pelo GitHub. O Setup do Callas ainda não tem assinatura própria.

## v8.9.16 — Dashboard Fênix responsivo e funcional

- **Início interativo:** Clean, Boost, Repair, Apps, Drivers e Atualizar abrem páginas próprias dentro da mesma janela.
- **Cartões de informações reais:** espaço de disco medido no PC, acesso a diagnósticos oficiais, apps de inicialização e ajustes de jogo. Nenhum percentual fictício de saúde ou otimização.
- **Layout responsivo:** reorganiza cartões para funcionar também em janelas menores.
- O visual foi baseado na [arte de referência](assets/optima-approved-preview.jpg). A interface usa controles Qt e informações do Windows.

## v8.9.15 — Fênix escolhida e prévia da interface

- **Ícone da Fênix aprovado:** a imagem selecionada foi adicionada como `assets/icons/phoenix-approved.png` e é usada na janela, no Setup, no menu Iniciar e nos atalhos.
- **Imagem do README:** a prévia aprovada do Callas Optima aparece em destaque, substituindo o banner antigo.
- Compatibilidade cumulativa, menus e ferramentas da v8.9.14 preservados.

## v8.9.14 — Interface Fênix e novos aplicativos

- **Callas Optima:** nova identidade visual Fênix, com tema azul e roxo, cartões e página inicial reformulados.
- **Navegação em uma só janela:** Clean, Boost, Repair, Apps, Drivers e Atualizar levam diretamente às páginas correspondentes; não abrem outra janela.
- **Discord e Steam:** download direto dos fornecedores, HTTPS e validação da assinatura digital antes de executar.
- **Epic Games Launcher e Wise Program Uninstaller:** botões direcionam ao download oficial no navegador, evitando executar arquivos não verificados.
- **Drivers:** acesso ao NVIDIA App e às ferramentas oficiais do Windows; nenhum driver é instalado ou revertido automaticamente.
- **Ícone Fênix:** o build cria ICO multirresolução para o Setup, menu Iniciar, Área de Trabalho e aplicativo.
- **Atualizador cumulativo preservado:** AppId, diretório de instalação, nome do EXE e validação de Setup continuam compatíveis com as instalações suportadas.
- O painel mostra apenas dados reais de armazenamento; a imagem de destaque é ilustrativa.

## v8.9.13 — Atualização cumulativa entre versões

- **Salto direto para a última Release estável:** o atualizador procura `releases/latest`, compara versões e baixa apenas o **Setup completo** da versão mais recente, sem executar cada atualização intermediária.
- **Compatibilidade mantida a partir do Setup 8.9.3**: Inno Setup preserva o mesmo AppId, nome de executável e diretório de instalação. O pipeline testa uma instalação 8.9.3 atualizada diretamente para o Setup atual, incluindo abertura da interface e bibliotecas Python/Qt.
- **Versões portáteis 8.9.0 a 8.9.2:** não podem receber esse salto pelo atualizador original porque os arquivos portáteis foram retirados das Releases. Para migrar, instale manualmente a versão estável mais recente pela página oficial de Releases. Não será reintroduzido executável portátil.
- **Recuperação:** uma instalação antiga que não abre, como a 8.9.4 em alguns PCs, exige executar o Setup atual por cima.
- Os testes automatizados verificam o salto do Setup e a estrutura da instalação. O fluxo completo de UAC e atualização dentro de cada versão antiga ainda depende de validação prática no Windows 11. Atualizações futuras devem manter compatibilidade ou documentar migração explícita.
- Dados e logs em `%LOCALAPPDATA%\\CallasTeck` e preferências do usuário devem permanecer fora da pasta de instalação; não apagamos essas pastas durante a atualização.

## v8.9.12 — ChatGPT e Codex na Central de Programas

- Adicionados dois cartões visuais: **ChatGPT** e **Codex**, na seção **Programas**, ao lado dos aplicativos existentes.
- Ambos abrem a [página oficial de download da OpenAI](https://chatgpt.com/download/) porque o novo aplicativo **ChatGPT para desktop já inclui Codex**. Não são instaladas duas cópias.
- Cartões com ícones vetoriais ilustrativos, confirmação em português e adaptação ao redimensionar.
- Guia oficial para selecionar pasta/projeto local; **sem acesso automático ao disco, login interceptado, elevação administrativa, chave de API ou executável de terceiros**.
- Em Windows 11 IoT LTSC, o instalador/Store do fornecedor pode depender da disponibilidade de componentes Microsoft Store; o Callas não tenta contornar essas restrições.
- Mantida a Release somente com o Setup do Callas Optimizer, sem edição portátil.

## v8.9.11 — Navegação sem numeração

- Os 13 itens de manutenção agora mostram **apenas os nomes e seus ícones**, sem os números herdados do antigo script BAT.
- A ordem permanece **Início → Programas → Manutenção → Central**.
- As rotas internas e as ações em Python foram preservadas. Nenhuma opção foi removida ou renumerada.
- Teste automatizado impede que números voltem aos rótulos do menu.

## v8.9.10 — Verificação da identificação do Setup

- O atualizador instalado verifica **o nome `Callas Optimizer.exe` e os metadados do instalador** após validar o SHA-256 e antes de abrir o UAC.
- Registra o nome do arquivo de atualização no log, facilitando identificar se existe um atualizador antigo.
- Teste de compilação simula a cópia do Setup para o nome amigável, confere os metadados e compara os hashes.
- **Importante para quem atualiza versões antigas:** a atualização é iniciada com o código da versão já instalada. Se a versão antiga usava nomes aleatórios, o UAC dessa primeira atualização ainda poderá exibi-los. Para corrigir imediatamente, instale o Setup atual manualmente por cima; as atualizações seguintes usarão o atualizador corrigido.
- `Fornecedor desconhecido` só será resolvido com assinatura digital confiável; nome e metadados não substituem a assinatura.

## v8.9.9 — Menu e identificação na atualização

- **Programas** movido para logo abaixo de **Início**, acima de todas as ferramentas de manutenção.
- O atualizador deixa de iniciar arquivos com nome aleatório no UAC: o Setup validado é salvo como `Callas Optimizer.exe` antes de solicitar a permissão de administrador.
- Adicionados `VersionInfoDescription` e `VersionInfoProductName` ao instalador, ambos com o nome **Callas Optimizer**.
- O GitHub Actions verifica a descrição e o nome de produto do Setup antes de publicar.
- **Atenção:** a mensagem **Fornecedor desconhecido** ainda pode aparecer sem certificado de assinatura de código confiável. Esta atualização corrige a identificação, não a assinatura.

## v8.9.8 — Confiabilidade dos downloads
- Ajustada a verificação da assinatura Authenticode do arquivo temporário com extensão executável.
- Corrigido o ciclo de vida do trabalhador de download para possibilitar instalar vários programas em sequência, sem referência Qt inválida.
- Canal oficial de atualização e distribuição preservados, com apenas um Setup x64 em Releases.
- Verificações locais e testes automatizados de segurança; download real e instalação em Windows 11 IoT LTSC ainda precisam de validação no computador do usuário.

## v8.9.7 — Medal, Logitech G HUB e Spotify

- A Central de aplicativos agora oferece **5 programas**: Brave, NVIDIA App, Medal, Logitech G HUB e Spotify.
- Medal, Logitech G HUB e Spotify podem ser baixados diretamente no programa, sem depender do WinGet (inclusive IoT LTSC).
- Downloads limitados a servidores HTTPS do fornecedor, com validação de executável e **assinatura Authenticode do editor** antes de abrir o instalador original.
- Se o servidor mudar ou o arquivo não tiver assinatura válida, o Callas não executa o arquivo e oferece o site oficial para baixar manualmente.
- Cards com ícones vetoriais e reorganização automática ao redimensionar a janela.
- Mantido o Setup como único executável publicado em Releases; Windows 11 x64 é o alvo de suporte.

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
- Mantida somente a versão Setup para download.
- O alerta de SmartScreen ainda pode aparecer sem assinatura digital.

## v8.9.4 — Ícone corrigido na Área de Trabalho e no menu Iniciar

O instalador agora copia `CallasOptimizer.ico` para a pasta do aplicativo e os atalhos usam **IconFilename explícito**, sem depender da extração do ícone do executável. A identificação AppUserModelID é igual à usada pelo Qt, para consistência na barra de tarefas. Um teste de instalação real no Windows verifica destino e ícone dos atalhos durante o GitHub Actions.

Para corrigir um atalho branco da versão 8.9.3, instale a 8.9.4 por cima: não é preciso desinstalar primeiro. O Windows pode demorar a atualizar o cache de ícones; se necessário, atualize a Área de Trabalho ou reinicie o Explorer.

## v8.9.3 — Instalação e ícone do Windows

**Recomendado:** baixe `Callas_Optimizer_Setup_x64.exe` na Release. O Setup instala em Program Files, cria atalho no Iniciar, oferece atalho de Área de Trabalho, integra com Aplicativos Instalados e inclui desinstalador. Não existe download de versão portátil.

O atualizador do aplicativo instalado usa o Setup oficial validado e solicita UAC quando necessário. A interface, navegação e limpeza já são Python/PySide6, mas 11 opções avançadas agora executam ações em Python.

O executável e o Setup não têm assinatura Authenticode; o SmartScreen pode alertar. Não desative o Windows Defender.

## O que mudou na versão 8.9.2

A interface fixa anterior foi substituída por uma nova aplicação **Python + PySide6 (Qt)**. Agora ela possui **maximizar, redimensionamento livre, barras de rolagem, páginas individuais para as 13 opções** e layout de aplicativos que se adapta à largura da janela.

- **Início:** visão geral e atalhos para tarefas frequentes.
- **Limpeza Total (7):** executa nativamente na interface, com escopo selecionável, cancelamento, contagem de arquivos e espaço recuperado, sem travar o aplicativo. Não segue links simbólicos e ignora arquivos bloqueados.
- **Programas:** ícones vetoriais reais do Brave e NVIDIA App, com instalação oficial e gerenciamento reversível de extensões SteamDB / Bonjourr.
- **Atualizações (11):** consulta a última Release estável, pede confirmação e verifica tamanho, formato PE e SHA-256 do Setup antes de iniciar a atualização.
- **Registros:** visualização dos logs das operações na interface.
- **Ferramentas 1–6, 8–10, 12–13:** operações em Python com controles de Registro, energia, serviços, DNS, DISM, SFC e restauração. Remoção do Edge pode não ser permitida em todas as edições; WinUtil abre o projeto oficial.

## Windows e requisitos

**Prioridade:** Windows 11 x64 Pro, Enterprise e IoT Enterprise LTSC. Windows 10 e ARM64 não são alvos testados.

O Setup inclui Python/Qt em Program Files, sem depender de Python instalado no computador. Os scripts auxiliares de Windows ficam em `%LOCALAPPDATA%\CallasTeck`. A compilação inclui somente dependências usadas pelo projeto.

1. Abra **[Releases](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest)**.
2. Baixe `Callas_Optimizer_Setup_x64.exe` (único EXE distribuído).
3. Execute o instalador e autorize o UAC.
4. Abra o aplicativo pelo menu Iniciar; a desinstalação fica em Aplicativos Instalados.

> O aplicativo ainda não tem assinatura digital própria; o SmartScreen pode alertar. **Não desative proteções do Windows para executá-lo.** Verifique a origem e o SHA-256 publicado na Release.

## Como funciona a atualização

Consulta: `https://api.github.com/repos/Callas157/Callas-Optimizer-Windows/releases/latest`

- O usuário pode verificar manualmente ou permitir verificação ao abrir.
- **Nunca atualiza sem perguntar.** A versão antiga permanece aberta durante o download e validação.
- Só encerra a interface quando a nova versão está pronta para substituir o executável.
- Mantém até dois backups recentes e tenta restaurar uma versão funcional quando o processo falha.
- Logs do atualizador em `%LOCALAPPDATA%\CallasTeck\atualizacoes.log`.
- Nas Releases é distribuído apenas o Setup e seu SHA-256; versões portáteis antigas foram retiradas.

A edição instalada usa o Setup com UAC para atualizar Program Files. Quem possui uma versão portátil antiga deverá instalar o Setup para migrar. Instalação interrompida não tem garantia de rollback transacional.

## Desenvolvimento

- `src/app.py`: interface Qt, navegação, atualização, programas, páginas e logs.
- `src/windows_actions.py`: ações Python, execução autorizada, backup de Registro/serviços e logs.
- `src/cleaner.py`: rotina de limpeza nativa, sem seguir links.
- `src/updater.ps1`: atualização por GitHub Releases, SHA-256 e recuperação.
- As operações de manutenção já não dependem do BAT. WinUtil abre o site oficial sem executar scripts pela internet; a remoção do Edge depende da edição do Windows.
- `src/extra_installers.py`: catálogo, download, verificação e execução dos instaladores de terceiros.
- `src/extensions.ps1` e `src/undo_extensions.ps1`: configuração e reversão das políticas locais de extensões do Brave.
- `assets/icons/`: Fênix aprovada em PNG e ícones SVG auxiliares; `scripts/make_icon.py` gera ICO multirresolução para a aplicação e os atalhos durante a compilação.
- `requirements-build.txt`: dependências do ambiente de compilação.
- `scripts/build.py`: PyInstaller no **Windows x64**; o executável fica em `dist/`.
- `scripts/check_version.py`, `scripts/verify_build.py`, `tests/`: integridade, proteção contra erros e testes de interface.
- `.github/workflows/release.yml`: constrói, testa, distribui somente o Setup e remove executáveis portáteis antigos das Releases.

O código pode ser desenvolvido e testado em Windows usando Python 3.12:

```powershell
py -3.12 -m pip install -r requirements-build.txt
py -3.12 -m unittest discover -s tests -v
py -3.12 src\app.py
```

Para gerar o executável, `py -3.12 scripts\build.py` em uma máquina Windows x64.

### Licenças e identidade visual

- Qt for Python / PySide6-Essentials: distribuição segundo os termos LGPLv3/GPL/comercial aplicáveis. O projeto disponibiliza o código, instruções de build e bibliotecas Qt dinâmicas empacotadas pelo PyInstaller. Respeite as condições da licença ao redistribuir.
- Os ícones de marca **Brave** e **NVIDIA** usam os caminhos vetoriais do projeto [Simple Icons](https://github.com/simple-icons/simple-icons) (CC0 para os desenhos). As marcas permanecem pertencentes aos respectivos titulares e não indicam afiliação ou endosso.
- Downloads diretos de instaladores usam as origens HTTPS autorizadas do catálogo e a assinatura Authenticode dos editores. Os instaladores são obtidos dos fornecedores durante a instalação.

## Avisos e testes

A limpeza deve ser usada com os aplicativos fechados. Arquivos bloqueados são ignorados; opções de limpeza adicionais exigem confirmação. Não se promete eliminar todos os temporários do sistema nem recuperar dados apagados.

**Testes:** build e testes estruturais no pipeline Windows. Instalação, desinstalação, UAC e atualização ponta a ponta ainda precisam de teste real no Windows 11.

---

**Projeto independente:** `Callas157/Callas-Optimizer-Windows`. O repositório `Callas157/arch-install` (Callas OS Linux) não é modificado.
