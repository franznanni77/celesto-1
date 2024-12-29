import streamlit as st
from datetime import datetime
import pytz
import re

def valida_numero_cellulare(numero):
    """
    Valida un numero di cellulare italiano.
    Regole di validazione:
    - Deve iniziare con +39 o 0039 (prefisso internazionale) oppure con 3 (formato nazionale)
    - Dopo il prefisso, deve avere un numero che inizia con 3 seguito da 8 o 9 cifre
    - Può contenere spazi o trattini come separatori
    
    Returns:
    - (bool, str): (validità del numero, messaggio esplicativo)
    """
    # Rimuoviamo spazi, trattini e parentesi
    numero_pulito = re.sub(r'[\s\-\(\)]', '', numero)
    
    # Pattern per numeri italiani (con e senza prefisso internazionale)
    pattern_completo = r'^(?:(?:\+39|0039))?3\d{8,9}$'
    
    if not numero_pulito:
        return False, "Il numero non può essere vuoto"
    
    if not re.match(pattern_completo, numero_pulito):
        return False, "Formato non valido. Esempi corretti: +39 345 1234567, 3451234567"
    
    # Verifichiamo la lunghezza dopo il prefisso
    numero_senza_prefisso = numero_pulito.replace('+39', '').replace('0039', '')
    if len(numero_senza_prefisso) not in [9, 10]:
        return False, "Il numero deve avere 9 o 10 cifre dopo il prefisso"
        
    return True, "Numero valido"

[... resto delle funzioni precedenti rimane invariato ...]

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

La precessione degli equinozi è un fenomeno astronomico che causa uno spostamento graduale 
dei punti equinoziali di circa 1 grado ogni 72 anni, influenzando il calcolo dell'ascendente 
nel lungo periodo.
""")

# Form per l'inserimento dei dati
with st.form("dati_personali"):
    col1, col2 = st.columns(2)
    
    with col1:
        nome = st.text_input("Nome")
        data_nascita = st.date_input("Data di nascita")
        cellulare = st.text_input("Numero di cellulare", help="Inserisci un numero di cellulare italiano (es. +39 345 1234567)")
        
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
    
    # Pulsante per inviare il form
    submit = st.form_submit_button("Calcola")

# Calcolo e visualizzazione dei risultati
if submit:
    # Validazione del numero di cellulare
    numero_valido, messaggio_validazione = valida_numero_cellulare(cellulare)
    
    if not numero_valido:
        st.error(f"Errore nel numero di cellulare: {messaggio_validazione}")
    elif nome and data_nascita and ora_nascita and citta_nascita:
        # Calcoliamo i risultati
        segno = calcola_segno_zodiacale(data_nascita)
        ascendente = calcola_ascendente(data_nascita, ora_nascita)
        gruppo = calcola_gruppo_energia(data_nascita)
        correzione = calcola_correzione_precessionale(data_nascita.year)
        
        # Visualizziamo i risultati
        st.success(f"Risultati per {nome}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Segno Zodiacale", segno)
            
        with col2:
            st.metric("Ascendente", ascendente)
            
        with col3:
            st.metric("Gruppo Energia", gruppo)
            
        # Dettagli del profilo
        st.write("### Dettagli del tuo profilo")
        st.write(f"""
        Caro/a {nome}, ecco la tua analisi astrologica:
        
        Il tuo segno zodiacale è {segno}, che rappresenta la tua essenza fondamentale.
        Il tuo ascendente in {ascendente} influenza il modo in cui ti presenti al mondo.
        Appartieni al {gruppo}, che determina il tuo livello energetico di base.
        
        Nato/a a {citta_nascita} alle {ora_nascita.strftime('%H:%M')}, il tuo ascendente è stato calcolato 
        considerando:
        - La posizione stagionale del Sole nel mese di {data_nascita.strftime('%B')}
        - Una correzione precessionale di {correzione:.2f} ore dovuta all'anno di nascita {data_nascita.year}
        
        Potrai ricevere i tuoi risultati dettagliati al numero: {cellulare}
        """)
        
        # Nota tecnica
        st.info("""
        Nota Tecnica: Questo calcolo dell'ascendente include correzioni astronomiche fondamentali, 
        ma per un calcolo completamente accurato sarebbero necessarie anche le coordinate geografiche 
        precise del luogo di nascita e altri fattori astronomici come la nutazione e l'aberrazione.
        """)
    else:
        st.error("Per favore, compila tutti i campi richiesti.")