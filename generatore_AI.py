"""
generatore_AI.py
---------------
Questo modulo implementa un generatore di oroscopi personalizzati utilizzando l'API di Anthropic Claude.
Il modulo gestisce la generazione di oroscopi basati su dati astrologici specifici dell'utente,
utilizzando un approccio strutturato e personalizzato per ogni previsione.

Autore: [Il tuo nome]
Data: [Data corrente]
Versione: 1.0
"""

from datetime import datetime
import json
import streamlit as st
from typing import Dict, Any
from anthropic import Anthropic

class GeneratoreOroscopo:
    """
    Classe che gestisce la generazione di oroscopi personalizzati utilizzando l'API di Anthropic.
    La classe si occupa di costruire prompt appropriati, interagire con l'API e formattare
    le risposte in un formato utilizzabile dall'applicazione.
    """
    
    def __init__(self):
        """
        Inizializza il generatore di oroscopi configurando il client Anthropic.
        La chiave API viene recuperata in modo sicuro dai secrets di Streamlit.
        
        Raises:
            ValueError: Se la chiave API non è configurata correttamente nei secrets di Streamlit.
        """
        try:
            # Inizializzazione del client Anthropic con la chiave dai secrets di Streamlit
            self.client = Anthropic(api_key=st.secrets["anthropic_api_key"])
            
            # Configurazione del modello - utilizziamo la versione più recente e capace
            self.model = "claude-3-opus-20240229"
        except Exception as e:
            raise ValueError(
                "Errore nell'inizializzazione del client Anthropic. "
                "Verifica che la chiave API sia configurata correttamente "
                f"nei secrets di Streamlit. Errore: {str(e)}"
            )
    
    def _determina_focus_giornaliero(self) -> str:
        """
        Determina il focus tematico dell'oroscopo basato sul giorno della settimana.
        Questo assicura che le previsioni siano rilevanti per il contesto temporale.
        
        Returns:
            str: Il tema specifico per il giorno corrente
        """
        focus_settimanale = {
            0: "riflessione e pianificazione",    # Domenica
            1: "carriera e ambizioni",            # Lunedì
            2: "comunicazione e relazioni",       # Martedì
            3: "creatività e progetti personali", # Mercoledì
            4: "crescita e sviluppo",            # Giovedì
            5: "socialità e collaborazioni",      # Venerdì
            6: "benessere e svago"               # Sabato
        }
        
        giorno_corrente = datetime.now().weekday()
        return focus_settimanale[giorno_corrente]

    def _costruisci_prompt(self, dati_utente: Dict[str, Any]) -> str:
        """
        Costruisce un prompt dettagliato per l'API di Anthropic, incorporando
        i dati astrologici dell'utente e le linee guida per la generazione.
        
        Args:
            dati_utente: Dizionario contenente i dati astrologici dell'utente
            
        Returns:
            str: Il prompt completo formattato per l'API
        """
        focus_giorno = self._determina_focus_giornaliero()
        
        # Costruzione del prompt con tutte le istruzioni necessarie
        prompt = f"""# ISTRUZIONI SISTEMA
Sei un rinomato astrologo con 30 anni di esperienza. Devi generare un oroscopo personalizzato seguendo queste linee guida per il tono e lo stile:
- Usa un tono positivo e incoraggiante, ma realistico
- Mantieni un linguaggio accessibile ma professionale
- Evita espressioni troppo vaghe o generiche
- Includi dettagli specifici legati alle configurazioni astrali
- Lunghezza massima: 150 parole

# DATI CLUSTER
{json.dumps(dati_utente, indent=4, ensure_ascii=False)}

# STRUTTURA OUTPUT
Genera un oroscopo giornaliero che includa:
1. Panoramica generale (2-3 frasi)
2. Focus specifico su: {focus_giorno} (1-2 frasi)
3. Consiglio personalizzato basato sui dati utente (1-2 frasi)
4. Numeri fortunati del giorno

# VINCOLI IMPORTANTI
- Non menzionare mai esplicitamente che l'oroscopo è generato da AI
- Evita previsioni troppo specifiche su salute o decisioni finanziarie
- Mantieni coerenza con le letture precedenti
- Non contraddire i principi astrologici fondamentali
- Assicurati che i consigli siano sempre costruttivi e realizzabili

Genera l'oroscopo seguendo queste linee guida."""

        return prompt

    def genera_oroscopo(self, dati_utente: Dict[str, Any]) -> Dict[str, str]:
        """
        Genera un oroscopo personalizzato utilizzando l'API di Anthropic.
        
        Args:
            dati_utente: Dizionario contenente i dati astrologici dell'utente
            
        Returns:
            Dict[str, str]: Dizionario contenente il testo dell'oroscopo e i numeri fortunati
        """
        try:
            # Preparazione e invio della richiesta all'API
            prompt = self._costruisci_prompt(dati_utente)
            
            # Generazione dell'oroscopo tramite API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.7,  # Bilanciamento tra creatività e coerenza
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Estrazione e formattazione della risposta
            # La risposta è strutturata come una lista di contenuti
            contenuto = message.content[0].text
            
            # Separazione del testo dell'oroscopo dai numeri fortunati
            parti = contenuto.split("Numeri fortunati:")
            
            # Creazione del dizionario di risposta
            oroscopo = {
                "testo": parti[0].strip(),
                "numeri_fortunati": parti[1].strip() if len(parti) > 1 else "Non disponibili"
            }
            
            return oroscopo
            
        except Exception as e:
            # Log dell'errore per debugging
            print(f"Errore dettagliato nella generazione dell'oroscopo: {str(e)}")
            
            # Notifica all'utente attraverso l'interfaccia Streamlit
            st.error(f"Errore nella generazione dell'oroscopo: {str(e)}")
            
            # Restituzione di una risposta di fallback
            return {
                "testo": "Mi dispiace, si è verificato un errore nella generazione dell'oroscopo. "
                        "Per favore, riprova più tardi.",
                "numeri_fortunati": "Non disponibili"
            }

# Esempio di utilizzo della classe
"""
# Nel tuo streamlit_app.py:

try:
    # Inizializzazione del generatore
    generatore = GeneratoreOroscopo()
    
    # Generazione dell'oroscopo con dati di esempio
    dati_utente = {
        "segno_zodiacale": "Ariete",
        "ascendente": "Leone",
        "gruppo_energia": "Fuoco dominante",
        "fase_lunare": "Luna Crescente",
        "età": 34,
        "pianeti_rilevanti": ["Marte in Capricorno", "Venere in Pesci"]
    }
    
    # Generazione e visualizzazione dell'oroscopo
    with st.spinner("Generazione oroscopo in corso..."):
        oroscopo = generatore.genera_oroscopo(dati_utente)
    
    st.write("### Il tuo oroscopo personalizzato")
    st.write(oroscopo["testo"])
    st.write(f"**Numeri fortunati**: {oroscopo['numeri_fortunati']}")
    
except Exception as e:
    st.error("Errore nella generazione dell'oroscopo. "
             "Verifica la configurazione e riprova.")
"""