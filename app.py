import streamlit as st
import pandas as pd
from datetime import datetime
import time
import re

# 1. Configuração da página
st.set_page_config(page_title="Meddle BR", page_icon="🩺", layout="centered")


ID_DA_PLANILHA = "1QIDAaiVyRltk6xkeBdMvLHf3xaODuBs9DWCpm1kjmZs"
GID_LISTA = "16863228" 
# Verifique se esse é o número no final do seu link

URL_JOGOS_BASE = f"https://docs.google.com/spreadsheets/d/{ID_DA_PLANILHA}/export?format=csv"
URL_LISTA_BASE = f"https://docs.google.com/spreadsheets/d/{ID_DA_PLANILHA}/export?format=csv&gid={GID_LISTA}"
# ----------------------------------

# Função para normalizar texto (Ignora espaços, parênteses e maiúsculas)
def normalizar(texto):
    return re.sub(r'[^a-zA-Z0-9]', '', str(texto)).lower()

@st.cache_data(ttl=1) # TTL de 1 segundo para não travar nada no Streamlit
def load_data(url_base, nome_tabela):
    try:
        # O PULO DO GATO: Adicionamos o timestamp atual no final da URL
        # Isso 'engana' o cache do Google e força a versão mais nova.
        cache_buster = f"&t={int(time.time())}"
        url_final = url_base + cache_buster
        
        df = pd.read_csv(url_final, sep=',', encoding='utf-8-sig', on_bad_lines='skip')
        
        # Se falhou em separar colunas, tenta ponto e vírgula
        if len(df.columns) == 1:
            df = pd.read_csv(url_final, sep=';', encoding='utf-8-sig', on_bad_lines='skip')

        # Limpeza agressiva de nomes de colunas
        df.columns = [str(c).strip().lower().replace('ç','c').replace('ã','a') for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao carregar {nome_tabela}: {e}")
        return pd.DataFrame()

# Interface Visual
st.title("Meddle BR 🩺")
st.write("Analise as dicas e escolha a hipótese diagnóstica.")

try:
    # Carregando com o novo sistema
    df_jogos = load_data(URL_JOGOS_BASE, "Calendário de Jogos")
    df_opcoes = load_data(URL_LISTA_BASE, "Lista de Doenças")
    
    if not df_opcoes.empty and 'doenca' in df_opcoes.columns:
        lista_doencas_completa = sorted(df_opcoes['doenca'].dropna().astype(str).unique().tolist())
    else:
        lista_doencas_completa = []

    # Lógica da data
    hoje = datetime.now().strftime("%d/%m/%Y")
    df_jogos['data'] = df_jogos['data'].astype(str).str.strip()
    jogo_hoje = df_jogos[df_jogos['data'] == hoje]

    if jogo_hoje.empty:
        st.warning(f"Nenhum caso clínico para hoje ({hoje}).")
        if st.button("Tentar atualizar planilha agora"):
            st.cache_data.clear()
            st.rerun()
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
                # COMPARAÇÃO INTELIGENTE
                elif normalizar(palpite) == normalizar(solucao):
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
                st.error(f"Fim de jogo! O diagnóstico correto era: **{solucao}**.")
            
            if st.button("Resetar jogo (Para testes)"):
                st.session_state.tentativas = 0
                st.session_state.terminou = False
                st.rerun()

except Exception as e:
    st.error(f"Erro: {e}")

# Botão na lateral para garantir o refresh total
if st.sidebar.button("🔄 Forçar Atualização da Planilha"):
    st.cache_data.clear()
    st.rerun()
