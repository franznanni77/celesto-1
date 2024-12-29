"""
streamlit_app.py
---------------
Applicazione Streamlit per il calcolo del profilo astrologico personale e la generazione
dell'oroscopo personalizzato utilizzando AI.
"""

import streamlit as st
from datetime import datetime
import pytz
from calcoli_astrologici import valida_numero_cellulare, genera_dati_astrologici
from generatore_AI import GeneratoreOroscopo

# Configurazione della pagina Streamlit
st.set_page_config(
    page_title="Calcolo Astrologico Personalizzato",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funzione per lo stile CSS personalizzato
def load_custom_css():
    st.markdown("""
        <style>
        .stButton>button {
            width: 100%;
            background-color: #4F8BF9;
            color: white;
        }
        .stMetric {
            background-color: #f0f2f6;
            padding: 10px;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)

# Carica lo stile CSS
load_custom_css()

# Titolo e descrizione dell'applicazione
st.title("🌟 Profilo Astrologico Personale")
st.write("""
Scopri il tuo profilo astrologico completo e ricevi un oroscopo personalizzato 
basato sulle tue configurazioni astrali uniche.
""")

# Sezione informativa sulla precisione del calcolo
with st.expander("ℹ️ Informazioni sulla precisione dei calcoli"):
    st.markdown("""
    ### 🔭 Precisione Astronomica
    Questa applicazione include:
    - Correzione stagionale basata sul mese di nascita
    - Correzione per il moto di precessione degli equinozi
    - Calcolo preciso dell'ora siderale
    - Validazione del formato numero di telefono italiano
    - Generazione di oroscopo personalizzato con AI
    """)

# Form per l'inserimento dei dati
with st.form("dati_personali"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome", help="Inserisci il tuo nome completo")
        data_nascita = st.date_input(
            "Data di nascita",
            min_value=datetime(1900, 1, 1).date(),
            max_value=datetime.now().date(),
            help="Seleziona la tua data di nascita"
        )
        cellulare = st.text_input(
            "Numero di cellulare",
            help="Inserisci un numero di cellulare italiano (es. +39 345 1234567)"
        )
        
    with col2:
        ora_nascita = st.time_input(
            "Ora di nascita",
            help="Inserisci l'ora di nascita il più precisamente possibile"
        )
        citta_nascita = st.text_input(
            "Città di nascita",
            help="Inserisci la città dove sei nato/a"
        )
    
    # Nota informativa sulla formattazione del numero
    st.info("""
    📱 **Formato numero di cellulare accettato:**
    - Con prefisso internazionale: +39 XXX XXXXXXX o 0039 XXX XXXXXXX
    - Formato nazionale: 3XX XXXXXXX
    - Spazi e trattini sono opzionali
    """)
    
    # Pulsante per inviare il form
    submit = st.form_submit_button("Calcola il tuo profilo astrologico")

# Elaborazione dei dati e visualizzazione dei risultati
if submit:
    # Validazione del numero di cellulare
    numero_valido, messaggio_validazione = valida_numero_cellulare(cellulare)
    
    if not numero_valido:
        st.error(f"Errore nel numero di cellulare: {messaggio_validazione}")
    elif nome and data_nascita and ora_nascita and citta_nascita:
        # Mostra un indicatore di caricamento
        with st.spinner("Elaborazione del tuo profilo astrologico in corso..."):
            try:
                # Generiamo i dati astrologici
                dati_astrologici = genera_dati_astrologici(data_nascita, ora_nascita)
                
                # Aggiungiamo il nome ai dati astrologici per il generatore AI
                dati_completi = {
                    **dati_astrologici,  # Tutti i dati astrologici
                    "nome": nome  # Il nome dell'utente
                }
                
                # Debug - Visualizza i dati che verranno inviati al generatore
                # print("Dati inviati al generatore:", dati_completi)
                
                # Visualizziamo i risultati principali
                st.success(f"Profilo astrologico di {nome}")
                
                # Metriche principali in tre colonne
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
                **Elementi base del tuo tema natale:**
                - Gruppo energia: {dati_astrologici['gruppo_energia']}
                - Fase lunare: {dati_astrologici['fase_lunare']}
                - Pianeti rilevanti: {' e '.join(dati_astrologici['pianeti_rilevanti'])}
                """)
                
                # Generazione dell'oroscopo personalizzato
                st.write("### 🔮 Il tuo oroscopo personalizzato")
                try:
                    generatore = GeneratoreOroscopo()
                    with st.spinner("Generazione del tuo oroscopo personalizzato..."):
                        oroscopo = generatore.genera_oroscopo(dati_completi)
                    
                    # Visualizzazione dell'oroscopo in un box dedicato
                    st.markdown(f"""
                    <div style='background-color: #f0f2f6; padding: 20px; border-radius: 10px;'>
                        {oroscopo}
                    </div>
                    """, unsafe_allow_html=True)
                    
                except Exception as e:
                    st.error(f"""
                    Si è verificato un errore nella generazione dell'oroscopo.
                    Dettagli: {str(e)}
                    """)
                
            except Exception as e:
                st.error("""
                Si è verificato un errore durante l'elaborazione dei dati.
                Per favore, verifica i dati inseriti e riprova.
                """)
                print(f"Errore nell'elaborazione dei dati: {str(e)}")
    else:
        st.error("Per favore, compila tutti i campi richiesti.")

# Footer informativo
st.markdown("""
---
📝 **Nota sulla privacy**: I dati inseriti vengono utilizzati solo per il calcolo del 
profilo astrologico e non vengono memorizzati.
""")