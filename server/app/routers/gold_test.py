from fastapi import APIRouter, HTTPException, Query
from ..database import get_db
from ..schemas import GoldTestCreate, GoldTestResponse, PaginationParams, PaginatedResponse
import sqlite3

router = APIRouter()

@router.post("/goldtest", response_model=GoldTestResponse, status_code=201)
def create_gold_test(test: GoldTestCreate):
    with get_db() as db:
        # Validate customer if provided
        if test.CustomerId:
            cur = db.execute('SELECT Id FROM customers WHERE Id = ? AND DeletedAt IS NULL', (test.CustomerId,))
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail='Customer not found')

        try:
            cur = db.execute(
                """INSERT INTO goldtest 
                (CustomerId, Status, Data, ModeOfPayment, Total) 
                VALUES (?, ?, ?, ?, ?)""",
                (test.CustomerId, test.Status, test.Data, test.ModeOfPayment, test.Total)
            )
            db.commit()
            
            cur = db.execute('SELECT * FROM goldtest WHERE rowid = ?', (cur.lastrowid,))
            new_test = cur.fetchone()
            if new_test:
                return dict(new_test)
            raise HTTPException(status_code=500, detail="Failed to create gold test")
        except sqlite3.IntegrityError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.get("/goldtest", response_model=PaginatedResponse)
def list_gold_tests(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    pagination = PaginationParams(page=page, limit=limit)
    
    with get_db() as db:
        count_cur = db.execute('SELECT COUNT(Id) FROM goldtest WHERE DeletedAt IS NULL')
        total_records = count_cur.fetchone()[0]

        cur = db.execute(
            'SELECT * FROM goldtest WHERE DeletedAt IS NULL ORDER BY CreatedDate DESC LIMIT ? OFFSET ?',
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

@router.get("/goldtest/{test_id}", response_model=GoldTestResponse)
def get_gold_test(test_id: str):
    with get_db() as db:
        cur = db.execute('SELECT * FROM goldtest WHERE Id = ? AND DeletedAt IS NULL', (test_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Gold test not found')
        return dict(row)

@router.put("/goldtest/{test_id}", response_model=GoldTestResponse)
def update_gold_test(test_id: str, test: GoldTestCreate):
    with get_db() as db:
        # Check if test exists
        cur = db.execute('SELECT Id FROM goldtest WHERE Id = ? AND DeletedAt IS NULL', (test_id,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Gold test not found')

        # Build update query
        fields = []
        params = []
        for key, value in test.dict(exclude_unset=True).items():
            fields.append(f"{key} = ?")
            params.append(value)

        if not fields:
            raise HTTPException(status_code=400, detail='No fields to update')

        params.append(test_id)
        db.execute(f'UPDATE goldtest SET {", ".join(fields)} WHERE Id = ?', params)
        db.commit()

        # Return updated test
        cur = db.execute('SELECT * FROM goldtest WHERE Id = ?', (test_id,))
        return dict(cur.fetchone())

@router.delete("/goldtest/{test_id}")
def delete_gold_test(test_id: str):
    with get_db() as db:
        db.execute('UPDATE goldtest SET DeletedAt = CURRENT_TIMESTAMP WHERE Id = ?', (test_id,))
        db.commit()
        return {"message": "Gold test deleted successfully"}