from dataclasses import dataclass
from typing import Optional

@dataclass
class BankDTO:
    BLZ: Optional[str] = None
    Name: Optional[str] = None

@dataclass
class WaehrungDTO:
    ID: Optional[int] = None
    Waehrung: Optional[str] = None

@dataclass
class KontoinhaberDTO:
    ID: Optional[int] = None
    Vorname: Optional[str] = None
    Nachname: Optional[str] = None
    Email: Optional[str] = None  
    Passwort: Optional[str] = None

@dataclass
class KontoDTO:
    IBAN: Optional[str] = None
    BIC: Optional[str] = None
    BLZ: Optional[str] = None
    Konto_Name: Optional[str] = None  
    Kontoinhaber_ID: Optional[int] = None
    Saldo: Optional[float] = None
    Waehrung_ID: Optional[int] = None

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

@dataclass
class DataInputDTOView:
    ID: Optional[int] = None
    IBAN_Auftragskonto: Optional[str] = None
    IBAN_Zahlungsbeteiligter: Optional[str] = None
    Name_Zahlungsbeteiligter: Optional[str] = None
    Verwendungszweck: Optional[str] = None
    Betrag: Optional[float] = None
    Saldo_nach_Buchung: Optional[float] = None
    Transaktions_Datum: Optional[str] = None
    Bemerkung: Optional[str] = None
    Kategorie: Optional[str] = None
    Buchungsart: Optional[str] = None


# @dataclass
# class KontoViewDTO:
#     IBAN: Optional[str] = None
#     BIC: Optional[str] = None
#     Bank_Name: Optional[str] = None
#     Konto_Name: Optional[str] = None  
#     Kontoinhaber_Name: Optional[str] = None
#     Saldo: Optional[float] = None
#     Waehrung: Optional[str] = None