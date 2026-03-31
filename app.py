import streamlit as st
import pandas as pd
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Meddle BR", page_icon="🩺", layout="centered")

# LINKS DAS PLANILHAS
URL_JOGOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaYRZ8o_poW_YRuUke9vFxlmoezEp1S98ih7SCOeYgwzxlHMiJn9NcNrmXuLrkNC8ngnCb6Vth27PG/pub?output=csv"
URL_LISTA_GERAL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaYRZ8o_poW_YRuUke9vFxlmoezEp1S98ih7SCOeYgwzxlHMiJn9NcNrmXuLrkNC8ngnCb6Vth27PG/pub?gid=16863228&single=true&output=csv"

@st.cache_data(ttl=600)
def load_data(url, nome_tabela):
    try:
        # 'on_bad_lines' pula linhas com erros de pontuação (como a linha 29)
        df = pd.read_csv(url, sep=None, engine='python', encoding='utf-8', on_bad_lines='skip')
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {nome_tabela}: {e}")
        return pd.DataFrame()

# Interface Visual
st.title("Meddle BR 🩺")
st.write("Analise as dicas e escolha a hipótese diagnóstica correta.")

try:
    # CARREGAMENTO DOS DADOS (Aqui estava o erro: agora passamos os 2 argumentos)
    df_jogos = load_data(URL_JOGOS, "Calendário de Jogos")
    df_opcoes = load_data(URL_LISTA_GERAL, "Lista de Doenças")
    
    if not df_opcoes.empty:
        lista_doencas_completa = sorted(df_opcoes['doenca'].unique().tolist())
    else:
        lista_doencas_completa = []

    # Lógica da data
    hoje = datetime.now().strftime("%d/%m/%Y")
    df_jogos['data'] = df_jogos['data'].astype(str).str.strip()
    jogo_hoje = df_jogos[df_jogos['data'] == hoje]

    if jogo_hoje.empty:
        st.warning(f"Nenhum caso clínico para hoje ({hoje}).")
    else:
        dados = jogo_hoje.iloc[0]
        solucao = str(dados['doenca']).strip()
        dicas = [dados['dica1'], dados['dica2'], dados['dica3'], dados['dica4'], dados['dica5'], dados['dica6']]

        # Controle de estado
        if 'tentativas' not in st.session_state:
            st.session_state.tentativas = 0
        if 'terminou' not in st.session_state:
            st.session_state.terminou = False
        if 'venceu' not in st.session_state:
            st.session_state.venceu = False

        st.divider()
        # Mostra as dicas
        for i in range(st.session_state.tentativas + 1):
            if i < 6:
                st.info(f"**Dica {i+1}:** {dicas[i]}")

        # Interface de jogo
        if not st.session_state.terminou:
            palpite = st.selectbox("Selecione seu diagnóstico:", [""] + lista_doencas_completa)
            
            if st.button("Confirmar Hipótese"):
                if palpite == "":
                    st.warning("Selecione uma doença!")
                elif palpite.strip().lower() == solucao.lower():
                    st.session_state.terminou = True
                    st.session_state.venceu = True
                    st.rerun()
                else:
                    st.session_state.tentativas += 1
                    if st.session_state.tentativas >= 6:
                        st.session_state.terminou = True
                        st.session_state.venceu = False
                    else:
                        st.error("Incorreto! Nova dica liberada.")
                    st.rerun()

        # Fim de jogo
        if st.session_state.terminou:
            st.divider()
            if st.session_state.venceu:
                st.balloons()
                st.success(f"🔥 Acertou! O diagnóstico era **{solucao}**.")
            else:
                st.error(f"Fim das tentativas. O diagnóstico era: **{solucao}**.")

except Exception as e:
    st.error(f"Erro crítico no sistema: {e}")
