import streamlit as st
import pandas as pd
from datetime import datetime

# 1. Configuração da página
st.set_page_config(page_title="Meddle BR", page_icon="🩺", layout="centered")

# 2. Links das Planilhas
URL_JOGOS = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaYRZ8o_poW_YRuUke9vFxlmoezEp1S98ih7SCOeYgwzxlHMiJn9NcNrmXuLrkNC8ngnCb6Vth27PG/pub?output=csv"
URL_LISTA_GERAL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSaYRZ8o_poW_YRuUke9vFxlmoezEp1S98ih7SCOeYgwzxlHMiJn9NcNrmXuLrkNC8ngnCb6Vth27PG/pub?gid=16863228&single=true&output=csv"

@st.cache_data(ttl=60) # Atualiza mais rápido (a cada 1 minuto) para testes
def load_data(url, nome_tabela):
    try:
        # 'utf-8-sig' remove caracteres invisíveis que o Google Sheets às vezes coloca
        df = pd.read_csv(url, sep=None, engine='python', encoding='utf-8-sig', on_bad_lines='skip')
        
        # LIMPEZA AGRESSIVA DE COLUNAS: tira espaços, põe minúsculo e remove acentos
        df.columns = [str(c).strip().lower().replace('ç','c').replace('ã','a') for c in df.columns]
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {nome_tabela}: {e}")
        return pd.DataFrame()

# Interface Visual
st.title("Meddle BR 🩺")
st.write("Analise as dicas e escolha a hipótese diagnóstica.")

try:
    df_jogos = load_data(URL_JOGOS, "Calendário de Jogos")
    df_opcoes = load_data(URL_LISTA_GERAL, "Lista de Doenças")
    
    # Validação da Coluna 'doenca' na lista de opções
    if not df_opcoes.empty and 'doenca' in df_opcoes.columns:
        lista_doencas_completa = sorted(df_opcoes['doenca'].dropna().astype(str).unique().tolist())
    else:
        # Se der erro, mostra ao desenvolvedor o que o código está vendo
        st.error("Coluna 'doenca' não encontrada na planilha de lista.")
        if not df_opcoes.empty: st.write(f"Colunas detectadas: {list(df_opcoes.columns)}")
        lista_doencas_completa = []

    # Lógica do Jogo de Hoje
    hoje = datetime.now().strftime("%d/%m/%Y")
    df_jogos['data'] = df_jogos['data'].astype(str).str.strip()
    jogo_hoje = df_jogos[df_jogos['data'] == hoje]

    if jogo_hoje.empty:
        st.warning(f"Sem caso clínico para hoje ({hoje}).")
    else:
        dados = jogo_hoje.iloc[0]
        solucao = str(dados['doenca']).strip()
        dicas = [dados['dica1'], dados['dica2'], dados['dica3'], dados['dica4'], dados['dica5'], dados['dica6']]

        if 'tentativas' not in st.session_state:
            st.session_state.tentativas = 0
        if 'terminou' not in st.session_state:
            st.session_state.terminou = False
        if 'venceu' not in st.session_state:
            st.session_state.venceu = False

        st.divider()
        for i in range(st.session_state.tentativas + 1):
            if i < 6: st.info(f"**Dica {i+1}:** {dicas[i]}")

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
                    st.rerun()

        if st.session_state.terminou:
            st.divider()
            if st.session_state.venceu:
                st.balloons()
                st.success(f"🔥 Acertou! O diagnóstico era **{solucao}**.")
            else:
                st.error(f"Fim de jogo! O diagnóstico era: **{solucao}**.")

except Exception as e:
    st.error(f"Ocorreu um erro: {e}")

# Botão secreto para você limpar o cache se mudar algo na planilha
if st.sidebar.button("🔄 Atualizar Dados (Limpar Cache)"):
    st.cache_data.clear()
    st.rerun()
