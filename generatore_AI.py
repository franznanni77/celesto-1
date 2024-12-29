def genera_oroscopo(self, dati_utente: Dict[str, Any]) -> Dict[str, str]:
    """
    Genera un oroscopo personalizzato utilizzando l'API di Anthropic e formatta il risultato.
    Questa è una versione sincrona della funzione che gestisce correttamente la risposta dell'API.
    
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
        
        # Estraiamo il contenuto del messaggio
        # La risposta è un oggetto Message, dobbiamo accedere al suo contenuto
        contenuto = message.content[0].text
        
        # Ora possiamo dividere il contenuto
        parti = contenuto.split("Numeri fortunati:")
        
        # Creiamo il dizionario di risposta
        oroscopo = {
            "testo": parti[0].strip(),
            "numeri_fortunati": parti[1].strip() if len(parti) > 1 else "Non disponibili"
        }
        
        return oroscopo
        
    except Exception as e:
        # Log dell'errore per debug
        print(f"Errore dettagliato: {str(e)}")
        
        # In caso di errore, restituiamo un messaggio appropriato
        st.error(f"Errore nella generazione dell'oroscopo: {str(e)}")
        return {
            "testo": "Mi dispiace, si è verificato un errore nella generazione dell'oroscopo. "
                    "Per favore, riprova più tardi.",
            "numeri_fortunati": "Non disponibili"
        }