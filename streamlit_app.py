import streamlit as st
from datetime import datetime
import pytz
from calcoli_astrologici import valida_numero_cellulare, genera_dati_astrologici

# Configurazione della pagina Streamlit
st.set_page_config(page_title="Calcolo Astrologico", page_icon="🌟")

# Titolo dell'applicazione
st.title("🌟 Calcolo Astrologico Personale")
st.write("Inserisci i tuoi dati per scoprire il tuo profilo astrologico")

# Spiegazione della precisione del calcolo
st.markdown("""
### 🔭 Precisione Astronomica
Questa versione dell'applicazione include:
- Correzione stagionale basata sul mese di nascita
- Correzione per il moto di precessione degli equinozi
- Calcolo preciso dell'ora siderale
- Validazione del formato numero di telefono italiano
""")

# Form per l'inserimento dei dati
with st.form("dati_personali"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome")
        data_nascita = st.date_input("Data di nascita")
        cellulare = st.text_input("Numero di cellulare", 
                                 help="Inserisci un numero di cellulare italiano (es. +39 345 1234567)")
        
    with col2:
        ora_nascita = st.time_input("Ora di nascita")
        citta_nascita = st.text_input("Città di nascita")
    
    # Nota informativa sulla formattazione del numero
    st.markdown("""
    📱 **Formato numero di cellulare accettato:**
    - Con prefisso internazionale: +39 XXX XXXXXXX o 0039 XXX XXXXXXX
    - Formato nazionale: 3XX XXXXXXX
    - Spazi e trattini sono opzionali
    """)
    
    submit = st.form_submit_button("Calcola")

# Calcolo e visualizzazione dei risultati
if submit:
    numero_valido, messaggio_validazione = valida_numero_cellulare(cellulare)
    
    if not numero_valido:
        st.error(f"Errore nel numero di cellulare: {messaggio_validazione}")
    elif nome and data_nascita and ora_nascita and citta_nascita:
        # Generiamo tutti i dati astrologici
        dati_astrologici = genera_dati_astrologici(data_nascita, ora_nascita)
        
        # Visualizziamo i risultati
        st.success(f"Risultati per {nome}")
        
        # Metriche principali
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Segno Zodiacale", dati_astrologici["segno_zodiacale"])
        with col2:
            st.metric("Ascendente", dati_astrologici["ascendente"])
        with col3:
            st.metric("Età", dati_astrologici["eta"])
            
        # Dettagli aggiuntivi
        st.write("### Dettagli del tuo profilo")
        st.write(f"""
        Caro/a {nome}, ecco la tua analisi astrologica completa:
        
        Hai {dati_astrologici['eta']} anni e il tuo segno zodiacale è {dati_astrologici['segno_zodiacale']}, 
        che rappresenta la tua essenza fondamentale.
        
        Il tuo ascendente in {dati_astrologici['ascendente']} influenza il modo in cui ti presenti al mondo.
        Appartieni al gruppo energia {dati_astrologici['gruppo_energia']}.
        
        Sei nato/a durante la fase di {dati_astrologici['fase_lunare']}, e i pianeti più rilevanti 
        per te sono {' e '.join(dati_astrologici['pianeti_rilevanti'])}.
        
        Nato/a a {citta_nascita} alle {ora_nascita.strftime('%H:%M')}
        """)
        
        # Mostriamo i dati in formato strutturato (utile per il prompt)
        st.write("### Dati strutturati per il prompt")
        st.json(dati_astrologici)
        
    else:
        st.error("Per favore, compila tutti i campi richiesti.")