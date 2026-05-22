# Bot Vinculador PRO — Guia de Instalação e Uso

## ✅ O que você vai precisar

- Computador com **Windows 10 ou 11** (64 bits)
- **Google Chrome instalado** (versão atual — o bot atualiza o driver automaticamente)
- O arquivo `BotVinculadorPRO.exe`

Só isso. Não precisa instalar Python, nada de código, nada de configuração.

---

## 📥 Como instalar

1. Receba o arquivo `BotVinculadorPRO.exe` enviado pelo seu gestor
2. Salve em qualquer pasta do seu computador (ex: `C:\Ferramentas\`)
3. Dê duplo clique para abrir

> ⚠️ **Alerta do Windows Defender / SmartScreen**
> Na primeira vez que abrir, o Windows pode exibir a tela azul "O Windows protegeu seu computador".
> Isso é normal para executáveis sem assinatura digital.
> Clique em **"Mais informações"** → **"Executar assim mesmo"**.

---

## 🚀 Como usar (passo a passo)

### Passo 1 — Preencha suas credenciais

Ao abrir o app, preencha os campos:
- **Usuário:** seu login no sistema Sell (ex: `VICTOR_NORONHA`)
- **Senha:** sua senha do sistema Sell
- **Condomínio:** o número/ID do condomínio que vai processar (ex: `577`)

Depois clique em **"Abrir Sistema e Logar"**. O Chrome vai abrir automaticamente e fazer login para você.

### Passo 2 — Navegue até a tabela

Com o Chrome aberto e logado, navegue no sistema Sell até a tabela de unidades do condomínio.
Filtre o condomínio se necessário para aparecerem as unidades na tela.

### Passo 3 — Leia as unidades

Clique em **"Ler Unidades da Tela"**. O bot vai varrer a tabela e listar todas as unidades encontradas.

- Unidades já processadas aparecem com ✅
- Unidades novas já ficam pré-selecionadas automaticamente

### Passo 4 — Selecione e execute

- Use **"Selecionar Todas"** ou clique individualmente nas unidades que quer processar
- Marque (ou desmarque) a opção **"Incluir unidades agregadas no vínculo"** conforme necessário
- Clique em **"▶ INICIAR ROBÔ"**

O bot vai processar cada unidade automaticamente. Acompanhe o progresso no painel "Status da Operação".

### Passo 5 — Confira as evidências

Após o processamento, vá para a aba **"📋 Visualizador de Prints e Histórico"**:
- Clique em qualquer unidade para ver o print de comprovante
- Use **"💾 Baixar para o PC"** para salvar o print como imagem
- O histórico é salvo automaticamente e persiste entre sessões

---

## 🔒 Segurança

- Suas credenciais **não são salvas** em nenhum arquivo — são esquecidas ao fechar o app
- O histórico de unidades processadas fica salvo em `historico_concluidas.txt` na mesma pasta do `.exe`
- Nenhuma informação é enviada para servidores externos

---

## ❓ Problemas comuns

| Problema | O que fazer |
|----------|-------------|
| Chrome não abre | Verifique se o Google Chrome está instalado |
| "Erro ao abrir sistema" | Verifique sua conexão com a internet e se o site da Sell está online |
| "Nenhuma unidade encontrada" | Confirme que você navegou até a tabela correta e filtrou o condomínio |
| "Erro de autenticação" | Verifique usuário e senha — tente logar manualmente no site |
| Bot travou no meio | Clique em **"⏹ PARAR ROBÔ"**, feche o Chrome manualmente e recomece |

---

## 📞 Suporte interno

Em caso de dúvidas, entre em contato com o responsável pela ferramenta na empresa.

---

*Bot Vinculador PRO v2.0 — Automação de Vínculo de Unidades — Sell Administradora*
