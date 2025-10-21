from fastapi import APIRouter, HTTPException, Query
from ..database import get_db
from ..schemas import GlobalSettingCreate, GlobalSettingResponse, GlobalSettingUpdate, PaginationParams, PaginatedResponse
import sqlite3

router = APIRouter()

@router.post("/globals", response_model=GlobalSettingResponse, status_code=201)
def create_global(setting: GlobalSettingCreate):
    with get_db() as db:
        try:
            cur = db.execute('INSERT INTO globals (Key, Value) VALUES (?, ?)', (setting.Key, setting.Value))
            db.commit()
            
            cur = db.execute('SELECT * FROM globals WHERE rowid = ?', (cur.lastrowid,))
            new_setting = cur.fetchone()
            if new_setting:
                return dict(new_setting)
            raise HTTPException(status_code=500, detail="Failed to create global setting")
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=409, detail=f'Key "{setting.Key}" already exists')

@router.get("/globals", response_model=PaginatedResponse)
def list_globals(page: int = Query(1, ge=1), limit: int = Query(20, ge=1, le=100)):
    pagination = PaginationParams(page=page, limit=limit)
    
    with get_db() as db:
        count_cur = db.execute('SELECT COUNT(Id) FROM globals WHERE DeletedAt IS NULL')
        total_records = count_cur.fetchone()[0]

        cur = db.execute(
            'SELECT * FROM globals WHERE DeletedAt IS NULL ORDER BY Key LIMIT ? OFFSET ?',
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

@router.get("/globals/{key}", response_model=GlobalSettingResponse)
def get_global(key: str):
    with get_db() as db:
        cur = db.execute('SELECT * FROM globals WHERE Key = ? AND DeletedAt IS NULL', (key,))
        row = cur.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail=f'Global setting with key "{key}" not found')
        return dict(row)

@router.put("/globals/{key}", response_model=GlobalSettingResponse)
def update_global(key: str, setting: GlobalSettingUpdate):
    with get_db() as db:
        # Check if setting exists
        cur = db.execute('SELECT Id FROM globals WHERE Key = ? AND DeletedAt IS NULL', (key,))
        if not cur.fetchone():
            raise HTTPException(status_code=404, detail=f'Global setting with key "{key}" not found')

        db.execute('UPDATE globals SET Value = ? WHERE Key = ?', (setting.Value, key))
        db.commit()

        # Return updated setting
        cur = db.execute('SELECT * FROM globals WHERE Key = ?', (key,))
        return dict(cur.fetchone())

@router.delete("/globals/{key}")
def delete_global(key: str):
    with get_db() as db:
        cur = db.execute('SELECT Id FROM globals WHERE Key = ? AND DeletedAt IS NULL', (key,))
        if not cur.fetchone():
            return {"message": "Global setting already deleted or does not exist"}

        db.execute('UPDATE globals SET DeletedAt = CURRENT_TIMESTAMP WHERE Key = ?', (key,))
        db.commit()
        return {"message": f'Global setting with key "{key}" deleted successfully'}