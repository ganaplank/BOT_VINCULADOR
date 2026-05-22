"""
Classe base SeleniumBot com lógica comum de automação.
Centraliza todas as operações Selenium para reutilização.
"""

from typing import Optional, List, Tuple
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
    ElementClickInterceptedException,
)
import time

from config import (
    Selectors, TIMEOUT_PADRAO, TIMEOUT_ENTRE_ACOES, 
    TIMEOUT_ENTRE_BACKS, TIMEOUT_APOS_BACKS, URL_PRINCIPAL,
    CONDOMINIO_ID, TIMEOUT_ELEMENTO_CLICKAVEL, TIMEOUT_APOS_CLIQUE
)
from logger import get_logger

log = get_logger("selenium_bot")


class SeleniumBotError(Exception):
    """Exceção base para erros do SeleniumBot"""
    pass


class LoginError(SeleniumBotError):
    """Erro ao fazer login"""
    pass


class NavigationError(SeleniumBotError):
    """Erro ao navegar"""
    pass


class ElementError(SeleniumBotError):
    """Erro ao encontrar/manipular elemento"""
    pass


class SeleniumBot:
    """Classe base com operações Selenium reutilizáveis"""
    
    def __init__(self, usuario: str, senha: str, headless: bool = False):
        """
        Inicializa o bot.
        
        Args:
            usuario: Nome de usuário
            senha: Senha do usuário
            headless: Se True, executa em modo headless (sem exibir navegador)
        """
        self.usuario = usuario
        self.senha = senha
        self.driver: Optional[webdriver.Chrome] = None
        self.headless = headless
        self._inicializar_driver()
    
    def _inicializar_driver(self) -> None:
        """Inicializa o driver do Chrome"""
        try:
            options = webdriver.ChromeOptions()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--disable-blink-features=AutomationControlled")
            
            self.driver = webdriver.Chrome(options=options)
            log.debug("Driver Chrome inicializado com sucesso")
        except Exception as e:
            log.error(f"Erro ao inicializar driver: {e}")
            raise SeleniumBotError(f"Falha ao inicializar Selenium: {e}")
    
    def abrir_site(self, url: str = URL_PRINCIPAL) -> None:
        """
        Abre o site principal.
        
        Args:
            url: URL a abrir
        
        Raises:
            SeleniumBotError: Se falhar ao abrir o site
        """
        if not self.driver:
            raise SeleniumBotError("Driver não foi inicializado")
        
        try:
            log.info(f"Abrindo {url}")
            self.driver.get(url)
            log.debug("Site carregado com sucesso")
        except Exception as e:
            log.error(f"Erro ao abrir site: {e}")
            raise SeleniumBotError(f"Falha ao abrir site: {e}")
    
    def fazer_login(self) -> None:
        """
        Realiza login automático.
        
        Raises:
            LoginError: Se falhar no login
        """
        try:
            log.info("Iniciando login automático")
            
            # Campo de usuário
            campo_usuario = WebDriverWait(self.driver, TIMEOUT_PADRAO).until(
                EC.presence_of_element_located((By.ID, Selectors.CAMPO_USUARIO_ID))
            )
            campo_usuario.clear()
            campo_usuario.send_keys(self.usuario)
            log.debug("Usuário preenchido")
            
            # Campo de senha
            campo_senha = self.driver.find_element(By.ID, Selectors.CAMPO_SENHA_ID)
            campo_senha.clear()
            campo_senha.send_keys(self.senha)
            log.debug("Senha preenchida")
            
            # Botão de entrar
            botao_entrar = self.driver.find_element(By.XPATH, Selectors.BOTAO_ENTRAR_XPATH)
            botao_entrar.click()
            log.debug("Botão de login clicado")
            
            time.sleep(TIMEOUT_ENTRE_ACOES)
            log.info("Login concluído com sucesso")
            
        except TimeoutException:
            msg = "Timeout ao aguardar campo de usuário"
            log.error(msg)
            raise LoginError(msg)
        except NoSuchElementException as e:
            msg = f"Elemento não encontrado durante login: {e}"
            log.error(msg)
            raise LoginError(msg)
        except Exception as e:
            msg = f"Erro durante login: {e}"
            log.error(msg)
            raise LoginError(msg)
    
    def entrar_iframe_principal(self) -> None:
        """
        Entra no iframe principal do sistema.
        
        Raises:
            NavigationError: Se falhar ao acessar o iframe
        """
        try:
            log.debug("Entrando no iframe principal")
            self.driver.switch_to.default_content()
            WebDriverWait(self.driver, TIMEOUT_PADRAO).until(
                EC.frame_to_be_available_and_switch_to_it(
                    (By.ID, Selectors.IFRAME_PRINCIPAL_ID)
                )
            )
            log.debug("Iframe principal acessado com sucesso")
        except TimeoutException:
            msg = "Timeout ao aguardar iframe"
            log.error(msg)
            raise NavigationError(msg)
        except Exception as e:
            msg = f"Erro ao acessar iframe: {e}"
            log.error(msg)
            raise NavigationError(msg)
    
    def sair_iframe(self) -> None:
        """Sai do iframe e volta para o conteúdo principal"""
        try:
            self.driver.switch_to.default_content()
            log.debug("Saído do iframe")
        except Exception as e:
            log.warning(f"Erro ao sair do iframe: {e}")
    
    def ler_unidades_tabela(self) -> List[str]:
        """
        Lê a lista de unidades da tabela.
        
        Returns:
            Lista de textos de unidades encontradas
        
        Raises:
            ElementError: Se falhar ao ler as unidades
        """
        try:
            log.info("Lendo unidades da tabela")
            self.entrar_iframe_principal()
            
            linhas = self.driver.find_elements(By.XPATH, Selectors.LINHAS_UNIDADES_XPATH)
            log.debug(f"Encontradas {len(linhas)} linhas de unidades")
            
            unidades = []
            for idx, linha in enumerate(linhas):
                try:
                    td_unidade = linha.find_element(By.XPATH, Selectors.TD_UNIDADE_XPATH)
                    texto = td_unidade.text.replace('\xa0', '').strip()
                    if texto:
                        unidades.append(texto)
                        log.debug(f"Unidade {idx+1}: {texto}")
                except NoSuchElementException:
                    log.debug(f"Linha {idx} não contém unidade válida")
                    continue
            
            log.info(f"Total de unidades lidas: {len(unidades)}")
            return unidades
            
        except Exception as e:
            msg = f"Erro ao ler unidades: {e}"
            log.error(msg)
            raise ElementError(msg)
    
    def clicar_botao_editar_unidade(self, texto_unidade: str) -> None:
        """
        Clica no botão de editar para uma unidade específica.
        
        Args:
            texto_unidade: Texto da unidade a editar
        
        Raises:
            ElementError: Se falhar ao clicar
        """
        try:
            log.debug(f"Procurando unidade: {texto_unidade}")
            xpath_linha = f"//table//tr[.//td[contains(text(), '{texto_unidade}')]]"
            
            linha = WebDriverWait(self.driver, TIMEOUT_PADRAO).until(
                EC.presence_of_element_located((By.XPATH, xpath_linha))
            )
            
            botao_editar = linha.find_element(By.XPATH, Selectors.BOTAO_EDITAR_XPATH)
            botao_editar.click()
            
            log.debug(f"Botão de editar clicado para: {texto_unidade}")
            time.sleep(TIMEOUT_APOS_CLIQUE)
            
        except TimeoutException:
            msg = f"Timeout ao procurar unidade: {texto_unidade}"
            log.error(msg)
            raise ElementError(msg)
        except NoSuchElementException as e:
            msg = f"Elemento não encontrado: {e}"
            log.error(msg)
            raise ElementError(msg)
        except Exception as e:
            msg = f"Erro ao clicar em editar: {e}"
            log.error(msg)
            raise ElementError(msg)
    
    def clicar_link_vinculo(self) -> None:
        """
        Clica no link de Vínculo.
        
        Raises:
            ElementError: Se falhar ao clicar
        """
        try:
            log.debug("Clicando em link de Vínculo")
            botao_vinculo = WebDriverWait(self.driver, TIMEOUT_ELEMENTO_CLICKAVEL).until(
                EC.element_to_be_clickable((By.LINK_TEXT, Selectors.LINK_VINCULO_TEXT))
            )
            botao_vinculo.click()
            time.sleep(TIMEOUT_APOS_CLIQUE)
            log.debug("Link de Vínculo clicado")
            
        except TimeoutException:
            msg = "Timeout ao aguardar link de Vínculo"
            log.error(msg)
            raise ElementError(msg)
        except Exception as e:
            msg = f"Erro ao clicar em Vínculo: {e}"
            log.error(msg)
            raise ElementError(msg)
    
    def preencher_condominio(self, condominio_id: str) -> None:
        """
        Preenche o campo de Condomínio.
        
        Args:
            condominio_id: ID do condomínio
        
        Raises:
            ElementError: Se falhar ao preencher
        """
        try:
            log.debug(f"Preenchendo condomínio: {condominio_id}")
            input_cond = WebDriverWait(self.driver, TIMEOUT_PADRAO).until(
                EC.presence_of_element_located((By.ID, Selectors.INPUT_CONDOMINIO_ID))
            )
            input_cond.clear()
            input_cond.send_keys(condominio_id)
            time.sleep(TIMEOUT_ENTRE_ACOES)
            log.debug("Condomínio preenchido")
            
        except TimeoutException:
            msg = "Timeout ao aguardar campo de condomínio"
            log.error(msg)
            raise ElementError(msg)
        except Exception as e:
            msg = f"Erro ao preencher condomínio: {e}"
            log.error(msg)
            raise ElementError(msg)
    
    def selecionar_unidade_dropdown(self, texto_unidade: str) -> None:
        """
        Seleciona a unidade no dropdown.
        
        Args:
            texto_unidade: Texto da unidade a selecionar
        
        Raises:
            ElementError: Se falhar ao selecionar
        """
        try:
            log.debug(f"Selecionando unidade no dropdown: {texto_unidade}")
            elemento_select = self.driver.find_element(By.ID, Selectors.SELECT_UNIDADE_ID)
            dropdown = Select(elemento_select)
            
            # Tentar selecionar pelo valor
            try:
                dropdown.select_by_value(texto_unidade)
                log.debug("Unidade selecionada por valor")
                return
            except NoSuchElementException:
                pass
            
            # Tentar selecionar pelo apartamento (última parte)
            apart_alvo = texto_unidade.split('/')[-1].strip()
            log.debug(f"Procurando apartamento: {apart_alvo}")
            
            for opcao in dropdown.options:
                if apart_alvo in opcao.text:
                    dropdown.select_by_visible_text(opcao.text)
                    log.debug(f"Unidade selecionada por texto: {opcao.text}")
                    return
            
            raise ElementError(f"Unidade {texto_unidade} não encontrada no dropdown")
            
        except Exception as e:
            msg = f"Erro ao selecionar unidade no dropdown: {e}"
            log.error(msg)
            raise ElementError(msg)
    
    def clicar_botao_adicionar(self) -> None:
        """
        Clica no botão de Adicionar.
        
        Raises:
            ElementError: Se falhar ao clicar
        """
        try:
            log.debug("Clicando em botão Adicionar")
            botao_add = WebDriverWait(self.driver, TIMEOUT_ELEMENTO_CLICKAVEL).until(
                EC.element_to_be_clickable((By.XPATH, Selectors.BOTAO_ADICIONAR_XPATH))
            )
            botao_add.click()
            time.sleep(TIMEOUT_APOS_CLIQUE)
            log.debug("Botão Adicionar clicado")
            
        except TimeoutException:
            msg = "Timeout ao aguardar botão Adicionar"
            log.error(msg)
            raise ElementError(msg)
        except Exception as e:
            msg = f"Erro ao clicar em Adicionar: {e}"
            log.error(msg)
            raise ElementError(msg)
    
    def voltar_na_navegacao(self, quantas_vezes: int = 3) -> None:
        """
        Volta na navegação N vezes.
        
        Args:
            quantas_vezes: Quantas vezes voltar
        """
        log.debug(f"Voltando {quantas_vezes} vezes")
        for i in range(quantas_vezes):
            try:
                self.driver.back()
                time.sleep(TIMEOUT_ENTRE_BACKS)
                log.debug(f"Volta {i+1}/{quantas_vezes} concluída")
            except Exception as e:
                log.warning(f"Erro na volta {i+1}: {e}")
        
        time.sleep(TIMEOUT_APOS_BACKS)
    
    def processar_unidade(
        self, 
        texto_unidade: str, 
        condominio_id: str = CONDOMINIO_ID
    ) -> Tuple[bool, str]:
        """
        Processa uma unidade completa (editar -> vínculo -> preencher -> adicionar -> voltar).
        
        Args:
            texto_unidade: Texto da unidade
            condominio_id: ID do condomínio
        
        Returns:
            Tupla (sucesso, mensagem)
        """
        try:
            log.info(f"Processando unidade: {texto_unidade}")
            
            # Garantir que está no iframe
            self.entrar_iframe_principal()
            
            # Clicar em editar
            self.clicar_botao_editar_unidade(texto_unidade)
            
            # Clicar em Vínculo
            self.clicar_link_vinculo()
            
            # Preencher condomínio
            self.preencher_condominio(condominio_id)
            
            # Selecionar unidade
            self.selecionar_unidade_dropdown(texto_unidade)
            
            # Clicar em Adicionar
            self.clicar_botao_adicionar()
            
            # Voltar
            self.voltar_na_navegacao(3)
            
            msg = f"Unidade {texto_unidade} processada com sucesso"
            log.info(msg)
            return True, msg
            
        except (LoginError, NavigationError, ElementError) as e:
            msg = f"Erro ao processar {texto_unidade}: {str(e)}"
            log.error(msg)
            # Tentar recuperar
            try:
                self.voltar_na_navegacao(3)
            except:
                pass
            return False, msg
        except Exception as e:
            msg = f"Erro inesperado ao processar {texto_unidade}: {e}"
            log.error(msg)
            return False, msg
    
    def fechar(self) -> None:
        """Fecha o driver"""
        try:
            if self.driver:
                self.driver.quit()
                log.info("Driver fechado com sucesso")
        except Exception as e:
            log.warning(f"Erro ao fechar driver: {e}")
    
    def __enter__(self):
        """Context manager: enter"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager: exit"""
        self.fechar()
