from fastapi import APIRouter, HTTPException, Query
from ..database import get_db
from ..schemas import WeightLossHistoryCreate, WeightLossHistoryResponse, PaginationParams, PaginatedResponse
import sqlite3

router = APIRouter()

@router.post("/weightlosshistory", response_model=WeightLossHistoryResponse, status_code=201)
def create_weight_loss_history(history: WeightLossHistoryCreate):
    with get_db() as db:
        # Validate customer exists
        cur = db.execute('SELECT Id FROM customers WHERE Id = ? AND DeletedAt IS NULL', (history.CustomerId,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail='Customer not found')

        try:
            cur = db.execute(
                'INSERT INTO weightlosshistory (CustomerId, Amount, ModeOfPayment) VALUES (?, ?, ?)',
                (history.CustomerId, history.Amount, history.ModeOfPayment)
            )
            db.commit()
            
            cur = db.execute('SELECT * FROM weightlosshistory WHERE rowid = ?', (cur.lastrowid,))
            new_history = cur.fetchone()
            if new_history:
                return dict(new_history)
            raise HTTPException(status_code=500, detail="Failed to create weight loss history")
        except sqlite3.IntegrityError as e:
            raise HTTPException(status_code=400, detail=str(e))

@router.get("/weightlosshistory", response_model=PaginatedResponse)
def list_all_weight_loss_history(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    pagination = PaginationParams(page=page, limit=limit)
    
    with get_db() as db:
        count_cur = db.execute('SELECT COUNT(Id) FROM weightlosshistory WHERE DeletedAt IS NULL')
        total_records = count_cur.fetchone()[0]

        cur = db.execute(
            'SELECT * FROM weightlosshistory WHERE DeletedAt IS NULL ORDER BY CreatedDate DESC LIMIT ? OFFSET ?',
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

@router.get("/customers/{customer_id}/weightlosshistory", response_model=PaginatedResponse)
def list_customer_weight_loss_history(customer_id: str, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    pagination = PaginationParams(page=page, limit=limit)
    
    with get_db() as db:
        count_cur = db.execute(
            'SELECT COUNT(Id) FROM weightlosshistory WHERE CustomerId = ? AND DeletedAt IS NULL',
            (customer_id,)
        )
        total_records = count_cur.fetchone()[0]

        cur = db.execute(
            'SELECT * FROM weightlosshistory WHERE CustomerId = ? AND DeletedAt IS NULL ORDER BY CreatedDate DESC LIMIT ? OFFSET ?',
            (customer_id, pagination.limit, pagination.offset)
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

@router.get("/weightlosshistory/{history_id}", response_model=WeightLossHistoryResponse)
def get_weight_loss_history(history_id: str):
    with get_db() as db:
        cur = db.execute('SELECT * FROM weightlosshistory WHERE Id = ? AND DeletedAt IS NULL', (history_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Weight loss history record not found')
        return dict(row)

@router.delete("/weightlosshistory/{history_id}")
def delete_weight_loss_history(history_id: str):
    with get_db() as db:
        db.execute('UPDATE weightlosshistory SET DeletedAt = CURRENT_TIMESTAMP WHERE Id = ?', (history_id,))
        db.commit()
        return {"message": "Weight loss history record deleted successfully"}