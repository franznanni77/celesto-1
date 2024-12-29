"""
generatore_AI.py
---------------
Questo modulo implementa un generatore di oroscopi personalizzati utilizzando Claude 3.5 Haiku,
con gestione degli errori migliorata e logging dettagliato.
"""

from datetime import datetime
import json
import streamlit as st
from typing import Dict, Any
from anthropic import Anthropic

class GeneratoreOroscopo:
    """
    Classe che gestisce la generazione di oroscopi personalizzati utilizzando Claude 3.5 Haiku.
    """
    
    def __init__(self):
        """
        Inizializza il generatore di oroscopi configurando il client Anthropic.
        """
        try:
            # Verifica che la chiave API sia presente nei secrets
            if "anthropic_api_key" not in st.secrets:
                raise ValueError("La chiave API Anthropic non è configurata nei secrets di Streamlit")
            
            # Inizializzazione del client Anthropic
            self.client = Anthropic(api_key=st.secrets["anthropic_api_key"])
            self.model = "claude-3-5-haiku-20241022"
            self.max_tokens = 1024
            self.temperature = 0.75
            
            print("Inizializzazione completata con successo")
            
        except Exception as e:
            print(f"Errore durante l'inizializzazione: {str(e)}")
            raise ValueError(
                "Errore nell'inizializzazione del client Anthropic. "
                "Verifica che la chiave API sia configurata correttamente. "
                f"Dettagli: {str(e)}"
            )
    
    def _determina_focus_giornaliero(self) -> str:
        """
        Determina il focus tematico dell'oroscopo basato sul giorno della settimana.
        """
        focus_settimanale = {
            0: "riflessione e pianificazione",
            1: "carriera e ambizioni",
            2: "comunicazione e relazioni",
            3: "creatività e progetti personali",
            4: "crescita e sviluppo",
            5: "socialità e collaborazioni",
            6: "benessere e svago"
        }
        
        giorno_corrente = datetime.now().weekday()
        return focus_settimanale[giorno_corrente]

    def _costruisci_prompt(self, dati_utente: Dict[str, Any]) -> str:
        """
        Costruisce il prompt per l'API, verificando la presenza dei dati necessari.
        """
        # Verifica che i dati utente contengano le informazioni necessarie
        required_fields = ["nome", "segno_zodiacale", "ascendente", "gruppo_energia"]
        missing_fields = [field for field in required_fields if field not in dati_utente]
        
        if missing_fields:
            raise ValueError(f"Dati mancanti: {', '.join(missing_fields)}")
            
        focus_giorno = self._determina_focus_giornaliero()
        
        prompt = f"""# ISTRUZIONI SISTEMA
Sei un astrologo esperto. Genera un oroscopo personalizzato breve ma significativo:
- Tono: positivo e incoraggiante
- Stile: professionale ma accessibile
- Evita genericità
- Lunghezza: 100-150 parole
- Usa il nome della persona almeno una volta nella panoramica generale

# DATI UTENTE
{json.dumps(dati_utente, indent=4, ensure_ascii=False)}

# STRUTTURA OUTPUT
Genera in questo ordine:
1. Panoramica generale (1-2 frasi, includendo il nome della persona)
2. Focus su: {focus_giorno} (1-2 frasi)
3. Consiglio personalizzato (1 frase)
4. Numeri fortunati del giorno

# VINCOLI
- No riferimenti ad AI
- Evita previsioni su salute/finanze
- Consigli realizzabili
- Coerenza astrologica

Genera l'oroscopo mantenendo questa struttura."""

        return prompt

    def genera_oroscopo(self, dati_utente: Dict[str, Any]) -> str:
        """
        Genera un oroscopo personalizzato con gestione degli errori migliorata.
        """
        try:
            # Verifica dei dati in input
            if not isinstance(dati_utente, dict):
                raise ValueError(f"I dati utente devono essere un dizionario. Ricevuto: {type(dati_utente)}")

            # Log dei dati ricevuti (escludi informazioni sensibili)
            print(f"Generazione oroscopo per segno: {dati_utente.get('segno_zodiacale')}")
            
            # Preparazione del prompt
            prompt = self._costruisci_prompt(dati_utente)
            
            # Chiamata all'API con gestione esplicita degli errori
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                # Verifica che la risposta contenga il contenuto atteso
                if not message.content:
                    raise ValueError("La risposta dell'API non contiene contenuto")
                
                # Estrai il testo della risposta
                oroscopo = message.content[0].text
                
                # Verifica che l'oroscopo sia stato generato correttamente
                if not oroscopo or len(oroscopo) < 50:  # verifica minima lunghezza
                    raise ValueError("L'oroscopo generato è troppo corto o vuoto")
                
                return oroscopo
                
            except Exception as api_error:
                print(f"Errore durante la chiamata API: {str(api_error)}")
                raise
            
        except Exception as e:
            # Log dettagliato dell'errore
            print(f"Errore dettagliato nella generazione dell'oroscopo: {str(e)}")
            st.error(f"Errore specifico: {str(e)}")
            
            # Risposta di fallback più informativa
            return ("Mi dispiace, si è verificato un errore durante la generazione dell'oroscopo. "
                   "L'errore potrebbe essere dovuto a: \n"
                   "1. Problemi di connessione con il servizio\n"
                   "2. Dati mancanti o non validi\n"
                   "3. Configurazione non corretta\n"
                   "Per favore, verifica i dati inseriti e riprova.")