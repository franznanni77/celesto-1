"""
streamlit_app.py
---------------
Applicazione Streamlit per il calcolo del profilo astrologico personale e la generazione
dell'oroscopo personalizzato utilizzando AI. Include gestione avanzata delle date
in formato europeo e salvataggio nel database MySQL.
"""

import streamlit as st
from datetime import datetime, timedelta, date
import pytz
from calcoli_astrologici import valida_numero_cellulare, genera_dati_astrologici
from generatore_AI import GeneratoreOroscopo

def get_default_date():
    """
    Calcola la data di default: giorno e mese correnti ma dell'anno 1980.
    Questo mantiene il giorno e mese attuali ma nel passato.
    """
    today = datetime.now()
    return datetime(1980, today.month, today.day).date()

def get_min_date():
    """
    Calcola la data minima consentita: 100 anni fa da oggi.
    """
    today = datetime.now()
    return datetime(today.year - 100, today.month, today.day).date()

def salva_oroscopo_db(dati_utente: dict, testo_oroscopo: str):
    """
    Salva l'oroscopo generato nel database con gestione SQL corretta.
    """
    try:
        # Importiamo text da sqlalchemy per gestire correttamente le query testuali
        from sqlalchemy import text
        
        # Inizializza la connessione
        conn = st.connection('mysql', type='sql')
        print("Connessione al database stabilita")
        
        # Query di inserimento avvolta in text()
        query = text("""
        INSERT INTO oroscopi (
            nome_utente, 
            data_nascita, 
            segno_zodiacale, 
            ascendente, 
            testo_oroscopo, 
            citta_nascita, 
            ora_nascita
        ) VALUES (
            :nome,
            :data_nascita,
            :segno_zodiacale,
            :ascendente,
            :testo_oroscopo,
            :citta_nascita,
            :ora_nascita
        )
        """)
        
        # Preparazione dei parametri con verifica dei valori
        params = {
            "nome": str(dati_utente.get('nome', '')),
            "data_nascita": dati_utente.get('data_nascita'),
            "segno_zodiacale": str(dati_utente.get('segno_zodiacale', '')),
            "ascendente": str(dati_utente.get('ascendente', '')),
            "testo_oroscopo": str(testo_oroscopo),
            "citta_nascita": str(dati_utente.get('citta_nascita', '')),
            "ora_nascita": dati_utente.get('ora_nascita')
        }
        
        # Debug: stampiamo i parametri
        print("Parametri:", params)
        
        # Esecuzione della query con gestione esplicita della sessione
        with conn.session as s:
            try:
                s.execute(query, params)
                s.commit()
                print("Query eseguita con successo")
                st.success("Oroscopo salvato con successo nel database!")
            except Exception as query_error:
                print(f"Errore durante l'esecuzione della query: {str(query_error)}")
                raise query_error
        
    except Exception as e:
        error_message = f"Errore dettagliato: {str(e)}\nTipo di errore: {type(e)}"
        print(error_message)
        st.error(f"Si è verificato un errore durante il salvataggio: {str(e)}")
        st.code(error_message)
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
        /* Stili esistenti migliorati */
        .stButton>button {
            width: 100%;
            background-color: #4F8BF9;
            color: white;
        }
        
        .stMetric {
            background-color: rgba(240, 242, 246, 0.1);
            padding: 10px;
            border-radius: 5px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: inherit;
        }
        
        .date-info {
            font-size: 0.9em;
            color: inherit;
            margin-bottom: 1em;
            opacity: 0.8;
        }
        
        /* Nuovi stili per l'oroscopo */
        .oroscopo-container {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 25px;
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: inherit;
            margin: 15px 0;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Stili specifici per il testo dell'oroscopo */
        .oroscopo-text {
            line-height: 1.6;
            font-size: 1.1em;
            color: inherit;
        }
        
        /* Stili per i numeri fortunati */
        .numeri-fortunati {
            margin-top: 15px;
            padding-top: 10px;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            font-weight: bold;
            color: inherit;
        }
        
        /* Miglioriamo la leggibilità delle metriche */
        .metric-container {
            background-color: rgba(255, 255, 255, 0.05);
            padding: 15px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            color: inherit;
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
    - Salvataggio sicuro dei dati nel database
    
    La precessione degli equinozi è un fenomeno astronomico che causa uno spostamento 
    graduale dei punti equinoziali di circa 1 grado ogni 72 anni, influenzando il 
    calcolo dell'ascendente nel lungo periodo.
    """)

# Form per l'inserimento dei dati
with st.form("dati_personali"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome", help="Inserisci il tuo nome completo")
        
        # Input della data con formato europeo e range personalizzato
        data_nascita = st.date_input(
            "Data di nascita",
            value=get_default_date(),
            min_value=get_min_date(),
            max_value=datetime.now().date(),
            help="Seleziona la tua data di nascita (formato: DD/MM/YYYY)",
            format="DD/MM/YYYY"
        )
        
        # Informazioni sul range di date disponibile
        st.markdown(f"""
        <div class="date-info">
        📅 Puoi selezionare una data tra il {get_min_date().strftime("%d/%m/%Y")} 
        e il {datetime.now().date().strftime("%d/%m/%Y")}
        </div>
        """, unsafe_allow_html=True)
        
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
    # Validazione dell'età
    anni = (datetime.now().date() - data_nascita).days / 365.25
    if anni > 90:
        st.warning(f"Hai selezionato una data di {int(anni)} anni fa. "
                  "Assicurati che sia corretto.")
    
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
                    "nome": nome,  # Il nome dell'utente
                     "data_nascita": data_nascita.strftime('%Y-%m-%d'),  # Convertiamo in stringa
                     "citta_nascita": citta_nascita,  # Città rimane stringa
                     "ora_nascita": ora_nascita.strftime('%H:%M:%S')  # Convertiamo in stringa
                }
                
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
                        
                        # Salva l'oroscopo nel database
                        salva_oroscopo_db(dati_completi, oroscopo)
                    
                    # Visualizzazione dell'oroscopo in un box dedicato
                        st.markdown(f"""
                            <div class="oroscopo-container">
                                 <div class="oroscopo-text">
                                    {oroscopo}
                                </div>
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
📝 **Nota sulla privacy**: I dati inseriti vengono utilizzati per il calcolo del 
profilo astrologico e vengono salvati in modo sicuro nel nostro database.
""")