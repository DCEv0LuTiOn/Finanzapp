from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class KontoinhaberDTO: # Datentransfer Objekt User
    # Optional ist wenn felder nicht befüllt werden sind sie None
    ID: Optional[int] = None
    Vorname: Optional[str] = None
    Nachname: Optional[str] = None
    Email: Optional[str] = None  
    Passwort: Optional[str] = None