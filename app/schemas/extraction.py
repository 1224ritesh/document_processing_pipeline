from pydantic import BaseModel, Field
from app.schemas.document_types import DocumentType


#Segregator

class PageClassification(BaseModel):
    page_number: int = Field(description="Zero-indexed page number")
    document_type: DocumentType = Field(description="Classified document type")
    confidence: float = Field(ge=0, le=1, description="Classification confidence")


class SegregationResult(BaseModel):
    classifications: list[PageClassification]


#ID Agent 

class IdentityExtraction(BaseModel):
    patient_name: str | None = Field(default=None, description="Full name of the patient")
    date_of_birth: str | None = Field(default=None, description="Date of birth")
    gender: str | None = Field(default=None, description="Gender")
    id_number: str | None = Field(default=None, description="Government ID number")
    policy_number: str | None = Field(default=None, description="Insurance policy number")
    insurer_name: str | None = Field(default=None, description="Insurance company name")
    contact_number: str | None = Field(default=None, description="Phone number")
    address: str | None = Field(default=None, description="Address")


#Discharge Summary Agent

class DischargeSummaryExtraction(BaseModel):
    patient_name: str | None = Field(default=None, description="Patient name")
    admission_date: str | None = Field(default=None, description="Date of admission")
    discharge_date: str | None = Field(default=None, description="Date of discharge")
    diagnosis: str | None = Field(default=None, description="Primary diagnosis")
    secondary_diagnosis: list[str] = Field(default_factory=list, description="Secondary diagnoses")
    procedures: list[str] = Field(default_factory=list, description="Procedures performed")
    treating_physician: str | None = Field(default=None, description="Treating physician name")
    physician_notes: str | None = Field(default=None, description="Physician notes or summary")


#Itemized Bill Agent

class BillItem(BaseModel):
    description: str = Field(description="Item or service description")
    quantity: int | None = Field(default=None, description="Quantity")
    unit_price: float | None = Field(default=None, description="Unit price")
    amount: float = Field(description="Total amount for this item")


class ItemizedBillExtraction(BaseModel):
    items: list[BillItem] = Field(default_factory=list, description="Line items")
    subtotal: float | None = Field(default=None, description="Subtotal before taxes/discounts")
    tax: float | None = Field(default=None, description="Tax amount")
    discount: float | None = Field(default=None, description="Discount amount")
    total_amount: float | None = Field(default=None, description="Final total amount")
    currency: str = Field(default="INR", description="Currency code")


#Final Output

class ProcessingResult(BaseModel):
    claim_id: str
    segregation: dict[str, list[int]] = Field(
        description="Mapping of document type to page numbers"
    )
    identity: IdentityExtraction | None = None
    discharge_summary: DischargeSummaryExtraction | None = None
    itemized_bill: ItemizedBillExtraction | None = None
