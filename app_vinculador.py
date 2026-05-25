import os
import sys
import json
import time
import re
import base64
import threading
import eel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import updater

# =============================================
# VERSÃO DO APLICATIVO
# =============================================
CURRENT_VERSION = "v1.0.0"

# Configura o diretório web
if getattr(sys, 'frozen', False):
    web_dir = os.path.join(sys._MEIPASS, 'web')
else:
    web_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web')

eel.init(web_dir)

class BotBackend:
    def __init__(self):
        self.driver = None
        self.todas_unidades = []
        self.todas_agregadas = {}
        self.executando = False
        self.ultimo_erro = "Nenhum erro registrado."
        self.prints_memoria = {}
        self.arquivo_historico = "historico_concluidas.txt"
        self.concluidas = self._carregar_historico()

    def log(self, msg):
        print(msg)
        eel.log_message(msg)()

    def _carregar_historico(self):
        concluidas = set()
        if os.path.exists(self.arquivo_historico):
            with open(self.arquivo_historico, "r", encoding="utf-8") as f:
                for linha in f:
                    item = linha.strip()
                    if item:
                        concluidas.add(item)
        return concluidas

    def _salvar_no_historico(self, unidade):
        if unidade not in self.concluidas:
            self.concluidas.add(unidade)
            with open(self.arquivo_historico, "a", encoding="utf-8") as f:
                f.write(unidade + "\n")
            eel.atualizar_historico(sorted(list(self.concluidas)))()

    def abrir_sistema(self, usuario, senha, condominio):
        self.log("Iniciando Chrome...")
        try:
            options = Options()
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--ignore-certificate-errors")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)

            paths_chrome = [
                os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'Google', 'Chrome', 'Application', 'chrome.exe'),
                os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'), 'Google', 'Chrome', 'Application', 'chrome.exe'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Google', 'Chrome', 'Application', 'chrome.exe')
            ]
            for p in paths_chrome:
                if os.path.exists(p):
                    options.binary_location = p
                    self.log("Google Chrome do sistema detectado.")
                    break

            if getattr(sys, 'frozen', False):
                pasta_exe = os.path.dirname(sys.executable)
            else:
                pasta_exe = os.path.dirname(os.path.abspath(__file__))

            driver_local = os.path.join(pasta_exe, 'chromedriver.exe')
            if os.path.exists(driver_local):
                self.log(f"ChromeDriver local encontrado. Usando...")
                service = Service(driver_local)
                self.driver = webdriver.Chrome(service=service, options=options)
            else:
                self.log("Detectando ChromeDriver via Selenium Manager...")
                self.driver = webdriver.Chrome(options=options)

            self.log("Chrome iniciado! Abrindo sistema...")
            # Abre a página de LOGIN - o sistema redireciona para o painel automaticamente após login
            self.driver.get("https://servc9-1.webware.com.br/bin/administradora/")
            self.log("Tentando preencher login automático...")
            try:
                # Tenta os seletores conhecidos do sistema Webware
                # (By.NAME 'mem'/'pass' é o padrão do Webware administradora)
                campo_usuario = None
                for sel in [("id","usuario"), ("name","mem"), ("id","login"), ("name","usuario")]:
                    try:
                        campo_usuario = WebDriverWait(self.driver, 4).until(
                            EC.presence_of_element_located((By.ID if sel[0]=="id" else By.NAME, sel[1]))
                        )
                        break
                    except Exception:
                        continue

                if campo_usuario is None:
                    raise Exception("Campo de usuário não encontrado")

                campo_usuario.clear()
                campo_usuario.send_keys(usuario)

                # Senha
                campo_senha = None
                for sel in [("id","senha"), ("name","pass"), ("id","password"), ("name","senha")]:
                    try:
                        campo_senha = self.driver.find_element(
                            By.ID if sel[0]=="id" else By.NAME, sel[1]
                        )
                        break
                    except Exception:
                        continue

                if campo_senha is None:
                    raise Exception("Campo de senha não encontrado")

                campo_senha.clear()
                campo_senha.send_keys(senha)

                # Botão de login
                botao_entrar = self.driver.find_element(
                    By.XPATH,
                    "//input[@type='Submit'] | //input[@type='submit'] | //button[@type='submit']"
                )
                botao_entrar.click()
                self.log("✅ Login automático realizado!")

            except Exception as e:
                self.log("⚠️ Não foi possível preencher o login automático.")
                self.log("👉 Faça o login manualmente na janela do Chrome.")

            self.log("Após o login, navegue até a tabela de unidades e clique em 'Ler Unidades'.")

            eel.habilitar_leitura()()

        except Exception as e:
            self.ultimo_erro = str(e)
            self.log(f"Falha ao abrir sistema: {e}")

    def ler_unidades(self):
        if not self.driver:
            self.log("ERRO: Chrome não está aberto.")
            return

        self.log("Lendo unidades da tabela...")
        try:
            self.todas_unidades = []
            self.todas_agregadas = {}
            js_data = []

            # Entra no iframe confirmado pelo diagnóstico
            self.driver.switch_to.default_content()
            try:
                self.driver.switch_to.frame("conteudoPrincipal")
                self.log("  [OK] Entrou no iframe conteudoPrincipal")
            except Exception as e:
                self.log(f"  [ERRO] Não conseguiu entrar no iframe: {e}")
                self.log("  Verifique se você está na tela correta do sistema.")
                eel.atualizar_lista_unidades([])()
                return

            # Usa o ID da tabela e a classe da linha confirmados pelo HTML fonte:
            # <table id='table_principal'> e <tr class='trL'> (linhas de dados)
            # Linhas de categoria (SubTitulo) e cabeçalho são ignoradas automaticamente
            linhas = self.driver.find_elements(
                By.XPATH, "//table[@id='table_principal']//tr[@class='trL']"
            )
            self.log(f"  [OK] {len(linhas)} linhas de tabela encontradas")

            # Padrão de código de unidade: NN/TIPO/NNNNNN
            # Exemplos: 01/Apart/000052, 01/Sala/000001, 02/Loja/000005
            # Funciona para qualquer condomínio independente do tipo de unidade
            RE_UNIDADE = re.compile(r'\d{2}/\w+/\d+')

            for linha in linhas:
                try:
                    celulas = linha.find_elements(By.TAG_NAME, "td")
                    # Diagnóstico confirmou: unidade está SEMPRE em celulas[1]
                    if len(celulas) < 2:
                        continue

                    texto_cel = celulas[1].text or ""
                    # Verifica se a célula contém código de unidade (qualquer formato)
                    if not RE_UNIDADE.search(texto_cel):
                        continue

                    # Separa principal das agregadas
                    # Formato: "01/Apart/000081\nAgregadas:\n01/Apart/000091"
                    todas = RE_UNIDADE.findall(texto_cel)
                    if not todas:
                        continue

                    principal = todas[0]
                    agregadas = todas[1:]

                    if principal in self.todas_unidades:
                        continue  # evita duplicata

                    self.todas_unidades.append(principal)
                    self.todas_agregadas[principal] = agregadas
                    js_data.append({
                        "nome": principal,
                        "concluido": principal in self.concluidas,
                        "info": ", ".join(agregadas) if agregadas else ""
                    })

                except Exception:
                    continue

            if self.todas_unidades:
                self.log(f"✅ {len(self.todas_unidades)} cadastros principais encontrados.")
                eel.atualizar_lista_unidades(js_data)()
            else:
                self.log("⚠️ Nenhuma unidade encontrada.")
                self.log("  Dica: aplique o filtro do condomínio antes de clicar em 'Ler Unidades'.")
                eel.atualizar_lista_unidades([])()

        except Exception as e:
            self.ultimo_erro = str(e)
            self.log(f"Erro ao ler unidades: {e}")


    def _entrar_iframe_principal(self):
        """Garante que o driver está dentro do iframe conteudoPrincipal."""
        self.driver.switch_to.default_content()
        WebDriverWait(self.driver, 10).until(
            EC.frame_to_be_available_and_switch_to_it((By.ID, "conteudoPrincipal"))
        )

    def iniciar_robo(self, condominio, unidades_alvo, vinc_agregadas):
        self.executando = True
        self.log(f"Iniciando robô para {len(unidades_alvo)} cadastros...")

        aba_principal = self.driver.current_window_handle

        for i, texto_unidade in enumerate(unidades_alvo):
            if not self.executando:
                self.log("Processo cancelado pelo usuário.")
                break

            self.log(f"\n[{i+1}/{len(unidades_alvo)}] Processando: {texto_unidade}")

            try:
                # --- PASSO 1: Entra no iframe e acha a linha ---
                self.driver.switch_to.window(aba_principal)
                self._entrar_iframe_principal()

                # Usa table ID e classe da linha confirmados pelo HTML fonte
                xpath_linha = (
                    f"//table[@id='table_principal']"
                    f"//tr[@class='trL'][.//td[contains(text(), '{texto_unidade}')]]"
                )
                linha_alvo = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath_linha))
                )
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({block:'center'});", linha_alvo
                )
                time.sleep(0.3)

                # --- PASSO 2: Pega o link do lápis (img alt='Editar Cadastro') ---
                # Confirmado pelo inspetor: <a href="..."><img alt="Editar Cadastro"></a>
                botao_lapis = linha_alvo.find_element(
                    By.XPATH, ".//a[img[@alt='Editar Cadastro']]"
                )
                link_edicao = botao_lapis.get_attribute("href")

                # --- PASSO 3: Abre a página de edição do usuário em nova aba ---
                self.driver.execute_script(f"window.open('{link_edicao}', '_blank');")
                time.sleep(1.5)
                self.driver.switch_to.window(self.driver.window_handles[-1])

                # --- PASSO 4: Processa o vínculo da unidade principal ---
                sucesso = self._processar_unidade(texto_unidade, condominio)
                if sucesso:
                    self._salvar_no_historico(texto_unidade)

                # --- PASSO 5: Processa agregadas (se habilitado) ---
                if vinc_agregadas:
                    agregadas = self.todas_agregadas.get(texto_unidade, [])
                    for agr in agregadas:
                        if not self.executando:
                            break
                        self.log(f"   -> Vinculando agregada: {agr}")
                        # Para cada agregada, reabre a página de edição e vincula
                        self.driver.switch_to.window(aba_principal)
                        self._entrar_iframe_principal()
                        linha_agr = WebDriverWait(self.driver, 10).until(
                            EC.presence_of_element_located(
                                (By.XPATH,
                                 f"//table[@id='table_principal']"
                                 f"//tr[@class='trL'][.//td[contains(text(), '{texto_unidade}')]]"
                                )
                            )
                        )
                        btn_agr = linha_agr.find_element(
                            By.XPATH, ".//a[img[@alt='Editar Cadastro']]"
                        )
                        link_agr = btn_agr.get_attribute("href")
                        self.driver.execute_script(f"window.open('{link_agr}', '_blank');")
                        time.sleep(1.5)
                        self.driver.switch_to.window(self.driver.window_handles[-1])
                        suc_agr = self._processar_unidade(agr, condominio)
                        if suc_agr:
                            self._salvar_no_historico(agr)

            except Exception as e:
                self.ultimo_erro = str(e)
                self.log(f"  [ERRO] {texto_unidade}: {str(e).split(chr(10))[0][:120]}")

            finally:
                # Fecha abas extras e volta para a aba principal
                while len(self.driver.window_handles) > 1:
                    self.driver.switch_to.window(self.driver.window_handles[-1])
                    self.driver.close()
                self.driver.switch_to.window(aba_principal)
                time.sleep(0.5)

        self.log("\nProcesso Concluído!")
        self.executando = False
        eel.robo_finalizado()()




    def _processar_unidade(self, unidade_nome, condominio):
        """
        Fluxo confirmado pelo inspetor HTML:
        1. Página de edição já está aberta na aba atual
        2. Clica no link 'Vínculo'
        3. Preenche id='c' com o condomínio
        4. Envia TAB (onblur carrega o dropdown de unidades)
        5. Aguarda 2.5s o dropdown carregar
        6. Seleciona a unidade no select id='FormUnidade' pelo value exato
        7. Captura print como evidência
        8. Clica em 'Adicionar'
        9. Aceita alert se aparecer
        """
        try:
            # Etapa 1: Clica no link 'Vínculo' da página de edição
            # Confirmado: <a href="/bin/gerenciamento/dpUsuarioVinculo.asp?L=...">Vínculo</a>
            btn_vinculo = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.LINK_TEXT, "Vínculo"))
            )
            btn_vinculo.click()
            self.log(f"   -> Clicou em Vínculo")

            # Etapa 2: Preenche o campo do condomínio (id='c')
            # Confirmado: <input id="c" onblur="PreencherSelectUnidade(...)">
            campo_cond = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "c"))
            )
            campo_cond.clear()
            campo_cond.send_keys(str(condominio))
            # TAB dispara o onblur que carrega o dropdown de unidades
            campo_cond.send_keys(Keys.TAB)
            self.log(f"   -> Condomínio {condominio} digitado, aguardando dropdown...")

            # Etapa 3: Aguarda o dropdown carregar (onblur faz requisição assíncrona)
            time.sleep(2.5)

            # Etapa 4: Seleciona a unidade pelo value exato no dropdown
            # Confirmado: <select id='FormUnidade'><option value='01/Apart/000052'>...
            select_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "FormUnidade"))
            )
            dropdown = Select(select_el)

            try:
                dropdown.select_by_value(unidade_nome)
                self.log(f"   -> Unidade '{unidade_nome}' selecionada no dropdown")
            except Exception:
                # Fallback: tenta match parcial pelo último segmento (número do apart)
                apart_num = unidade_nome.split('/')[-1].strip()
                selecionou = False
                for op in dropdown.options:
                    if apart_num in op.get_attribute("value"):
                        dropdown.select_by_value(op.get_attribute("value"))
                        self.log(f"   -> Selecionado por match parcial: {op.get_attribute('value')}")
                        selecionou = True
                        break
                if not selecionou:
                    self.log(f"   [AVISO] Unidade '{unidade_nome}' não encontrada no dropdown.")
                    return False

            time.sleep(0.5)

            # Etapa 5: Captura print como evidência (antes de confirmar)
            self._capturar_print_memoria(unidade_nome)

            # Etapa 6: Clica em 'Adicionar'
            # Confirmado: <input type='button' value='Adicionar' onclick='validar_envio()'>
            btn_add = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@type='button' and @value='Adicionar']")
                )
            )
            btn_add.click()
            time.sleep(1)

            # Etapa 7: Aceita alert se aparecer
            try:
                WebDriverWait(self.driver, 3).until(EC.alert_is_present())
                alerta = self.driver.switch_to.alert
                texto_alerta = alerta.text
                alerta.accept()
                self.log(f"   -> Alert: {texto_alerta[:80]}")
            except Exception:
                pass  # sem alert é normal em alguns casos

            self.log(f"   [SUCESSO] {unidade_nome} vinculada!")
            return True

        except Exception as e:
            self.ultimo_erro = str(e)
            self.log(f"   [ERRO] {unidade_nome}: {str(e).split(chr(10))[0][:100]}")
            return False

    def _capturar_print_memoria(self, unidade):
        try:
            time.sleep(1)
            b64_img = self.driver.get_screenshot_as_base64()
            self.prints_memoria[unidade] = b64_img
        except Exception as e:
            self.log(f"   [AVISO] Print falhou: {e}")

