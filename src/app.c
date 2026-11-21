/* Callas Optimizer V8.9.1 - GUI Win32 nativa x64, sem runtime externo.
 * Compilado sem CRT para PE64 com clang/LLVM. Fonte editavel incluso.
 */
typedef unsigned char BYTE;
typedef unsigned short WORD;
typedef unsigned int UINT;
typedef unsigned long DWORD;
typedef long LONG;
typedef long long LONG64;
typedef unsigned long long ULONG_PTR;
typedef long long LONG_PTR;
typedef ULONG_PTR WPARAM;
typedef LONG_PTR LPARAM;
typedef LONG_PTR LRESULT;
typedef void *HANDLE;
typedef HANDLE HWND;
typedef HANDLE HINSTANCE;
typedef HANDLE HBRUSH;
typedef HANDLE HDC;
typedef HANDLE HGDIOBJ;
typedef HANDLE HBITMAP;
typedef HANDLE HPEN;
typedef HANDLE HFONT;
typedef HANDLE HCURSOR;
typedef HANDLE HICON;
typedef HANDLE HKEY;
typedef const unsigned short *LPCWSTR;
typedef unsigned short WCHAR;
typedef WCHAR *LPWSTR;
typedef const char *LPCSTR;
typedef void *LPVOID;
typedef const void *LPCVOID;
typedef int BOOL;
typedef unsigned short ATOM;
typedef DWORD COLORREF;
#define NULL ((void*)0)
#define TRUE 1
#define FALSE 0
#define WINAPI __stdcall
#define RGB2(r,g,b) ((DWORD)((r)|((g)<<8)|((b)<<16)))
#define SW_SHOWNORMAL 1
#define SW_SHOW 5
#define SW_HIDE 0
#define WM_TIMER 275
#define WM_CREATE 1
#define WM_DESTROY 2
#define WM_SIZE 5
#define WM_PAINT 15
#define WM_CLOSE 16
#define WM_ERASEBKGND 20
#define WM_SETCURSOR 32
#define WM_MOUSEMOVE 512
#define WM_LBUTTONUP 514
#define WS_OVERLAPPED 0x00000000
#define WS_CAPTION 0x00c00000
#define WS_SYSMENU 0x00080000
#define WS_MINIMIZEBOX 0x00020000
#define WS_VISIBLE 0x10000000
#define WS_CLIPCHILDREN 0x02000000
#define CS_HREDRAW 2
#define CS_VREDRAW 1
#define IDC_ARROW ((LPCWSTR)32512)
#define IDC_HAND ((LPCWSTR)32649)
#define COLOR_WINDOW 5
#define DT_LEFT 0
#define DT_CENTER 1
#define DT_VCENTER 4
#define DT_SINGLELINE 32
#define DT_NOPREFIX 2048
#define TRANSPARENT 1
#define PS_SOLID 0
#define SRCCOPY 0x00cc0020
#define MB_OK 0
#define MB_ICONINFORMATION 0x40
#define MB_ICONWARNING 0x30
#define MB_ICONERROR 0x10
#define MB_YESNO 4
#define IDYES 6
#define FILE_ATTRIBUTE_NORMAL 128
#define GENERIC_WRITE 0x40000000
#define GENERIC_READ 0x80000000
#define OPEN_EXISTING 3
#define CREATE_ALWAYS 2
#define INVALID_HANDLE_VALUE ((HANDLE)(-1))
#define HKEY_LOCAL_MACHINE ((HKEY)(LONG_PTR)-2147483646LL)
#define KEY_QUERY_VALUE 0x0001
#define REG_SZ 1
#define HWND_DESKTOP ((HWND)0)

typedef struct {LONG left,top,right,bottom;} RECT;
typedef struct {LONG x,y;} POINT;
typedef struct {UINT cbSize; UINT style; void* lpfnWndProc; int cbClsExtra,cbWndExtra; HINSTANCE hInstance; HICON hIcon; HCURSOR hCursor; HBRUSH hbrBackground; LPCWSTR lpszMenuName,lpszClassName; HICON hIconSm;} WNDCLASSEXW;
typedef struct {HWND hwnd; UINT message; WPARAM wParam; LPARAM lParam; DWORD time; POINT pt; DWORD lPrivate;} MSG;
typedef struct {HDC hdc; BOOL fErase; RECT rcPaint; BOOL fRestore; BOOL fIncUpdate; BYTE rgbReserved[32];} PAINTSTRUCT;

