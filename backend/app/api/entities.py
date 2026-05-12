from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.DataModels import Account, Category, Person
from app.schemas.finance import (
    AccountCreate, AccountResponse,
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
        is_day_to_day=account_in.is_day_to_day
    )
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).all()

# --- CATEGORÍAS ---

@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(name=category_in.name)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()

# --- PERSONAS ---

@router.post("/people", response_model=PersonResponse, status_code=201)
def create_person(person_in: PersonCreate, db: Session = Depends(get_db)):
    db_person = Person(name=person_in.name)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

@router.get("/people", response_model=List[PersonResponse])
def list_people(db: Session = Depends(get_db)):
    return db.query(Person).all()