# 💻 AssistTec AI — Agente Inteligente de Apoio a Orçamentos Técnicos

## 1. Descrição do Projeto
O **AssistTec AI** é uma aplicação web interativa desenvolvida em Python e Streamlit que atua como um assistente técnico inteligente para oficinas e assistências de reparo de computadores e notebooks. O sistema auxilia profissionais na análise preliminar de solicitações de serviço, estrutura hipóteses diagnósticas com o suporte da Inteligência Artificial (API da Groq / Llama 3.3), calcula orçamentos de forma determinística e armazena os dados de forma persistente utilizando um banco de dados relacional (SQLite).

## 2. Problema que Resolve
Muitas pequenas assistências técnicas enfrentam dificuldades para organizar o diagnóstico inicial de equipamentos complexos e calcular orçamentos de peças e mão de obra de forma rápida e transparente. O AssistTec AI organiza esses dados, reduz erros de estimativa e fornece uma base técnica fundamentada antes da intervenção física.

## 3. Objetivo
Fornecer uma ferramenta funcional para:
- Coletar dados detalhados de equipamentos e defeitos.
- Gerar análises e hipóteses técnicas estruturadas via IA.
- Calcular subtotais e custos totais com precisão aritmética em Python.
- Persistir atendimentos e orçamentos em banco relacional.

## 4. Tecnologias Utilizadas
- **Python 3.10+**: Lógica de negócio, validações e cálculos.
- **Streamlit**: Interface web interativa e responsiva.
- **Groq API (Llama 3.3)**: Síntese de pareceres técnicos e hipóteses.
- **SQLite**: Banco de dados relacional embutido para persistência de histórico.
- **Git & GitHub**: Versionamento de código.

## 5. Arquitetura e Estrutura de Pastas
assisttec-ai/
├── app.py              # Aplicação principal (Interface, lógica, banco e IA)
├── prompt.md           # Prompt original utilizado para concepção do agente
├── requirements.txt    # Dependências do projeto
├── .env.example        # Exemplo de configuração de variáveis de ambiente
├── .gitignore          # Arquivos ignorados pelo Git
└── README.md           # Documentação técnica