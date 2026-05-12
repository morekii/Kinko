from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.DataModels import Account, Category, Person
from app.schemas.finance import (
    AccountCreate, AccountResponse, AccountUpdate,
    CategoryCreate, CategoryResponse,
    PersonCreate, PersonResponse
)

router = APIRouter(tags=["Configuración Base"])

# --- CUENTAS ---

@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(account_in: AccountCreate, db: Session = Depends(get_db)):
    db_account = Account(
        name=account_in.name, 
        entity=account_in.entity, 
        type=account_in.type,
        currency=account_in.currency,
        is_day_to_day=account_in.is_day_to_day,
        is_active=account_in.is_active,
        closing_day=account_in.closing_day,
        due_day=account_in.due_day
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    # Retornamos solo las cuentas activas para no ensuciar la UI
    return db.query(Account).filter(Account.is_active == True).all()

@router.patch("/accounts/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, account_in: AccountUpdate, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    update_data = account_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_account, key, value)
        
    db.commit()
    db.refresh(db_account)
    return db_account

@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """Soft delete: Oculta la cuenta de la interfaz preservando la contabilidad histórica."""
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    db_account.is_active = False
    db.commit()
    return None

# --- CATEGORÍAS ---

@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category_in.name, is_active=category_in.is_active)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.is_active == True).all()

@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db_category.is_active = False
    db.commit()
    return None

# --- PERSONAS ---

@router.post("/people", response_model=PersonResponse, status_code=201)
def create_person(person_in: PersonCreate, db: Session = Depends(get_db)):
    db_person = Person(name=person_in.name, is_active=person_in.is_active)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

@router.get("/people", response_model=List[PersonResponse])
def list_people(db: Session = Depends(get_db)):
    return db.query(Person).filter(Person.is_active == True).all()

@router.delete("/people/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    db_person.is_active = False
    db.commit()
    return None