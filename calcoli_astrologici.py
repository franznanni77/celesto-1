import datetime
from calendar import monthrange
import re
from datetime import date

def calcola_eta(data_nascita):
    """
    Calcola l'età esatta di una persona dalla data di nascita.
    """
    oggi = date.today()
    eta = oggi.year - data_nascita.year - ((oggi.month, oggi.day) < (data_nascita.month, data_nascita.day))
    return eta

def valida_numero_cellulare(numero):
    """
    Valida un numero di cellulare italiano.
    """
    numero_pulito = re.sub(r'[\s\-\(\)]', '', numero)
    pattern_completo = r'^(?:(?:\+39|0039))?3\d{8,9}$'
    
    if not numero_pulito:
        return False, "Il numero non può essere vuoto"
    
    if not re.match(pattern_completo, numero_pulito):
        return False, "Formato non valido. Esempi corretti: +39 345 1234567, 3451234567"
    
    numero_senza_prefisso = numero_pulito.replace('+39', '').replace('0039', '')
    if len(numero_senza_prefisso) not in [9, 10]:
        return False, "Il numero deve avere 9 o 10 cifre dopo il prefisso"
        
    return True, "Numero valido"

def calcola_segno_zodiacale(data):
    """
    Calcola il segno zodiacale in base alla data di nascita
    """
    giorno = data.day
    mese = data.month
    
    if (mese == 3 and giorno >= 21) or (mese == 4 and giorno <= 19):
        return "Ariete"
    elif (mese == 4 and giorno >= 20) or (mese == 5 and giorno <= 20):
        return "Toro"
    elif (mese == 5 and giorno >= 21) or (mese == 6 and giorno <= 20):
        return "Gemelli"
    elif (mese == 6 and giorno >= 21) or (mese == 7 and giorno <= 22):
        return "Cancro"
    elif (mese == 7 and giorno >= 23) or (mese == 8 and giorno <= 22):
        return "Leone"
    elif (mese == 8 and giorno >= 23) or (mese == 9 and giorno <= 22):
        return "Vergine"
    elif (mese == 9 and giorno >= 23) or (mese == 10 and giorno <= 22):
        return "Bilancia"
    elif (mese == 10 and giorno >= 23) or (mese == 11 and giorno <= 21):
        return "Scorpione"
    elif (mese == 11 and giorno >= 22) or (mese == 12 and giorno <= 21):
        return "Sagittario"
    elif (mese == 12 and giorno >= 22) or (mese == 1 and giorno <= 19):
        return "Capricorno"
    elif (mese == 1 and giorno >= 20) or (mese == 2 and giorno <= 18):
        return "Acquario"
    else:
        return "Pesci"

def calcola_correzione_precessionale(anno):
    """
    Calcola la correzione dovuta alla precessione degli equinozi.
    """
    ANNO_RIFERIMENTO = 2000
    GRADI_PER_ANNO = 1 / 72
    
    differenza_anni = anno - ANNO_RIFERIMENTO
    spostamento_gradi = differenza_anni * GRADI_PER_ANNO
    spostamento_ore = (spostamento_gradi * 24) / 360
    
    return spostamento_ore

def calcola_ascendente(data, ora):
    """
    Calcola l'ascendente basato su data e ora di nascita
    """
    ora_decimale = ora.hour + ora.minute / 60.0
    mese = data.month
    anno = data.year
    
    aggiustamento_mensile = (mese - 1) * 2
    correzione_precessionale = calcola_correzione_precessionale(anno)
    ora_aggiustata = (ora_decimale + aggiustamento_mensile + correzione_precessionale) % 24
    
    if 6 <= ora_aggiustata < 8:
        return "Leone"
    elif 8 <= ora_aggiustata < 10:
        return "Vergine"
    elif 10 <= ora_aggiustata < 12:
        return "Bilancia"
    elif 12 <= ora_aggiustata < 14:
        return "Scorpione"
    elif 14 <= ora_aggiustata < 16:
        return "Sagittario"
    elif 16 <= ora_aggiustata < 18:
        return "Capricorno"
    elif 18 <= ora_aggiustata < 20:
        return "Acquario"
    elif 20 <= ora_aggiustata < 22:
        return "Pesci"
    elif 22 <= ora_aggiustata < 24:
        return "Ariete"
    elif 0 <= ora_aggiustata < 2:
        return "Toro"
    elif 2 <= ora_aggiustata < 4:
        return "Gemelli"
    else:
        return "Cancro"

def calcola_fase_lunare(data):
    """
    Calcola la fase lunare approssimativa basata sulla data.
    """
    data_riferimento = datetime.date(2000, 1, 1)
    giorni_passati = (data - data_riferimento).days
    posizione_nel_ciclo = (giorni_passati % 30) / 30.0
    
    if 0 <= posizione_nel_ciclo < 0.125:
        return "Luna Nuova"
    elif 0.125 <= posizione_nel_ciclo < 0.375:
        return "Luna Crescente"
    elif 0.375 <= posizione_nel_ciclo < 0.625:
        return "Luna Piena"
    elif 0.625 <= posizione_nel_ciclo < 0.875:
        return "Luna Calante"
    else:
        return "Luna Nuova"

def determina_elemento_dominante(data_nascita, ora_nascita):
    """
    Determina l'elemento dominante basato su data e ora di nascita.
    """
    somma = data_nascita.day + ora_nascita.hour
    
    if somma % 4 == 0:
        return "Fuoco"
    elif somma % 4 == 1:
        return "Terra"
    elif somma % 4 == 2:
        return "Aria"
    else:
        return "Acqua"

def calcola_pianeti_rilevanti(data):
    """
    Determina le posizioni planetarie rilevanti per la data specificata.
    """
    mese = data.month
    pianeti = []
    
    if mese in [12, 1, 2]:
        pianeti.extend(["Saturno in Capricorno", "Mercurio in Acquario"])
    elif mese in [3, 4, 5]:
        pianeti.extend(["Marte in Ariete", "Venere in Toro"])
    elif mese in [6, 7, 8]:
        pianeti.extend(["Sole in Leone", "Mercurio in Gemelli"])
    else:
        pianeti.extend(["Venere in Bilancia", "Plutone in Scorpione"])
        
    if data.day <= 10:
        pianeti.append("Luna in Cancro")
    elif data.day <= 20:
        pianeti.append("Giove in Sagittario")
    else:
        pianeti.append("Nettuno in Pesci")
            
    return pianeti[:2]

def genera_dati_astrologici(data_nascita, ora_nascita):
    """
    Genera un dizionario completo con tutti i dati astrologici.
    """
    eta = calcola_eta(data_nascita)
    segno = calcola_segno_zodiacale(data_nascita)
    ascendente = calcola_ascendente(data_nascita, ora_nascita)
    elemento = determina_elemento_dominante(data_nascita, ora_nascita)
    gruppo_energia = f"{elemento} dominante"
    fase_lunare = calcola_fase_lunare(data_nascita)
    pianeti = calcola_pianeti_rilevanti(data_nascita)
    
    return {
        "eta": eta,
        "segno_zodiacale": segno,
        "ascendente": ascendente,
        "gruppo_energia": gruppo_energia,
        "fase_lunare": fase_lunare,
        "pianeti_rilevanti": pianeti
    }