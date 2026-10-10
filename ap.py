import os
import sqlite3
import datetime
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# Configuração da Página
st.set_page_config(
    page_title="AssistTec AI — Apoio Técnico e Orçamentos",
    page_icon="💻",
    layout="wide"
)

# ==========================================
# 1. BANCO DE DADOS RELACIONAL (SQLite)
# ==========================================
DB_NAME = "assisttec.db"

def inicializar_banco():
    """Cria as tabelas relacionais caso não existam."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela de Atendimentos / Análises
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS atendimentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_criacao TEXT,
            tipo_equipamento TEXT,
            fabricante TEXT,
            modelo TEXT,
            problema TEXT,
            parecer_ia TEXT
        )
    """)
    
    # Tabela de Orçamentos
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS orcamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            data_criacao TEXT,
            equipamento TEXT,
            mao_obra REAL,
            custos_extras REAL,
            total_pecas REAL,
            valor_total REAL
        )
    """)
    
    conn.commit()
    conn.close()

# Inicializa o banco ao carregar o script
inicializar_banco()


# ==========================================
# 2. VALIDADORES E REGRAS DE NEGÓCIO
# ==========================================
def validar_dados_entrada(equipamento: dict, problema: str) -> tuple[bool, str]:
    """Valida os campos obrigatórios da solicitação técnica."""
    if not equipamento.get("tipo"):
        return False, "O tipo de equipamento é obrigatório."
    if not equipamento.get("fabricante"):
        return False, "O fabricante é obrigatório."
    if not problema or len(problema.strip()) < 10:
        return False, "A descrição do problema relatado deve conter pelo menos 10 caracteres."
    return True, ""


# ==========================================
# 3. INTEGRAÇÃO COM A API DA GROQ
# ==========================================
def obter_cliente_groq():
    """Obtém o cliente da API da Groq utilizando secrets do Streamlit ou variáveis de ambiente."""
    try:
        api_key = st.secrets.get("GROQ_API_KEY", os.getenv("GROQ_API_KEY"))
    except Exception:
        api_key = os.getenv("GROQ_API_KEY")
        
    if not api_key:
        return None
    return Groq(api_key=api_key)

def gerar_analise_tecnica_groq(equipamento: dict, problema: str, sintomas: str, historico: str) -> str:
    """Envia os dados estruturados para o modelo Llama 3.3 via Groq API."""
    cliente = obter_cliente_groq()
    if not cliente:
        return "⚠️ Erro: Chave de API da Groq não configurada. Configure o secret `GROQ_API_KEY`."

    prompt_sistema = (
        "Você é o AssistTec AI, um assistente técnico sênior especializado em suporte a assistências técnicas de informática. "
        "Sua função é analisar solicitações de reparo e fornecer diretrizes técnicas estritamente fundamentadas.\n"
        "REGRAS ESTRITAS:\n"
        "1. Nunca invente diagnósticos definitivos sem evidências físicas.\n"
        "2. Identifique claramente dados ausentes ou informações que exijam testes.\n"
        "3. Destaque riscos elétricos, térmicos ou de perda de dados (backup).\n"
        "4. Ordene hipóteses por plausibilidade.\n"
        "5. Seja direto, técnico e estruturado em Markdown."
    )

    prompt_usuario = f"""
Dados do Equipamento:
- Tipo: {equipamento.get('tipo')}
- Fabricante/Modelo: {equipamento.get('fabricante')} {equipamento.get('modelo', 'N/A')}
- Idade: {equipamento.get('idade', 'N/A')}
- Processador / RAM / Armazenamento: {equipamento.get('processador', 'N/A')} | {equipamento.get('ram', 'N/A')} | {equipamento.get('armazenamento', 'N/A')}
- Estado Físico: {equipamento.get('estado_fisico', 'N/A')}

Problema Relatado:
{problema}

Sintomas Observados:
{sintomas}

Histórico Informado pelo Cliente:
{historico}

