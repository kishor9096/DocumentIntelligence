from pydantic import BaseModel
from typing import List, Optional

class IDDocument(BaseModel):
    document_type: str
    issued_by: str
    issue_date: str
    expiration_date: Optional[str]
    holder_name: str
    holder_photo: str  # URL or base64 string of the photo

class Passport(IDDocument):
    passport_number: str
    nationality: str

class DriverLicense(IDDocument):
    license_number: str
    state: str

class NationalID(IDDocument):
    national_id_number: str

# List of supported ID documents
ID_DOCUMENTS = [
    Passport,
    DriverLicense,
    NationalID
] 