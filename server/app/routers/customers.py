from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..database import get_db
from ..schemas import CustomerCreate, CustomerUpdate, CustomerResponse, PaginationParams, PaginatedResponse
import sqlite3

router = APIRouter()

@router.post("/customers", response_model=CustomerResponse, status_code=201)
def create_customer(customer: CustomerCreate):
    with get_db() as db:
        # Check for phone number uniqueness
        if customer.Phone:
            cur = db.execute('SELECT Id FROM customers WHERE Phone = ? AND DeletedAt IS NULL', (customer.Phone,))
            if cur.fetchone():
                raise HTTPException(status_code=409, detail=f'Phone number {customer.Phone} already exists')

        try:
            cur = db.execute(
                'INSERT INTO customers (Name, Phone, Balance, Notes, Disabled) VALUES (?, ?, ?, ?, ?)',
                (customer.Name, customer.Phone, customer.Balance, customer.Notes, customer.Disabled)
            )
            db.commit()
            
            # Fetch the created customer
            cur = db.execute('SELECT * FROM customers WHERE rowid = ?', (cur.lastrowid,))
            new_customer = cur.fetchone()
            if new_customer:
                return dict(new_customer)
            raise HTTPException(status_code=500, detail="Failed to create customer")
        except sqlite3.IntegrityError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.get("/customers", response_model=PaginatedResponse)
def list_customers(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    pagination = PaginationParams(page=page, limit=limit)
    
    with get_db() as db:
        # Count total records
        count_cur = db.execute('SELECT COUNT(Id) FROM customers WHERE DeletedAt IS NULL')
        total_records = count_cur.fetchone()[0]

        # Fetch paginated data
        cur = db.execute(
            'SELECT * FROM customers WHERE DeletedAt IS NULL ORDER BY CreatedDate DESC LIMIT ? OFFSET ?',
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

@router.get("/customers/search", response_model=PaginatedResponse)
def search_customers(q: str = Query(..., min_length=1), page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    if not q:
        raise HTTPException(status_code=400, detail="Search query 'q' is required")
    
    pagination = PaginationParams(page=page, limit=limit)
    like_query = f'%{q}%'
    
    with get_db() as db:
        # Count total records
        count_cur = db.execute(
            'SELECT COUNT(Id) FROM customers WHERE (Name LIKE ? OR Phone LIKE ?) AND DeletedAt IS NULL',
            (like_query, like_query)
        )
        total_records = count_cur.fetchone()[0]

        # Fetch paginated data
        cur = db.execute(
            'SELECT * FROM customers WHERE (Name LIKE ? OR Phone LIKE ?) AND DeletedAt IS NULL ORDER BY Name LIMIT ? OFFSET ?',
            (like_query, like_query, pagination.limit, pagination.offset)
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

@router.get("/customers/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str):
    with get_db() as db:
        cur = db.execute('SELECT * FROM customers WHERE Id = ? AND DeletedAt IS NULL', (customer_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Customer not found')
        return dict(row)

@router.put("/customers/{customer_id}", response_model=CustomerResponse)
def update_customer(customer_id: str, customer: CustomerUpdate):
    with get_db() as db:
        # Check if customer exists
        cur = db.execute('SELECT Id FROM customers WHERE Id = ? AND DeletedAt IS NULL', (customer_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Customer not found')

        # Build update query
        fields = []
        params = []
        for key, value in customer.dict(exclude_unset=True).items():
            fields.append(f"{key} = ?")
            params.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail='No fields to update')

        params.append(customer_id)
        db.execute(f'UPDATE customers SET {", ".join(fields)} WHERE Id = ?', params)
        db.commit()

        # Return updated customer
        cur = db.execute('SELECT * FROM customers WHERE Id = ?', (customer_id,))
        return dict(cur.fetchone())

@router.delete("/customers/{customer_id}")
def delete_customer(customer_id: str):
    with get_db() as db:
        db.execute('UPDATE customers SET DeletedAt = CURRENT_TIMESTAMP WHERE Id = ?', (customer_id,))
        db.commit()
        return {"message": "Customer deleted successfully"}