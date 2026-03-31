import streamlit as st
import pandas as pd
from datetime import datetime
import time
import re

# 1. Configuração da página
st.set_page_config(page_title="Meddle BR", page_icon="🩺", layout="centered")

# --- SEUS LINKS ---
ID_DA_PLANILHA = "1QIDAaiVyRltk6xkeBdMvLHf3xaODuBs9DWCpm1kjmZs"
GID_LISTA = "16863228" 

URL_JOGOS_BASE = f"https://docs.google.com/spreadsheets/d/{ID_DA_PLANILHA}/export?format=csv"
URL_LISTA_BASE = f"https://docs.google.com/spreadsheets/d/{ID_DA_PLANILHA}/export?format=csv&gid={GID_LISTA}"

# Função para criar o efeito visual de riscado usando Unicode
def riscar(texto):
    return ''.join([char + '\u0336' for char in texto])

def normalizar(texto):
    return re.sub(r'[^a-zA-Z0-9]', '', str(texto)).lower()

@st.cache_data(ttl=1)
def load_data(url_base, nome_tabela):
    try:
        cache_buster = f"&t={int(time.time())}"
        url_final = url_base + cache_buster
        df = pd.read_csv(url_final, sep=',', encoding='utf-8-sig', on_bad_lines='skip')
        if len(df.columns) == 1:
            df = pd.read_csv(url_final, sep=';', encoding='utf-8-sig', on_bad_lines='skip')
        df.columns = [str(c).strip().lower().replace('ç','c').replace('ã','a') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {nome_tabela}: {e}")
        return pd.DataFrame()

st.title("Meddle BR 🩺")

try:
    df_jogos = load_data(URL_JOGOS_BASE, "Calendário de Jogos")
    df_opcoes = load_data(URL_LISTA_BASE, "Lista de Doenças")
    
    if 'tentativas' not in st.session_state: st.session_state.tentativas = 0
    if 'terminou' not in st.session_state: st.session_state.terminou = False
    if 'venceu' not in st.session_state: st.session_state.venceu = False
    if 'chutes_feitos' not in st.session_state: st.session_state.chutes_feitos = []

    # Lista completa vinda da planilha
    if not df_opcoes.empty and 'doenca' in df_opcoes.columns:
        lista_completa = sorted(df_opcoes['doenca'].dropna().astype(str).unique().tolist())
    else:
        lista_completa = []

    hoje = datetime.now().strftime("%d/%m/%Y")
    df_jogos['data'] = df_jogos['data'].astype(str).str.strip()
    jogo_hoje = df_jogos[df_jogos['data'] == hoje]

    if jogo_hoje.empty:
        st.warning(f"Sem caso clínico para hoje ({hoje}).")
    else:
        dados = jogo_hoje.iloc[0]
        solucao = str(dados['doenca']).strip()
        dicas = [dados['dica1'], dados['dica2'], dados['dica3'], dados['dica4'], dados['dica5'], dados['dica6']]

        st.divider()
        for i in range(st.session_state.tentativas + 1):
            if i < 6: st.info(f"**Dica {i+1}:** {dicas[i]}")

        if not st.session_state.terminou:
            # O PULO DO GATO: O format_func aplica o visual de riscado na lista
            palpite = st.selectbox(
                "Selecione seu diagnóstico:", 
                [""] + lista_completa,
                format_func=lambda x: riscar(x) if x in st.session_state.chutes_feitos else x
            )
            
            if st.button("Confirmar Hipótese"):
                if palpite == "":
                    st.warning("Selecione uma doença!")
                elif palpite in st.session_state.chutes_feitos:
                    st.warning(f"Você já tentou '{palpite}'! Escolha uma opção que não esteja riscada.")
                else:
                    st.session_state.chutes_feitos.append(palpite)
                    
                    if normalizar(palpite) == normalizar(solucao):
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
            
            if st.button("Recomeçar (Apenas para Testes)"):
                st.session_state.tentativas = 0
                st.session_state.terminou = False
                st.session_state.chutes_feitos = []
                st.rerun()

except Exception as e:
    st.error(f"Erro: {e}")

if st.sidebar.button("🔄 Forçar Atualização"):
    st.cache_data.clear()
    st.rerun()
