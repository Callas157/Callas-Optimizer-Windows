@echo off
setlocal EnableExtensions
title CALLAS OPTIMIZER V8.8
color 0F

rem ============================================================
rem  CALLAS OPTIMIZER V8.8
rem  Manutencao para Windows 10 e 11 (Home, Pro, Enterprise, LTSC, IoT)
rem  Arquivo 100% ASCII com quebra de linha CRLF
rem  (evita o bug de goto/labels com UTF-8 e LF)
rem ============================================================

set "VER=8.8"
rem Pasta de dados, logs e backups: CallasTeck ao lado do script (pendrive, Downloads, Area de Trabalho...)
set "SELF=%~f0"
for %%I in ("%SELF%") do set "SELFDIR=%%~dpI"
set "DOCS="
for /f "tokens=2*" %%A in ('reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Personal 2^>nul ^| findstr /i "REG_"') do set "DOCS=%%B"
if defined DOCS call set "DOCS=%DOCS%"
if not defined DOCS set "DOCS=%USERPROFILE%\Documents"
set "BKDIR=%LOCALAPPDATA%\CallasTeck"
set "EDGEBK=%BKDIR%\edge_removed.flag"
set "BKSVC=%BKDIR%\services_backup.txt"
set "HIBFLAG=%BKDIR%\hibernate_off.flag"
set "LOG=%BKDIR%\callas_teck.log"
set "GAMER_GUID=99999999-9999-9999-9999-999999999999"
set "CLSID_KEY=HKCU\Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
set "POL_WU=HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate"
set "POL_DC=HKLM\SOFTWARE\Policies\Microsoft\Windows\DataCollection"
set "POL_AD=HKLM\SOFTWARE\Policies\Microsoft\Windows\AdvertisingInfo"
set "POL_GD=HKLM\SOFTWARE\Policies\Microsoft\Windows\GameDVR"
set "POL_SY=HKLM\SOFTWARE\Policies\Microsoft\Windows\System"
set "XBOXFLAG=%BKDIR%\xbox_overlay_off.flag"
set "GMFLAG=%BKDIR%\game_mode_on.flag"
rem Mouse nos menus + fonte maior: 1 = ligado, 0 = desliga (volta ao modo so teclado)
set "MOUSE=1"
rem Altura da fonte do console em pixels (padrao do Windows = 16). Janela segue 80x46.
set "FONT_SIZE=18"
set "FSZ=%FONT_SIZE%"
rem Submenus Modo Gamer e Edge: fonte maior; janela em colunas x linhas (mesmo tamanho em pixels)
set "FONT_BIG=25"
set "BIG_COLS=57"
set "BIG_LINES=33"
set "BIGUI="
set "CON="
if not "%MOUSE%"=="0" set "CON=conhost.exe"
set "PAD="
rem Arquivo temporario exclusivo de cada janela (evita colisao entre janelas)
set "RBF=%BKDIR%\rb_%RANDOM%%RANDOM%.tmp"
rem ================================
rem  AUTO-ELEVACAO (pede permissao de administrador sozinho)
rem  Usa fltmc (nao depende do servico Servidor, ao contrario do
rem  net session) e o argumento :elevado evita loop de reinicio.
rem ================================
set "NETDIR=%BKDIR%"
set "NETF=%NETDIR%\rede_adaptador.csv"
fltmc >nul 2>&1
if %errorlevel% neq 0 goto pedir_admin
if /i "%~1"==":elevado" shift
goto admin_ok

:pedir_admin
if /i "%~1"==":elevado" (
    echo.
    echo [!] Nao foi possivel obter permissao de administrador.
    echo     Clique com o botao direito no arquivo e escolha "Executar como administrador".
    echo.
    pause
    exit /b 1
)
echo.
echo Solicitando permissao de administrador...
powershell -NoProfile -Command "Start-Process -FilePath $env:SELF -ArgumentList ':elevado' -Verb RunAs" >nul 2>&1
if errorlevel 1 (
    echo.
    echo [!] Permissao de administrador negada ou indisponivel.
    echo.
    pause
    exit /b 1
)
exit /b 0

:admin_ok
cd /d "%~dp0" 2>nul

rem Windows Terminal ignora fonte/tamanho/mouse do script: reabre no console classico
set "ISCON="
set "WAS_WT=nao"
if defined WT_SESSION set "WAS_WT=sim"
if /i "%~1"==":conhost" set "ISCON=1"
if /i "%~1"==":conhost" shift
if defined ISCON set "WT_SESSION="
if defined ISCON goto host_ok
if not defined WT_SESSION goto host_ok
if "%MOUSE%"=="0" goto host_ok
start "" conhost.exe cmd /c ""%~f0" :conhost %~1"
if not errorlevel 1 exit /b 0
:host_ok

rem Habilita cores 24-bit (arco-iris) no console
reg add "HKCU\Console" /v VirtualTerminalLevel /t REG_DWORD /d 1 /f >nul 2>&1

rem Tamanho da janela (colunas x linhas). 90x38 cabe o menu em duas colunas.
set "WIN_COLS=90"
set "WIN_LINES=38"

if not exist "%BKDIR%" if exist "%DOCS%\CallasTeck\" xcopy "%DOCS%\CallasTeck" "%BKDIR%" /e /i /y /q >nul 2>&1
if not exist "%BKDIR%" mkdir "%BKDIR%" >nul 2>&1
rem Quando o .BAT estiver em pasta protegida, usa area de dados gravavel.
> "%BKDIR%\.writecheck" echo ok 2>nul
if errorlevel 1 (
    set "BKDIR=%ProgramData%\CallasTeck"
    if not exist "%ProgramData%\CallasTeck" mkdir "%ProgramData%\CallasTeck" >nul 2>&1
) else (
    del /q "%BKDIR%\.writecheck" >nul 2>&1
)
rem Atualiza os caminhos derivados se houve fallback.
set "EDGEBK=%BKDIR%\edge_removed.flag"
set "BKSVC=%BKDIR%\services_backup.txt"
set "HIBFLAG=%BKDIR%\hibernate_off.flag"
set "LOG=%BKDIR%\callas_teck.log"
set "XBOXFLAG=%BKDIR%\xbox_overlay_off.flag"
set "GMFLAG=%BKDIR%\game_mode_on.flag"
set "RBF=%BKDIR%\rb_%RANDOM%%RANDOM%.tmp"
set "NETDIR=%BKDIR%"
set "NETF=%NETDIR%\rede_adaptador.csv"
if not exist "%BKDIR%\" (
    echo [X] Nao foi possivel criar a pasta CallasTeck.
    pause
    exit /b 1
)

rem Migra dados antigos (ProgramData\CallasTeck) para a nova pasta e remove a antiga
if exist "%ProgramData%\CallasTeck\" (
    if /i not "%ProgramData%\CallasTeck"=="%BKDIR%" (
        xcopy "%ProgramData%\CallasTeck" "%BKDIR%" /e /i /y /q >nul 2>&1
        if not errorlevel 1 rd /s /q "%ProgramData%\CallasTeck" >nul 2>&1
    )
)
>> "%BKDIR%\mouse_debug.log" echo [%date% %time%] inicio: windows_terminal=%WAS_WT% conhost_relancado=%ISCON%

rem ================================
rem  TAMANHO DA JANELA (vale para todas as janelas do script)
rem ================================
if not "%MOUSE%"=="0" call :psm font "" 0 ""
mode con: cols=%WIN_COLS% lines=%WIN_LINES% >nul 2>&1

rem ================================
rem  DETECTA EDICAO DO WINDOWS
rem ================================
set "EDITION=Desconhecida"
for /f "tokens=3" %%A in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v EditionID 2^>nul ^| findstr /i "EditionID"') do set "EDITION=%%A"

rem Nivel 0 de telemetria so e aceito em Enterprise / Education / IoT
set "TELE=1"
echo %EDITION%| findstr /i "Enterprise Education IoT" >nul && set "TELE=0"

rem ================================
rem  DETECTA VERSAO DO WINDOWS (10 / 11)
rem ================================
set "BUILD=0"
for /f "tokens=3" %%A in ('reg query "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion" /v CurrentBuildNumber 2^>nul ^| findstr /i "CurrentBuildNumber"') do set "BUILD=%%A"
set "WINNAME=Windows"
if %BUILD% GEQ 10240 set "WINNAME=Windows 10"
if %BUILD% GEQ 22000 set "WINNAME=Windows 11"
rem Cores 24-bit exigem Windows 10 1703 (build 15063) ou mais novo
set "NOVT="
if %BUILD% LSS 15063 set "NOVT=1"
if %BUILD% GTR 0 if %BUILD% LSS 10240 (
    echo.
    echo [!] Este script suporta apenas Windows 10 e Windows 11.
    echo.
    pause
    exit /b 1
)

rem ================================
rem  ROTEADOR DE ARGUMENTOS (janelas dedicadas)
rem ================================
if /i "%~1"==":limpeza_real" goto limpeza_real
if /i "%~1"==":reparo_real" goto reparo_real
if /i "%~1"==":gui1" (
    set "GUI_LAUNCH=1"
    goto gamer
)
if /i "%~1"==":gui2" (
    set "GUI_LAUNCH=1"
    goto remover_edge
)
if /i "%~1"==":gui3" (
    set "GUI_LAUNCH=1"
    goto wumenu
)
if /i "%~1"==":gui4" (
    set "GUI_LAUNCH=1"
    goto rede
)
if /i "%~1"==":gui5" (
    set "GUI_LAUNCH=1"
    goto telemetria
)
if /i "%~1"==":gui6" (
    set "GUI_LAUNCH=1"
    goto disparar_reparo
)
if /i "%~1"==":gui7" (
    set "GUI_LAUNCH=1"
    goto limpeza_nova_janela
)
if /i "%~1"==":gui8" (
    set "GUI_LAUNCH=1"
    goto menuclassico
)
if /i "%~1"==":gui9" (
    set "GUI_LAUNCH=1"
    goto desligamento
)
if /i "%~1"==":gui10" (
    set "GUI_LAUNCH=1"
    goto disparar_winutil
)
if /i "%~1"==":gui11" (
    set "GUI_LAUNCH=1"
    goto atualizar_versao
)
if /i "%~1"==":gui12" (
    set "GUI_LAUNCH=1"
    goto ponto_restauracao
)
if /i "%~1"==":gui13" (
    set "GUI_LAUNCH=1"
    goto restaurar
)

