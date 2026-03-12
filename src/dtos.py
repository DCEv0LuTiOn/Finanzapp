from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class KontoinhaberDTO: # Datentransfer Objekt
    # Optional ist wenn felder nicht befüllt werden sind sie None
    ID: Optional[int] = None
    Vorname: Optional[str] = None
    Nachname: Optional[str] = None
    Email: Optional[str] = None  
    Passwort: Optional[str] = None

@dataclass
class KontoDTO:
    IBAN: Optional[int] = None
    BIC: Optional[str] = None
    Bank_Name: Optional[str] = None
    Konto_Name: Optional[str] = None  
    Kontoinhaber_ID: Optional[int] = None
    Saldo: Optional[float] = None
    Waehrung: Optional[str] = None

@dataclass
class KontoDTO:
    IBAN: Optional[int] = None
    BIC: Optional[str] = None
    Bank_Name: Optional[str] = None
    Konto_Name: Optional[str] = None  
    Kontoinhaber_ID: Optional[int] = None
    Saldo: Optional[float] = None
    Waehrung: Optional[str] = None

@dataclass
class BuchungsartDTO:
    ID: Optional[int] = None
    Buchungsart: Optional[str] = None

@dataclass
class KategorieDTO:
    ID: Optional[int] = None
    Bezeichnung: Optional[str] = None
    Kontoinhaber_ID: Optional[int] = None

@dataclass
class TransaktionDTO:
    ID: Optional[int] = None
    IBAN_Auftragskonto: Optional[str] = None
    IBAN_Zahlungsbeteiligter: Optional[str] = None
    Name_Zahlungsbeteiligter: Optional[str] = None
    Verwendungszweck: Optional[str] = None
    Betrag: Optional[float] = None
    Saldo_nach_Buchung: Optional[float] = None
    Transaktions_Datum: Optional[str] = None
    Buchungsart_ID: Optional[int] = None
    Kategorie_ID: Optional[int] = None
    Bemerkung: Optional[str] = None