__declspec(dllimport) HINSTANCE WINAPI GetModuleHandleW(LPCWSTR);
__declspec(dllimport) DWORD WINAPI GetEnvironmentVariableW(LPCWSTR,LPWSTR,DWORD);
__declspec(dllimport) BOOL WINAPI CreateDirectoryW(LPCWSTR,void*);
__declspec(dllimport) HANDLE WINAPI CreateFileW(LPCWSTR,DWORD,DWORD,void*,DWORD,DWORD,HANDLE);
__declspec(dllimport) BOOL WINAPI WriteFile(HANDLE,LPCVOID,DWORD,DWORD*,void*);
__declspec(dllimport) BOOL WINAPI CloseHandle(HANDLE);
__declspec(dllimport) void WINAPI ExitProcess(UINT);
__declspec(dllimport) DWORD WINAPI GetLastError(void);
__declspec(dllimport) DWORD WINAPI GetModuleFileNameW(HINSTANCE,LPWSTR,DWORD);
__declspec(dllimport) DWORD WINAPI GetCurrentProcessId(void);
__declspec(dllimport) BOOL WINAPI DeleteFileW(LPCWSTR);
__declspec(dllimport) BOOL WINAPI ReadFile(HANDLE,LPVOID,DWORD,DWORD*,void*);
__declspec(dllimport) ATOM WINAPI RegisterClassExW(const WNDCLASSEXW*);
__declspec(dllimport) HWND WINAPI CreateWindowExW(DWORD,LPCWSTR,LPCWSTR,DWORD,int,int,int,int,HWND,HANDLE,HINSTANCE,void*);
__declspec(dllimport) LRESULT WINAPI DefWindowProcW(HWND,UINT,WPARAM,LPARAM);
__declspec(dllimport) BOOL WINAPI ShowWindow(HWND,int);
__declspec(dllimport) BOOL WINAPI UpdateWindow(HWND);
__declspec(dllimport) BOOL WINAPI GetMessageW(MSG*,HWND,UINT,UINT);
__declspec(dllimport) BOOL WINAPI TranslateMessage(const MSG*);
__declspec(dllimport) LRESULT WINAPI DispatchMessageW(const MSG*);
__declspec(dllimport) HDC WINAPI BeginPaint(HWND,PAINTSTRUCT*);
__declspec(dllimport) BOOL WINAPI EndPaint(HWND,const PAINTSTRUCT*);
__declspec(dllimport) BOOL WINAPI GetClientRect(HWND,RECT*);
__declspec(dllimport) BOOL WINAPI FillRect(HDC,const RECT*,HBRUSH);
__declspec(dllimport) BOOL WINAPI InvalidateRect(HWND,const RECT*,BOOL);
__declspec(dllimport) ULONG_PTR WINAPI SetTimer(HWND,ULONG_PTR,UINT,void*);
__declspec(dllimport) BOOL WINAPI KillTimer(HWND,ULONG_PTR);
__declspec(dllimport) HCURSOR WINAPI LoadCursorW(HINSTANCE,LPCWSTR);
__declspec(dllimport) HCURSOR WINAPI SetCursor(HCURSOR);
__declspec(dllimport) int WINAPI MessageBoxW(HWND,LPCWSTR,LPCWSTR,UINT);
__declspec(dllimport) void WINAPI PostQuitMessage(int);
__declspec(dllimport) HDC WINAPI CreateCompatibleDC(HDC);
__declspec(dllimport) BOOL WINAPI DeleteDC(HDC);
__declspec(dllimport) HBITMAP WINAPI CreateCompatibleBitmap(HDC,int,int);
__declspec(dllimport) BOOL WINAPI BitBlt(HDC,int,int,int,int,HDC,int,int,DWORD);
__declspec(dllimport) HBRUSH WINAPI CreateSolidBrush(DWORD);
__declspec(dllimport) HGDIOBJ WINAPI SelectObject(HDC,HGDIOBJ);
__declspec(dllimport) BOOL WINAPI DeleteObject(HGDIOBJ);
__declspec(dllimport) BOOL WINAPI RoundRect(HDC,int,int,int,int,int,int);
__declspec(dllimport) BOOL WINAPI Ellipse(HDC,int,int,int,int);
__declspec(dllimport) HPEN WINAPI CreatePen(int,int,DWORD);
__declspec(dllimport) HFONT WINAPI CreateFontW(int,int,int,int,int,DWORD,DWORD,DWORD,DWORD,DWORD,DWORD,DWORD,DWORD,LPCWSTR);
__declspec(dllimport) DWORD WINAPI SetTextColor(HDC,DWORD);
__declspec(dllimport) int WINAPI SetBkMode(HDC,int);
__declspec(dllimport) int WINAPI DrawTextW(HDC,LPCWSTR,int,RECT*,UINT);
__declspec(dllimport) HINSTANCE WINAPI ShellExecuteW(HWND,LPCWSTR,LPCWSTR,LPCWSTR,LPCWSTR,int);
__declspec(dllimport) LONG WINAPI RegOpenKeyExW(HKEY,LPCWSTR,DWORD,DWORD,HKEY*);
__declspec(dllimport) LONG WINAPI RegQueryValueExW(HKEY,LPCWSTR,DWORD*,DWORD*,BYTE*,DWORD*);
__declspec(dllimport) LONG WINAPI RegCloseKey(HKEY);

