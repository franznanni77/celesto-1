"""
01_Visualizza_Oroscopi.py
-----------------------
Pagina per visualizzare e filtrare gli oroscopi salvati nel database.
Include funzionalità di ricerca e filtraggio avanzate.
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
from sqlalchemy import text

@st.cache_data(ttl=300)
def carica_oroscopi(_conn, filtri=None):
    """
    Recupera gli oroscopi dal database applicando i filtri specificati.
    Include gestione migliorata delle conversioni temporali.
    """
    query = """
    SELECT 
        id,
        nome_utente,
        DATE(data_nascita) as data_nascita,
        segno_zodiacale,
        ascendente,
        testo_oroscopo,
        citta_nascita,
        TIME(ora_nascita) as ora_nascita,
        DATE(data_generazione) as data_generazione
    FROM oroscopi
    WHERE 1=1
    """
    
    params = {}
    
    if filtri:
        if filtri.get('nome'):
            query += " AND nome_utente LIKE :nome"
            params['nome'] = f"%{filtri['nome']}%"
            
        if filtri.get('segno'):
            query += " AND segno_zodiacale = :segno"
            params['segno'] = filtri['segno']
            
        if filtri.get('periodo'):
            data_corrente = datetime.now().date()
            if filtri['periodo'] == 'ultima_settimana':
                data_inizio = (data_corrente - timedelta(days=7))
                query += " AND DATE(data_generazione) >= :data_inizio"
                params['data_inizio'] = data_inizio
            elif filtri['periodo'] == 'ultimo_mese':
                data_inizio = (data_corrente - timedelta(days=30))
                query += " AND DATE(data_generazione) >= :data_inizio"
                params['data_inizio'] = data_inizio
    
    query += " ORDER BY data_generazione DESC"
    
    try:
        # Eseguiamo la query e otteniamo il DataFrame
        df = _conn.query(query, params=params)
        
        if not df.empty:
            # Convertiamo le date in formato datetime
            df['data_nascita'] = pd.to_datetime(df['data_nascita']).dt.date
            df['data_generazione'] = pd.to_datetime(df['data_generazione']).dt.date
            
            # Non è necessario convertire ora_nascita poiché MySQL già la restituisce nel formato corretto
            
        return df
        
    except Exception as e:
        st.error(f"Errore nell'esecuzione della query: {str(e)}")
        print(f"Errore dettagliato: {str(e)}")  # Per debugging
        return pd.DataFrame()

def mostra_filtri():
    """
    Crea l'interfaccia per i filtri di ricerca nella sidebar.
    
    Returns:
        dict: Dizionario contenente i filtri selezionati dall'utente
    """
    st.sidebar.header("Filtri di Ricerca")
    
    # Filtro per nome
    nome_filtro = st.sidebar.text_input("Cerca per nome")
    
    # Filtro per segno zodiacale con tutti i segni disponibili
    segni = ["Tutti", "Ariete", "Toro", "Gemelli", "Cancro", "Leone", "Vergine",
             "Bilancia", "Scorpione", "Sagittario", "Capricorno", "Acquario", "Pesci"]
    segno_filtro = st.sidebar.selectbox("Segno Zodiacale", segni)
    
    # Filtro per periodo temporale
    periodi = {
        "tutto": "Tutto",
        "ultima_settimana": "Ultima settimana",
        "ultimo_mese": "Ultimo mese"
    }
    periodo_filtro = st.sidebar.selectbox("Periodo", list(periodi.values()))
    
    # Costruzione del dizionario dei filtri
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
    # Aggiungi pulsante per tornare alla home
    st.markdown("""
    <a href="/" target="_self" class="nav-button">
        🏠 Torna alla Home
    </a>
    """, unsafe_allow_html=True)
    
    st.title("📚 Archivio Oroscopi")
    st.write("Esplora gli oroscopi generati e salvati nel database.")
    
    try:
        # Inizializziamo la connessione al database
        conn = st.connection('mysql', type='sql')
        
        # Otteniamo i filtri dall'interfaccia utente
        filtri = mostra_filtri()
        
        # Carichiamo i dati con indicatore di caricamento
        with st.spinner("Caricamento oroscopi..."):
            df = carica_oroscopi(conn, filtri)
        
        # Visualizziamo le statistiche se ci sono dati
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Totale oroscopi", len(df))
            with col2:
                st.metric("Segni unici", df['segno_zodiacale'].nunique())
            with col3:
                st.metric("Persone diverse", df['nome_utente'].nunique())
        
            # Visualizziamo gli oroscopi in expander per una migliore organizzazione
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