bot = BotBackend()

@eel.expose
def abrir_sistema(user, pwd, cond):
    threading.Thread(target=bot.abrir_sistema, args=(user, pwd, cond), daemon=True).start()

@eel.expose
def ler_unidades():
    threading.Thread(target=bot.ler_unidades, daemon=True).start()

@eel.expose
def iniciar_robo(condominio, unidades_alvo, vinc_agregadas):
    threading.Thread(target=bot.iniciar_robo, args=(condominio, unidades_alvo, vinc_agregadas), daemon=True).start()

@eel.expose
def parar_robo():
    if bot.executando:
        bot.executando = False
        bot.log("[BOT] Parada solicitada...")

@eel.expose
def obter_ultimo_erro():
    return bot.ultimo_erro

@eel.expose
def get_todas_concluidas():
    return sorted(list(bot.concluidas))

@eel.expose
def get_print(unidade):
    return bot.prints_memoria.get(unidade, None)

@eel.expose
def excluir_print(unidade):
    if unidade in bot.prints_memoria:
        del bot.prints_memoria[unidade]

@eel.expose
def salvar_login(user, pwd, cond, lembrar_login, lembrar_cond):
    arquivo_config = "config.json"
    dados = {}
    
    if os.path.exists(arquivo_config):
        try:
            with open(arquivo_config, 'r', encoding='utf-8') as f:
                dados = json.load(f)
        except:
            pass

    if lembrar_login:
        dados["usuario"] = user
        dados["senha"] = base64.b64encode(pwd.encode('utf-8')).decode('utf-8')
    else:
        dados.pop("usuario", None)
        dados.pop("senha", None)

    if lembrar_cond:
        dados["condominio"] = cond
    else:
        dados.pop("condominio", None)

    if dados:
        with open(arquivo_config, 'w', encoding='utf-8') as f:
            json.dump(dados, f)
    else:
        if os.path.exists(arquivo_config):
            os.remove(arquivo_config)