void* memset(void* dest,int ch,ULONG_PTR n){volatile BYTE* p=(volatile BYTE*)dest;while(n--)*p++=(BYTE)ch;return dest;}

/* recursos incluidos pelo compilador; Windows nao baixa codigo de terceiros para inicializar o menu */
extern const BYTE asset_engine[];
extern const DWORD asset_engine_size;
extern const BYTE asset_brave[];
extern const DWORD asset_brave_size;
extern const BYTE asset_nvidia[];
extern const DWORD asset_nvidia_size;
extern const BYTE asset_ext[];
extern const DWORD asset_ext_size;
extern const BYTE asset_updater[];
extern const DWORD asset_updater_size;
extern const BYTE asset_undo[];
extern const DWORD asset_undo_size;

static HWND mainwin;
static HCURSOR cursor_arrow,cursor_hand;
static HFONT font36,font24,font20,font16,font14,font13,font12,font13b;
static int selected=0, mousex=-1,mousey=-1, win11=1, hover=-1;
static int update_pending=0,update_manual=0, update_ticks=0;
static int update_install_pending=0,update_install_ticks=0;
static WCHAR folder[560],enginepath[640],bravepath[640],nvidiapath[640],extpath[640],undopath[640],updaterpath[640],statuspath[640];
static const WCHAR* names[14]={
 L"PAINEL INICIAL",L"Modo Gamer",L"Remover Microsoft Edge",L"Windows Update",L"Rede e DNS",L"Privacidade / Telemetria",L"Reparar sistema",L"Limpeza total",L"Menu classico Win11",L"Desligamento",L"WinUtil",L"Atualizar aplicativo",L"Ponto de restauracao",L"Restaurar padroes"};
static const WCHAR* descriptions[14]={
 L"Sua central personalizada para otimizar e preparar o Windows 11.",
 L"Ajustes para jogos, servicos, Xbox, hibernacao e plano de energia.",
 L"Remocao e restauracao do Microsoft Edge; operacao avancada.",
 L"Gerenciar atualizacoes e politicas do Windows Update.",
 L"DNS, ajustes de rede, backup e restauracao de adaptadores.",
 L"Controles de privacidade e reducao de telemetria.",
 L"Verificacoes e reparo do Windows via ferramentas oficiais.",
 L"Apaga temporarios e lixeira; mostra progresso e gera logs.",
 L"Ativar ou desfazer menu de contexto classico no Windows 11.",
 L"Agendar, modificar ou cancelar desligamento do computador.",
 L"Abrir a ferramenta WinUtil de Chris Titus Tech.",
 L"Consultar e instalar a versao estavel publicada no GitHub.",
 L"Criar um ponto de restauracao do sistema.",
 L"Reverter configuracoes alteradas pelo Callas Optimizer."};

