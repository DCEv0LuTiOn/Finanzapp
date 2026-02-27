from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class UserDTO: # Datentransfer Objekt User
    # Optional ist wenn felder nicht befüllt werden sind sie None
    id: Optional[int] = None
    surname: Optional[str] = None
    first_name: Optional[str] = None
    email: Optional[str] = None  
    creation_date: Optional[str] = None