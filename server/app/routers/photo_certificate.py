from fastapi import APIRouter, HTTPException, Query
from ..database import get_db
from ..schemas import PhotoCertificateCreate, PhotoCertificateResponse, PaginationParams, PaginatedResponse
import sqlite3

router = APIRouter()

@router.post("/photocertificate", response_model=PhotoCertificateResponse, status_code=201)
def create_photo_certificate(certificate: PhotoCertificateCreate):
    with get_db() as db:
        # Validate customer if provided
        if certificate.CustomerId:
            cur = db.execute('SELECT Id FROM customers WHERE Id = ? AND DeletedAt IS NULL', (certificate.CustomerId,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail='Customer not found')

        try:
            cur = db.execute(
                """INSERT INTO photocertificate 
                (CustomerId, Media, Status, Data, ModeOfPayment, Total, GST, GSTBillNumber, TotalTax) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    certificate.CustomerId, certificate.Media, certificate.Status,
                    certificate.Data, certificate.ModeOfPayment, certificate.Total,
                    certificate.GST, certificate.GSTBillNumber, certificate.TotalTax
                )
            )
            db.commit()
            
            cur = db.execute('SELECT * FROM photocertificate WHERE rowid = ?', (cur.lastrowid,))
            new_cert = cur.fetchone()
            if new_cert:
                return dict(new_cert)
            raise HTTPException(status_code=500, detail="Failed to create photo certificate")
        except sqlite3.IntegrityError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.get("/photocertificate", response_model=PaginatedResponse)
def list_photo_certificates(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    pagination = PaginationParams(page=page, limit=limit)
    
    with get_db() as db:
        count_cur = db.execute('SELECT COUNT(Id) FROM photocertificate WHERE DeletedAt IS NULL')
        total_records = count_cur.fetchone()[0]

        cur = db.execute(
            'SELECT * FROM photocertificate WHERE DeletedAt IS NULL ORDER BY CreatedDate DESC LIMIT ? OFFSET ?',
            (pagination.limit, pagination.offset)
        )
        rows = [dict(row) for row in cur.fetchall()]

        return {
            "data": rows,
            "pagination": {
                "total_records": total_records,
                "current_page": pagination.page,
                "total_pages": (total_records + pagination.limit - 1) // pagination.limit if total_records > 0 else 0,
                "limit": pagination.limit
            }
        }

@router.get("/photocertificate/{certificate_id}", response_model=PhotoCertificateResponse)
def get_photo_certificate(certificate_id: str):
    with get_db() as db:
        cur = db.execute('SELECT * FROM photocertificate WHERE Id = ? AND DeletedAt IS NULL', (certificate_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Photo certificate not found')
        return dict(row)

@router.put("/photocertificate/{certificate_id}", response_model=PhotoCertificateResponse)
def update_photo_certificate(certificate_id: str, certificate: PhotoCertificateCreate):
    with get_db() as db:
        # Check if certificate exists
        cur = db.execute('SELECT Id FROM photocertificate WHERE Id = ? AND DeletedAt IS NULL', (certificate_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Photo certificate not found')

        # Build update query
        fields = []
        params = []
        for key, value in certificate.dict(exclude_unset=True).items():
            fields.append(f"{key} = ?")
            params.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail='No fields to update')

        params.append(certificate_id)
        db.execute(f'UPDATE photocertificate SET {", ".join(fields)} WHERE Id = ?', params)
        db.commit()

        # Return updated certificate
        cur = db.execute('SELECT * FROM photocertificate WHERE Id = ?', (certificate_id,))
        return dict(cur.fetchone())

@router.delete("/photocertificate/{certificate_id}")
def delete_photo_certificate(certificate_id: str):
    with get_db() as db:
        db.execute('UPDATE photocertificate SET DeletedAt = CURRENT_TIMESTAMP WHERE Id = ?', (certificate_id,))
        db.commit()
        return {"message": "Photo certificate deleted successfully"}