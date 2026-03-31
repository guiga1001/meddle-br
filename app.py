
import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Meddle BR", page_icon="🩺", layout="centered")

# Link da sua planilha (que você me enviou)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaYRZ8o_poW_YRuUke9vFxlmoezEp1S98ih7SCOeYgwzxlHMiJn9NcNrmXuLrkNC8ngnCb6Vth27PG/pub?output=csv"

@st.cache_data(ttl=600)
def load_data():
    # O comando 'sep=None' faz o Python descobrir sozinho se é vírgula ou ponto e vírgula
    df = pd.read_csv(SHEET_URL, sep=None, engine='python', encoding='utf-8')
    # Limpa espaços extras nos nomes das colunas, caso existam
    df.columns = df.columns.str.strip()
    return df

# Interface Visual
st.title("Meddle BR 🩺")
st.write("Tente adivinhar o diagnóstico com base nas dicas clínicas.")

try:
    df = load_data()
    hoje = datetime.now().strftime("%d/%m/%Y")
    
    # Filtra a linha do dia de hoje
    jogo_hoje = df[df['data'] == hoje]

    if jogo_hoje.empty:
        st.warning("Opa! Não encontrei o diagnóstico para o dia de hoje na planilha. Verifique a coluna 'data'.")
    else:
        dados = jogo_hoje.iloc[0]
        solucao = dados['doenca']
        dicas = [dados['dica1'], dados['dica2'], dados['dica3'], dados['dica4'], dados['dica5'], dados['dica6']]
        
        # Lista de sugestões para o usuário (todas as doenças da sua planilha)
        lista_doencas = sorted(df['doenca'].unique().tolist())

        # Controle de estado (sessão)
        if 'tentativas' not in st.session_state:
            st.session_state.tentativas = 0
        if 'terminou' not in st.session_state:
            st.session_state.terminou = False

        # Exibição das dicas
        for i in range(st.session_state.tentativas + 1):
            if i < 6:
                st.info(f"**Dica {i+1}:** {dicas[i]}")

        # Interface de palpite
        if not st.session_state.terminou:
            palpite = st.selectbox("Escolha seu diagnóstico:", [""] + lista_doencas, index=0)
            
            if st.button("Enviar Palpite"):
                if palpite == "":
                    st.warning("Selecione uma doença!")
                elif palpite == solucao:
                    st.session_state.terminou = True
                    st.session_state.venceu = True
                    st.rerun()
                else:
                    st.session_state.tentativas += 1
                    if st.session_state.tentativas >= 6:
                        st.session_state.terminou = True
                        st.session_state.venceu = False
                    st.rerun()

        # Resultado Final
        if st.session_state.terminou:
            if st.session_state.venceu:
                st.balloons()
                st.success(f"🔥 Acertou! O diagnóstico era **{solucao}**.")
            else:
                st.error(f"Fim de jogo! O diagnóstico correto era: **{solucao}**.")
            
            if st.button("Jogar novamente amanhã"):
                pass # O Streamlit reinicia automaticamente ao carregar

except Exception as e:
    st.error(f"Erro detalhado: {e}")
