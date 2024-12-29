"""
generatore_AI.py
---------------
Questo modulo implementa un generatore di oroscopi personalizzati utilizzando Claude 3.5 Haiku,
ottimizzato per risposte rapide mantenendo alta qualità e personalizzazione.
"""

from datetime import datetime
import json
import streamlit as st
from typing import Dict, Any
from anthropic import Anthropic

class GeneratoreOroscopo:
    """
    Classe che gestisce la generazione di oroscopi personalizzati utilizzando Claude 3.5 Haiku.
    Ottimizzata per risposte rapide e fluide, mantenendo un alto livello di personalizzazione.
    """
    
    def __init__(self):
        """
        Inizializza il generatore di oroscopi configurando il client Anthropic.
        Utilizza Claude 3.5 Haiku per performance ottimali.
        
        Raises:
            ValueError: Se la chiave API non è configurata correttamente nei secrets di Streamlit.
        """
        try:
            # Inizializzazione del client Anthropic con la chiave dai secrets di Streamlit
            self.client = Anthropic(api_key=st.secrets["anthropic_api_key"])
            
            # Utilizziamo Claude 3.5 Haiku per risposte rapide
            self.model = "claude-3-5-haiku-20241022"
            
            # Configurazione ottimizzata per Haiku
            self.max_tokens = 1024  # Ridotto per risposte più concise
            self.temperature = 0.75  # Leggermente aumentata per maggiore creatività
            
        except Exception as e:
            raise ValueError(
                "Errore nell'inizializzazione del client Anthropic. "
                "Verifica che la chiave API sia configurata correttamente "
                f"nei secrets di Streamlit. Errore: {str(e)}"
            )
    
    def _determina_focus_giornaliero(self) -> str:
        """
        Determina il focus tematico dell'oroscopo basato sul giorno della settimana.
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
        Costruisce un prompt ottimizzato per Claude 3.5 Haiku, mantenendo la concisione
        ma garantendo la personalizzazione dell'oroscopo.
        """
        focus_giorno = self._determina_focus_giornaliero()
        
        # Prompt ottimizzato per risposte più concise ma significative
        prompt = f"""# ISTRUZIONI SISTEMA
Sei un astrologo esperto. Genera un oroscopo personalizzato breve ma significativo:
- Tono: positivo e incoraggiante
- Stile: professionale ma accessibile
- Evita genericità
- Lunghezza: 100-150 parole

# DATI UTENTE
{json.dumps(dati_utente, indent=4, ensure_ascii=False)}

# STRUTTURA OUTPUT
Genera in questo ordine:
1. Panoramica generale (1-2 frasi)
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

    def genera_oroscopo(self, dati_utente: Dict[str, Any]) -> Dict[str, str]:
        """
        Genera un oroscopo personalizzato utilizzando Claude 3.5 Haiku.
        Ottimizzato per risposte rapide e di alta qualità.
        
        Args:
            dati_utente: Dizionario contenente i dati astrologici dell'utente
            
        Returns:
            Dict[str, str]: Dizionario contenente il testo dell'oroscopo e i numeri fortunati
        """
        try:
            # Preparazione e invio della richiesta all'API
            prompt = self._costruisci_prompt(dati_utente)
            
            # Generazione dell'oroscopo con parametri ottimizzati per Haiku
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
            
            # Estrazione e formattazione della risposta
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
            # Log dettagliato dell'errore
            print(f"Errore nella generazione dell'oroscopo: {str(e)}")
            
            # Notifica all'utente
            st.error("Si è verificato un errore nella generazione dell'oroscopo.")
            
            # Risposta di fallback
            return {
                "testo": "Mi dispiace, si è verificato un errore nella generazione dell'oroscopo. "
                        "Per favore, riprova più tardi.",
                "numeri_fortunati": "Non disponibili"
            }