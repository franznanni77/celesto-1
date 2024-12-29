"""
whatsapp_sender.py
-----------------
Modulo per l'invio di messaggi WhatsApp utilizzando l'API UltraMsg.
Gestisce l'invio dell'oroscopo personalizzato al numero di telefono fornito.
"""

import http.client
import ssl
import json
from typing import Dict, Optional

class WhatsAppSender:
    """
    Classe per gestire l'invio di messaggi WhatsApp tramite UltraMsg API.
    """
    
    def __init__(self, token: str = "vtn2mmq726dg7w07"):
        """
        Inizializza il sender con il token dell'API.
        
        Args:
            token: Token di autenticazione per UltraMsg API
        """
        self.token = token
        self.base_url = "api.ultramsg.com"
        self.instance = "instance13878"
    
    def _formatta_numero(self, numero: str) -> str:
        """
        Formatta il numero di telefono nel formato richiesto dall'API.
        Rimuove spazi, trattini e assicura il prefisso internazionale.
        
        Args:
            numero: Numero di telefono da formattare
            
        Returns:
            str: Numero formattato
        """
        # Rimuove spazi, trattini e parentesi
        numero_pulito = ''.join(filter(str.isdigit, numero))
        
        # Se il numero inizia con 0039, lo sostituisce con +39
        if numero_pulito.startswith('0039'):
            numero_pulito = '+39' + numero_pulito[4:]
        # Se il numero inizia con 3 (formato italiano), aggiunge +39
        elif numero_pulito.startswith('3'):
            numero_pulito = '+39' + numero_pulito
        
        return numero_pulito

    def _prepara_messaggio(self, dati_utente: Dict, oroscopo: str) -> str:
        """
        Prepara il messaggio WhatsApp formattando i dati dell'oroscopo.
        
        Args:
            dati_utente: Dizionario contenente i dati dell'utente
            oroscopo: Testo dell'oroscopo generato
            
        Returns:
            str: Messaggio formattato
        """
        messaggio = f"""🌟 *Oroscopo Personalizzato per {dati_utente['nome']}*

*Segno Zodiacale:* {dati_utente['segno_zodiacale']}
*Ascendente:* {dati_utente['ascendente']}
*Data di Nascita:* {dati_utente['data_nascita']}

{oroscopo}

_Generato da CelestoApp_"""
        
        return messaggio

    def invia_oroscopo(self, numero_telefono: str, dati_utente: Dict, oroscopo: str) -> bool:
        """
        Invia l'oroscopo via WhatsApp al numero specificato.
        
        Args:
            numero_telefono: Numero di telefono del destinatario
            dati_utente: Dizionario contenente i dati dell'utente
            oroscopo: Testo dell'oroscopo generato
            
        Returns:
            bool: True se l'invio ha avuto successo, False altrimenti
        """
        try:
            # Formatta il numero di telefono
            numero_formattato = self._formatta_numero(numero_telefono)
            
            # Prepara il messaggio
            messaggio = self._prepara_messaggio(dati_utente, oroscopo)
            
            # Prepara la connessione
            context = ssl._create_unverified_context()
            conn = http.client.HTTPSConnection(self.base_url, context=context)
            
            # Prepara il payload
            payload = f"token={self.token}&to={numero_formattato}&body={messaggio}"
            payload = payload.encode('utf8').decode('iso-8859-1')
            
            # Imposta gli headers
            headers = {
                'content-type': "application/x-www-form-urlencoded"
            }
            
            # Invia la richiesta
            conn.request("POST", f"/{self.instance}/messages/chat", payload, headers)
            
            # Ottiene la risposta
            response = conn.getresponse()
            data = response.read()
            
            # Verifica il successo dell'invio
            risultato = json.loads(data.decode('utf-8'))
            
            if risultato.get('sent') == 'true':
                print(f"Messaggio inviato con successo a {numero_formattato}")
                return True
            else:
                print(f"Errore nell'invio del messaggio: {risultato}")
                return False
                
        except Exception as e:
            print(f"Errore durante l'invio del messaggio WhatsApp: {str(e)}")
            return False
        
        finally:
            if 'conn' in locals():
                conn.close()

# Esempio di utilizzo:
"""
sender = WhatsAppSender()
dati_esempio = {
    "nome": "Mario Rossi",
    "segno_zodiacale": "Ariete",
    "ascendente": "Leone",
    "data_nascita": "1980-04-15"
}
oroscopo_esempio = "Il tuo oroscopo personalizzato..."
risultato = sender.invia_oroscopo("+393401234567", dati_esempio, oroscopo_esempio)
"""