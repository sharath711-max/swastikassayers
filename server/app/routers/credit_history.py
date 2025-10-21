from fastapi import APIRouter, HTTPException, Query
from ..database import get_db
from ..schemas import CreditHistoryCreate, CreditHistoryResponse, PaginationParams, PaginatedResponse
import sqlite3

router = APIRouter()

@router.post("/credithistory", status_code=201)
def create_credit_history(history: CreditHistoryCreate):
    with get_db() as db:
        # Validate customer exists
        cur = db.execute('SELECT Balance FROM customers WHERE Id = ? AND DeletedAt IS NULL', (history.CustomerId,))
        customer = cur.fetchone()
        if not customer:
            raise HTTPException(status_code=404, detail='Customer not found')

        previous_balance = customer['Balance']
        
        # Calculate new balance
        if history.Type == 'credit':
            new_balance = previous_balance + history.Amount
        else:  # debit
            new_balance = previous_balance - history.Amount

        try:
            # Begin transaction
            db.execute(
                'INSERT INTO credithistory (CustomerId, Type, Amount, ModeOfPayment, PreviousBalance) VALUES (?, ?, ?, ?, ?)',
                (history.CustomerId, history.Type, history.Amount, history.ModeOfPayment, previous_balance)
            )
            db.execute('UPDATE customers SET Balance = ? WHERE Id = ?', (new_balance, history.CustomerId))
            db.commit()
            
            return {"message": "Credit history created and customer balance updated successfully"}
        except sqlite3.Error as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f'Database transaction failed: {e}')

@router.get("/credithistory", response_model=PaginatedResponse)
def list_all_credit_history(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    pagination = PaginationParams(page=page, limit=limit)
    
    with get_db() as db:
        count_cur = db.execute('SELECT COUNT(Id) FROM credithistory WHERE DeletedAt IS NULL')
        total_records = count_cur.fetchone()[0]

        cur = db.execute(
            'SELECT * FROM credithistory WHERE DeletedAt IS NULL ORDER BY CreatedDate DESC LIMIT ? OFFSET ?',
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

@router.get("/customers/{customer_id}/credithistory", response_model=PaginatedResponse)
def list_customer_credit_history(customer_id: str, page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    pagination = PaginationParams(page=page, limit=limit)
    
    with get_db() as db:
        count_cur = db.execute(
            'SELECT COUNT(Id) FROM credithistory WHERE CustomerId = ? AND DeletedAt IS NULL',
            (customer_id,)
        )
        total_records = count_cur.fetchone()[0]

        cur = db.execute(
            'SELECT * FROM credithistory WHERE CustomerId = ? AND DeletedAt IS NULL ORDER BY CreatedDate DESC LIMIT ? OFFSET ?',
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

@router.get("/credithistory/{history_id}", response_model=CreditHistoryResponse)
def get_credit_history(history_id: str):
    with get_db() as db:
        cur = db.execute('SELECT * FROM credithistory WHERE Id = ? AND DeletedAt IS NULL', (history_id,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail='Credit history record not found')
        return dict(row)

@router.delete("/credithistory/{history_id}")
def delete_credit_history(history_id: str):
    with get_db() as db:
        db.execute('UPDATE credithistory SET DeletedAt = CURRENT_TIMESTAMP WHERE Id = ?', (history_id,))
        db.commit()
        return {"message": "Credit history record deleted successfully"}