Elabore uma análise técnica estruturada contendo:
1. Resumo da solicitação.
2. Hipóteses técnicas ordenadas por plausibilidade.
3. Informações ausentes ou dúvidas relevantes.
4. Procedimentos recomendados de diagnóstico (não invasivos e seguros).
5. Possíveis peças, componentes ou serviços envolvidos.
"""

    try:
        completion = cliente.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.2,
            max_tokens=1200
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro de comunicação com a API da Groq: {str(e)}"


# ==========================================
# 4. CALCULADORA DE ORÇAMENTO DETERMINÍSTICA
# ==========================================
def calcular_orcamento(mao_obra: float, pecas: list, custos_extras: float) -> dict:
    """Calcula subtotais e total de forma determinística em Python."""
    total_pecas = sum(p.get("custo", 0.0) * p.get("qtd", 1) for p in pecas)
    total_geral = mao_obra + total_pecas + custos_extras
    return {
        "total_pecas": total_pecas,
        "mao_obra": mao_obra,
        "custos_extras": custos_extras,
        "total_geral": total_geral
    }


# ==========================================
# 5. INTERFACE STREAMLIT (UI)
# ==========================================
st.title("💻 AssistTec AI — Agente de Apoio a Orçamentos Técnicos")
st.markdown("Ferramenta de assistência preliminar para análise de equipamentos, diagnóstico estruturado, orçamento e persistência em banco relacional.")

with st.sidebar:
    st.header("⚙️ Configurações & Navegação")
    st.info(
        "**Recursos Ativos:**\n"
        "• Análise Inteligente via Groq (Llama 3.3)\n"
        "• Cálculo determinístico de custos\n"
        "• Banco de Dados SQLite integrado\n"
    )
    st.markdown("---")
    st.markdown("**Arquitetura:** Python, Streamlit, SQLite, Groq API.")

# Abas principais da interface
tab_analise, tab_orcamento, tab_historico = st.tabs([
    "🔍 Análise Técnica & IA", 
    "💰 Calculadora de Orçamento", 
    "📂 Histórico Salvo (Banco de Dados)"
])

with tab_analise:
    st.subheader("1. Coleta de Dados do Atendimento")
    
    with st.form("form_analise_tecnica"):
        col1, col2, col3 = st.columns(3)
        with col1:
            tipo_eq = st.selectbox("Tipo de Equipamento", ["Notebook", "Computador Desktop", "All-in-One", "Outro"])
            fabricante = st.text_input("Fabricante", placeholder="Ex: Dell, Lenovo, HP")
            modelo = st.text_input("Modelo", placeholder="Ex: Inspiron 15 3000")
        with col2:
            idade = st.selectbox("Idade Aproximada", ["Menos de 1 ano", "1 a 3 anos", "3 a 5 anos", "Mais de 5 anos", "Desconhecida"])
            processador = st.text_input("Processador", placeholder="Ex: Intel Core i5")
            ram = st.text_input("Memória RAM", placeholder="Ex: 8GB DDR4")
        with col3:
            armazenamento = st.text_input("Armazenamento", placeholder="Ex: SSD 256GB NVMe")
            estado_fisico = st.selectbox("Estado Físico Aparente", ["Excelente", "Marcas de uso leves", "Desgastado / Arranhado", "Danos estruturais / Quedas"])
            urgencia = st.selectbox("Urgência do Atendimento", ["Normal", "Urgente", "Crítica"])

        st.markdown("---")
        problema = st.text_area("Problema Relatado pelo Cliente *", placeholder="Ex: O notebook não liga ao pressionar o botão de energia, nem acende os LEDs.")
        sintomas = st.text_area("Sintomas Observados / Mensagens de Erro / Ruídos", placeholder="Ex: Cheiro sutil de queimado na região do conector de energia.")
        historico = st.text_area("Histórico Informado (Quedas, líquidos, atualizações)", placeholder="Ex: Cliente relatou que derramou água levemente no teclado há duas semanas.")

        submitted = st.form_submit_button("🚀 Gerar Análise Técnica com IA")

    if submitted:
        equipamento_dict = {
            "tipo": tipo_eq,
            "fabricante": fabricante,
            "modelo": modelo,
            "idade": idade,
            "processador": processador,
            "ram": ram,
            "armazenamento": armazenamento,
            "estado_fisico": estado_fisico
        }

        valido, msg_erro = validar_dados_entrada(equipamento_dict, problema)
        if not valido:
            st.error(f"⚠️ {msg_erro}")
        else:
            with st.spinner("Consultando o modelo de linguagem (Groq Llama 3.3)..."):
                parecer_ia = gerar_analise_tecnica_groq(equipamento_dict, problema, sintomas, historico)
                
            st.success("Análise gerada com sucesso!")
            st.subheader("📋 Parecer Técnico Preliminar e Recomendações")
            st.markdown(parecer_ia)
            
            # Botão para salvar no Banco Relacional
            if st.button("💾 Salvar Atendimento no Banco de Dados"):
                try:
                    conn = sqlite3.connect(DB_NAME)
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO atendimentos (data_criacao, tipo_equipamento, fabricante, modelo, problema, parecer_ia)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (str(datetime.datetime.now()), tipo_eq, fabricante, modelo, problema, parecer_ia))
                    conn.commit()
                    conn.close()
                    st.success("✅ Atendimento e parecer salvos com sucesso no banco SQLite!")
                except Exception as e:
                    st.error(f"Erro ao salvar no banco: {str(e)}")

            st.warning("⚠️ **Aviso Importante:** Esta análise é gerada por Inteligência Artificial com base estritamente nos dados informados.")

with tab_orcamento:
    st.subheader("2. Apoio à Elaboração de Orçamento Preliminar")
    st.markdown("Insira os valores para calcular e persistir o orçamento de forma relacional.")

    equipamento_orc = st.text_input("Identificação do Equipamento (Ex: Notebook Dell Inspiron)", placeholder="Dell Inspiron 15")
    
    col_orc1, col_orc2 = st.columns(2)
    
    with col_orc1:
        st.markdown("#### 🛠️ Mão de Obra e Custos")
        valor_mao_obra = st.number_input("Valor da Mão de Obra (R$)", min_value=0.0, value=150.0, step=10.0)
        custos_adicionais = st.number_input("Custos Adicionais / Logística (R$)", min_value=0.0, value=0.0, step=5.0)

    with col_orc2:
        st.markdown("#### 📦 Peças e Componentes")
        num_pecas = st.number_input("Quantidade de tipos de peças", min_value=0, max_value=5, value=1)
        
        pecas_lista = []
        for i in range(int(num_pecas)):
            st.markdown(f"**Peça {i+1}**")
            nome_p = st.text_input(f"Nome da Peça {i+1}", value="SSD 480GB SATA", key=f"peca_nome_{i}")
            custo_p = st.number_input(f"Custo Unitário (R$) {i+1}", min_value=0.0, value=180.0, key=f"peca_custo_{i}")
            qtd_p = st.number_input(f"Quantidade {i+1}", min_value=1, value=1, key=f"peca_qtd_{i}")
            pecas_lista.append({"nome": nome_p, "custo": custo_p, "qtd": qtd_p})

    if st.button("🧮 Calcular e Salvar Orçamento"):
        resultado_calc = calcular_orcamento(valor_mao_obra, pecas_lista, custos_adicionais)
        
        st.markdown("---")
        st.subheader("📊 Resumo Financeiro da Proposta Preliminar")
        col_res1, col_res2, col_res3, col_res4 = st.columns(4)
        col_res1.metric("Custo Total de Peças", f"R$ {resultado_calc['total_pecas']:.2f}")
        col_res2.metric("Mão de Obra", f"R$ {resultado_calc['mao_obra']:.2f}")
        col_res3.metric("Custos Adicionais", f"R$ {resultado_calc['custos_extras']:.2f}")
        col_res4.metric("Valor Total do Orçamento", f"R$ {resultado_calc['total_geral']:.2f}")
        
        # Salva o orçamento no banco relacional
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orcamentos (data_criacao, equipamento, mao_obra, custos_extras, total_pecas, valor_total)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                str(datetime.datetime.now()), 
                equipamento_orc or "Não especificado", 
                resultado_calc['mao_obra'], 
                resultado_calc['custos_extras'], 
                resultado_calc['total_pecas'], 
                resultado_calc['total_geral']
            ))
            conn.commit()
            conn.close()
            st.success("✅ Orçamento salvo com sucesso no banco de dados relacional!")
        except Exception as e:
            st.error(f"Erro ao salvar orçamento: {str(e)}")

with tab_historico:
    st.subheader("📂 Registros Armazenados no Banco Relacional (SQLite)")
    
    subtab_atd, subtab_orc = st.tabs(["Atendimentos Registrados", "Orçamentos Registrados"])
    
    with subtab_atd:
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, data_criacao, tipo_equipamento, fabricante, modelo, problema, parecer_ia FROM atendimentos ORDER BY id DESC")
            registros = cursor.fetchall()
            conn.close()
            
            if not registros:
                st.info("Nenhum atendimento salvo no banco de dados ainda.")
            else:
                for reg in registros:
                    with st.expander(f"ID #{reg[0]} — {reg[2]} ({reg[3]} {reg[4]}) em {reg[1][:16]}"):
                        st.write(f"**Problema Relatado:** {reg[5]}")
                        st.markdown(f"**Parecer da IA:**\n{reg[6]}")
        except Exception as e:
            st.error(f"Erro ao carregar atendimentos: {str(e)}")
            
    with subtab_orc:
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("SELECT id, data_criacao, equipamento, mao_obra, custos_extras, total_pecas, valor_total FROM orcamentos ORDER BY id DESC")
            orcamentos = cursor.fetchall()
            conn.close()
            
            if not orcamentos:
                st.info("Nenhum orçamento salvo no banco de dados ainda.")
            else:
                for orc in orcamentos:
                    with st.expander(f"Orçamento ID #{orc[0]} — {orc[2]} (Total: R$ {orc[6]:.2f}) em {orc[1][:16]}"):
                        st.write(f"**Mão de Obra:** R$ {orc[3]:.2f}")
                        st.write(f"**Custos Extras:** R$ {orc[4]:.2f}")
                        st.write(f"**Total de Peças:** R$ {orc[5]:.2f}")
                        st.markdown(f"### **Valor Total:** R$ {orc[6]:.2f}")
        except Exception as e:
            st.error(f"Erro ao carregar orçamentos: {str(e)}")