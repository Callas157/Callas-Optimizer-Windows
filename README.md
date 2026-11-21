<div align="center">
  <img src="assets/banner.jpg" alt="Callas Optimizer - Windows Edition" width="100%" />

# Callas Optimizer — Windows Edition

**Central gráfica de otimização, manutenção e preparação do Windows.**

**Windows 11 Pro • Enterprise • IoT Enterprise LTSC** · x64 · Interface nativa · Atualizações via GitHub Releases

[![Latest release](https://img.shields.io/github/v/release/Callas157/Callas-Optimizer-Windows?display_name=tag&logo=github)](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest)
[![Windows](https://img.shields.io/badge/Windows-11%20x64-1684FF?logo=windows11&logoColor=white)](#compatibilidade)
[![Source](https://img.shields.io/badge/código-fonte-disponível-3C8DFF)](#desenvolvimento)

**[Baixar versão mais recente](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest)**
</div>

## O que faz

O Callas Optimizer reúne, numa interface escura com detalhes azuis, as ferramentas do script Callas Optimizer 8.8, com destaque para a **Limpeza Total**, modo gamer, rede/DNS, privacidade, reparo do Windows, opções de restauração e mais.

- **Brave Browser:** baixa instalador de origem oficial, valida assinatura digital e permite configuração de SteamDB e Bonjourr (políticas reversíveis do navegador).
- **NVIDIA App:** baixa o aplicativo de origem oficial e valida assinatura digital. Não altera drivers automaticamente.
- **Atualizador:** ao abrir, consulta em segundo plano o [GitHub Releases](https://github.com/Callas157/Callas-Optimizer-Windows/releases), compara a versão local com a última release estável e mostra pop-up **dentro do aplicativo** perguntando se deseja atualizar. Também tem botão **VERIFICAR UPDATE**.
- **Instalação segura:** somente após o usuário aceitar, baixa o novo executável, valida **SHA-256** publicado pela API de assets do GitHub, guarda uma cópia da versão anterior e reinicia. Se a substituição falhar, tenta restaurar o backup.
- **Logs:** `%LOCALAPPDATA%\CallasTeck\atualizacoes.log`.

## Como instalar

1. Abra [Releases](https://github.com/Callas157/Callas-Optimizer-Windows/releases/latest).
2. Baixe **`Callas_Optimizer_Windows_x64.exe`**.
3. Guarde numa pasta com permissão de gravação (por exemplo, `Documentos\Callas Optimizer`) e execute com duplo clique.
4. Para operações administrativas, autorize o UAC quando solicitado.

> O instalador gráfico **não precisa de WinGet**, útil em instalações IoT Enterprise LTSC. Os comandos avançados do mecanismo BAT continuam abrindo console separado. O executável não possui assinatura de código própria; o SmartScreen pode alertar. **Não desative proteções do Windows para executá-lo.**

## Como funcionam as atualizações

O aplicativo consulta somente a rota oficial:

`https://api.github.com/repos/Callas157/Callas-Optimizer-Windows/releases/latest`

Uma versão **`v8.9.1`** é considerada nova em relação à **`8.9.0`**. Release em rascunho/pré-lançamento e arquivos sem SHA-256 verificável são recusados. A confirmação é feita em janela nativa, a instalação exige aceite, e não é baixado nem executado código via link arbitrário.

**Publicação de versões:** envie o código ao repositório e crie uma tag `vX.Y.Z`. O GitHub Actions compila e publica o `.exe` e o arquivo `SHA256SUMS.txt`. A versão no código precisa corresponder à tag. Somente releases publicadas e estáveis aparecem para os usuários.

## Compatibilidade

- **Principal:** Windows 11 x64 (Pro, Enterprise, IoT Enterprise LTSC).
- **Windows 10 x64:** não foi validado; aviso exibido na inicialização.
- **ARM64:** não validado.
- A primeira versão com atualização automática é **8.9.0**; o motor de manutenção preserva as correções da versão **8.8**.
- Atualização no mesmo caminho exige permissão de escrita. Se o `.exe` estiver em `Program Files`, pode ser necessário movê-lo para uma pasta do usuário ou realizar a atualização com privilégios apropriados.

## Desenvolvimento

- `src/app.c`: interface nativa Win32.
- `src/updater.ps1`: consulta à API, validação de SHA-256 e substituição com backup.
- `src/Callas_Optimizer_V8_8_GUI_Engine.bat`: operações de manutenção.
- `src/install_*.ps1`, `src/extensions.ps1`, `src/undo_extensions.ps1`: instaladores e configurações.
- `assets/banner.jpg`: identidade visual.
- `scripts/build.py`: build reproduzível de executável Windows x64 com LLVM Clang + lld-link.
- `.github/workflows/release.yml`: publicação automática a partir de tags.
- `dist/`: executável pronto e SHA256SUMS.

Compile com `python3 scripts/build.py` num ambiente com `clang`, `lld-link` e Python 3. Os arquivos de importação WinAPI necessários estão em `importlibs/`.

## Cuidados importantes

**As rotinas de manutenção alteram configurações do sistema.** Leia as confirmações, crie um ponto de restauração e mantenha backups. A instalação do Brave por política local pode exibir “Gerenciado pela organização” e pode ser desfeita pela interface. A atualização automática **não significa instalação silenciosa**: o usuário sempre decide.

**Estado de testes:** compilação Win64 e recursos embutidos verificados; execução real no Windows 11 e atualização ponta a ponta com release publicada ainda precisam de teste.

---

**Callas Optimizer — Windows Edition** · Projeto separado do **Callas OS (Linux)**. Nenhum arquivo do Callas OS faz parte deste repositório.
