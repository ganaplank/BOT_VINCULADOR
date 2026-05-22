# Bot Vinculador - Documentação

## ⚙️ Instalação de Dependências

Instale as dependências necessárias:

```bash
pip install -r requirements.txt
```

## 🚀 Como Usar

### Via Interface Gráfica (Recomendado)

1. Abra o app:
```bash
python app_vinculador.py
```

2. **Preencha seus dados:**
   - **Usuário:** Seu login no sistema Sell
   - **Senha:** Sua senha no sistema Sell
   - **Condomínio:** O ID do condomínio a processar

3. **Navegue até a tabela** no sistema Sell e clique em "Ler Unidades da Tela"

4. **Selecione as unidades** que deseja processar e clique em "INICIAR ROBÔ"

### Via Linha de Comando

1. Configure credenciais no arquivo `.env` (opcional):
```bash
cp .env.example .env
# Edite .env com suas credenciais (opcional)
```

2. Execute o bot:
```bash
python bot.py
```

3. O programa pedirá:
   - Usuário (se não estiver no .env)
   - Senha (se não estiver no .env)
   - ID do Condomínio

## 📝 O que Preencher

### Na Interface Gráfica

**Aba "Operação do Robô":**

- **Usuário:** Seu login/CPF para acessar o sistema
- **Senha:** Sua senha do sistema
- **Condomínio:** O número/ID do condomínio

**Exemplo:**
- Usuário: `VICTOR_NORONHA`
- Senha: `Sua@senha123`
- Condomínio: `577`

### Informações Importantes

❌ **NÃO existem valores pré-configurados** - cada usuário preenche com seus dados  
✅ **Totalmente seguro** - os dados não são salvos em arquivo  
✅ **Uso único** - dados são esquecidos após o app fechar  

## 📂 Estrutura

- `app_vinculador.py` - Interface gráfica (GUI)
- `bot.py` - Versão de linha de comando (CLI)
- `config.py` - Configurações do sistema
- `logger.py` - Sistema de logging
- `selenium_bot.py` - Engine Selenium
- `.env.example` - Exemplo de arquivo de configuração

## ✨ Funcionalidades

- ✅ Login automático
- ✅ Leitura de unidades da tabela
- ✅ Processamento em lote
- ✅ Captura de prints de comprovante
- ✅ Histórico de unidades processadas
- ✅ Visualização de prints
- ✅ Tratamento robusto de erros

## 🔍 Histórico e Prints

Os prints são salvos na memória durante a sessão e podem ser:
- Visualizados na aba "Histórico"
- Baixados para seu computador
- Excluídos da memória

O histórico de unidades concluídas fica em: `historico_concluidas.txt`

## ⚠️ Troubleshooting

**"Erro ao abrir site"**
- Verifique sua conexão com internet
- Verifique se o site está online

**"Nenhuma unidade encontrada"**
- Você navegou até a tabela correta?
- Filtrou o condomínio antes de clicar em "Ler Unidades"?

**"Erro de autenticação"**
- Verifique se seu usuário e senha estão corretos
- Verifique se sua conta não está bloqueada

## 📞 Suporte

Para problemas, verifique o arquivo de log: `logs/bot_YYYYMMDD_HHMMSS.log`

---

**Versão:** 2.0 (Refatorada)  
**Status:** ✅ Pronto para produção
