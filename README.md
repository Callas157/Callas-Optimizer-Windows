<div align="center">
  <img src="assets/banner.jpg" alt="Callas Optimizer — Windows Edition" width="100%" />

# Callas Optimizer — Windows Edition

**Central de manutenção para Windows 11, com interface gráfica em Python/Qt e atualizações pelo GitHub Releases.**

[![Release](https://img.shields.io/github/v/release/Callas157/Callas-Optimizer-Windows?logo=github)](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest)
[![Windows 11](https://img.shields.io/badge/Windows-11%20x64-1976FF?logo=windows11&logoColor=white)](#compatibilidade)
[![Python + Qt](https://img.shields.io/badge/GUI-Python%20%2B%20Qt-2868b2)](#desenvolvimento)

**[Baixar a versão estável mais recente](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest)**
</div>

## v8.9.3 — Instalação e ícone do Windows

**Recomendado:** baixe `Callas_Optimizer_Setup_x64.exe` na Release. O Setup instala em Program Files, cria atalho no Iniciar, oferece atalho de Área de Trabalho, integra com Aplicativos Instalados e inclui desinstalador. A versão portátil permanece disponível.

O atualizador distingue o app instalado (Setup oficial validado + UAC) do portátil (substituição do EXE + backup). A interface, navegação e limpeza já são Python/PySide6, mas 11 opções avançadas ainda executam o motor BAT legado 8.8.

O executável e o Setup não têm assinatura Authenticode; o SmartScreen pode alertar. Não desative o Windows Defender.

## O que mudou na versão 8.9.2

A interface fixa anterior foi substituída por uma nova aplicação **Python + PySide6 (Qt)**. Agora ela possui **maximizar, redimensionamento livre, barras de rolagem, páginas individuais para as 13 opções** e layout de aplicativos que se adapta à largura da janela.

- **Início:** visão geral e atalhos para tarefas frequentes.
- **Limpeza Total (7):** executa nativamente na interface, com escopo selecionável, cancelamento, contagem de arquivos e espaço recuperado, sem travar o aplicativo. Não segue links simbólicos e ignora arquivos bloqueados.
- **Programas:** ícones vetoriais reais do Brave e NVIDIA App, com instalação oficial e gerenciamento reversível de extensões SteamDB / Bonjourr.
- **Atualizações (11):** consulta a última Release estável; ao encontrar versão nova, pede sua confirmação. Baixa o EXE, valida o tamanho, cabeçalho PE64 e hash SHA-256, cria backup e somente então fecha para substituir e reiniciar.
- **Registros:** visualização dos logs das operações na interface.
- **Ferramentas 1–6, 8–10, 12–13:** mantidas sem mudar o funcionamento do motor BAT **8.8** (uma janela de console ainda é aberta para os submenus antigos). Elas serão migradas progressivamente para a nova UI.

## Windows e requisitos

**Prioridade:** Windows 11 x64 Pro, Enterprise e IoT Enterprise LTSC. Windows 10 e ARM64 não são alvos testados.

O executável é standalone: não é necessário instalar Python ou Qt. A primeira execução extrai os scripts de manutenção para `%LOCALAPPDATA%\CallasTeck`. A compilação inclui somente dependências usadas pelo projeto.

1. Abra **[Releases](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest)**.
2. Baixe `Callas_Optimizer_Windows_x64.exe`.
3. Guarde em uma pasta **com permissão de gravação**, por exemplo `Documentos\Callas Optimizer`.
4. Execute com duplo clique. Funções administrativas solicitam UAC quando necessário.

> O aplicativo ainda não tem assinatura digital própria; o SmartScreen pode alertar. **Não desative proteções do Windows para executá-lo.** Verifique a origem e o SHA-256 publicado na Release.

## Como funciona a atualização

Consulta: `https://api.github.com/repos/Callas157/Callas-Optimizer-Windows/releases/latest`

- O usuário pode verificar manualmente ou permitir verificação ao abrir.
- **Nunca atualiza sem perguntar.** A versão antiga permanece aberta durante o download e validação.
- Só encerra a interface quando a nova versão está pronta para substituir o executável.
- Mantém até dois backups recentes e tenta restaurar uma versão funcional quando o processo falha.
- Logs do atualizador em `%LOCALAPPDATA%\CallasTeck\atualizacoes.log`.
- O EXE publicado deve ter **100 MiB ou menos** para continuar compatível com atualizadores das versões 8.9.0/8.9.1.

A edição instalada usa o Setup com UAC para atualizar Program Files. A versão portátil exige pasta gravável. Instalação interrompida não tem garantia de rollback transacional.

## Desenvolvimento

- `src/app.py`: interface Qt, navegação, atualização, programas, páginas e logs.
- `src/cleaner.py`: rotina de limpeza nativa, sem seguir links.
- `src/updater.ps1`: atualização por GitHub Releases, SHA-256 e recuperação.
- `src/Callas_Optimizer_V8_8_GUI_Engine.bat`: compatibilidade com as funções avançadas anteriores.
- `src/install_brave.ps1`, `src/install_nvidia.ps1`, `src/extensions.ps1` e `src/undo_extensions.ps1`: instaladores e configurações.
- `assets/icons/`: ícones SVG do Callas, Brave e NVIDIA; `callas.ico.b64` é convertido no build para o ícone da janela do Windows.
- `requirements-build.txt`: dependências do ambiente de compilação.
- `scripts/build.py`: PyInstaller no **Windows x64**; o executável fica em `dist/`.
- `scripts/check_version.py`, `scripts/verify_build.py`, `tests/`: integridade, proteção contra erros e testes de interface.
- `.github/workflows/release.yml`: constrói, testa e publica a versão `VERSION` em Release estável quando tudo passa.

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
- Os instaladores Brave/NVIDIA são obtidos de fornecedores oficiais e validados por assinatura de editor; o aplicativo não redistribui seus instaladores.

## Avisos e testes

A limpeza deve ser usada com os aplicativos fechados. Arquivos bloqueados são ignorados; opções de limpeza adicionais exigem confirmação. Não se promete eliminar todos os temporários do sistema nem recuperar dados apagados.

**Testes:** build e testes estruturais no pipeline Windows. Instalação, desinstalação, UAC e atualização ponta a ponta ainda precisam de teste real no Windows 11.

---

**Projeto independente:** `Callas157/Callas-Optimizer-Windows`. O repositório `Callas157/arch-install` (Callas OS Linux) não é modificado.
