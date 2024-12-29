"""
generatore_AI.py
---------------
Questo modulo gestisce la generazione dell'oroscopo personalizzato utilizzando l'API di Anthropic.
La chiave API viene gestita in modo sicuro attraverso i secrets di Streamlit.
"""

import anthropic
from datetime import datetime
import json
import streamlit as st
from typing import Dict, Any

class GeneratoreOroscopo:
    """
    Classe per la generazione di oroscopi personalizzati utilizzando l'API di Anthropic.
    La classe utilizza i secrets di Streamlit per gestire in modo sicuro la chiave API.
    """
    
    def __init__(self):
        """
        Inizializza il generatore di oroscopi utilizzando la chiave API dai secrets di Streamlit.
        La chiave deve essere configurata nei secrets di Streamlit come 'anthropic_api_key'.
        """
        try:
            # Inizializziamo il client Anthropic usando la chiave dai secrets
            self.client = anthropic.Client(api_key=st.secrets["anthropic_api_key"])
            # Utilizziamo il modello più recente per risultati ottimali
            self.model = "claude-3-opus-20240229"
        except Exception as e:
            raise ValueError("Errore nell'inizializzazione del client Anthropic. "
                           "Verifica che la chiave API sia configurata correttamente "
                           "nei secrets di Streamlit.") from e
        
    def _determina_focus_giornaliero(self) -> str:
        """
        Determina il focus tematico basato sul giorno della settimana.
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
        
        return focus_settimanale[datetime.now().weekday()]

    def _costruisci_prompt(self, dati_utente: Dict[str, Any]) -> str:
        """
        Costruisce il prompt per l'API di Anthropic utilizzando i dati dell'utente.
        """
        focus_giorno = self._determina_focus_giornaliero()
        
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
        Genera un oroscopo personalizzato utilizzando l'API di Anthropic e formatta il risultato.
        Questa è una versione sincrona della funzione, che non richiede await.
        
        Args:
            dati_utente: Dizionario contenente i dati astrologici dell'utente
            
        Returns:
            Dict[str, str]: Dizionario contenente l'oroscopo e i numeri fortunati formattati
        """
        try:
            # Costruiamo il prompt e facciamo la chiamata all'API
            prompt = self._costruisci_prompt(dati_utente)
            
            # Chiamata sincrona all'API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.7,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Formattiamo l'output dividendo il testo principale dai numeri fortunati
            contenuto = message.content
            parti = contenuto.split("Numeri fortunati:")
            
            oroscopo = {
                "testo": parti[0].strip(),
                "numeri_fortunati": parti[1].strip() if len(parti) > 1 else "Non disponibili"
            }
            
            return oroscopo
            
        except Exception as e:
            # In caso di errore, registriamo l'errore e restituiamo un messaggio appropriato
            st.error(f"Errore nella generazione dell'oroscopo: {str(e)}")
            return {
                "testo": "Mi dispiace, si è verificato un errore nella generazione dell'oroscopo. "
                        "Per favore, riprova più tardi.",
                "numeri_fortunati": "Non disponibili"
            }