@eel.expose
def obter_login_salvo():
    arquivo_config = "config.json"
    if os.path.exists(arquivo_config):
        try:
            with open(arquivo_config, 'r', encoding='utf-8') as f:
                dados = json.load(f)
                pwd_decodificada = base64.b64decode(dados["senha"].encode('utf-8')).decode('utf-8')
                return {
                    "usuario": dados["usuario"],
                    "senha": pwd_decodificada,
                    "condominio": dados.get("condominio", "")
                }
        except Exception:
            pass
    return None

@eel.expose
def verificar_update_disponivel():
    """Verifica se há uma nova versão no GitHub e notifica a UI."""
    info = updater.verificar_update(CURRENT_VERSION)
    if info:
        eel.notificar_update(info["version"], info["download_url"], info["release_notes"])()

@eel.expose
def iniciar_download_update(download_url):
    """Inicia o download e aplicação do update em segundo plano."""
    def _progresso(percent):
        eel.progresso_update(percent)()

    def _task():
        ok = updater.baixar_e_aplicar_update(download_url, callback_progresso=_progresso)
        if not ok:
            eel.progresso_update(-1)()  # -1 = erro

    threading.Thread(target=_task, daemon=True).start()

if __name__ == "__main__":
    # Limpa arquivos .old.exe residuais de atualizações anteriores
    updater.limpar_residuos()

    # Verifica update em background sem bloquear a inicialização
    threading.Thread(
        target=verificar_update_disponivel,
        daemon=True
    ).start()

    eel.start('index.html', size=(950, 800), mode='chrome')