:menu
if defined GUI_LAUNCH exit /b 0
if defined BIGUI call :ui_normal
cls
set "op="
set "PAD="
(
call :banner
echo(                               =====Windows Optimizer=====
echo(                                          V%VER%
echo(                        Detectado: %WINNAME% - Edicao: %EDITION%
echo(
echo(      ==============================================================================
echo(
echo(      [1]  MODO GAMER                         [8]  MENU CLASSICO ^(Win11^)
echo(
echo(      [2]  REMOVER MICROSOFT EDGE             [9]  GERENCIAR DESLIGAMENTO
echo(
echo(      [3]  WINDOWS UPDATE CONTROL             [10] WINUTIL - CHRIS TITUS TECH
echo(
echo(      [4]  REDE                               [11] ATUALIZAR VERSAO DO SCRIPT
echo(
echo(      [5]  PRIVACIDADE / ANTI TELEMETRIA      [12] PONTO DE RESTAURACAO
echo(
echo(      [6]  REPARAR SISTEMA                    [13] RESTAURAR PADROES
echo(
echo(      [7]  LIMPEZA TOTAL                      [0]  SAIR
echo(
echo(      ==============================================================================
echo(      Escolha uma opcao:
) > "%RBF%"
call :rainbow "%RBF%" n
call :ask_line op

if "%op%"=="1" goto gamer
if "%op%"=="2" goto remover_edge
if "%op%"=="3" goto wumenu
if "%op%"=="4" goto rede
if "%op%"=="5" goto telemetria
if "%op%"=="6" goto disparar_reparo
if "%op%"=="7" goto limpeza_nova_janela
if "%op%"=="8" goto menuclassico
if "%op%"=="9" goto desligamento
if "%op%"=="10" goto disparar_winutil
if "%op%"=="11" goto atualizar_versao
if "%op%"=="12" goto ponto_restauracao
if "%op%"=="13" goto restaurar
if "%op%"=="0" exit /b 0
goto menu

rem ============================================================
rem  [1] MODO GAMER
rem ============================================================
:gamer
call :ui_big
cls
set "PAD=    "
set "gm="
set "GAUTO="
set "GONLY="
(
echo(
echo(
echo(%PAD%=================================================
echo(%PAD%                   MODO GAMER
echo(%PAD%=================================================
echo(
echo(
echo(%PAD%[1]  AUTOMATICO
echo(%PAD%     Desativa SysMain, Windows Search, impressao
echo(%PAD%     ^(Spooler^), biometria / cartao inteligente,
echo(%PAD%     geolocalizacao, hotspot, overlay Xbox /
echo(%PAD%     Game Bar e hibernacao + Inicializacao Rapida
echo(%PAD%     Remove o app Xbox, se existir, e define
echo(%PAD%     tela e suspensao como nunca
echo(
echo(
echo(%PAD%[2]  SO XBOX
echo(%PAD%     Overlay / Game Bar e remove o app Xbox
echo(
echo(
echo(%PAD%[3]  SO SERVICOS
echo(%PAD%     Apenas os servicos, mantem o app Xbox
echo(
echo(
echo(%PAD%[4]  RESTAURAR
echo(
echo(%PAD%[5]  AREA DE TRANSFERENCIA   [0]  Voltar
echo(
echo(
echo(%PAD%=================================================
echo(%PAD%Escolha:
) > "%RBF%"
call :rainbow "%RBF%" n
call :ask_line gm
if "%gm%"=="1" set "GAUTO=1"
if "%gm%"=="1" call :ui_normal
if "%gm%"=="1" goto gamer_run
if "%gm%"=="2" set "GAUTO=1"
if "%gm%"=="2" set "GONLY=x"
if "%gm%"=="2" call :ui_normal
if "%gm%"=="2" goto gamer_run
if "%gm%"=="3" set "GAUTO=1"
if "%gm%"=="3" set "GONLY=s"
if "%gm%"=="3" call :ui_normal
if "%gm%"=="3" goto gamer_run
if "%gm%"=="4" call :ui_normal
if "%gm%"=="4" goto gamer_restore
if "%gm%"=="5" call :ui_normal
if "%gm%"=="5" goto gamer_clip
if "%gm%"=="0" call :ui_normal
if "%gm%"=="0" goto menu
goto gamer

:gamer_run
cls
call :hdr "                     MODO GAMER"
if defined GAUTO call :say "[*] Modo AUTOMATICO: aplicando tudo sem perguntas..."
echo.
if "%GONLY%"=="x" goto gamer_xbox
if "%GONLY%"=="s" goto gamer_svc
call :say "[*] Ativando plano Desempenho Maximo..."
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 %GAMER_GUID% >nul 2>&1
powercfg -setactive %GAMER_GUID% >nul 2>&1
if errorlevel 1 (
    call :say "[!] Desempenho Maximo indisponivel aqui. Usando Alto Desempenho."
    powercfg -setactive SCHEME_MIN >nul 2>&1
)
call :say "[*] Tela e suspensao: nunca..."
powercfg -change -monitor-timeout-ac 0 >nul 2>&1
powercfg -change -standby-timeout-ac 0 >nul 2>&1
:gamer_svc
call :say "[*] Desativando servicos desnecessarios..."
for %%S in (WerSvc MapsBroker RetailDemo Fax RemoteRegistry) do call :svc_disable %%S
echo.
call :gsn "Desativar tambem SysMain e Windows Search? [S/N]: "
if errorlevel 2 goto gamer_extra
for %%S in (SysMain WSearch) do call :svc_disable %%S

:gamer_extra
echo.
call :say "Servicos extras sem uso num PC focado em jogos:" "  - Spooler e PrintNotify: impressao" "    (quebra tambem Imprimir em PDF)" "  - Geolocalizacao, Hotspot movel, Telefone e" "    Controle dos Pais" "  - Cartao inteligente e biometria" "    (inclui digital do Windows Hello)"
call :gsn "Desativar esses servicos? [S/N]: "
if errorlevel 2 goto gamer_xbox
for %%S in (Spooler PrintNotify lfsvc icssvc PhoneSvc WpcMonSvc SCardSvr ScDeviceEnum SCPolicySvc SEMgrSvc WbioSrvc) do call :svc_disable %%S
if "%GONLY%"=="s" goto gamer_fim

:gamer_xbox
if "%GONLY%"=="s" goto gamer_fim
echo.
call :say "O Windows tenta abrir o overlay do Xbox" "(ms-gamingoverlay) ao iniciar um jogo ou conectar" "o controle, mesmo sem os apps Xbox instalados."
call :gsn "Desativar overlay/Game Bar e silenciar esse aviso? [S/N]: "
if errorlevel 2 goto gamer_gmode
call :xbox_overlay_off
call :xbox_app_remove
if "%GONLY%"=="x" goto gamer_fim

:gamer_gmode
echo.
call :say "[*] Ativando o Modo Jogo do Windows..."
call :game_mode_on

:gamer_hib
echo.
call :gsn "Desativar hibernacao e Inicializacao Rapida? [S/N]: "
if errorlevel 2 goto gamer_fim
powercfg -h off >nul 2>&1
echo hibernacao desativada pelo Callas Optimizer> "%HIBFLAG%"
:gamer_fim
set "GAUTO="
set "GONLY="
call :log "Modo gamer aplicado"
echo.
call :say "[OK] Modo Gamer aplicado. Use a opcao 13 para reverter."
call :pausa_rb
goto menu

:gamer_restore
cls
call :hdr "                  RESTAURAR MODO GAMER"
call :say "[*] Plano de energia..."
powercfg -setactive SCHEME_BALANCED >nul 2>&1
powercfg -delete %GAMER_GUID% >nul 2>&1
call :say "[*] Servicos..."
for %%S in (WerSvc MapsBroker RetailDemo Fax RemoteRegistry SysMain WSearch Spooler PrintNotify lfsvc icssvc PhoneSvc WpcMonSvc SCardSvr ScDeviceEnum SCPolicySvc SEMgrSvc WbioSrvc) do call :svc_restore_one %%S
if exist "%HIBFLAG%" (
    call :say "[*] Reativando hibernacao..."
    powercfg -h on >nul 2>&1
    del /f /q "%HIBFLAG%" >nul 2>&1
)
if exist "%XBOXFLAG%" (
    call :say "[*] Overlay Xbox / Game Bar..."
    reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /f >nul 2>&1
    reg delete "HKCU\System\GameConfigStore" /v GameDVR_Enabled /f >nul 2>&1
    reg delete "HKCU\Software\Microsoft\GameBar" /v UseNexusForGameBarEnabled /f >nul 2>&1
    reg delete "HKCU\Software\Microsoft\GameBar" /v ShowStartupPanel /f >nul 2>&1
    reg delete "%POL_GD%" /v AllowGameDVR /f >nul 2>&1
    for %%P in (ms-gamingoverlay ms-gamebar ms-gamebarservices) do reg delete "HKLM\SOFTWARE\Classes\%%P" /f >nul 2>&1
    del /f /q "%XBOXFLAG%" >nul 2>&1
)
if exist "%GMFLAG%" (
    call :say "[*] Modo Jogo..."
    reg delete "HKCU\Software\Microsoft\GameBar" /v AutoGameModeEnabled /f >nul 2>&1
    reg delete "HKCU\Software\Microsoft\GameBar" /v AllowAutoGameMode /f >nul 2>&1
    del /f /q "%GMFLAG%" >nul 2>&1
)
call :log "Modo gamer revertido"
echo.
call :say "[OK] Modo Gamer revertido. Reiniciar o PC e recomendado."
call :pausa_rb
goto menu

:gamer_clip
cls
set "CLPOL="
for /f "tokens=3" %%A in ('reg query "%POL_SY%" /v AllowClipboardHistory 2^>nul ^| findstr REG_DWORD') do set "CLPOL=%%A"
for /f "tokens=3" %%A in ('reg query "%POL_SY%" /v AllowCrossDeviceClipboard 2^>nul ^| findstr REG_DWORD') do if "%%A"=="0x0" set "CLPOL=0x0"
if "%CLPOL%"=="0x0" goto gamer_clip_on
reg add "%POL_SY%" /v AllowClipboardHistory /t REG_DWORD /d 0 /f >nul 2>&1
reg add "%POL_SY%" /v AllowCrossDeviceClipboard /t REG_DWORD /d 0 /f >nul 2>&1
call :log "Area de transferencia desativada via politica"
call :say "[OK] Area de transferencia desativada via politica."
call :pausa_rb
goto menu

:gamer_clip_on
reg delete "%POL_SY%" /v AllowClipboardHistory /f >nul 2>&1
reg delete "%POL_SY%" /v AllowCrossDeviceClipboard /f >nul 2>&1
reg delete "HKCU\Software\Policies\Microsoft\Windows\System" /v AllowClipboardHistory /f >nul 2>&1
reg delete "HKCU\Software\Policies\Microsoft\Windows\System" /v AllowCrossDeviceClipboard /f >nul 2>&1
call :log "Area de transferencia liberada (politica removida)"
call :say "[OK] Area de transferencia liberada."
call :pausa_rb
goto menu

rem ============================================================
rem  [2] REMOVER MICROSOFT EDGE
rem ============================================================
:remover_edge
call :ui_big
cls
set "PAD=    "
set "ed="
(
echo(
echo(%PAD%=================================================
echo(%PAD%                MICROSOFT EDGE
echo(%PAD%=================================================
echo(
echo(%PAD%Remover: desativa o Edge Update, apaga as
echo(%PAD%tarefas agendadas, bloqueia a reinstalacao
echo(%PAD%por politica, desinstala o Edge e apaga as
echo(%PAD%pastas dele ^(Edge, EdgeUpdate, EdgeCore, Temp^).
echo(%PAD%O WebView2 Runtime NAO e removido
echo(%PAD%^(outros programas dependem dele^).
echo(
echo(%PAD%[!] Tenha outro navegador instalado antes
echo(%PAD%    de continuar.
echo(
echo(
echo(%PAD%[1]  Remover Microsoft Edge
echo(
echo(%PAD%[2]  Restaurar Microsoft Edge
echo(
echo(%PAD%[0]  Voltar
echo(
echo(%PAD%=================================================
echo(%PAD%Escolha:
) > "%RBF%"
call :rainbow "%RBF%" n
call :ask_line ed
if "%ed%"=="1" call :ui_normal
if "%ed%"=="1" goto edge_remove_go
if "%ed%"=="2" call :ui_normal
if "%ed%"=="2" goto edge_restore
if "%ed%"=="0" call :ui_normal
if "%ed%"=="0" goto menu
goto remover_edge

:edge_remove_go
cls
call :hdr "                REMOVER MICROSOFT EDGE"
call :sn "Continuar? [S/N]: "
if errorlevel 2 goto remover_edge

set "PF86=%ProgramFiles%"
if defined ProgramFiles(x86) set "PF86=%ProgramFiles(x86)%"

echo.
call :say "[1/7] Encerrando processos do Edge..."
taskkill /f /im msedge.exe >nul 2>&1
taskkill /f /im MicrosoftEdgeUpdate.exe >nul 2>&1
taskkill /f /im msedgeupdate.exe >nul 2>&1

call :say "[2/7] Desativando servicos do Edge Update..."
for %%S in (edgeupdate edgeupdatem MicrosoftEdgeElevationService) do call :svc_disable %%S

call :say "[3/7] Removendo tarefas agendadas do Edge Update..."
for /f "tokens=1 delims=," %%T in ('schtasks /query /fo csv /nh 2^>nul ^| findstr /i "MicrosoftEdgeUpdate"') do (
    schtasks /change /tn "%%~T" /disable >nul 2>&1
    schtasks /delete /tn "%%~T" /f >nul 2>&1
)

call :say "[4/7] Aplicando bloqueios no registro..."
reg add "HKLM\SOFTWARE\Microsoft\EdgeUpdate" /v DoNotUpdateToEdgeWithChromium /t REG_DWORD /d 1 /f >nul
reg add "HKLM\SOFTWARE\Policies\Microsoft\EdgeUpdate" /v InstallDefault /t REG_DWORD /d 0 /f >nul
reg add "HKLM\SOFTWARE\Policies\Microsoft\EdgeUpdate" /v "Install{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}" /t REG_DWORD /d 0 /f >nul
reg add "HKLM\SOFTWARE\Policies\Microsoft\EdgeUpdate" /v "Update{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}" /t REG_DWORD /d 0 /f >nul

call :say "[5/7] Desinstalando o Edge, se ainda existir..."
if exist "%PF86%\Microsoft\Edge\Application" (
    for /d %%V in ("%PF86%\Microsoft\Edge\Application\*") do (
        if exist "%%~fV\Installer\setup.exe" "%%~fV\Installer\setup.exe" --uninstall --system-level --verbose-logging --force-uninstall
    )
) else (
    call :say "       Edge ja nao estava instalado."
)

call :say "[6/7] Apagando pastas do Edge..."
taskkill /f /im msedge.exe >nul 2>&1
if exist "%PF86%\Microsoft\EdgeUpdate" rd /s /q "%PF86%\Microsoft\EdgeUpdate" >nul 2>&1
if exist "%PF86%\Microsoft\Edge" rd /s /q "%PF86%\Microsoft\Edge" >nul 2>&1
if exist "%PF86%\Microsoft\Temp" rd /s /q "%PF86%\Microsoft\Temp" >nul 2>&1
if exist "%PF86%\Microsoft\EdgeCore" rd /s /q "%PF86%\Microsoft\EdgeCore" >nul 2>&1
if exist "%PF86%\Microsoft\EdgeCore" call :say "       [AVISO] EdgeCore em uso, nao apagou." "       Reinicie e rode esta opcao de novo."

call :say "[7/7] Removendo atalhos do Edge..."
del /f /q "%PUBLIC%\Desktop\Microsoft Edge.lnk" >nul 2>&1
del /f /q "%USERPROFILE%\Desktop\Microsoft Edge.lnk" >nul 2>&1
del /f /q "%ProgramData%\Microsoft\Windows\Start Menu\Programs\Microsoft Edge.lnk" >nul 2>&1

echo edge removido pelo Callas Optimizer> "%EDGEBK%"
call :log "Microsoft Edge removido e bloqueado"
echo.
call :say "[OK] Edge removido e bloqueado. Reinicie o PC para finalizar."
call :pausa_rb
goto menu

:edge_restore
cls
call :hdr "               RESTAURAR MICROSOFT EDGE"
call :say "[1/2] Removendo bloqueios do registro..."
reg delete "HKLM\SOFTWARE\Microsoft\EdgeUpdate" /v DoNotUpdateToEdgeWithChromium /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Policies\Microsoft\EdgeUpdate" /v InstallDefault /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Policies\Microsoft\EdgeUpdate" /v "Install{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}" /f >nul 2>&1
reg delete "HKLM\SOFTWARE\Policies\Microsoft\EdgeUpdate" /v "Update{56EB18F8-B008-4CBD-B6D2-8C97FE7E9062}" /f >nul 2>&1
del /f /q "%EDGEBK%" >nul 2>&1
call :say "[2/2] Reinstalando o Microsoft Edge..."
where winget >nul 2>&1
if errorlevel 1 goto edge_restore_manual
winget install --id Microsoft.Edge -e --silent --accept-package-agreements --accept-source-agreements
if errorlevel 1 goto edge_restore_manual
call :log "Microsoft Edge restaurado"
echo.
call :say "[OK] Microsoft Edge reinstalado."
call :pausa_rb
goto menu

:edge_restore_manual
call :log "Edge: bloqueios removidos, reinstalacao manual"
echo.
call :say "[i] Bloqueios removidos, mas nao foi possivel instalar" "    sozinho. Abrindo a pagina oficial de download..."
start "" https://www.microsoft.com/edge/download
call :pausa_rb
goto menu

rem ============================================================
rem  [8] MENU CLASSICO
rem ============================================================
:menuclassico
cls
set "PAD=             "
call :hdr "                MENU DE CONTEXTO CLASSICO"
echo.
if %BUILD% GTR 0 if %BUILD% LSS 22000 (
    call :say "[i] O menu de contexto classico so existe no Windows 11." "    No Windows 10 ele ja e o padrao, nada a fazer."
    call :pausa_rb
    goto menu
)
> "%RBF%" echo(%PAD%[A] Ativar   [R] Reverter   [V] Voltar:
call :rainbow "%RBF%" n
set "ACARGS="
set "ACSEC=0"
set "ACDEF="
call :ask_choice ARV
if errorlevel 3 goto menu
if errorlevel 2 goto menuclassico_rev
reg add "%CLSID_KEY%\InprocServer32" /f /ve >nul
call :restart_explorer
call :log "Menu classico ativado"
echo.
call :say "[OK] Menu classico ativado."
call :pausa_rb
goto menu

:menuclassico_rev
reg delete "%CLSID_KEY%" /f >nul 2>&1
call :restart_explorer
call :log "Menu classico revertido"
echo.
call :say "[OK] Menu padrao do Windows 11 restaurado."
call :pausa_rb
goto menu

rem ============================================================
rem  [4] REDE
rem ============================================================
:rede
cls
set "PAD=             "
set "rd="
(
echo(
echo(
echo(
echo(
echo(%PAD%======================================================
echo(%PAD%                        REDE
echo(%PAD%======================================================
echo(
echo(%PAD%[1]  Otimizar configuracoes de rede
echo(
echo(%PAD%[2]  Salvar configuracao do adaptador
echo(
echo(%PAD%[3]  Limpeza de rede
echo(
echo(%PAD%[4]  DNS Cloudflare / Google
echo(
echo(%PAD%[0]  Voltar
echo(
echo(%PAD%======================================================
echo(%PAD%Escolha:
) > "%RBF%"
call :rainbow "%RBF%" n
call :ask_line rd
if "%rd%"=="1" goto rede_aplicar
if "%rd%"=="2" goto rede_salvar
if "%rd%"=="3" goto rede_limpeza
if "%rd%"=="4" goto rede_dns
if "%rd%"=="0" goto menu
goto rede

:rede_aplicar
cls
set "PAD=             "
call :say "[*] Aplicando configuracao no adaptador..."
call :psnet apply
set "NETERR=%errorlevel%"
echo.
if "%NETERR%"=="0" call :say "[OK] Configuracao aplicada ao adaptador."
if "%NETERR%"=="0" call :log "Configuracao de rede aplicada"
if "%NETERR%"=="1" call :say "[!] Nenhum adaptador de rede ativo encontrado."
if "%NETERR%"=="3" call :say "[!] Arquivo de configuracao nao encontrado:" "    %NETF%"
if "%NETERR%"=="3" call :say "    Use a opcao 2 antes de formatar."
if "%NETERR%"=="2" call :say "[!] Nao foi possivel ler o arquivo de configuracao."
if "%NETERR%"=="4" call :say "[!] Algumas configuracoes nao foram aplicadas. Veja rede.log."
if "%NETERR%"=="9" call :say "[!] Falha ao executar. Veja rede.log."
call :pausa_rb
goto rede

:rede_salvar
cls
set "PAD=             "
if not exist "%NETDIR%" mkdir "%NETDIR%" >nul 2>&1
call :say "[*] Lendo configuracao do adaptador..."
call :psnet save
set "NETERR=%errorlevel%"
echo.
if "%NETERR%"=="0" call :say "[OK] Configuracao salva em:" "    %NETF%"
if "%NETERR%"=="0" call :log "Configuracao de rede salva"
if "%NETERR%"=="1" call :say "[!] Nenhum adaptador de rede ativo encontrado."
if "%NETERR%"=="2" call :say "[!] Nao foi possivel salvar o arquivo nesta pasta."
if "%NETERR%"=="9" call :say "[!] Falha ao executar. Veja rede.log."
call :pausa_rb
goto rede

:rede_dns
cls
set "PAD=             "
set "dn="
(
echo(
echo(
echo(
echo(
echo(%PAD%======================================================
echo(%PAD%                          DNS
echo(%PAD%======================================================
echo(
echo(%PAD%[1]  Cloudflare
echo(
echo(%PAD%[2]  Google
echo(
echo(%PAD%[3]  Automatico
echo(
echo(%PAD%[0]  Voltar
echo(
echo(%PAD%======================================================
echo(%PAD%Escolha:
) > "%RBF%"
call :rainbow "%RBF%" n
call :ask_line dn
if "%dn%"=="1" set "DNSN=Cloudflare"
if "%dn%"=="1" set "DNSV=1.1.1.1"
if "%dn%"=="1" set "DNSB=1.0.0.1"
if "%dn%"=="1" goto dns_set
if "%dn%"=="2" set "DNSN=Google"
if "%dn%"=="2" set "DNSV=8.8.8.8"
if "%dn%"=="2" set "DNSB=8.8.4.4"
if "%dn%"=="2" goto dns_set
if "%dn%"=="3" goto dns_auto
if "%dn%"=="0" goto rede
goto rede_dns

:dns_set
cls
set "PAD=             "
call :say "[*] Aplicando DNS %DNSN%..."
set "DNSLIST=%DNSV%,%DNSB%"
call :psnet dns
if errorlevel 1 goto dns_fail
call :log "DNS %DNSN% aplicado"
echo.
call :say "[OK] DNS %DNSN% aplicado."
call :pausa_rb
goto rede_dns

:dns_auto
cls
set "PAD=             "
call :say "[*] Restaurando DNS automatico..."
call :psnet dnsauto
if errorlevel 1 goto dns_fail
call :log "DNS automatico restaurado"
echo.
call :say "[OK] DNS automatico restaurado."
call :pausa_rb
goto rede_dns

:dns_fail
echo.
call :say "[!] Nao foi possivel alterar o DNS. Veja rede.log."
call :pausa_rb
goto rede_dns

:rede_limpeza
cls
set "PAD=             "
call :say "[*] Limpando cache DNS..."
ipconfig /flushdns >nul
call :say "[OK] DNS limpo."
netsh winsock reset >nul
netsh int ip reset >nul 2>&1
call :log "DNS limpo"
call :log "Reset de rede executado"
echo.
call :say "[OK] Reset concluido. REINICIE o computador para finalizar."
call :pausa_rb
goto rede

rem ============================================================
rem  [5] PRIVACIDADE / ANTI TELEMETRIA
rem ============================================================
:telemetria
cls
set "PAD=             "
call :hdr "             PRIVACIDADE / ANTI TELEMETRIA"
call :say "Edicao detectada: %EDITION%"
if "%TELE%"=="1" call :say "[i] Esta edicao nao aceita o nivel 0." "    Sera aplicado o nivel minimo permitido: 1."
echo.
for %%S in (DiagTrack dmwappushsvc WerSvc) do call :svc_disable %%S
reg add "%POL_DC%" /v AllowTelemetry /t REG_DWORD /d %TELE% /f >nul
reg add "%POL_AD%" /v DisabledByGroupPolicy /t REG_DWORD /d 1 /f >nul
call :log "Telemetria ajustada, nivel %TELE%"
call :say "[OK] Telemetria reduzida. Use a opcao 13 para reverter."
call :pausa_rb
goto menu

rem ============================================================
rem  [9] DESLIGAMENTO
rem ============================================================
:desligamento
cls
set "PAD=             "
set "d="
set "mins="
(
echo(
echo(
echo(
echo(
echo(%PAD%======================================================
echo(%PAD%                GERENCIAR DESLIGAMENTO
echo(%PAD%======================================================
echo(
echo(%PAD%[1]  5 minutos
echo(
echo(%PAD%[2]  15 minutos
echo(
echo(%PAD%[3]  30 minutos
echo(
echo(%PAD%[4]  1 hora
echo(
echo(%PAD%[5]  Cancelar agendamento
echo(
echo(%PAD%[6]  Personalizado
echo(
echo(%PAD%[0]  Voltar
echo(
echo(%PAD%======================================================
echo(%PAD%Escolha:
) > "%RBF%"
call :rainbow "%RBF%" n
call :ask_line d

if "%d%"=="1" set "mins=5"
if "%d%"=="2" set "mins=15"
if "%d%"=="3" set "mins=30"
if "%d%"=="4" set "mins=60"
if "%d%"=="5" goto deslig_cancel
if "%d%"=="6" goto deslig_custom
if "%d%"=="0" goto menu
if not defined mins goto desligamento
goto deslig_apply

:deslig_custom
set "mins="
set /p "mins=%PAD%Minutos (1 a 1440): "
powershell -NoProfile -Command "if($env:mins -match '^[0-9]{1,4}$' -and [int]$env:mins -ge 1 -and [int]$env:mins -le 1440){exit 0}else{exit 1}" >nul 2>&1
if errorlevel 1 goto desligamento
goto deslig_apply

:deslig_apply
set "secs="
set /a secs=mins*60 2>nul
if not defined secs goto desligamento
if %secs% LEQ 0 goto desligamento
if %secs% GTR 86400 goto desligamento
shutdown /a >nul 2>&1
shutdown /s /t %secs%
if errorlevel 1 (
    call :say "[!] Falha ao agendar o desligamento."
    call :log "Falha ao agendar desligamento"
) else (
    call :log "Desligamento agendado: %mins% min"
    call :say "[OK] Desligamento agendado para daqui a %mins% minuto(s)."
)
call :pausa_rb
goto desligamento

:deslig_cancel
shutdown /a >nul 2>&1
if errorlevel 1 (
    echo.
    call :say "[i] Nao havia desligamento agendado."
) else (
    echo.
    call :say "[OK] Agendamento cancelado."
)
call :pausa_rb
goto desligamento

rem ============================================================
rem  [3] WINDOWS UPDATE CONTROL
rem ============================================================
:wumenu
cls
set "PAD=             "
set "wu="
(
echo(
echo(
echo(
echo(
echo(%PAD%======================================================
echo(%PAD%                WINDOWS UPDATE CONTROL
echo(%PAD%======================================================
echo(
echo(%PAD%[1]  Desativar atualizacoes automaticas
echo(
echo(%PAD%[2]  Apenas notificar antes de baixar
echo(
echo(%PAD%[3]  Congelar servicos
echo(
echo(%PAD%[4]  Restaurar padrao
echo(
echo(%PAD%[0]  Voltar
echo(
echo(%PAD%======================================================
echo(%PAD%Escolha:
) > "%RBF%"
call :rainbow "%RBF%" n
call :ask_line wu

if "%wu%"=="1" goto wupolicy
if "%wu%"=="2" goto wunotify
if "%wu%"=="3" goto wufreeze
if "%wu%"=="4" goto wurestore
if "%wu%"=="0" goto menu
goto wumenu

:wupolicy
reg add "%POL_WU%\AU" /v NoAutoUpdate /t REG_DWORD /d 1 /f >nul
call :log "WU: atualizacao automatica desativada por politica"
echo.
call :say "[OK] Atualizacoes automaticas desativadas por politica." "     Os servicos continuam ativos: DISM, Store e" "     Defender funcionam."
call :pausa_rb
goto wumenu

:wunotify
reg add "%POL_WU%\AU" /v NoAutoUpdate /t REG_DWORD /d 0 /f >nul
reg add "%POL_WU%\AU" /v AUOptions /t REG_DWORD /d 2 /f >nul
call :log "WU: apenas notificar"
echo.
call :say "[OK] Configurado para notificar antes de baixar."
call :pausa_rb
goto wumenu

:wufreeze
echo.
call :say "[!] ATENCAO: isso desabilita Windows Update," "    BITS, Delivery Optimization e Update" "    Orchestrator. Afeta Microsoft Store e as" "    definicoes do Defender, e o DISM /RestoreHealth" "    nao conseguira baixar arquivos." "    O Windows pode reativar os servicos sozinho."
echo.
call :sn "Continuar? [S/N]: "
if errorlevel 2 goto wumenu
for %%S in (wuauserv bits dosvc UsoSvc) do call :svc_disable %%S
call :log "WU: servicos congelados"
echo.
call :say "[OK] Servicos de atualizacao desabilitados."
call :pausa_rb
goto wumenu

:wurestore
reg delete "%POL_WU%\AU" /f >nul 2>&1
call :svc_restore_one wuauserv demand
call :svc_restore_one bits demand
call :svc_restore_one dosvc delayed-auto
call :svc_restore_one UsoSvc delayed-auto
call :log "WU: padrao restaurado"
echo.
call :say "[OK] Windows Update restaurado."
call :pausa_rb
goto wumenu

rem ============================================================
rem  [13] RESTAURAR PADROES
rem ============================================================
:restaurar
cls
set "PAD=             "
call :hdr "                 RESTAURAR PADROES"
call :say "Isso reverte: plano de energia, hibernacao" "(se foi desativada por este script), menu classico," "overlay Xbox / Game Bar, Modo Jogo, politicas de" "telemetria e Windows Update, e os servicos" "alterados (via backup)."
echo.
call :sn "Continuar? [S/N]: "
if errorlevel 2 goto menu
echo.
call :say "[*] Plano de energia..."
powercfg -setactive SCHEME_BALANCED >nul 2>&1
powercfg -delete %GAMER_GUID% >nul 2>&1
if exist "%HIBFLAG%" (
    call :say "[*] Reativando hibernacao..."
    powercfg -h on >nul 2>&1
    del /f /q "%HIBFLAG%" >nul 2>&1
)
call :say "[*] Politicas..."
reg delete "%POL_DC%" /v AllowTelemetry /f >nul 2>&1
reg delete "%POL_AD%" /v DisabledByGroupPolicy /f >nul 2>&1
reg delete "%POL_WU%\AU" /f >nul 2>&1
if exist "%XBOXFLAG%" (
    call :say "[*] Overlay Xbox / Game Bar..."
    reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /f >nul 2>&1
    reg delete "HKCU\System\GameConfigStore" /v GameDVR_Enabled /f >nul 2>&1
    reg delete "HKCU\Software\Microsoft\GameBar" /v UseNexusForGameBarEnabled /f >nul 2>&1
    reg delete "HKCU\Software\Microsoft\GameBar" /v ShowStartupPanel /f >nul 2>&1
    reg delete "%POL_GD%" /v AllowGameDVR /f >nul 2>&1
    for %%P in (ms-gamingoverlay ms-gamebar ms-gamebarservices) do reg delete "HKLM\SOFTWARE\Classes\%%P" /f >nul 2>&1
    del /f /q "%XBOXFLAG%" >nul 2>&1
)
if exist "%GMFLAG%" (
    call :say "[*] Modo Jogo..."
    reg delete "HKCU\Software\Microsoft\GameBar" /v AutoGameModeEnabled /f >nul 2>&1
    reg delete "HKCU\Software\Microsoft\GameBar" /v AllowAutoGameMode /f >nul 2>&1
    del /f /q "%GMFLAG%" >nul 2>&1
)
call :say "[*] Servicos..."
call :svc_restore_all
if errorlevel 1 call :log "Restaurar padroes: falha em alguns servicos"
call :say "[*] Menu de contexto..."
reg delete "%CLSID_KEY%" /f >nul 2>&1
call :restart_explorer
call :log "Padroes restaurados"
echo.
call :say "[OK] Padroes restaurados. Reiniciar o PC e recomendado."
call :pausa_rb
goto menu

rem ============================================================
rem  [7] LIMPEZA TOTAL (V8.8 - correcao: executa na mesma janela)
rem ============================================================
:limpeza_nova_janela
rem Nao usar START/conhost aqui: falhas de abertura deixavam a opcao 7 sem resposta.
call :ui_normal
set "PAD=             "
call :limpeza_real
goto menu

:limpeza_real
title CALLAS OPTIMIZER V8.8 - Limpeza Total
cls
call :hdr "                    LIMPEZA TOTAL"
call :say "[i] A limpeza exclui arquivos temporarios e esvazia" "    a Lixeira. Pode reiniciar a Area de Trabalho." "    Feche programas e salve arquivos importantes." "    Prefetch e dumps de diagnostico serao preservados." "    Logs de eventos e DISM serao opcionais."
echo.
call :sn "Iniciar limpeza total? [S/N]: "
if errorlevel 2 (
    title CALLAS OPTIMIZER V8.8
    exit /b 0
)
set "CLEAN_WARN=0"
set "FREE_BEFORE="
set "FREE_AFTER="
call :getfree FREE_BEFORE
call :log "Limpeza total iniciada"
echo.
rem O bloco PowerShell e integrado ao proprio BAT (nao requer downloads).
rem Ele informa progresso, verifica exclusoes e reinicia apenas os servicos
rem que estavam ativos antes da limpeza, mesmo em caso de erro.
call :psclean
set "CLEAN_RC=%errorlevel%"
if not "%CLEAN_RC%"=="0" set "CLEAN_WARN=1"

echo.
call :say "[10/11] Limpar logs do Visualizador de Eventos?" "      Isso apaga historicos uteis para diagnosticos." "      O log de Seguranca (Security) sera preservado."
call :sn "      Limpar logs? [S/N] (padrao N em 10s): " "/t 10 /d N"
if errorlevel 2 goto limp_dism
call :say "      Limpando logs disponiveis (pode demorar)..."
set "EVFAIL=0"
for /f "delims=" %%G in ('wevtutil.exe el 2^>nul') do (
    if /i not "%%G"=="Security" (
        wevtutil.exe cl "%%G" >nul 2>&1
        if errorlevel 1 set "EVFAIL=1"
    )
)
if "%EVFAIL%"=="0" (
    call :say "      Logs disponiveis limpos."
) else (
    set "CLEAN_WARN=1"
    call :say "      [!] Alguns logs sao protegidos ou estavam em uso."
    call :log "Limpeza de logs de eventos parcialmente concluida"
)

:limp_dism
echo.
call :say "[11/11] Executar DISM /StartComponentCleanup?" "      Pode demorar e reduzir a opcao de remover updates."
call :sn "      Executar? [S/N] (padrao N em 10s): " "/t 10 /d N"
if errorlevel 2 goto limp_fim
dism /online /cleanup-image /startcomponentcleanup
if errorlevel 1 (
    set "CLEAN_WARN=1"
    call :log "DISM StartComponentCleanup falhou"
    call :say "[!] DISM falhou; confira os logs do Windows."
) else (
    call :log "DISM StartComponentCleanup concluido"
)

:limp_fim
call :getfree FREE_AFTER
call :log "Limpeza total finalizada; avisos=%CLEAN_WARN%"
echo.
if "%CLEAN_WARN%"=="0" (
    call :hdr "             LIMPEZA TOTAL FINALIZADA"
) else (
    call :hdr "          LIMPEZA FINALIZADA COM AVISOS"
    call :say "Verifique o log de limpeza em CallasTeck\limpeza.log"
)
if not defined FREE_BEFORE goto limp_end
if not defined FREE_AFTER goto limp_end
set /a FREED=FREE_AFTER-FREE_BEFORE 2>nul
if not defined FREED goto limp_end
if %FREED% LSS 0 set "FREED=0"
call :say "Espaco liberado: aproximadamente %FREED% MB"
:limp_end
echo.
call :pausa_rb
title CALLAS OPTIMIZER V8.8
exit /b 0

rem ============================================================
rem  [6] REPARAR SISTEMA (janela dedicada, em sequencia)
rem ============================================================
:disparar_reparo
start "CALLAS OPTIMIZER - Reparo" %CON% cmd /c ""%~f0" :reparo_real"
goto menu

:reparo_real
title CALLAS OPTIMIZER - Reparo do Sistema
cls
call :hdr "       ETAPA 1/3: DISM (REPARO DA IMAGEM BASE)"
echo.

rem O DISM /RestoreHealth baixa arquivos via Windows Update.
rem Se os servicos estiverem desabilitados, habilita so durante o reparo.
set "WUDIS="
set "BITSDIS="
call :svc_is_disabled wuauserv && set "WUDIS=1"
call :svc_is_disabled bits && set "BITSDIS=1"
if defined WUDIS sc config wuauserv start= demand >nul 2>&1
if defined BITSDIS sc config bits start= demand >nul 2>&1
if defined WUDIS call :say "[i] Windows Update estava desabilitado: habilitado temporariamente."
call :say "Baixando pacotes de integridade da Microsoft... aguarde."
echo.

dism /online /cleanup-image /restorehealth
set "DISMERR=%errorlevel%"

if defined WUDIS (
    sc stop wuauserv >nul 2>&1
    sc config wuauserv start= disabled >nul 2>&1
)
if defined BITSDIS (
    sc stop bits >nul 2>&1
    sc config bits start= disabled >nul 2>&1
)

if not "%DISMERR%"=="0" goto rep_falha

echo.
call :say "[OK] DISM concluido com sucesso."
echo.
call :hdr "       ETAPA 2/3: SFC (VERIFICADOR DE ARQUIVOS)"
echo.
sfc /scannow
set "SFCERR=%errorlevel%"
if not "%SFCERR%"=="0" (
    call :say "[!] SFC retornou codigo %SFCERR%. Verifique o resultado acima."
    call :log "SFC retornou codigo %SFCERR%"
)
echo.
call :hdr "       ETAPA 3/3: CHKDSK (VERIFICACAO ONLINE)"
echo.
powershell -NoProfile -Command "try { $r = Repair-Volume -DriveLetter $env:SystemDrive[0] -Scan -ErrorAction Stop; Write-Host ('Resultado: ' + $r) } catch { Write-Host ('[!] ' + $_.Exception.Message); exit 1 }"
if errorlevel 1 goto rep_chk_falha
call :log "Reparo DISM + SFC + CHKDSK concluido"
goto rep_fim

:rep_chk_falha
echo.
call :say "[!] A verificacao de disco nao pode ser concluida." "    Nao e critico: o DISM e o SFC ja foram executados." "    Para ver o motivo, rode como admin no Prompt de Comando:" "    chkdsk %SystemDrive% /scan"
call :log "Verificacao de disco falhou"

:rep_fim
echo.
call :hdr "     REPARO FINALIZADO (Pode fechar esta janela)"
call :pausa_rb
exit

:rep_falha
echo.
call :say "======================================================" "[X] O DISM falhou (codigo %DISMERR%)." "    Verifique a conexao com a internet e o Windows Update." "    O SFC nao foi executado para evitar um resultado enganoso." "======================================================"
call :log "DISM falhou, codigo %DISMERR%"
call :pausa_rb
exit

rem ============================================================
rem  [10] WINUTIL - CHRIS TITUS TECH (janela dedicada)
rem ============================================================
:disparar_winutil
call :say "[!] O WinUtil executa codigo baixado da internet." "    Use apenas se confiar na fonte do script."
call :sn "Executar WinUtil? [S/N]: "
if errorlevel 2 goto menu
start "CALLAS OPTIMIZER - WinUtil" %CON% powershell -NoProfile -ExecutionPolicy Bypass -Command "[Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; try { irm https://christitus.com/win | iex } catch { Write-Host ('[!] Falha: ' + $_.Exception.Message) -ForegroundColor Red; Read-Host }"
goto menu

rem ============================================================
rem  SUBROTINAS
rem ============================================================

:log
>>"%LOG%" echo [%date% %time%] %~1
exit /b 0

rem --- Arco-iris estatico: imprime um arquivo de texto com cor por coluna
rem     %1 = arquivo | %2 = n (cursor fica no fim da ultima linha) ---

:rainbow
if defined NOVT goto rainbow_plain
powershell -NoProfile -Command "$e=[string][char]27;$W=72;$l=@(Get-Content -LiteralPath '%~1' -Encoding OEM);$nn=('%~2' -eq 'n');$n=0;foreach($x in $l){$o='';for($i=0;$i -lt $x.Length;$i++){$c=$x[$i];if($c -eq ' '){$o+=' ';continue};$h=6*($i+2*$n)/$W;$h=$h-6*[math]::Floor($h/6);$s=[int][math]::Floor($h);$f=$h-$s;$q=[int](255*(1-$f));$t=[int](255*$f);$p=@(@(255,$t,0),@($q,255,0),@(0,255,$t),@(0,$q,255),@($t,0,255),@(255,0,$q))[$s];$o+=$e+'[38;2;'+$p[0]+';'+$p[1]+';'+$p[2]+'m'+$c};$o+=$e+'[0m';if($nn -and $n -eq ($l.Count-1)){Write-Host ($o+' ') -NoNewline}else{Write-Host $o};$n++}"
del /f /q "%~1" >nul 2>&1
exit /b 0

:rainbow_plain
type "%~1"
del /f /q "%~1" >nul 2>&1
exit /b 0

rem --- Cabecalho de tela em arco-iris: call :hdr "titulo" ---

:hdr
> "%RBF%" echo(%PAD%======================================================
>> "%RBF%" echo(%PAD%%~1
>> "%RBF%" echo(%PAD%======================================================
>> "%RBF%" echo(
call :rainbow "%RBF%"
exit /b 0

rem --- Imprime 1 ou mais linhas (cada argumento = 1 linha) em arco-iris: call :say "a" "b" ---

:say
> "%RBF%" echo(%PAD%%~1
:say_loop
shift
if "%~1"=="" goto say_go
>> "%RBF%" echo(%PAD%%~1
goto say_loop
:say_go
call :rainbow "%RBF%"
exit /b 0

rem --- Pergunta S/N em arco-iris: call :sn "texto" ["/t 10 /d N"]  (devolve o errorlevel do choice) ---

:sn
set "SQ=%~1"
set "SQ=%SQ:[S/N]=[S] Sim  [N] Nao%"
> "%RBF%" echo(%PAD%%SQ%
call :rainbow "%RBF%" n
set "ACARGS=%~2"
set "ACSEC=0"
set "ACDEF="
if defined ACARGS for /f "tokens=2,4" %%T in ("%ACARGS%") do (
    set "ACSEC=%%T"
    if /i "%%U"=="S" (set "ACDEF=1") else (set "ACDEF=2")
)
call :ask_choice SN
exit /b %errorlevel%

rem --- Entrada por teclado OU mouse. O helper PowerShell fica no fim deste
rem     arquivo (depois de #PSMBEGIN). Se falhar, cai no modo classico. ---

:psm
set "MRES=%RBF%.res"
del /f /q "%MRES%" >nul 2>&1
if "%MOUSE%"=="0" exit /b 1
powershell -NoProfile -Command "try{$t=[IO.File]::ReadAllText($env:SELF);$i=$t.LastIndexOf('#PSM'+'BEGIN');& ([scriptblock]::Create($t.Substring($i))) -Res '%MRES%' -Mode '%~1' -Keys '%~2' -Secs %~3 -Def '%~4' -Size %FSZ%}catch{Add-Content -LiteralPath ($env:BKDIR+'\mouse_debug.log') -Value ('psm: '+$_.Exception.Message)}" 2>nul
if exist "%MRES%" exit /b 0
if /i not "%~1"=="font" >> "%BKDIR%\mouse_debug.log" echo [%date% %time%] helper sem resultado: modo=%~1
exit /b 1

rem --- call :ask_line VAR  (texto digitado ou numero clicado) ---

:ask_line
set "%~1="
call :psm line "" 0 ""
if errorlevel 1 goto ask_line_classic
set /p "%~1=" < "%MRES%"
del /f /q "%MRES%" >nul 2>&1
exit /b 0

:ask_line_classic
set /p "%~1="
exit /b 0

rem --- call :ask_choice TECLAS  (errorlevel = posicao da tecla escolhida) ---

:ask_choice
set "ACKEYS=%~1"
call :psm choice "%ACKEYS%" %ACSEC% "%ACDEF%"
if errorlevel 1 goto ask_choice_classic
set "ACR="
set /p "ACR=" < "%MRES%"
del /f /q "%MRES%" >nul 2>&1
if not defined ACR goto ask_choice_classic
exit /b %ACR%

:ask_choice_classic
choice /c %ACKEYS% /n %ACARGS%
exit /b %errorlevel%

rem --- Letras maiores nos submenus (muda a fonte e o tamanho da janela, mesmo tamanho em pixels) ---

:ui_big
if defined BIGUI exit /b 0
if "%MOUSE%"=="0" exit /b 0
set "FSZ=%FONT_BIG%"
call :psm font "" 0 ""
if errorlevel 1 goto ui_big_fail
set "FSZ=%FONT_SIZE%"
mode con: cols=%BIG_COLS% lines=%BIG_LINES% >nul 2>&1
set "BIGUI=1"
exit /b 0

:ui_big_fail
set "FSZ=%FONT_SIZE%"
exit /b 0

:ui_normal
set "PAD=             "
if not defined BIGUI exit /b 0
set "BIGUI="
set "FSZ=%FONT_SIZE%"
call :psm font "" 0 ""
mode con: cols=%WIN_COLS% lines=%WIN_LINES% >nul 2>&1
exit /b 0

rem --- Pergunta do Modo Gamer: no modo AUTOMATICO responde SIM sozinho (errorlevel 1) ---

:gsn
if not defined GAUTO goto gsn_ask
set "GQ=%~1"
set "GQ=%GQ: [S/N]: =%"
call :say "[auto] SIM - %GQ%"
exit /b 1

:gsn_ask
call :sn "%~1"
exit /b %errorlevel%

:pausa_rb
> "%RBF%" echo(%PAD%Pressione qualquer tecla para continuar. . .
call :rainbow "%RBF%" n
call :psm any "" 0 ""
if errorlevel 1 pause >nul
del /f /q "%MRES%" >nul 2>&1
exit /b 0

:banner
echo(
echo(                          ####   ###   #      #       ###    ####
echo(                         #      #   #  #      #      #   #  #
echo(                         #      #####  #      #      #####   ###
echo(                         #      #   #  #      #      #   #      #
echo(                          ####  #   #  #####  #####  #   #  ####
echo(
echo(               ###   ####   #####  #####  #   #  #####  #####  #####  ####
echo(              #   #  #   #    #      #    ## ##    #       #   #      #   #
echo(              #   #  ####     #      #    # # #    #      #    ####   ####
echo(              #   #  #        #      #    #   #    #     #     #      #  #
echo(               ###   #        #    #####  #   #  #####  #####  #####  #   #
echo(
exit /b 0

rem --- Overlay Xbox / Game Bar: desliga os gatilhos e registra um handler
rem     vazio para ms-gamingoverlay, evitando o aviso de app nao encontrado ---

:xbox_app_remove
powershell -NoProfile -ExecutionPolicy Bypass -Command "$pk='Microsoft.GamingApp','Microsoft.XboxApp','Microsoft.XboxGamingOverlay','Microsoft.XboxGameOverlay','Microsoft.XboxSpeechToTextOverlay'; Stop-Process -Name XboxPcApp,XboxPcAppFT,GameBar,GameBarFTServer -Force -ErrorAction SilentlyContinue; $f=@(Get-AppxPackage -AllUsers | Where-Object { $pk -contains $_.Name }); if(-not $f){ exit 3 }; foreach($p in $f){ Remove-AppxPackage -Package $p.PackageFullName -AllUsers -ErrorAction SilentlyContinue }; Get-AppxProvisionedPackage -Online | Where-Object { $pk -contains $_.DisplayName } | Remove-AppxProvisionedPackage -Online -ErrorAction SilentlyContinue | Out-Null" >nul 2>&1
if errorlevel 3 goto xbox_app_nao
call :log "App Xbox removido"
call :say "[OK] App Xbox removido."
exit /b 0
:xbox_app_nao
call :say "[*] App Xbox nao encontrado."
exit /b 0

:xbox_overlay_off
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\GameDVR" /v AppCaptureEnabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\System\GameConfigStore" /v GameDVR_Enabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v UseNexusForGameBarEnabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v ShowStartupPanel /t REG_DWORD /d 0 /f >nul 2>&1
reg add "%POL_GD%" /v AllowGameDVR /t REG_DWORD /d 0 /f >nul 2>&1
for %%P in (ms-gamingoverlay ms-gamebar ms-gamebarservices) do (
    reg add "HKLM\SOFTWARE\Classes\%%P" /ve /d "URL:%%P" /f >nul 2>&1
    reg add "HKLM\SOFTWARE\Classes\%%P" /v "URL Protocol" /t REG_SZ /d "" /f >nul 2>&1
    reg add "HKLM\SOFTWARE\Classes\%%P\shell\open\command" /ve /d "rundll32.exe" /f >nul 2>&1
)
echo overlay xbox desativado pelo Callas Optimizer> "%XBOXFLAG%"
call :log "Overlay Xbox / Game Bar desativado"
exit /b 0

rem --- Modo Jogo: na IoT Enterprise LTSC vem desligado por padrao ---

:game_mode_on
reg add "HKCU\Software\Microsoft\GameBar" /v AutoGameModeEnabled /t REG_DWORD /d 1 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\GameBar" /v AllowAutoGameMode /t REG_DWORD /d 1 /f >nul 2>&1
echo modo jogo ativado pelo Callas Optimizer> "%GMFLAG%"
call :log "Modo Jogo ativado"
exit /b 0

:atualizar_versao
cls
set "PAD=             "
set "nv="
echo.
set /p "nv=%PAD%Nova versao: "
if not defined nv goto menu
for /f "delims=0123456789." %%A in ("%nv%") do goto ver_invalida
if "%nv:~0,1%"=="." goto ver_invalida
if "%nv:~-1%"=="." goto ver_invalida
if not "%nv:..=%"=="%nv%" goto ver_invalida
if "%nv%"=="%VER%" goto ver_invalida
set "OLDVER=%VER%"
set "NEWVER=%nv%"
call :psnet ver
set "NETERR=%errorlevel%"
if "%NETERR%"=="0" goto ver_abrir
echo.
if "%NETERR%"=="5" call :say "[!] Ja existe um arquivo com essa versao nesta pasta."
if not "%NETERR%"=="5" call :say "[!] Nao foi possivel criar a nova versao. Veja callas_teck.log."
call :pausa_rb
goto menu

:ver_invalida
echo.
call :say "[!] Versao invalida."
call :pausa_rb
goto menu

:ver_abrir
set "NEWF="
set /p "NEWF="<"%RBF%.ver"
del "%RBF%.ver" >nul 2>&1
call :log "Nova versao criada: %NEWF%"
start "CALLAS OPTIMIZER" %CON% cmd /c ""%NEWF%""
exit

:ponto_restauracao
cls
set "PAD=             "
call :say "[*] Criando ponto de restauracao..."
call :psnet restore
set "NETERR=%errorlevel%"
echo.
if "%NETERR%"=="0" call :say "[OK] Ponto de restauracao criado."
if "%NETERR%"=="0" call :log "Ponto de restauracao criado"
if not "%NETERR%"=="0" call :say "[!] Nao foi possivel criar o ponto. Veja callas_teck.log."
call :pausa_rb
goto menu

:psnet
set "NETLOG=%BKDIR%\rede.log"
for %%M in (ver restore) do if /i "%~1"=="%%M" set "NETLOG=%LOG%"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try{$t=[IO.File]::ReadAllText($env:SELF);$i=$t.LastIndexOf('#NET'+'BEGIN');$j=$t.LastIndexOf('#NET'+'END');& ([scriptblock]::Create($t.Substring($i,$j-$i))) -Mode '%~1' -File $env:NETF}catch{Add-Content -LiteralPath $env:NETLOG -Value ('net: '+$_.Exception.Message);exit 9}" 2>> "%NETLOG%"
set "PSNETRC=%errorlevel%"
>> "%NETLOG%" echo [%date% %time%] %~1 codigo=%PSNETRC%
exit /b %PSNETRC%

rem --- Limpeza total (PowerShell incluido no BAT, sem arquivos extras) ---
:psclean
set "CLEANLOG=%BKDIR%\limpeza.log"
powershell -NoProfile -ExecutionPolicy Bypass -Command "try { $t=[IO.File]::ReadAllText($env:SELF); $a=$t.LastIndexOf('#CLEAN'+'BEGIN'); $b=$t.LastIndexOf('#CLEAN'+'END'); if($a -lt 0 -or $b -le $a){throw 'Modulo de limpeza nao encontrado'}; & ([scriptblock]::Create($t.Substring($a,$b-$a))) } catch { Write-Host ('[X] Falha ao executar limpeza: '+$_.Exception.Message); try{Add-Content -LiteralPath $env:CLEANLOG -Value $_.ToString()}catch{}; exit 9 }"
exit /b %errorlevel%

:getfree
set "%~1="
for /f %%F in ('powershell -NoProfile -Command "[math]::Round(([System.IO.DriveInfo]$env:SystemDrive).AvailableFreeSpace/1MB)"') do set "%~1=%%F"
exit /b 0

rem :cleandir antigo removido da limpeza principal. Mantido como atalho
rem apenas para pastas temporarias canonicas, sem seguir junctions.
:cleandir
set "CALLAS_CLEANDIR=%~1"
if not defined CALLAS_CLEANDIR exit /b 1
powershell -NoProfile -ExecutionPolicy Bypass -Command "$p=$env:CALLAS_CLEANDIR; $allow=@($env:TEMP,$env:TMP,($env:SystemRoot+'\Temp')) | Where-Object { $_ }; if(-not (@($allow | ForEach-Object {[IO.Path]::GetFullPath($_).TrimEnd('\')}) -contains [IO.Path]::GetFullPath($p).TrimEnd('\'))) { exit 3 }; try { $d=Get-Item -LiteralPath $p -ErrorAction Stop; if($d.Attributes -band [IO.FileAttributes]::ReparsePoint){exit 4}; Get-ChildItem -LiteralPath $p -Force | Where-Object { -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) } | Remove-Item -Force -Recurse -ErrorAction Stop; exit 0 } catch { exit 2 }" >nul 2>&1
exit /b %errorlevel%

:ensure_explorer
timeout /t 3 /nobreak >nul
tasklist /fi "imagename eq explorer.exe" | find /i "explorer.exe" >nul || start "" explorer.exe
exit /b 0

:restart_explorer
taskkill /f /im explorer.exe >nul 2>&1
call :ensure_explorer
exit /b 0

rem --- Servicos: backup do tipo de inicio original antes de desabilitar ---

:svc_backup
if exist "%BKSVC%" findstr /b /i /c:"%~1=" "%BKSVC%" >nul 2>&1 && exit /b 0
set "SVST="
set "SVDL="
for /f "tokens=3" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\%~1" /v Start 2^>nul ^| findstr REG_DWORD') do set "SVST=%%A"
for /f "tokens=3" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\%~1" /v DelayedAutostart 2^>nul ^| findstr REG_DWORD') do set "SVDL=%%A"
if not defined SVST exit /b 0
set "SVMODE=demand"
if "%SVST%"=="0x2" set "SVMODE=auto"
if "%SVST%"=="0x2" if "%SVDL%"=="0x1" set "SVMODE=delayed-auto"
if "%SVST%"=="0x3" set "SVMODE=demand"
if "%SVST%"=="0x4" set "SVMODE=disabled"
>>"%BKSVC%" echo %~1=%SVMODE%
exit /b 0

:svc_disable
sc query %~1 >nul 2>&1 || exit /b 0
call :svc_backup %~1
sc stop %~1 >nul 2>&1
sc config %~1 start= disabled >nul 2>&1
exit /b 0

:svc_is_disabled
set "SVST="
for /f "tokens=3" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\%~1" /v Start 2^>nul ^| findstr REG_DWORD') do set "SVST=%%A"
if "%SVST%"=="0x4" exit /b 0
exit /b 1

:svc_start_if_enabled
set "SVST="
for /f "tokens=3" %%A in ('reg query "HKLM\SYSTEM\CurrentControlSet\Services\%~1" /v Start 2^>nul ^| findstr REG_DWORD') do set "SVST=%%A"
if not defined SVST exit /b 0
if "%SVST%"=="0x4" exit /b 0
net start %~1 >nul 2>&1
exit /b 0

:svc_restore_one
set "RM="
if exist "%BKSVC%" for /f "usebackq tokens=1,2 delims==" %%A in ("%BKSVC%") do if /i "%%A"=="%~1" set "RM=%%B"
if not defined RM set "RM=%~2"
if not defined RM exit /b 0
sc config %~1 start= %RM% >nul 2>&1
if errorlevel 1 (
    call :log "Falha ao restaurar servico %~1 - inicio %RM%"
    exit /b 1
)
if /i not "%RM%"=="disabled" if /i not "%RM%"=="demand" sc start %~1 >nul 2>&1
if exist "%BKSVC%" (
    findstr /v /b /i /c:"%~1=" "%BKSVC%" > "%BKSVC%.tmp"
    move /y "%BKSVC%.tmp" "%BKSVC%" >nul
)
exit /b 0

:svc_restore_all
if not exist "%BKSVC%" exit /b 0
set "SVCFAILED=0"
del /f /q "%BKSVC%.failed" >nul 2>&1
for /f "usebackq tokens=1,2 delims==" %%A in ("%BKSVC%") do (
    sc config %%A start= %%B >nul 2>&1
    if errorlevel 1 (
        set "SVCFAILED=1"
        >> "%BKSVC%.failed" echo %%A=%%B
        call :log "Falha ao restaurar servico %%A"
    ) else (
        if /i "%%B"=="auto" sc start %%A >nul 2>&1
        if /i "%%B"=="delayed-auto" sc start %%A >nul 2>&1
    )
)
if exist "%BKSVC%.failed" (
    move /y "%BKSVC%.failed" "%BKSVC%" >nul 2>&1
) else (
    del /f /q "%BKSVC%" >nul 2>&1
)
if "%SVCFAILED%"=="1" call :say "[!] Alguns servicos nao foram restaurados. Backup mantido."
exit /b %SVCFAILED%

#NETBEGIN
param([string]$Mode = 'save', [string]$File = '')
$ErrorActionPreference = 'Stop'
function Log([string]$m) { try { Add-Content -LiteralPath $env:NETLOG -Value ((Get-Date -Format s) + ' ' + $m) } catch { } }
if ($Mode -eq 'ver') {
    try {
        $old = $env:OLDVER; $new = $env:NEWVER
        $src = $env:SELF
        $dir = [IO.Path]::GetDirectoryName($src)
        $name = [IO.Path]::GetFileNameWithoutExtension($src)
        $ext = [IO.Path]::GetExtension($src)
        $ou = 'V' + $old.Replace('.', '_'); $nu = 'V' + $new.Replace('.', '_')
        if ($name.Contains($ou)) { $nn = $name.Replace($ou, $nu) } else { $nn = $name + '_' + $nu }
        $dst = Join-Path $dir ($nn + $ext)
        if (Test-Path -LiteralPath $dst) { exit 5 }
        $t = [IO.File]::ReadAllText($src)
        $t = $t.Replace('V' + $old, 'V' + $new).Replace('VER=' + $old, 'VER=' + $new)
        [IO.File]::WriteAllText($dst, $t, [Text.Encoding]::ASCII)
        [IO.File]::WriteAllText($env:RBF + '.ver', $dst, [Text.Encoding]::ASCII)
    } catch { Log ('ver: ' + $_.Exception.Message); exit 2 }
    exit 0
}
if ($Mode -eq 'restore') {
    $rk = 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\SystemRestore'
    $fq = 'SystemRestorePointCreationFrequency'
    $old = $null
    $ok = $false
    try {
        $old = (Get-ItemProperty -LiteralPath $rk -Name $fq -ErrorAction SilentlyContinue).$fq
        Enable-ComputerRestore -Drive ($env:SystemDrive + '\')
        New-ItemProperty -LiteralPath $rk -Name $fq -PropertyType DWord -Value 0 -Force | Out-Null
        Checkpoint-Computer -Description 'Callas Optimizer' -RestorePointType 'MODIFY_SETTINGS' -WarningAction SilentlyContinue -WarningVariable wv
        if ($wv) { throw ('aviso: ' + ($wv -join ' ')) }
        $ok = $true
    } catch { Log ('restore: ' + $_.Exception.Message) }
    try {
        if ($null -eq $old) { Remove-ItemProperty -LiteralPath $rk -Name $fq -ErrorAction SilentlyContinue }
        else { New-ItemProperty -LiteralPath $rk -Name $fq -PropertyType DWord -Value $old -Force | Out-Null }
    } catch { }
    if ($ok) { exit 0 } else { exit 6 }
}
$a = $null
$all = @()
try {
    $all = @(Get-NetAdapter -Physical | Where-Object { $_.Status -eq 'Up' })
    $a = $all | Where-Object { $_.InterfaceDescription -match 'Realtek' } | Select-Object -First 1
    if (-not $a) { $a = $all | Select-Object -First 1 }
} catch { Log ('adaptador: ' + $_.Exception.Message) }
if (-not $a) { exit 1 }
$n = $a.Name
Log ('adaptador: ' + $a.Name + ' | ' + $a.InterfaceDescription + ' | driver ' + $a.DriverVersionString)
if ($Mode -eq 'dns' -or $Mode -eq 'dnsauto') {
    $ok = 0
    foreach ($ad in $all) {
        try {
            if ($Mode -eq 'dnsauto') { Set-DnsClientServerAddress -InterfaceIndex $ad.ifIndex -ResetServerAddresses }
            else { Set-DnsClientServerAddress -InterfaceIndex $ad.ifIndex -ServerAddresses ($env:DNSLIST -split ',') }
            $ok++
            Log ('dns ' + $ad.Name + ' -> ' + ((Get-DnsClientServerAddress -InterfaceIndex $ad.ifIndex -AddressFamily IPv4).ServerAddresses -join ','))
        } catch { Log ('dns ' + $ad.Name + ': ' + $_.Exception.Message) }
    }
    try { Clear-DnsClientCache } catch { }
    if ($ok -gt 0) { exit 0 } else { exit 4 }
}
if ($Mode -eq 'save') {
    try {
        $rows = @()
        foreach ($p in @(Get-NetAdapterAdvancedProperty -Name $n)) {
            $rows += [pscustomobject]@{ Tipo = 'ADV'; Chave = [string]$p.RegistryKeyword; Valor = (@($p.RegistryValue) -join ','); Nome = [string]$p.DisplayName }
        }
        $pm = Get-NetAdapterPowerManagement -Name $n -ErrorAction SilentlyContinue
        if ($pm) { $rows += [pscustomobject]@{ Tipo = 'PWR'; Chave = 'AllowComputerToTurnOffDevice'; Valor = [string]$pm.AllowComputerToTurnOffDevice; Nome = '' } }
        $rows | Export-Csv -LiteralPath $File -NoTypeInformation -Encoding UTF8
    } catch { Log ('save: ' + $_.Exception.Message); exit 2 }
    exit 0
}
if ($Mode -eq 'apply') {
    if (-not (Test-Path -LiteralPath $File)) { exit 3 }
    try { $cfg = @(Import-Csv -LiteralPath $File -Encoding UTF8) } catch { Log ('apply: ' + $_.Exception.Message); exit 2 }
    $applied=0; $failed=0
    foreach ($r in $cfg) {
        try {
            if ($r.Tipo -eq 'ADV') {
                if ([string]::IsNullOrEmpty($r.Valor)) { continue }
                $cur = Get-NetAdapterAdvancedProperty -Name $n -RegistryKeyword $r.Chave -ErrorAction Stop
                if ($cur) { Set-NetAdapterAdvancedProperty -Name $n -RegistryKeyword $r.Chave -RegistryValue ($r.Valor -split ',') -NoRestart -ErrorAction Stop; $applied++ }
            } elseif ($r.Tipo -eq 'PWR') {
                if ($r.Valor -eq 'Enabled' -or $r.Valor -eq 'Disabled') { Set-NetAdapterPowerManagement -Name $n -AllowComputerToTurnOffDevice $r.Valor -NoRestart -ErrorAction Stop; $applied++ }
            }
        } catch { $failed++; Log ('apply ' + $r.Chave + ': ' + $_.Exception.Message) }
    }
    if($applied -eq 0) { Log 'apply: nada aplicado'; exit 4 }
    try { Restart-NetAdapter -Name $n -ErrorAction Stop } catch { $failed++; Log ('restart: ' + $_.Exception.Message) }
    if($failed -gt 0) { exit 4 }
    exit 0
}
exit 2
#NETEND

#CLEANBEGIN
# Limpeza integrada, compativel com Windows PowerShell 5.1 (Windows 10/11).
# Projetada para preservar pastas originais, pontos de reanalise e logs de diagnostico.
$ErrorActionPreference = 'Stop'
$warnings = 0
$logPath = $env:CLEANLOG
function LogClean([string]$msg) {
    try { Add-Content -LiteralPath $logPath -Value ((Get-Date -Format 'yyyy-MM-dd HH:mm:ss')+' '+$msg) -Encoding UTF8 } catch { }
}
function WarnClean([string]$msg) {
    $script:warnings++
    Write-Host ('      [!] '+$msg) -ForegroundColor Yellow
    LogClean ('AVISO: '+$msg)
}
function NormalizeClean([string]$p) {
    if ([string]::IsNullOrWhiteSpace($p)) { return '' }
    try {
        $full=[IO.Path]::GetFullPath($p).TrimEnd('\').ToLowerInvariant()
        $root=[IO.Path]::GetPathRoot($full).TrimEnd('\').ToLowerInvariant()
        if($full -eq $root) { return '' }
        if($full -eq $env:SystemRoot.TrimEnd('\').ToLowerInvariant()) { return '' }
        if($full -eq $env:USERPROFILE.TrimEnd('\').ToLowerInvariant()) { return '' }
        return $full
    } catch { return '' }
}
$allowed = @{}
$paths = @(
    $env:TEMP, $env:TMP,
    (Join-Path $env:SystemRoot 'Temp'),
    (Join-Path $env:SystemRoot 'SoftwareDistribution\Download'),
    (Join-Path $env:SystemRoot 'ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache'),
    (Join-Path $env:ProgramData 'Microsoft\Windows\WER\ReportQueue'),
    (Join-Path $env:ProgramData 'Microsoft\Windows\WER\ReportArchive'),
    (Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Explorer')
)
foreach($p in $paths) { $key=NormalizeClean $p; if($key) { $allowed[$key]=$true } }
function RemoveSafe([string]$path) {
    $item=Get-Item -LiteralPath $path -Force -ErrorAction Stop
    if($item.Attributes -band [IO.FileAttributes]::ReparsePoint) { return $false }
    if($item.PSIsContainer) {
        foreach($child in @(Get-ChildItem -LiteralPath $path -Force -ErrorAction Stop)) {
            if(-not (RemoveSafe $child.FullName)) { return $false }
        }
    }
    Remove-Item -LiteralPath $path -Force -ErrorAction Stop
    return $true
}
function ClearFolder([string]$path, [string]$fileMask='*') {
    $key=NormalizeClean $path
    if(-not $key -or -not $allowed.ContainsKey($key)) {
        WarnClean ('Caminho nao autorizado; ignorado: '+$path); return
    }
    $self=(NormalizeClean $env:SELF)
    $bk=(NormalizeClean $env:BKDIR)
    if(($self -and $self.StartsWith($key+'\')) -or ($bk -and ($bk -eq $key -or $bk.StartsWith($key+'\')))) {
        WarnClean ('Pasta preservada porque contem o script ou seus logs: '+$path); return
    }
    if(-not (Test-Path -LiteralPath $path -PathType Container)) { LogClean ('Pasta ausente: '+$path); return }
    try {
        $folder=Get-Item -LiteralPath $path -Force -ErrorAction Stop
        if($folder.Attributes -band [IO.FileAttributes]::ReparsePoint) { WarnClean ('Junction nao removida: '+$path); return }
        $entries=@(Get-ChildItem -LiteralPath $path -Force -Filter $fileMask -ErrorAction Stop)
    } catch { WarnClean ('Falha ao listar '+$path+': '+$_.Exception.Message); return }
    $ok=0; $failed=0; $skipped=0
    foreach($entry in $entries) {
        if($entry.Attributes -band [IO.FileAttributes]::ReparsePoint) { $skipped++; continue }
        try {
            if(RemoveSafe $entry.FullName) { $ok++ } else { $skipped++ }
        } catch {
            $failed++
            if($failed -le 2) { LogClean ('Arquivo bloqueado: '+$entry.FullName+' - '+$_.Exception.Message) }
        }
    }
    LogClean ('Pasta '+$path+': '+$ok+' removidos, '+$failed+' bloqueados, '+$skipped+' junctions ignoradas')
    if($failed -gt 0) { WarnClean ($failed.ToString()+' item(ns) bloqueado(s) em '+$path) }
    if($skipped -gt 0) { WarnClean ($skipped.ToString()+' item(ns)/junction(s) preservado(s) em '+$path) }
}
function ClearFile([string]$path) {
    try {
        $parent=Split-Path -Parent $path
        if(-not ($allowed.ContainsKey((NormalizeClean $parent))) -and (NormalizeClean $parent) -ne (NormalizeClean $env:LOCALAPPDATA)) {
            WarnClean ('Arquivo fora da lista segura: '+$path); return
        }
        if(Test-Path -LiteralPath $path -PathType Leaf) { Remove-Item -LiteralPath $path -Force -ErrorAction Stop; LogClean ('Arquivo removido: '+$path) }
    } catch { WarnClean ('Arquivo bloqueado: '+$path) }
}
$stopped = New-Object 'System.Collections.Generic.List[string]'
$explorerStopped = $false
try {
    Write-Host '[1/11] Preparando servicos de atualizacao...'
    foreach($name in @('wuauserv','BITS','DoSvc')) {
        try {
            $svc=Get-Service -Name $name -ErrorAction SilentlyContinue
            if($svc -and $svc.Status -eq 'Running') {
                Stop-Service -Name $name -ErrorAction Stop
                $svc.WaitForStatus('Stopped', [TimeSpan]::FromSeconds(15))
                $stopped.Add($name)
                LogClean ('Servico parado temporariamente: '+$name)
            }
        } catch { WarnClean ('Nao foi possivel parar '+$name+'; itens em uso serao preservados') }
    }
    Write-Host '[2/11] Limpando arquivos temporarios do usuario...'
    ClearFolder $env:TEMP
    if((NormalizeClean $env:TMP) -ne (NormalizeClean $env:TEMP)) { ClearFolder $env:TMP }
    Write-Host '[3/11] Limpando arquivos temporarios do Windows...'
    ClearFolder (Join-Path $env:SystemRoot 'Temp')
    Write-Host '[4/11] Prefetch preservado (evita piorar o carregamento de programas).'
    Write-Host '[5/11] Limpando caches de Windows Update e Delivery Optimization...'
    $wu = Get-Service -Name wuauserv -ErrorAction SilentlyContinue
    $bits = Get-Service -Name BITS -ErrorAction SilentlyContinue
    if(($wu -and $wu.Status -eq 'Running') -or ($bits -and $bits.Status -eq 'Running')) {
        WarnClean 'Windows Update/BITS em execucao; cache de downloads preservado'
    } else { ClearFolder (Join-Path $env:SystemRoot 'SoftwareDistribution\Download') }
    $dosvc = Get-Service -Name DoSvc -ErrorAction SilentlyContinue
    if($dosvc -and $dosvc.Status -eq 'Running') {
        WarnClean 'Delivery Optimization em execucao; seu cache foi preservado'
    } else { ClearFolder (Join-Path $env:SystemRoot 'ServiceProfiles\NetworkService\AppData\Local\Microsoft\Windows\DeliveryOptimization\Cache') }
    Write-Host '[6/11] Limpando relatorios antigos do Windows Error Reporting...'
    ClearFolder (Join-Path $env:ProgramData 'Microsoft\Windows\WER\ReportQueue')
    ClearFolder (Join-Path $env:ProgramData 'Microsoft\Windows\WER\ReportArchive')
    Write-Host '       Dumps (MEMORY.DMP e CrashDumps) preservados para diagnostico.'
    Write-Host '[7/11] Esvaziando a Lixeira...'
    try { Clear-RecycleBin -Force -ErrorAction Stop; LogClean 'Lixeira esvaziada' }
    catch { WarnClean ('Lixeira indisponivel ou parcialmente limpa: '+$_.Exception.Message) }
    Write-Host '[8/11] Limpando cache DNS...'
    try { Clear-DnsClientCache -ErrorAction Stop; LogClean 'Cache DNS limpo' }
    catch { WarnClean ('Cache DNS nao limpo: '+$_.Exception.Message) }
    Write-Host '[9/11] Limpando cache de icones e miniaturas...'
    try {
        $explorer = @(Get-Process -Name explorer -ErrorAction SilentlyContinue)
        if($explorer.Count -gt 0) {
            Stop-Process -Name explorer -Force -ErrorAction Stop
            $explorerStopped = $true
            Start-Sleep -Milliseconds 800
        }
    } catch { WarnClean ('Explorer em uso: '+$_.Exception.Message) }
    ClearFile (Join-Path $env:LOCALAPPDATA 'IconCache.db')
    ClearFolder (Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Explorer') 'iconcache*'
    ClearFolder (Join-Path $env:LOCALAPPDATA 'Microsoft\Windows\Explorer') 'thumbcache*'
} catch { WarnClean ('Falha inesperada na limpeza: '+$_.Exception.Message) }
finally {
    if($explorerStopped) {
        try {
            if(-not (Get-Process -Name explorer -ErrorAction SilentlyContinue)) {
                Start-Process -FilePath 'explorer.exe' -ErrorAction Stop
            }
            LogClean 'Explorer verificado/reiniciado'
        } catch { WarnClean ('Nao foi possivel reiniciar o Explorer: '+$_.Exception.Message) }
    }
    foreach($name in $stopped) {
        try {
            $svc=Get-Service -Name $name -ErrorAction Stop
            if($svc.Status -ne 'Running') { Start-Service -Name $name -ErrorAction Stop }
            LogClean ('Servico restaurado: '+$name)
        } catch { WarnClean ('Nao foi possivel reiniciar servico '+$name+': '+$_.Exception.Message) }
    }
}
if($warnings -eq 0) { Write-Host '[OK] Etapas 1 a 9 concluidas.' } else { Write-Host ('[!] Etapas 1 a 9 com '+$warnings+' aviso(s). Veja limpeza.log') }
LogClean ('Conclusao do nucleo da limpeza. Avisos='+$warnings)
if($warnings -gt 0) { exit 2 }
exit 0
#CLEANEND

#PSMBEGIN
param([string]$Res, [string]$Mode = 'line', [string]$Keys = '', [int]$Secs = 0, [string]$Def = '', [int]$Size = 20)
$ErrorActionPreference = 'Stop'
function Log([string]$m) { try { Add-Content -LiteralPath (Join-Path $env:BKDIR 'mouse_debug.log') -Value ((Get-Date -Format s) + ' ' + $m) } catch { } }
try {
Add-Type -Language CSharp -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class CMx {
  [StructLayout(LayoutKind.Explicit)]
  public struct KEY_REC {
    [FieldOffset(0)] public int Down;
    [FieldOffset(4)] public ushort Rep;
    [FieldOffset(6)] public ushort VK;
    [FieldOffset(8)] public ushort SC;
    [FieldOffset(10)] public ushort Ch;
    [FieldOffset(12)] public uint Ctl;
  }
  [StructLayout(LayoutKind.Explicit)]
  public struct MOUSE_REC {
    [FieldOffset(0)] public short X;
    [FieldOffset(2)] public short Y;
    [FieldOffset(4)] public uint Btn;
    [FieldOffset(8)] public uint Ctl;
    [FieldOffset(12)] public uint Flags;
  }
  [StructLayout(LayoutKind.Explicit, Size=20)]
  public struct INREC {
    [FieldOffset(0)] public ushort Type;
    [FieldOffset(4)] public KEY_REC Key;
    [FieldOffset(4)] public MOUSE_REC Mouse;
  }
  [StructLayout(LayoutKind.Sequential, CharSet=CharSet.Unicode)]
  public struct FONTEX {
    public uint cb; public uint nFont; public short X; public short Y;
    public int Family; public int Weight;
    [MarshalAs(UnmanagedType.ByValTStr, SizeConst=32)] public string Face;
  }
  [DllImport("kernel32.dll")] public static extern IntPtr GetStdHandle(int n);
  [DllImport("kernel32.dll")] public static extern bool GetConsoleMode(IntPtr h, out uint m);
  [DllImport("kernel32.dll")] public static extern bool SetConsoleMode(IntPtr h, uint m);
  [DllImport("kernel32.dll", EntryPoint="ReadConsoleInputW")] public static extern bool ReadIn(IntPtr h, out INREC r, uint n, out uint got);
  [DllImport("kernel32.dll")] public static extern bool FlushConsoleInputBuffer(IntPtr h);
  [DllImport("kernel32.dll")] public static extern uint WaitForSingleObject(IntPtr h, uint ms);
  [DllImport("kernel32.dll", CharSet=CharSet.Unicode)] public static extern bool SetCurrentConsoleFontEx(IntPtr h, bool max, ref FONTEX f);
  public static bool SetFont(int size) {
    FONTEX f = new FONTEX();
    f.cb = (uint)Marshal.SizeOf(typeof(FONTEX));
    f.nFont = 0; f.X = 0; f.Y = (short)size; f.Family = 54; f.Weight = 400; f.Face = "Consolas";
    return SetCurrentConsoleFontEx(GetStdHandle(-11), false, ref f);
  }
}
'@
} catch { Log ('addtype: ' + $_.Exception.Message); exit 2 }

if ($Mode -eq 'font') {
    try { if ([CMx]::SetFont($Size)) { [IO.File]::WriteAllText($Res, '1', [Text.Encoding]::ASCII) } else { Log 'SetCurrentConsoleFontEx retornou falso' } } catch { Log ('font: ' + $_.Exception.Message) }
    exit 0
}

function RowText([int]$y) {
    $w = $Host.UI.RawUI.BufferSize.Width
    $r = New-Object System.Management.Automation.Host.Rectangle 0, $y, ($w - 1), $y
    $c = $Host.UI.RawUI.GetBufferContents($r)
    $sb = New-Object System.Text.StringBuilder
    for ($i = 0; $i -lt $w; $i++) { $cell = $c.GetValue(0, $i); [void]$sb.Append($cell.Character) }
    return $sb.ToString()
}

function Pick([string]$row, [int]$x) {
    $ms = [regex]::Matches($row, $pat)
    $pick = $null
    for ($k = 0; $k -lt $ms.Count; $k++) {
        $s = $ms[$k].Index
        if ($k + 1 -lt $ms.Count) { $e = $ms[$k + 1].Index - 1 } else { $e = $row.TrimEnd().Length }
        if ($Mode -eq 'line') {
            if ($k -eq 0 -or $x -ge $s) { $pick = $ms[$k].Groups[1].Value }
        } elseif ($x -ge $s -and $x -le $e) {
            $pick = $ms[$k].Groups[1].Value
        }
    }
    return $pick
}

$pat = '\[([0-9]{1,2})\]'
if ($Mode -eq 'choice') { $pat = '\[([A-Za-z])\]' }
[uint32]$old = 0
$hIn = [IntPtr]::Zero
try {
    $hIn = [CMx]::GetStdHandle(-10)
    if (-not [CMx]::GetConsoleMode($hIn, [ref]$old)) { Log 'GetConsoleMode falhou (entrada redirecionada?)'; exit 2 }
    $new = [uint32](([int64]$old -bor 0x90) -band (-bnot [int64]0x246))
    [void][CMx]::SetConsoleMode($hIn, $new)
    [void][CMx]::FlushConsoleInputBuffer($hIn)
    $t0 = [DateTime]::UtcNow
    $deadline = $null
    if ($Secs -gt 0) { $deadline = $t0.AddSeconds($Secs) }
    $typed = ''
    $result = $null
    $rec = New-Object 'CMx+INREC'
    [uint32]$got = 0
    while ($null -eq $result) {
        $wait = [uint32]4294967295
        if ($deadline) {
            $left = ($deadline - [DateTime]::UtcNow).TotalMilliseconds
            if ($left -le 0) { $result = $Def; break }
            $wait = [uint32][Math]::Min([Math]::Ceiling($left), 200)
        }
        if ([CMx]::WaitForSingleObject($hIn, $wait) -ne 0) { continue }
        if (-not [CMx]::ReadIn($hIn, [ref]$rec, 1, [ref]$got)) { throw 'read' }
        $type = [int]$rec.Type
        if ($type -eq 1) {
            if ($rec.Key.Down -ne 0 -and $rec.Key.Ch -ne 0) {
                $c = [char][int]$rec.Key.Ch
                if ($Mode -eq 'any') {
                    $result = 'k'
                } elseif ($Mode -eq 'choice') {
                    $ix = $Keys.IndexOf([string]$c, [StringComparison]::OrdinalIgnoreCase)
                    if ($ix -ge 0) { $result = [string]($ix + 1) }
                } else {
                    $code = [int]$c
                    if ($code -eq 13) {
                        [Console]::Out.Write("`r`n")
                        $result = $typed
                    } elseif ($code -eq 8) {
                        if ($typed.Length -gt 0) {
                            $typed = $typed.Substring(0, $typed.Length - 1)
                            [Console]::Out.Write("`b `b")
                        }
                    } elseif ($code -ge 32) {
                        $typed += [string]$c
                        [Console]::Out.Write([string]$c)
                    }
                }
            }
        } elseif ($type -eq 2) {
            $fl = [int]$rec.Mouse.Flags
            if ((($rec.Mouse.Btn -band 1) -ne 0) -and ($fl -eq 0 -or $fl -eq 2)) {
                if ($Mode -eq 'any') {
                    if ($fl -eq 0 -and ([DateTime]::UtcNow - $t0).TotalMilliseconds -gt 500) { $result = 'm' }
                } else {
                    $row = RowText ([int]$rec.Mouse.Y)
                    $tok = Pick $row ([int]$rec.Mouse.X)
                    if ($tok) {
                        if ($Mode -eq 'line') {
                            [Console]::Out.Write($tok + "`r`n")
                            $result = $tok
                        } else {
                            $ix = $Keys.IndexOf($tok, [StringComparison]::OrdinalIgnoreCase)
                            if ($ix -ge 0) { $result = [string]($ix + 1) }
                        }
                    }
                }
            }
        }
    }
    [void][CMx]::SetConsoleMode($hIn, $old)
    [void][CMx]::FlushConsoleInputBuffer($hIn)
    $out = ''
    if ($Mode -ne 'any') { $out = [string]$result }
    [IO.File]::WriteAllText($Res, $out, [Text.Encoding]::ASCII)
    exit 0
} catch {
    Log ('run: ' + $_.Exception.Message)
    try { [void][CMx]::SetConsoleMode($hIn, $old); [void][CMx]::FlushConsoleInputBuffer($hIn) } catch { }
    exit 2
}