static int wlen(const WCHAR* s){int n=0;if(s)while(s[n])n++;return n;}
static void wcopy(WCHAR* dst,const WCHAR* src){int i=0;if(src){for(;src[i]&&i<580;i++)dst[i]=src[i];}dst[i]=0;}
static void wappend(WCHAR* dst,const WCHAR* src){int i=wlen(dst),j=0;while(src&&src[j]&&i<625)dst[i++]=src[j++];dst[i]=0;}
static void wnum(WCHAR *d,int v){WCHAR buf[16];int n=0,i=0;if(v<0){*d++='-';v=-v;}do{buf[n++]=(WCHAR)('0'+v%10);v/=10;}while(v&&n<14);while(n)d[i++]=buf[--n];d[i]=0;}
static BOOL inside(int x,int y,int x1,int y1,int x2,int y2){return x>=x1&&x<=x2&&y>=y1&&y<=y2;}
static void fill(HDC dc,int x,int y,int w,int h,DWORD col){RECT r={x,y,x+w,y+h};HBRUSH b=CreateSolidBrush(col);FillRect(dc,&r,b);DeleteObject(b);}
static void rounded(HDC dc,int x,int y,int w,int h,int radius,DWORD col,DWORD border){
 HBRUSH b=CreateSolidBrush(col); HPEN p=CreatePen(PS_SOLID,1,border);
 HGDIOBJ ob=SelectObject(dc,b),op=SelectObject(dc,p);
 RoundRect(dc,x,y,x+w,y+h,radius,radius);
 SelectObject(dc,ob);SelectObject(dc,op);DeleteObject(b);DeleteObject(p);
}
static void txt(HDC dc,const WCHAR *s,int x,int y,int w,int h,HFONT font,DWORD color,int center){
 RECT r={x,y,x+w,y+h};HGDIOBJ old=SelectObject(dc,font);SetTextColor(dc,color);SetBkMode(dc,TRANSPARENT);
 DrawTextW(dc,s,-1,&r,DT_SINGLELINE|DT_VCENTER|DT_NOPREFIX|(center?DT_CENTER:DT_LEFT));SelectObject(dc,old);
}
static void button(HDC dc,int x,int y,int w,int h,const WCHAR* title,int accent,int active){
 DWORD bg=accent?RGB2(24,100,242):RGB2(33,41,59);
 DWORD bd=accent?RGB2(58,137,255):RGB2(62,76,106);
 if(active){bg=accent?RGB2(46,122,255):RGB2(45,57,80);}
 rounded(dc,x,y,w,h,18,bg,bd);
 txt(dc,title,x+8,y+1,w-16,h-2,font14,RGB2(245,249,255),1);
}
static int ishover(int x1,int y1,int x2,int y2){return inside(mousex,mousey,x1,y1,x2,y2);}
static void paint(HDC dc,int W,int H){
 fill(dc,0,0,W,H,RGB2(12,16,27));
 fill(dc,0,0,W,90,RGB2(17,23,38));
 fill(dc,0,90,W,2,RGB2(42,55,82));
 rounded(dc,25,22,54,52,18,RGB2(27,103,245),RGB2(81,155,252));
 txt(dc,L"C",42,23,28,51,font36,RGB2(255,255,255),1);
 txt(dc,L"CALLAS OPTIMIZER",94,16,360,36,font24,RGB2(247,250,255),0);
 txt(dc,L"CENTRAL DE MANUTENCAO   /   WINDOWS 11",96,52,472,24,font12,RGB2(140,157,187),0);
 rounded(dc,W-185,25,140,38,18,RGB2(28,39,60),RGB2(54,76,107));
 txt(dc,L"VERSAO   8.9.1",W-172,24,113,40,font13b,RGB2(100,169,255),1);
 button(dc,W-410,25,205,38,L"VERIFICAR UPDATE",0,ishover(W-410,25,W-205,63));
 fill(dc,282,92,2,H-92,RGB2(39,49,70));
 txt(dc,L"FERRAMENTAS",25,112,225,30,font13b,RGB2(122,146,184),0);
 for(int i=0;i<=13;i++){
    int y=150+i*39;
    int sel=(i==selected);
    if(sel) rounded(dc,15,y,253,33,13,RGB2(30,63,118),RGB2(51,95,160));
    else if(ishover(16,y,268,y+33)) rounded(dc,15,y,253,33,13,RGB2(25,32,49),RGB2(32,48,75));
    if(i==0) txt(dc,L"//",25,y+1,23,31,font13b,RGB2(110,168,255),0);
    else {
        WCHAR num[8];wnum(num,i);
        txt(dc,num,27,y+1,24,31,font13b,sel?RGB2(130,190,255):RGB2(100,121,157),0);
    }
    txt(dc,names[i],55,y+1,208,31,sel?font13b:font13,sel?RGB2(249,251,255):RGB2(178,191,212),0);
 }
 txt(dc,L"Callas Optimizer / Windows",23,H-37,252,22,font12,RGB2(103,121,151),0);
 int rightx=316,innerW=W-343;
 txt(dc,L"CALLAS / CONTROLE CENTRAL",rightx,112,innerW,25,font13b,RGB2(96,163,245),0);
 txt(dc,selected?names[selected]:L"Pronto para otimizar",rightx,144,innerW,54,font36,RGB2(248,249,252),0);
 txt(dc,descriptions[selected],rightx,202,innerW,30,font14,RGB2(174,190,214),0);
 rounded(dc,rightx,255,innerW,112,22,RGB2(22,32,49),RGB2(47,66,98));
 txt(dc,L"OPERACOES DE MANUTENCAO",rightx+22,267,innerW-30,24,font12,RGB2(105,154,220),0);
 button(dc,rightx+20,304,330,47,selected?L"EXECUTAR OPCAO SELECIONADA":L"ABRIR MENU COMPLETO",1,ishover(rightx+20,304,rightx+350,351));
 button(dc,rightx+365,304,innerW-385,47,L"ABRIR MENU ORIGINAL",0,ishover(rightx+365,304,W-27,351));
 if(update_install_pending)txt(dc,L"ATUALIZACAO: baixando e validando (nao feche o programa)",rightx,368,innerW,20,font12,RGB2(120,205,174),0);
 txt(dc,L"INSTALADORES OFICIAIS",rightx,386,innerW,30,font13b,RGB2(114,163,230),0);
 int half=(innerW-16)/2;
 rounded(dc,rightx,422,half,194,22,RGB2(21,32,49),RGB2(48,67,95));
 rounded(dc,rightx+half+16,422,half,194,22,RGB2(21,32,49),RGB2(48,67,95));
 rounded(dc,rightx+21,440,41,40,14,RGB2(202,82,73),RGB2(237,122,106));
 txt(dc,L"B",rightx+24,441,35,37,font20,RGB2(255,255,255),1);
 txt(dc,L"Brave Browser",rightx+76,439,half-92,32,font20,RGB2(245,246,250),0);
 txt(dc,L"SteamDB + Bonjourr",rightx+21,484,half-40,25,font14,RGB2(180,195,214),0);
 txt(dc,L"Instalacao sem winget",rightx+21,509,half-40,24,font12,RGB2(119,144,174),0);
 button(dc,rightx+21,555,half-42,44,L"INSTALAR + CONFIGURAR",1,ishover(rightx+21,555,rightx+half-21,599));
 int nx=rightx+half+16;
 rounded(dc,nx+21,440,41,40,14,RGB2(84,154,62),RGB2(122,210,87));
 txt(dc,L"N",nx+23,441,36,37,font20,RGB2(255,255,255),1);
 txt(dc,L"NVIDIA App",nx+76,439,half-90,32,font20,RGB2(245,246,250),0);
 txt(dc,L"Download oficial NVIDIA",nx+21,484,half-30,25,font14,RGB2(180,195,214),0);
 txt(dc,L"Sem trocar o driver sozinho",nx+21,509,half-30,24,font12,RGB2(119,144,174),0);
 button(dc,nx+21,555,half-42,44,L"BAIXAR E INSTALAR",1,ishover(nx+21,555,nx+half-21,599));
 rounded(dc,rightx,630,innerW,94,22,RGB2(18,27,42),RGB2(45,64,91));
 txt(dc,L"Extensoes do Brave: configuracao automatica e reversivel",rightx+18,639,innerW-32,25,font13b,RGB2(191,207,230),0);
 button(dc,rightx+19,670,234,37,L"CONFIGURAR EXTENSOES",0,ishover(rightx+19,670,rightx+253,707));
 button(dc,rightx+267,670,234,37,L"DESFAZER POLITICAS",0,ishover(rightx+267,670,rightx+501,707));
 txt(dc,L"Ao forcar extensoes o Brave mostra 'Gerenciado'.",rightx+514,676,innerW-529,31,font12,RGB2(134,153,181),0);
 txt(dc,win11?L"COMPATIVEL: WINDOWS 11 X64 / IoT LTSC / PRO":L"AVISO: WINDOWS 11 NAO DETECTADO",rightx,H-39,innerW,24,font12,win11?RGB2(120,185,159):RGB2(240,177,110),0);
}

