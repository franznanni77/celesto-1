"""
visualizza_oroscopi.py
---------------------
Questo modulo gestisce la visualizzazione e il filtraggio degli oroscopi salvati nel database.
Fornisce un'interfaccia utente intuitiva per esplorare lo storico degli oroscopi generati.
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text

# Aggiungi un pulsante per tornare alla pagina principale
st.markdown("""
<a href="/" target="_self" class="nav-button">
    🏠 Torna alla Home
</a>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache per 5 minuti
def carica_oroscopi(_conn, filtri=None):
    """
    Recupera gli oroscopi dal database applicando i filtri specificati.
    La funzione utilizza il caching di Streamlit per migliorare le performance.
    L'underscore davanti a 'conn' indica a Streamlit di non tentare di memorizzare
    nella cache l'oggetto di connessione.
    
    Args:
        _conn: Connessione al database Streamlit (con underscore per evitare il caching)
        filtri: Dizionario contenente i criteri di filtro (opzionale)
    
    Returns:
        DataFrame pandas contenente i risultati della query
    """
    # Costruiamo la query base
    query = """
    SELECT 
        id,
        nome_utente,
        data_nascita,
        segno_zodiacale,
        ascendente,
        testo_oroscopo,
        citta_nascita,
        ora_nascita,
        data_generazione
    FROM oroscopi
    WHERE 1=1
    """
    
    # Parametri per la query
    params = {}
    
    # Aggiungiamo i filtri se specificati
    if filtri:
        if filtri.get('nome'):
            query += " AND nome_utente LIKE :nome"
            params['nome'] = f"%{filtri['nome'

def mostra_filtri():
    """
    Crea l'interfaccia per i filtri di ricerca.
    
    Returns:
        Dizionario contenente i filtri selezionati dall'utente
    """
    st.sidebar.header("Filtri di Ricerca")
    
    # Filtro per nome
    nome_filtro = st.sidebar.text_input("Cerca per nome")
    
    # Filtro per segno zodiacale
    segni = ["Tutti", "Ariete", "Toro", "Gemelli", "Cancro", "Leone", "Vergine",
             "Bilancia", "Scorpione", "Sagittario", "Capricorno", "Acquario", "Pesci"]
    segno_filtro = st.sidebar.selectbox("Segno Zodiacale", segni)
    
    # Filtro per periodo
    periodi = {
        "tutto": "Tutto",
        "ultima_settimana": "Ultima settimana",
        "ultimo_mese": "Ultimo mese"
    }
    periodo_filtro = st.sidebar.selectbox("Periodo", list(periodi.values()))
    
    # Costruiamo il dizionario dei filtri
    filtri = {}
    if nome_filtro:
        filtri['nome'] = nome_filtro
    if segno_filtro != "Tutti":
        filtri['segno'] = segno_filtro
    if periodo_filtro != "Tutto":
        filtri['periodo'] = [k for k, v in periodi.items() if v == periodo_filtro][0]
    
    return filtri

def main():
    """
    Funzione principale che gestisce l'interfaccia utente per la visualizzazione
    degli oroscopi salvati.
    """
    st.title("📚 Archivio Oroscopi")
    st.write("Esplora gli oroscopi generati e salvati nel database.")
    
    try:
        # Inizializziamo la connessione al database
        conn = st.connection('mysql', type='sql')
        
        # Otteniamo i filtri dall'interfaccia utente
        filtri = mostra_filtri()
        
        # Carichiamo i dati
        with st.spinner("Caricamento oroscopi..."):
            df = carica_oroscopi(conn, filtri)
        
        # Mostriamo alcune statistiche
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Totale oroscopi", len(df))
            with col2:
                st.metric("Segni unici", df['segno_zodiacale'].nunique())
            with col3:
                st.metric("Persone diverse", df['nome_utente'].nunique())
        
            # Visualizziamo gli oroscopi
            for _, row in df.iterrows():
                with st.expander(f"{row['nome_utente']} - {row['segno_zodiacale']} "
                               f"({row['data_generazione'].strftime('%d/%m/%Y')})"):
                    st.write(f"**Data di nascita:** {row['data_nascita'].strftime('%d/%m/%Y')}")
                    st.write(f"**Città di nascita:** {row['citta_nascita']}")
                    st.write(f"**Ora di nascita:** {row['ora_nascita'].strftime('%H:%M')}")
                    st.write(f"**Ascendente:** {row['ascendente']}")
                    st.markdown("---")
                    st.markdown(f"**Oroscopo:**\n{row['testo_oroscopo']}")
        else:
            st.info("Nessun oroscopo trovato con i filtri selezionati.")
            
    except Exception as e:
        st.error(f"Si è verificato un errore durante il caricamento dei dati: {str(e)}")
        print(f"Errore dettagliato: {str(e)}")

if __name__ == "__main__":
    main()