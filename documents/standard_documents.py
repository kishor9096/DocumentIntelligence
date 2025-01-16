from pydantic import BaseModel
from typing import List, Optional

class StandardDocument(BaseModel):
    document_type: str
    title: str
    author: str
    publication_date: str
    content_summary: str

class Invoice(StandardDocument):
    invoice_number: str
    total_amount: float

class Receipt(StandardDocument):
    receipt_number: str
    total_amount: float

class Report(StandardDocument):
    report_id: str
    department: str

# New Resume schema
class EmployerDetail(BaseModel):
    employer_name: str
    from_date: str  # Format: YYYY-MM-DD
    to_date: str  # Format: YYYY-MM-DD
    current_employer: bool
    city: str
    state: str

class Resume(StandardDocument):
    name: str
    highest_qualification: str
    address: str
    email_id: str
    contact_number: str
    skills: List[str]  # List of skills
    employers_details: List[EmployerDetail]  # List of employer details

# List of supported standard documents
STANDARD_DOCUMENTS = [
    Invoice,
    Receipt,
    Report,
    Resume  # Add Resume to the list of standard documents
] 