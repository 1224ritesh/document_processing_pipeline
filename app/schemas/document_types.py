from enum import Enum


class DocumentType(str, Enum):

    CLAIM_FORM = "claim_form"
    CHEQUE_OR_BANK_DETAILS = "cheque_or_bank_details"
    IDENTITY_DOCUMENT = "identity_document"
    ITEMIZED_BILL = "itemized_bill"
    DISCHARGE_SUMMARY = "discharge_summary"
    PRESCRIPTION = "prescription"
    INVESTIGATION_REPORT = "investigation_report"
    CASH_RECEIPT = "cash_receipt"
    OTHER = "other"
