import streamlit as st
from datetime import datetime, timedelta, date
import pandas as pd
from sqlalchemy import text

@st.cache_data(ttl=300)
def carica_oroscopi(_conn, filtri=None):
    """
    Recupera gli oroscopi dal database con gestione ottimizzata delle date.
    La funzione utilizza conversioni esplicite per garantire la corretta 
    gestione dei formati temporali.
    """
    query = """
    SELECT 
        id,
        nome_utente,
        DATE_FORMAT(data_nascita, '%Y-%m-%d') as data_nascita,
        segno_zodiacale,
        ascendente,
        testo_oroscopo,
        citta_nascita,
        TIME_FORMAT(ora_nascita, '%H:%i') as ora_nascita,
        DATE_FORMAT(data_generazione, '%Y-%m-%d') as data_generazione
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
            data_corrente = datetime.now()
            if filtri['periodo'] == 'ultima_settimana':
                data_inizio = (data_corrente - timedelta(days=7)).strftime('%Y-%m-%d')
                query += " AND DATE(data_generazione) >= :data_inizio"
                params['data_inizio'] = data_inizio
            elif filtri['periodo'] == 'ultimo_mese':
                data_inizio = (data_corrente - timedelta(days=30)).strftime('%Y-%m-%d')
                query += " AND DATE(data_generazione) >= :data_inizio"
                params['data_inizio'] = data_inizio
    
    query += " ORDER BY data_generazione DESC"
    
    try:
        df = _conn.query(query, params=params)
        
        if not df.empty:
            df['data_nascita'] = pd.to_datetime(df['data_nascita']).dt.date
            df['data_generazione'] = pd.to_datetime(df['data_generazione']).dt.date
            
        return df
        
    except Exception as e:
        st.error(f"Errore nell'esecuzione della query: {str(e)}")
        print(f"Errore dettagliato: {str(e)}")
        return pd.DataFrame()

def mostra_filtri():
    """
    Crea l'interfaccia per i filtri di ricerca con valori iniziali puliti.
    """
    st.sidebar.header("Filtri di Ricerca")
    
    # Aggiungiamo il pulsante di reset all'inizio della sidebar
    if st.sidebar.button("🔄 Reset Filtri"):
        # Reset di tutti i valori nella session_state
        if 'nome_filtro' in st.session_state:
            del st.session_state.nome_filtro
        if 'segno_filtro' in st.session_state:
            del st.session_state.segno_filtro
        if 'periodo_filtro' in st.session_state:
            del st.session_state.periodo_filtro
    
    # Usiamo valori vuoti/default se non presenti nella session_state
    nome_filtro = st.sidebar.text_input(
        "Cerca per nome",
        value="",  # Default vuoto
        key='nome_filtro'
    )
    
    segni = ["Tutti", "Ariete", "Toro", "Gemelli", "Cancro", "Leone", "Vergine",
             "Bilancia", "Scorpione", "Sagittario", "Capricorno", "Acquario", "Pesci"]
    segno_filtro = st.sidebar.selectbox(
        "Segno Zodiacale",
        segni,
        index=0,  # Forziamo "Tutti" come default
        key='segno_filtro'
    )
    
    periodi = {
        "tutto": "Tutto",
        "ultima_settimana": "Ultima settimana",
        "ultimo_mese": "Ultimo mese"
    }
    periodo_filtro = st.sidebar.selectbox(
        "Periodo",
        list(periodi.values()),
        index=0,  # Forziamo "Tutto" come default
        key='periodo_filtro'
    )
    
    # Costruiamo il dizionario dei filtri solo se sono stati effettivamente selezionati valori
    filtri = {}
    if nome_filtro.strip():  # Aggiungiamo .strip() per evitare spazi vuoti
        filtri['nome'] = nome_filtro
    if segno_filtro != "Tutti":
        filtri['segno'] = segno_filtro
    if periodo_filtro != "Tutto":
        filtri['periodo'] = [k for k, v in periodi.items() if v == periodo_filtro][0]
    
    return filtri

def prepara_dati_per_export(df):
    """
    Prepara il DataFrame per l'esportazione in CSV.
    """
    try:
        export_df = df.copy()
        
        if 'data_nascita' in export_df.columns:
            export_df['data_nascita'] = export_df['data_nascita'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '')
        if 'data_generazione' in export_df.columns:
            export_df['data_generazione'] = export_df['data_generazione'].apply(lambda x: x.strftime('%d/%m/%Y') if pd.notnull(x) else '')
            
        colonne = {
            'nome_utente': 'Nome',
            'data_nascita': 'Data di Nascita',
            'ora_nascita': 'Ora di Nascita',
            'citta_nascita': 'Città di Nascita',
            'segno_zodiacale': 'Segno Zodiacale',
            'ascendente': 'Ascendente',
            'testo_oroscopo': 'Oroscopo',
            'data_generazione': 'Data Generazione'
        }
        export_df = export_df.rename(columns=colonne)
        
        colonne_ordinate = [
            'Nome', 'Data di Nascita', 'Ora di Nascita', 'Città di Nascita',
            'Segno Zodiacale', 'Ascendente', 'Oroscopo', 'Data Generazione'
        ]
        export_df = export_df[colonne_ordinate]
        
        return export_df
        
    except Exception as e:
        st.error(f"Errore nella preparazione dei dati per l'export: {str(e)}")
        return pd.DataFrame()

def formatta_data(data):
    """
    Formatta una data in modo sicuro.
    """
    try:
        if isinstance(data, (date, datetime)):
            return data.strftime('%d/%m/%Y')
        return str(data)
    except:
        return "Data non disponibile"

def formatta_ora(ora):
    """
    Formatta un'ora in modo sicuro.
    """
    try:
        return f"{ora[:5]}" if ora else "Ora non specificata"
    except:
        return "Ora non disponibile"

def main():
    """
    Funzione principale per la visualizzazione degli oroscopi.
    """
    st.markdown("""
    <a href="/" target="_self" class="nav-button">
        🏠 Torna alla Home
    </a>
    """, unsafe_allow_html=True)
    
    st.title("📚 Archivio Oroscopi")
    st.write("Esplora gli oroscopi generati e salvati nel database.")
    
    try:
        conn = st.connection('mysql', type='sql')
        filtri = mostra_filtri()
        
        with st.spinner("Caricamento oroscopi..."):
            df = carica_oroscopi(conn, filtri)
        
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Totale oroscopi", len(df))
            with col2:
                st.metric("Segni unici", df['segno_zodiacale'].nunique())
            with col3:
                st.metric("Persone diverse", df['nome_utente'].nunique())
            
            # Sezione esportazione
            st.markdown("### Esporta Dati")
            export_df = prepara_dati_per_export(df)
            
            if not export_df.empty:
                csv = export_df.to_csv(index=False)
                st.download_button(
                    label="📥 Scarica dati in formato CSV",
                    data=csv,
                    file_name=f"oroscopi_export_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    help="Clicca per scaricare i dati visualizzati in formato CSV"
                )
            
            # Visualizzazione oroscopi
            st.markdown("### Oroscopi")
            for _, row in df.iterrows():
                with st.expander(
                    f"{row['nome_utente']} - {row['segno_zodiacale']} "
                    f"({formatta_data(row['data_generazione'])})"
                ):
                    st.write(f"**Data di nascita:** {formatta_data(row['data_nascita'])}")
                    st.write(f"**Città di nascita:** {row['citta_nascita']}")
                    st.write(f"**Ora di nascita:** {formatta_ora(row['ora_nascita'])}")
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