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
- **Sistema de Auto-Update (Atualizador Automático) via GitHub Releases** integrado e 100% funcional. Ao iniciar, o app consulta o GitHub Releases em background e oferece atualização via modal na UI com barra de progresso.
- **Mapeamento de Condomínio por Bloco (Multi-Condo)**: O campo centralizado de condomínio foi removido. Ao ler as unidades, os blocos são identificados e mapeados para os respectivos condomínios diretamente na interface pelo usuário. O robô aplica o ID correto durante o processamento de cada bloco.
- Build compilado com sucesso via PyInstaller (`app_vinculador.spec`).
- Subida concluída para repositório GitHub (`https://github.com/ganaplank/BOT_VINCULADOR`).

---

## 5. Tarefas Secundárias Futuras (Aviso de Antivírus)
O usuário relatou que o executável gerado pelo PyInstaller está disparando avisos de falso positivo no Windows Defender ("vírus"). 
- **Solução Definida:** Compilar o *bootloader* do PyInstaller localmente na máquina do usuário para alterar o hash do binário.
- **Instrução para a IA:** Quando o usuário solicitar, baixe o source do PyInstaller, certifique-se de que há um compilador C instalado (como MinGW/GCC) e execute o processo de compilação do bootloader antes de gerar o próximo build da aplicação.

## 6. Lista de Tarefas Ativas (Checklist)
*(Esta seção é atualizada em tempo real conforme novas tarefas são solicitadas e concluídas. Em caso de queda da IA, a próxima deve continuar a partir do primeiro item em aberto `[ ]`)*

- `[x]` Investigar e corrigir botões sem resposta (Abrir Sistema, Ver Log, etc.):
  - `[x]` Comparar `index.html` e `main.js` atuais com o backup `BACKUP_20260525_0948` (ou anterior)
  - `[x]` Identificar elementos ID quebrados ou listeners desvinculados no JavaScript
  - `[x]` Corrigir `index.html` e `main.js` para restabelecer a funcionalidade original
  - `[x]` Compilar novo executável (`BotVinculadorPRO.exe`) e testar/comitar

- `[x]` Implementar "Finalizar sessão atual" e Reestruturação de Layout:
  - `[x]` Adicionar `#session_bar` e reposicionar contêineres em `index.html`
  - `[x]` Adicionar estilos de transição CSS para a classe `.session-active` e layout flexível em `style.css`
  - `[x]` Implementar callbacks de login/logout, botão de finalizar sessão e manipulação de classes no `main.js`
  - `[x]` Criar e expor `finalizar_sessao` no `app_vinculador.py` para fechar o Selenium
  - `[x]` Compilar novo executável (`BotVinculadorPRO.exe`) e comitar no GitHub

- `[x]` Corrigir quebra/overflow da interface pós-login (ações rápidas e botões ocultados):
  - `[x]` Ajustar estilos de flexbox para `.main-operational-layout` e `.checklist-area` com `min-height: 0`
  - `[x]` Mudar `.list-container` de altura fixa de 200px para `flex: 1` e `min-height: 0`
  - `[x]` Limitar altura de `#mapeamento_blocos` com `max-height: 100%` e scroll vertical
  - `[x]` Compilar novo executável (`BotVinculadorPRO.exe`) e testar/comitar no GitHub

- `[ ]` Mudar layout para rolagem de página natural (estilo website):
  - `[ ]` Alterar `.app-main` em `style.css` para ter scroll vertical (`overflow-y: auto`)
  - `[ ]` Ajustar `web/index.html` removendo a classe `h-100` do card de seleção
  - `[ ]` Remover limites de altura de flexbox e permitir que `.list-container` e `#mapeamento_blocos` cresçam naturalmente
  - `[ ]` Compilar novo executável (`BotVinculadorPRO.exe`) e testar/comitar no GitHub


