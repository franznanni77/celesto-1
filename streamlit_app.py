import streamlit as st
from datetime import datetime, date
from sqlalchemy import text
import logging
from calcoli_astrologici import valida_numero_cellulare, genera_dati_astrologici
from generatore_AI import GeneratoreOroscopo
from whatsapp_sender import WhatsAppSender

# Configurazione del logging
logging.basicConfig(level=logging.ERROR)

def get_data_default():
    """
    Ottiene la data di default: giorno e mese correnti dell'anno 1980.
    """
    today = datetime.now()
    return date(1980, today.month, today.day)

def get_data_minima():
    """
    Ottiene la data minima consentita: 100 anni fa da oggi.
    """
    today = datetime.now()
    return date(today.year - 100, today.month, today.day)

def salva_oroscopo_nel_database(conn, dati_utente: dict, testo_oroscopo: str) -> bool:
    """
    Salva l'oroscopo generato nel database.
    """
    query = """
    INSERT INTO oroscopi (
        nome_utente,
        data_nascita,
        segno_zodiacale,
        ascendente,
        testo_oroscopo,
        citta_nascita,
        ora_nascita,
        data_generazione
    ) VALUES (
        :nome,
        :data_nascita,
        :segno_zodiacale,
        :ascendente,
        :testo_oroscopo,
        :citta_nascita,
        :ora_nascita,
        CURRENT_TIMESTAMP
    )
    """
    params = {
        "nome": dati_utente.get("nome", ""),
        "data_nascita": dati_utente.get("data_nascita", ""),
        "segno_zodiacale": dati_utente.get("segno_zodiacale", ""),
        "ascendente": dati_utente.get("ascendente", ""),
        "testo_oroscopo": testo_oroscopo,
        "citta_nascita": dati_utente.get("citta_nascita", ""),
        "ora_nascita": dati_utente.get("ora_nascita", "")
    }
    try:
        with conn.session as session:
            session.execute(text(query), params)
            session.commit()
        return True
    except Exception as e:
        logging.error(f"Errore nel salvataggio dell'oroscopo: {e}")
        return False

def carica_stili_css():
    """
    Carica gli stili CSS personalizzati.
    """
    st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        background-color: #4F8BF9;
        color: white;
    }
    .oroscopo-container {
        background-color: rgba(255, 255, 255, 0.05);
        padding: 25px;
        border-radius: 10px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: inherit;
        margin: 15px 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    </style>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(
        page_title="Profilo Astrologico Personale",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    carica_stili_css()
    st.title("🌟 Profilo Astrologico Personale")
    st.markdown("""
    <a href="Visualizza_Oroscopi" target="_self" class="nav-button">
        📚 Visualizza Archivio Oroscopi
    </a>
    """, unsafe_allow_html=True)
    st.write("""
    Scopri il tuo profilo astrologico completo e ricevi un oroscopo personalizzato.
    """)
    with st.form("dati_personali"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome", help="Inserisci il tuo nome completo")
            data_nascita = st.date_input(
                "Data di nascita",
                value=get_data_default(),
                min_value=get_data_minima(),
                max_value=datetime.now().date(),
                help="Seleziona la tua data di nascita (formato: DD/MM/YYYY)",
                format="DD/MM/YYYY"
            )
            st.markdown(f"""
            <div class="date-info">
            📅 Seleziona una data tra il {get_data_minima().strftime("%d/%m/%Y")} e il {datetime.now().date().strftime("%d/%m/%Y")}
            </div>
            """, unsafe_allow_html=True)
            cellulare = st.text_input(
                "Numero di cellulare",
                help="Inserisci un numero di cellulare italiano (es. +39 345 1234567)"
            )
            invia_whatsapp = st.checkbox(
                "Invia oroscopo via WhatsApp",
                value=False,
                help="Deseleziona se non vuoi ricevere l'oroscopo via WhatsApp"
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
        submit = st.form_submit_button("Calcola il tuo profilo astrologico")
    if submit:
        if not nome or not data_nascita or not ora_nascita or not citta_nascita:
            st.error("Per favore, compila tutti i campi richiesti.")
            return
        # Validazione del numero di cellulare
        numero_valido, messaggio_validazione = valida_numero_cellulare(cellulare)
        if not numero_valido:
            st.error(f"Errore nel numero di cellulare: {messaggio_validazione}")
            return
        # Calcolo dati astrologici
        dati_astrologici = genera_dati_astrologici(data_nascita, ora_nascita)
        # Preparazione dati per il generatore AI
        dati_completi = {
            "nome": nome,
            "data_nascita": data_nascita.strftime('%Y-%m-%d'),
            "segno_zodiacale": dati_astrologici["segno_zodiacale"],
            "ascendente": dati_astrologici["ascendente"],
            "citta_nascita": citta_nascita,
            "ora_nascita": ora_nascita.strftime('%H:%M'),
            **dati_astrologici
        }
        # Generazione oroscopo
        generatore = GeneratoreOroscopo()
        oroscopo = generatore.genera_oroscopo(dati_completi)
        # Salvataggio oroscopo nel database
        conn = st.connection('mysql', type='sql')
        if salva_oroscopo_nel_database(conn, dati_completi, oroscopo):
            st.success("Oroscopo salvato con successo nel database!")
            # Invio via WhatsApp
            if invia_whatsapp:
                sender = WhatsAppSender()
                if sender.invia_oroscopo(cellulare, dati_completi, oroscopo):
                    st.success("Oroscopo inviato via WhatsApp!")
                else:
                    st.warning("Non è stato possibile inviare l'oroscopo via WhatsApp.")
        else:
            st.error("Errore nel salvataggio dell'oroscopo.")
        # Visualizzazione oroscopo
        st.markdown(f"""
        <div class="oroscopo-container">
            {oroscopo}
        </div>
        """, unsafe_allow_html=True)
    # Footer informativo
    st.markdown("""
    ---
    📝 **Nota sulla privacy**: I dati inseriti vengono utilizzati per il calcolo del profilo astrologico e sono salvati in modo sicuro.
    """)

if __name__ == "__main__":
    main()