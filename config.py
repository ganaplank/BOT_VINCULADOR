"""
Configurações centralizadas do Bot Vinculador.
Todas as constantes, seletores e timeouts em um único lugar.
"""

import os
from typing import Final
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# ============================================================================
# CREDENCIAIS (via variáveis de ambiente - opcional para CLI)
# Se vazio, o app pedirá para o usuário preencher
# ============================================================================
USUARIO: Final[str] = os.getenv("USUARIO", "").strip()
SENHA: Final[str] = os.getenv("SENHA", "").strip()
CONDOMINIO_ID: Final[str] = os.getenv("CONDOMINIO_ID", "").strip()

# ============================================================================
# URLs
# ============================================================================
URL_PRINCIPAL: Final[str] = "https://servc9-1.webware.com.br/bin/gerenciamento/dpPainelWm.asp"

# ============================================================================
# TIMEOUTS (em segundos)
# ============================================================================
TIMEOUT_PADRAO: Final[int] = 10
TIMEOUT_ELEMENTO_CLICKAVEL: Final[int] = 10
TIMEOUT_ENTRE_ACOES: Final[float] = 1.5
TIMEOUT_ENTRE_BACKS: Final[float] = 0.5
TIMEOUT_APOS_BACKS: Final[float] = 2.0
TIMEOUT_APOS_CLIQUE: Final[float] = 1.5

# ============================================================================
# SELETORES CSS E XPATH
# ============================================================================
class Selectors:
    """Todos os seletores CSS/XPath centralizados"""
    
    # Login
    CAMPO_USUARIO_ID: Final[str] = "usuario"
    CAMPO_SENHA_ID: Final[str] = "senha"
    BOTAO_ENTRAR_XPATH: Final[str] = "//button[@type='submit' and contains(text(), 'ENTRAR')]"
    
    # Iframe
    IFRAME_PRINCIPAL_ID: Final[str] = "conteudoPrincipal"
    
    # Tabela de Unidades
    LINHAS_UNIDADES_XPATH: Final[str] = "//table//tr[.//a[img[@alt='Editar Cadastro']]]"
    TD_UNIDADE_XPATH: Final[str] = ".//td[contains(text(), '/Apart/')]"
    BOTAO_EDITAR_XPATH: Final[str] = ".//a[img[@alt='Editar Cadastro']]"
    
    # Vínculo
    LINK_VINCULO_TEXT: Final[str] = "Vínculo"
    
    # Formulário de Vínculo
    INPUT_CONDOMINIO_ID: Final[str] = "c"
    SELECT_UNIDADE_ID: Final[str] = "FormUnidade"
    
    # Botões de Ação
    BOTAO_ADICIONAR_XPATH: Final[str] = (
        "//button[@type='submit' and contains(text(), 'ENTRAR')] | "
        "//input[@type='button' and @value='Adicionar'] | "
        "//*[@value='Adicionar']"
    )

# ============================================================================
# DESENVOLVIMENTO E LOGGING
# ============================================================================
DEBUG: Final[bool] = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")
LOG_LEVEL: Final[str] = os.getenv("LOG_LEVEL", "INFO")

# ============================================================================
# ARQUIVO DE HISTÓRICO
# ============================================================================
ARQUIVO_HISTORICO: Final[str] = "historico_concluidas.txt"
PASTA_PRINTS: Final[str] = "prints_vinculos"

# ============================================================================
# VALIDAÇÃO
# ============================================================================
def validar_credenciais() -> bool:
    """Verifica se as credenciais estão configuradas"""
    if not USUARIO or not SENHA:
        return False
    return True


def validar_configuracao() -> tuple[bool, str]:
    """
    Valida se a configuração está completa.
    Retorna (válido, mensagem)
    """
    if not validar_credenciais():
        return False, "Credenciais não configuradas. Configure USUARIO e SENHA no arquivo .env"
    
    if not CONDOMINIO_ID:
        return False, "CONDOMINIO_ID não configurado no arquivo .env"
    
    return True, "Configuração válida"
