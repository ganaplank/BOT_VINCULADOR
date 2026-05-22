# Contexto do Projeto para Assistente IA (Handoff)

Este arquivo foi criado para transferir o contexto exato do projeto para outra instância de Inteligência Artificial. **[Assistente IA: Leia este documento cuidadosamente antes de prosseguir com qualquer código].**

## 1. Visão Geral do Projeto
- **Nome:** Bot Vinculador PRO
- **Tecnologias:** Python (Backend), Eel (Integração Web/Desktop), HTML/CSS/JS puro (Frontend), Selenium (Automação Web), PyInstaller (Build do Executável).
- **Objetivo:** O aplicativo automatiza a vinculação e leitura de unidades em um portal web imobiliário/condominial. Ele loga na plataforma, extrai dados das unidades na tela e usa um robô em segundo plano para fazer marcações/vínculos de unidades agregadas de forma automática.

## 2. Arquitetura da Interface (Frontend)
O projeto passou recentemente por uma grande refatoração estrutural e estética.
- **Estilo Visual:** *Flat Design* Corporativo (sem `backdrop-filter`, sem degradês e sem elementos gamers). Cores sólidas (Slate/Gray) no Modo Escuro e fundos de altíssimo contraste no Modo Claro. Tema alternável via botão ☀️/🌙.
- **Layout:** Dashboard de duas colunas (`.dashboard-grid`). 
  - *Coluna Esquerda:* Controles estáticos de formulário, login e botões de ação ("Ler Unidades", "Iniciar Robô").
  - *Coluna Direita:* Exibição de dados em tela cheia, com filtros horizontais no topo e área de scroll para as checkboxes de unidades.
- **Barra Lateral (Sidebar):** Fica oculta por padrão (com `width: 0`) e pode ser chamada usando o botão de Menu (☰) no topo da tela (`.main-header`).

## 3. Estado Atual (O que já está pronto)
- Comunicação bidirecional Eel implementada e funcionando (logs e updates em tempo real do Python para o JS).
- Filtros por Nome/Número, Bloco e Faixa Numérica 100% funcionais na interface.
- Geração e salvamento de Prints (Comprovantes de vínculo) no diretório local.
- Build automatizado via PyInstaller (`app_vinculador.spec`).
- Subida concluída para repositório GitHub (`https://github.com/ganaplank/BOT_VINCULADOR`).

## 4. Próximo Passo (Imediato)
A próxima tarefa que o usuário deseja implementar é o **Sistema de Auto-Update (Atualizador Automático)** via GitHub Releases.

### Detalhes da Implementação Pendente (Auto-Updater):
1. **Verificação de Versão:** Ao iniciar, o backend Python deve bater na API do GitHub (`api.github.com/repos/ganaplank/BOT_VINCULADOR/releases/latest`) de forma assíncrona.
2. **Notificação (Eel):** Se a versão no GitHub for maior que a constante local (ex: `CURRENT_VERSION = 'v1.0.0'`), enviar evento para o frontend exibir um modal corporativo na UI.
3. **Download:** Se o usuário aceitar, o Python faz o download do binário de Lançamento (Asset `.exe`) da release respectiva usando a biblioteca `requests` ou nativa. Mostrar tela de *Loading* de progresso na UI.
4. **Substituição e Restart:** 
   - O aplicativo atual usa `os.rename()` para renomear o `.exe` em execução para algo como `BotVinculadorPRO.old.exe`.
   - O novo arquivo assume o nome padrão `BotVinculadorPRO.exe`.
   - Lança um subprocesso com o novo executável e chama `sys.exit()` no antigo.
   - *Nota de Boot:* O `app_vinculador.py` deverá possuir uma verificação logo no início da execução que busque e delete (via `os.remove`) qualquer arquivo `*.old.exe` esquecido na pasta, limpando o rastro da atualização anterior.

---
**[Instrução para a IA de Casa]:** O usuário deseja começar imediatamente a implementar o sistema de Auto-Update descrito no passo 4. Verifique a estrutura atual nos arquivos `main.js`, `app_vinculador.py` e crie as funções necessárias.

## 5. Tarefas Secundárias Futuras (Aviso de Antivírus)
O usuário relatou que o executável gerado pelo PyInstaller está disparando avisos de falso positivo no Windows Defender ("vírus"). 
- **Solução Definida:** Compilar o *bootloader* do PyInstaller localmente na máquina do usuário para alterar o hash do binário.
- **Instrução para a IA:** Quando o usuário solicitar, baixe o source do PyInstaller, certifique-se de que há um compilador C instalado (como MinGW/GCC) e execute o processo de compilação do bootloader antes de gerar o próximo build da aplicação.
