from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# Constants
PAYMENT_MODES = ['bill', 'cash', 'upi', 'cheque', 'neft']
CERT_STATUS = ['pending', 'completed', 'cancelled']

class CustomerBase(BaseModel):
    Name: str = Field(..., min_length=1)
    Phone: Optional[str] = None
    Balance: float = Field(0.00, ge=0)
    Notes: Optional[str] = None
    Disabled: bool = False

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    Name: Optional[str] = Field(None, min_length=1)
    Phone: Optional[str] = None
    Balance: Optional[float] = Field(None, ge=0)
    Notes: Optional[str] = None
    Disabled: Optional[bool] = None

class CustomerResponse(CustomerBase):
    Id: str
    CreatedDate: datetime
    LastModifiedDate: datetime
    DeletedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class CreditHistoryBase(BaseModel):
    CustomerId: str
    Type: str
    Amount: float = Field(..., gt=0)
    ModeOfPayment: str

    @validator('Type')
    def validate_type(cls, v):
        if v not in ['credit', 'debit']:
            raise ValueError("Type must be 'credit' or 'debit'")
        return v

    @validator('ModeOfPayment')
    def validate_payment_mode(cls, v):
        if v not in PAYMENT_MODES:
            raise ValueError(f"ModeOfPayment must be one of {PAYMENT_MODES}")
        return v

class CreditHistoryCreate(CreditHistoryBase):
    pass

class CreditHistoryResponse(CreditHistoryBase):
    Id: str
    PreviousBalance: float
    CreatedDate: datetime
    LastModifiedDate: datetime
    DeletedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class CertificateBase(BaseModel):
    CustomerId: Optional[str] = None
    Status: str = "pending"
    Data: Optional[str] = None
    ModeOfPayment: str
    Total: float = Field(..., ge=0)

    @validator('Status')
    def validate_status(cls, v):
        if v not in CERT_STATUS:
            raise ValueError(f"Status must be one of {CERT_STATUS}")
        return v

    @validator('ModeOfPayment')
    def validate_payment_mode(cls, v):
        if v not in PAYMENT_MODES:
            raise ValueError(f"ModeOfPayment must be one of {PAYMENT_MODES}")
        return v

class GoldCertificateCreate(CertificateBase):
    GST: float = Field(0.00, ge=0)
    GSTBillNumber: Optional[str] = None
    TotalTax: float = Field(0.00, ge=0)

class GoldCertificateResponse(GoldCertificateCreate):
    Id: str
    CreatedDate: datetime
    LastModifiedDate: datetime
    DeletedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class GoldTestCreate(CertificateBase):
    pass

class GoldTestResponse(GoldTestCreate):
    Id: str
    CreatedDate: datetime
    LastModifiedDate: datetime
    DeletedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class PhotoCertificateCreate(CertificateBase):
    Media: Optional[str] = None
    GST: float = Field(0.00, ge=0)
    GSTBillNumber: Optional[str] = None
    TotalTax: float = Field(0.00, ge=0)

class PhotoCertificateResponse(PhotoCertificateCreate):
    Id: str
    CreatedDate: datetime
    LastModifiedDate: datetime
    DeletedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class SilverCertificateCreate(CertificateBase):
    GST: float = Field(0.00, ge=0)
    GSTBillNumber: Optional[str] = None
    TotalTax: float = Field(0.00, ge=0)

class SilverCertificateResponse(SilverCertificateCreate):
    Id: str
    CreatedDate: datetime
    LastModifiedDate: datetime
    DeletedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class WeightLossHistoryBase(BaseModel):
    CustomerId: str
    Amount: float = Field(..., gt=0)
    ModeOfPayment: str

    @validator('ModeOfPayment')
    def validate_payment_mode(cls, v):
        if v not in PAYMENT_MODES:
            raise ValueError(f"ModeOfPayment must be one of {PAYMENT_MODES}")
        return v

class WeightLossHistoryCreate(WeightLossHistoryBase):
    pass

class WeightLossHistoryResponse(WeightLossHistoryBase):
    Id: str
    CreatedDate: datetime
    LastModifiedDate: datetime
    DeletedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class GlobalSettingBase(BaseModel):
    Key: str = Field(..., min_length=1)
    Value: Optional[str] = None

class GlobalSettingCreate(GlobalSettingBase):
    pass

class GlobalSettingResponse(GlobalSettingBase):
    Id: str
    CreatedDate: datetime
    LastModifiedDate: datetime
    DeletedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class GlobalSettingUpdate(BaseModel):
    Value: str

class PaginationParams:
    def __init__(
        self,
        page: int = 1,
        limit: int = 20
    ):
        self.page = max(1, page)
        self.limit = max(1, min(limit, 100))
        self.offset = (self.page - 1) * self.limit

class PaginatedResponse(BaseModel):
    data: List[Any]
    pagination: Dict[str, Any]