static void buildpath(WCHAR* out,LPCWSTR name){wcopy(out,folder);wappend(out,L"\\");wappend(out,name);}
static BOOL writeasset(LPCWSTR path,const BYTE* bytes,DWORD size){
 HANDLE f=CreateFileW(path,GENERIC_WRITE,0,NULL,CREATE_ALWAYS,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE)return FALSE;
 DWORD got=0;BOOL ok=WriteFile(f,bytes,size,&got,NULL);CloseHandle(f);
 return ok&&got==size;
}
static BOOL prepare_assets(void){
 DWORD n=GetEnvironmentVariableW(L"LOCALAPPDATA",folder,480);
 if(n==0||n>470)return FALSE;
 wappend(folder,L"\\CallasTeck");CreateDirectoryW(folder,NULL);
 buildpath(enginepath,L"Callas_Optimizer_V8_8_GUI_Engine.bat");
 buildpath(bravepath,L"install_brave.ps1");
 buildpath(nvidiapath,L"install_nvidia.ps1");
 buildpath(extpath,L"extensions.ps1");
 buildpath(undopath,L"undo_extensions.ps1");
 buildpath(updaterpath,L"updater.ps1");
 { WCHAR n[32]; wnum(n,(int)GetCurrentProcessId()); buildpath(statuspath,L"updater-"); wappend(statuspath,n); wappend(statuspath,L".status"); }
 return writeasset(enginepath,asset_engine,asset_engine_size)
    &&writeasset(bravepath,asset_brave,asset_brave_size)
    &&writeasset(nvidiapath,asset_nvidia,asset_nvidia_size)
    &&writeasset(extpath,asset_ext,asset_ext_size)
    &&writeasset(undopath,asset_undo,asset_undo_size)
    &&writeasset(updaterpath,asset_updater,asset_updater_size);
}
static void detect_windows(void){
 HKEY key=0;WCHAR ver[100];DWORD typ=0,len=sizeof(ver);
 if(RegOpenKeyExW(HKEY_LOCAL_MACHINE,L"SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion",0,KEY_QUERY_VALUE,&key)==0){
   if(RegQueryValueExW(key,L"CurrentBuildNumber",NULL,&typ,(BYTE*)ver,&len)==0&&typ==REG_SZ){
     int v=0;for(int i=0;ver[i]>='0'&&ver[i]<='9'&&i<15;i++)v=v*10+(ver[i]-'0');
     if(v&&v<22000)win11=0;
   }
   RegCloseKey(key);
 }
}
static BOOL confirm_action(int n){
 if(!win11){if(MessageBoxW(mainwin,L"Aplicacao priorizada para Windows 11. Esta edicao nao foi detectada. Continuar por sua conta?",L"Compatibilidade",MB_YESNO|MB_ICONWARNING)!=IDYES)return FALSE;}
 if(n==7) return MessageBoxW(mainwin,L"A limpeza total apaga temporarios e esvazia a Lixeira. Salve seus arquivos e feche aplicativos antes de continuar. Deseja abrir a limpeza?",L"Confirmar limpeza",MB_YESNO|MB_ICONWARNING)==IDYES;
 if(n==2) return MessageBoxW(mainwin,L"Remover o Microsoft Edge pode causar problemas com componentes do Windows. Abra somente se souber o que esta fazendo. Continuar?",L"Funcao avancada",MB_YESNO|MB_ICONWARNING)==IDYES;
 if(n==3||n==5||n==13)return MessageBoxW(mainwin,L"Esta funcao modifica configuracoes do Windows. Recomenda-se criar um ponto de restauracao antes de prosseguir. Continuar?",L"Confirmar alteracoes",MB_YESNO|MB_ICONWARNING)==IDYES;
 return TRUE;
}
static void launch_bat(int op){
 if(!confirm_action(op))return;
 WCHAR args[850];wcopy(args,L"/c \"\"");wappend(args,enginepath);wappend(args,L"\"");
 if(op>0){WCHAR val[15];wappend(args,L" :gui");wnum(val,op);wappend(args,val);}
 wappend(args,L"\"");
 HINSTANCE rc=ShellExecuteW(mainwin,L"runas",L"cmd.exe",args,folder,SW_SHOWNORMAL);
 if((ULONG_PTR)rc<=32) MessageBoxW(mainwin,L"Nao foi possivel abrir a ferramenta. Verifique a permissao de administrador ou o bloqueio do Windows.",L"Falha ao executar",MB_OK|MB_ICONERROR);
}
static void launch_ps(const WCHAR* path){
 if(!win11){if(MessageBoxW(mainwin,L"Os instaladores foram preparados para Windows 11 x64. Deseja continuar?",L"Compatibilidade",MB_YESNO|MB_ICONWARNING)!=IDYES)return;}
 WCHAR args[950];wcopy(args,L"-NoLogo -NoProfile -ExecutionPolicy Bypass -File \"");wappend(args,path);wappend(args,L"\"");
 HINSTANCE rc=ShellExecuteW(mainwin,L"open",L"powershell.exe",args,folder,SW_SHOWNORMAL);
 if((ULONG_PTR)rc<=32)MessageBoxW(mainwin,L"PowerShell nao abriu. Confira sua instalacao do Windows.",L"Falha",MB_OK|MB_ICONERROR);
}
static void begin_update_check(int manual){
 if(update_pending||update_install_pending)return;
 update_manual=manual;update_pending=1;update_ticks=0;
 DeleteFileW(statuspath);
 WCHAR args[1024];
 wcopy(args,L"-NoLogo -NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File \"");
 wappend(args,updaterpath);
 wappend(args,L"\" -Check -CurrentVersion 8.9.1 -StatusFile \"");
 wappend(args,statuspath);wappend(args,L"\"");
 HINSTANCE rc=ShellExecuteW(mainwin,L"open",L"powershell.exe",args,folder,SW_HIDE);
 if((ULONG_PTR)rc<=32){
  update_pending=0;
  if(manual)MessageBoxW(mainwin,L"Nao foi possivel iniciar a verificacao de atualizacoes.",L"Callas Optimizer",MB_OK|MB_ICONERROR);
 }else SetTimer(mainwin,83,1200,NULL);
}
static void install_update(void){
 if(update_install_pending)return;
 static WCHAR own[600];if(!GetModuleFileNameW(NULL,own,600))return;
 DeleteFileW(statuspath);
 static WCHAR args[1600];WCHAR pid[24];
 wnum(pid,(int)GetCurrentProcessId());
 wcopy(args,L"-NoLogo -NoProfile -ExecutionPolicy Bypass -File \"");
 wappend(args,updaterpath);
 wappend(args,L"\" -Install -CurrentVersion 8.9.1 -Target \"");
 wappend(args,own);wappend(args,L"\" -WaitPid ");wappend(args,pid);
 wappend(args,L" -StatusFile \"");wappend(args,statuspath);wappend(args,L"\"");
 HINSTANCE rc=ShellExecuteW(mainwin,L"open",L"powershell.exe",args,folder,SW_HIDE);
 if((ULONG_PTR)rc<=32){
  MessageBoxW(mainwin,L"Nao foi possivel iniciar o atualizador.",L"Falha de atualizacao",MB_OK|MB_ICONERROR);
 }else{
  update_install_pending=1; update_install_ticks=0;
  SetTimer(mainwin,84,1200,NULL);
  InvalidateRect(mainwin,NULL,FALSE);
 }
}
static void poll_update_install(void){
 if(!update_install_pending)return;
 if(++update_install_ticks>300){KillTimer(mainwin,84);update_install_pending=0;InvalidateRect(mainwin,NULL,FALSE);
  MessageBoxW(mainwin,L"A atualizacao excedeu o tempo esperado. Confira o log em AppData\\Local\\CallasTeck.",L"Atualizacao",MB_OK|MB_ICONWARNING);return;}
 HANDLE f=CreateFileW(statuspath,GENERIC_READ,3,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE)return;
 char raw[100];DWORD n=0;BOOL ok=ReadFile(f,raw,sizeof(raw)-1,&n,NULL);CloseHandle(f);
 if(!ok||n<3)return;raw[n]=0;KillTimer(mainwin,84);update_install_pending=0;
 if(raw[0]=='R'&&raw[1]=='E'&&raw[2]=='A'){ExitProcess(0);}
 InvalidateRect(mainwin,NULL,FALSE);
 MessageBoxW(mainwin,L"Falha ao baixar ou verificar a nova versao. O aplicativo atual foi mantido. Consulte AppData\\Local\\CallasTeck\\atualizacoes.log.",L"Atualizacao cancelada",MB_OK|MB_ICONWARNING);
}
static void poll_update(void){
 if(!update_pending)return;
 if(++update_ticks>45){KillTimer(mainwin,83);update_pending=0;
  if(update_manual)MessageBoxW(mainwin,L"Tempo excedido. Confira sua conexao com o GitHub.",L"Atualizacao",MB_OK|MB_ICONWARNING);
  return;}
 HANDLE f=CreateFileW(statuspath,GENERIC_READ,3,NULL,OPEN_EXISTING,FILE_ATTRIBUTE_NORMAL,NULL);
 if(f==INVALID_HANDLE_VALUE)return;
 char raw[180];DWORD n=0;BOOL ok=ReadFile(f,raw,sizeof(raw)-1,&n,NULL);CloseHandle(f);
 if(!ok||n<3)return;
 raw[n]=0;KillTimer(mainwin,83);update_pending=0;
 if(raw[0]=='A'&&raw[1]=='V'&&raw[2]=='A'){
  WCHAR msg[360],ver[80];int j=0;
  for(DWORD i=10;i<n&&j<70;i++){if(raw[i]=='\n'||raw[i]=='\r')break;ver[j++]=(WCHAR)(unsigned char)raw[i];}
  ver[j]=0;
  wcopy(msg,L"Nova versao disponivel: ");wappend(msg,ver);
  wappend(msg,L"\n\nDeseja baixar, verificar SHA-256 e atualizar agora? O aplicativo sera reiniciado.");
  if(MessageBoxW(mainwin,msg,L"Atualizacao do Callas Optimizer",MB_YESNO|MB_ICONINFORMATION)==IDYES)install_update();
 }else if(update_manual){
  MessageBoxW(mainwin,raw[0]=='C'?L"O Callas Optimizer ja esta atualizado.":L"Nao foi possivel consultar o GitHub Releases. Verifique internet e se o repositorio tem uma release publicada.",L"Verificar atualizacoes",MB_OK|(raw[0]=='C'?MB_ICONINFORMATION:MB_ICONWARNING));
 }
}
static int hit(int x,int y){
 if(inside(x,y,690,25,895,63))return 7;
 for(int i=0;i<=13;i++)if(inside(x,y,16,150+i*39,268,183+i*39))return 100+i;
 int rightx=316,innerW=1100-343,half=(innerW-16)/2,nx=rightx+half+16;
 if(inside(x,y,rightx+20,304,rightx+350,351))return 1;
 if(inside(x,y,rightx+365,304,1100-27,351))return 2;
 if(inside(x,y,rightx+21,555,rightx+half-21,599))return 3;
 if(inside(x,y,nx+21,555,nx+half-21,599))return 4;
 if(inside(x,y,rightx+19,670,rightx+253,707))return 5;
 if(inside(x,y,rightx+267,670,rightx+501,707))return 6;
 return -1;
}
static void do_click(int x,int y){
 if(inside(x,y,690,25,895,63)){begin_update_check(1);return;}
 for(int i=0;i<=13;i++)if(inside(x,y,16,150+i*39,268,183+i*39)){selected=i;InvalidateRect(mainwin,NULL,FALSE);return;}
 int rightx=316, innerW=1100-343, half=(innerW-16)/2;
 if(inside(x,y,rightx+20,304,rightx+350,351)){if(selected==11)begin_update_check(1);else launch_bat(selected);return;}
 if(inside(x,y,rightx+365,304,1100-27,351)){launch_bat(0);return;}
 if(inside(x,y,rightx+21,555,rightx+half-21,599)){
   if(MessageBoxW(mainwin,L"Brave e as extensoes SteamDB/Bonjourr serao instalados via fontes oficiais. As extensoes usarao politica local (Brave pode mostrar 'Gerenciado pela organizacao'). Voce pode desfazer depois. Continuar?",L"Instalacao do Brave",MB_YESNO|MB_ICONINFORMATION)==IDYES)launch_ps(bravepath);
   return;
 }
 int nx=rightx+half+16;
 if(inside(x,y,nx+21,555,nx+half-21,599)){launch_ps(nvidiapath);return;}
 if(inside(x,y,rightx+19,670,rightx+253,707)){
  if(MessageBoxW(mainwin,L"Aplicar politicas locais para instalar SteamDB e Bonjourr no Brave? Enquanto estiverem ativas, o navegador mostrara 'Gerenciado pela organizacao'.",L"Configurar extensoes",MB_YESNO|MB_ICONINFORMATION)==IDYES)launch_ps(extpath);
  return;
 }
 if(inside(x,y,rightx+267,670,rightx+501,707)){launch_ps(undopath);return;}
}
static LRESULT WINAPI WindowProc(HWND hwnd,UINT m,WPARAM w,LPARAM l){
 if(m==WM_ERASEBKGND)return 1;
 if(m==WM_TIMER&&w==83){poll_update();return 0;}
 if(m==WM_TIMER&&w==84){poll_update_install();return 0;}
 if(m==WM_PAINT){PAINTSTRUCT ps;HDC dc=BeginPaint(hwnd,&ps);RECT r;GetClientRect(hwnd,&r);int W=r.right-r.left,H=r.bottom-r.top;
  HDC mem=CreateCompatibleDC(dc);HBITMAP bmp=CreateCompatibleBitmap(dc,W,H);HGDIOBJ old=SelectObject(mem,bmp);
  paint(mem,W,H);BitBlt(dc,0,0,W,H,mem,0,0,SRCCOPY);SelectObject(mem,old);DeleteObject(bmp);DeleteDC(mem);EndPaint(hwnd,&ps);return 0;
 }
 if(m==WM_MOUSEMOVE){int x=(short)(l&0xffff),y=(short)((l>>16)&0xffff);mousex=x;mousey=y;int next=hit(x,y);if(next!=hover){hover=next;InvalidateRect(hwnd,NULL,FALSE);}return 0;}
 if(m==WM_LBUTTONUP){int x=(short)(l&0xffff),y=(short)((l>>16)&0xffff);do_click(x,y);return 0;}
 if(m==WM_SETCURSOR){SetCursor(hover>=0?cursor_hand:cursor_arrow);return 1;}
 if(m==WM_DESTROY){PostQuitMessage(0);return 0;}
 return DefWindowProcW(hwnd,m,w,l);
}
void WINAPI mainCRTStartup(void){
 HINSTANCE mod=GetModuleHandleW(NULL);
 cursor_arrow=LoadCursorW(NULL,IDC_ARROW);cursor_hand=LoadCursorW(NULL,IDC_HAND);
 font36=CreateFontW(38,0,0,0,700,0,0,0,1,0,0,0,0,L"Segoe UI");
 font24=CreateFontW(25,0,0,0,700,0,0,0,1,0,0,0,0,L"Segoe UI");
 font20=CreateFontW(20,0,0,0,700,0,0,0,1,0,0,0,0,L"Segoe UI");
 font16=CreateFontW(17,0,0,0,500,0,0,0,1,0,0,0,0,L"Segoe UI");
 font14=CreateFontW(15,0,0,0,500,0,0,0,1,0,0,0,0,L"Segoe UI");
 font13=CreateFontW(14,0,0,0,500,0,0,0,1,0,0,0,0,L"Segoe UI");
 font13b=CreateFontW(14,0,0,0,700,0,0,0,1,0,0,0,0,L"Segoe UI");
 font12=CreateFontW(13,0,0,0,500,0,0,0,1,0,0,0,0,L"Segoe UI");
 detect_windows();
 WNDCLASSEXW wc={0};wc.cbSize=sizeof(wc);wc.style=CS_HREDRAW|CS_VREDRAW;wc.lpfnWndProc=(void*)WindowProc;wc.hInstance=mod;
 wc.hCursor=cursor_arrow;wc.lpszClassName=L"CallasOptimizerDesktop891";
 if(!RegisterClassExW(&wc)){ExitProcess(1);}
 mainwin=CreateWindowExW(0,wc.lpszClassName,L"Callas Optimizer 8.9.1 | Windows Edition",WS_OVERLAPPED|WS_CAPTION|WS_SYSMENU|WS_MINIMIZEBOX,80,60,1116,804,NULL,NULL,mod,NULL);
 if(!mainwin){ExitProcess(2);}
 BOOL assetsok=prepare_assets();
 if(!assetsok)MessageBoxW(mainwin,L"Nao foi possivel preparar os arquivos locais. Verifique as permissoes de escrita em AppData\\Local\\CallasTeck.",L"Problema com arquivos",MB_OK|MB_ICONERROR);
 ShowWindow(mainwin,SW_SHOW);UpdateWindow(mainwin);
 if(assetsok)begin_update_check(0);
 MSG msg={0};while(GetMessageW(&msg,NULL,0,0)>0){TranslateMessage(&msg);DispatchMessageW(&msg);}
 ExitProcess(0);
}
