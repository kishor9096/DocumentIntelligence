resume_schema = {
    "name": "string",
    "highest_qualification": "string",
    "address": "string",
    "email_id": "string",
    "contact_number": "string",
    "skills": ["string"],
    "employers_details": [
        {
            "employer_name": "string",
            "from_date": "string",  # Format: YYYY-MM-DD
            "to_date": "string",  # Format: YYYY-MM-DD
            "current_employer": "boolean",
            "city": "string",
            "state": "string"
        }
    ]
}

invoice_schema = {
    "invoice_number": "string",
    "date": "string",  # Format: YYYY-MM-DD
    "total_amount": "number",
    "items": [
        {
            "description": "string",
            "quantity": "number",
            "price": "number"
        }
    ]
}

receipt_schema = {
    "receipt_number": "string",
    "date": "string",  # Format: YYYY-MM-DD
    "total_amount": "number",
    "items": [
        {
            "description": "string",
            "quantity": "number",
            "price": "number"
        }
    ]
}

report_schema = {
    "report_id": "string",
    "title": "string",
    "author": "string",
    "date": "string",  # Format: YYYY-MM-DD
    "content_summary": "string"
}

# New schemas for ID documents
id_document_schema = {
    "document_type": "string",
    "issued_by": "string",
    "issue_date": "string",  # Format: YYYY-MM-DD
    "expiration_date": "string",  # Optional, Format: YYYY-MM-DD
    "holder_name": "string",
    "holder_photo": "string",  # URL or base64 string of the photo
}

# Passport Schema
passport_schema = {
    **id_document_schema,
    "passport_number": "string",
    "nationality": "string",
    "date_of_birth": "string",  # Format: YYYY-MM-DD
    "gender": "string",  # Optional
}

# Driver License Schema
driver_license_schema = {
    **id_document_schema,
    "license_number": "string",
    "state": "string",
    "date_of_birth": "string",  # Format: YYYY-MM-DD
    "gender": "string",  # Optional
}

# National ID Schema
national_id_schema = {
    **id_document_schema,
    "national_id_number": "string",
    "country_of_issue": "string",  # Country that issued the ID
}

# Additional U.S. and Non-U.S. ID Document Schemas
# Voter ID Schema
voter_id_schema = {
    **id_document_schema,
    "voter_id_number": "string",
    "state": "string",
}

# Military ID Schema
military_id_schema = {
    **id_document_schema,
    "military_id_number": "string",
    "branch_of_service": "string",
}

# Green Card Schema (Permanent Resident Card)
green_card_schema = {
    **id_document_schema,
    "alien_registration_number": "string",
    "expiration_date": "string",  # Format: YYYY-MM-DD
}

# List of supported ID documents
ID_DOCUMENTS = {
    "passport": passport_schema,
    "driver_license": driver_license_schema,
    "national_id": national_id_schema,
    "voter_id": voter_id_schema,
    "military_id": military_id_schema,
    "green_card": green_card_schema,
} 