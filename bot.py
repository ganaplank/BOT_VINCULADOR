"""
Bot simples em linha de comando para vinculação automática.
Versão refatorada usando SeleniumBot.
"""

from typing import List
from config import USUARIO, SENHA, validar_credenciais
from selenium_bot import SeleniumBot, SeleniumBotError
from logger import get_logger

log = get_logger("bot_cli")


def menu_opcoes_processamento(unidades: List[str]) -> List[str]:
    """
    Menu interativo para escolher quais unidades processar.
    
    Args:
        unidades: Lista de todas as unidades disponíveis
    
    Returns:
        Lista de unidades selecionadas para processar
    """
    print("\n" + "="*60)
    print("O QUE VOCÊ QUER FAZER COM ESSA LISTA?")
    print("[1] Processar TODAS na ordem normal")
    print("[2] Processar TODAS de trás pra frente (Invertido)")
    print("[3] Filtrar por texto (ex: digitar '0019' para pegar só esse bloco/andar)")
    print("[4] Escolher números específicos da lista acima (ex: 1, 2, 5, 10)")
    print("="*60)
    
    opcao = input("Digite o número da opção (1/2/3/4): ").strip()
    
    if opcao == '1':
        return unidades
    elif opcao == '2':
        return unidades[::-1]
    elif opcao == '3':
        filtro = input("Digite o texto que deseja filtrar: ").strip()
        filtradas = [u for u in unidades if filtro in u]
        if not filtradas:
            print(f"Nenhuma unidade encontrada com o filtro '{filtro}'")
            return []
        return filtradas
    elif opcao == '4':
        try:
            escolhas = input("Digite os números das unidades separados por vírgula (ex: 1, 5, 12): ")
            indices = [int(x.strip()) - 1 for x in escolhas.split(',') if x.strip().isdigit()]
            selecionadas = [unidades[i] for i in indices if 0 <= i < len(unidades)]
            if not selecionadas:
                print("Nenhuma unidade válida selecionada")
                return []
            return selecionadas
        except (ValueError, IndexError) as e:
            print(f"Erro ao processar seleção: {e}")
            return []
    else:
        print("Opção inválida")
        return []


def main():
    """Função principal"""
    
    # Validar configurações
    valido, msg = validar_credenciais()
    if not valido:
        log.error(msg)
        print(f"\n❌ Erro: {msg}")
        print("\nCrie um arquivo .env com suas credenciais:")
        print("  USUARIO=seu_usuario")
        print("  SENHA=sua_senha")
        return
    
    log.info("=" * 60)
    log.info("Iniciando Bot Vinculador")
    log.info("=" * 60)
    
    try:
        # Inicializar bot
        with SeleniumBot(USUARIO, SENHA) as bot:
            
            # Abrir site
            bot.abrir_site()
            
            # Fazer login
            print("\n[BOT] Iniciando login automático...")
            bot.fazer_login()
            print(" -> Login realizado com sucesso! Aguardando o sistema carregar...")
            
            # Instruções ao usuário
            print("\n" + "="*60)
            print("1. Navegue até a tela da tabela com as unidades.")
            print("2. Se precisar, filtre o condomínio para que os cadastros apareçam.")
            print("3. Quando a tabela estiver pronta na tela, volte aqui.")
            print("="*60)
            input("--> Aperte ENTER aqui no terminal para o bot ler as unidades da tela... ")
            
            # Ler unidades
            print("\nLendo unidades disponíveis na tela...")
            unidades = bot.ler_unidades_tabela()
            
            if not unidades:
                print("Nenhuma unidade encontrada. Verifique se você está na tela certa.")
                return
            
            # Listar unidades encontradas
            print(f"\nEncontradas {len(unidades)} unidades:")
            for idx, unidade in enumerate(unidades, 1):
                print(f"  [{idx}] {unidade}")
            
            # Menu de seleção
            unidades_alvo = menu_opcoes_processamento(unidades)
            
            if not unidades_alvo:
                print("Nenhuma unidade selecionada. Encerrando...")
                return
            
            # Pedir condomínio
            condominio_id = input("\n📝 Digite o ID do Condomínio: ").strip()
            if not condominio_id:
                print("❌ ID do condomínio não pode estar vazio!")
                return
            
            print(f"\n[BOT] Iniciando processamento de {len(unidades_alvo)} unidades...")
            print("="*60)
            
            # Processar cada unidade
            sucesso_count = 0
            erro_count = 0
            
            for i, unidade in enumerate(unidades_alvo, 1):
                print(f"\n[{i}/{len(unidades_alvo)}] Processando: {unidade}")
                sucesso, mensagem = bot.processar_unidade(unidade, condominio_id)
                
                if sucesso:
                    print(f" ✅ {mensagem}")
                    sucesso_count += 1
                else:
                    print(f" ❌ {mensagem}")
                    erro_count += 1
            
            # Resumo final
            print("\n" + "="*60)
            print("RESUMO DO PROCESSAMENTO")
            print("="*60)
            print(f"✅ Sucesso: {sucesso_count}")
            print(f"❌ Erros: {erro_count}")
            print(f"📊 Total: {len(unidades_alvo)}")
            print("="*60)
            
            if erro_count == 0:
                print("\n✨ Processo finalizado com sucesso!")
            else:
                print(f"\n⚠️  Processo finalizado com {erro_count} erro(s)")
            
    except SeleniumBotError as e:
        log.error(f"Erro do bot: {e}")
        print(f"\n❌ Erro: {e}")
        return
    except KeyboardInterrupt:
        log.warning("Processo interrompido pelo usuário")
        print("\n\n⚠️  Processo interrompido pelo usuário")
        return
    except Exception as e:
        log.error(f"Erro inesperado: {e}")
        print(f"\n❌ Erro inesperado: {e}")
        return
    finally:
        log.info("Bot finalizado")


if __name__ == "__main__":
    main()