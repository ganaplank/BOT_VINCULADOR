"""
updater.py - Sistema de Atualização Automática via GitHub Releases
Bot Vinculador PRO
"""
import os
import sys
import subprocess
import threading
import urllib.request
import json


# Repositório no GitHub
GITHUB_API_URL = "https://api.github.com/repos/ganaplank/BOT_VINCULADOR/releases/latest"
EXE_ASSET_NAME = "BotVinculadorPRO.exe"


def _parse_version(version_str: str) -> tuple:
    """Converte 'v1.2.3' em (1, 2, 3) para comparação."""
    cleaned = version_str.lstrip("v").strip()
    try:
        return tuple(int(x) for x in cleaned.split("."))
    except Exception:
        return (0, 0, 0)


def verificar_update(current_version: str) -> dict | None:
    """
    Consulta a API do GitHub e retorna um dict com info da release mais recente
    se houver uma versão nova disponível. Retorna None caso contrário.

    Retorno (se houver update):
        {
            "version": "v1.1.0",
            "download_url": "https://...",
            "release_notes": "Notas da versão..."
        }
    """
    try:
        req = urllib.request.Request(
            GITHUB_API_URL,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "BotVinculadorPRO"}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode("utf-8"))

        latest_version = data.get("tag_name", "v0.0.0")
        release_notes = data.get("body", "")

        # Encontra o asset .exe
        download_url = None
        for asset in data.get("assets", []):
            if asset.get("name") == EXE_ASSET_NAME:
                download_url = asset.get("browser_download_url")
                break

        if download_url is None:
            return None  # Release existe mas sem o .exe esperado

        # Compara versões
        if _parse_version(latest_version) > _parse_version(current_version):
            return {
                "version": latest_version,
                "download_url": download_url,
                "release_notes": release_notes[:500] if release_notes else ""
            }

    except Exception as e:
        print(f"[Updater] Erro ao verificar update: {e}")

    return None


def _get_exe_path() -> str:
    """Retorna o caminho absoluto do executável atual."""
    if getattr(sys, "frozen", False):
        return sys.executable
    # Em modo dev, simula o caminho do exe
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), EXE_ASSET_NAME)


def baixar_e_aplicar_update(download_url: str, callback_progresso=None) -> bool:
    """
    Faz o download do novo .exe, substitui o atual e reinicia a aplicação.

    callback_progresso(percent: int) -> None  — chamado durante o download.
    Retorna True se aplicou com sucesso, False se houve erro.
    """
    exe_atual = _get_exe_path()
    exe_novo = exe_atual + ".new"
    exe_old = exe_atual.replace(".exe", ".old.exe")

    try:
        # Download com progress
        def _report(block_count, block_size, total_size):
            if callback_progresso and total_size > 0:
                percent = min(int(block_count * block_size * 100 / total_size), 100)
                callback_progresso(percent)

        urllib.request.urlretrieve(download_url, exe_novo, reporthook=_report)

        if callback_progresso:
            callback_progresso(100)

        # Verifica se o arquivo baixado é válido (deve ter pelo menos 1 MB)
        if os.path.getsize(exe_novo) < 1_000_000:
            os.remove(exe_novo)
            print("[Updater] Arquivo baixado parece inválido (muito pequeno).")
            return False

        # Renomeia o exe atual para .old e coloca o novo no lugar
        if os.path.exists(exe_atual):
            os.rename(exe_atual, exe_old)
        os.rename(exe_novo, exe_atual)

        # Inicia o novo executável e encerra o atual
        subprocess.Popen([exe_atual], close_fds=True)
        sys.exit(0)

    except Exception as e:
        print(f"[Updater] Erro ao aplicar update: {e}")
        # Rollback
        if os.path.exists(exe_new := exe_novo):
            try:
                os.remove(exe_new)
            except Exception:
                pass
        return False


def limpar_residuos():
    """Remove arquivos *.old.exe deixados por atualizações anteriores."""
    try:
        pasta = os.path.dirname(_get_exe_path())
        for arquivo in os.listdir(pasta):
            if arquivo.endswith(".old.exe"):
                caminho = os.path.join(pasta, arquivo)
                os.remove(caminho)
                print(f"[Updater] Arquivo residual removido: {arquivo}")
    except Exception as e:
        print(f"[Updater] Aviso ao limpar resíduos: {e}")
