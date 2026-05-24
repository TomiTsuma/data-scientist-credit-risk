from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str
    version: str


class SegmentRequest(BaseModel):
    customer_id: str | None = None
    age: int = Field(30, ge=18, le=90)
    account_age_days: int = Field(365, ge=0)
    financed_amount: float = Field(150000, ge=0)
    outstanding_balance: float = Field(80000, ge=0)
    repayment_progress: float = Field(0.5, ge=0, le=1)
    arrears_balance: float = Field(0, ge=0)
    days_past_due: int = Field(0, ge=0)
    is_in_arrears: int = Field(0, ge=0, le=1)
    is_default: int = Field(0, ge=0, le=1)
    is_healthy: int = Field(1, ge=0, le=1)
    country_name: str = "Kenya"
    gender: str = "Male"
    age_bucket: str = "25-34"
    payment_type: str = "PAYG"
    product_tier: str = "New"
    lead_source: str = "Agent"
    installation_delay_days: float = 7
    days_to_sale: float = 14


class SegmentResponse(BaseModel):
    segment_id: int
    segment_name: str
    customer_id: str | None = None
