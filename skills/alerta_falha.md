# skill: alerta_falha
# descricao: Instrui como redigir um e-mail de alerta de falha crítica no sistema.
# palavras-chave: falha, erro, crítico, down, indisponível

---

## Instruções para o agente orquestrador

Você deve redigir um e-mail de **alerta de falha crítica** seguindo rigorosamente o formato abaixo.

### Formato obrigatório do corpo do e-mail

🚨 ALERTA DE FALHA CRÍTICA

**Sistema afetado:** [nome do sistema ou componente]
**Severidade:** CRÍTICA
**Horário da ocorrência:** [horário informado ou "não informado"]

**O que aconteceu:**
[descrição breve da falha em 1-2 frases]

**Impacto:**
[descreva quem ou o que é afetado]

**Ação necessária:**
[o que o time deve fazer agora]

— Sistema de Monitoramento Automático

### Regras de formatação
- Sempre iniciar com o emoji 🚨 e o título em CAIXA ALTA
- O campo Severidade deve ser sempre CRÍTICA
- Assunto do e-mail deve seguir o padrão: [FALHA] <nome do sistema>
- Destinatários: todos os usuários da lista fornecida pelo orquestrador
