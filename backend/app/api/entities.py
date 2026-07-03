from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from decimal import Decimal
from app.core.database import get_db
from app.models.DataModels import Account, Category, Person, Entry, Subscription
from app.schemas.finance import (
    AccountCreate, AccountResponse, AccountUpdate,
    CategoryCreate, CategoryResponse, CategoryUpdate,
    PersonCreate, PersonResponse, PersonUpdate
)

router = APIRouter(tags=["Configuración Base"])

# --- CUENTAS ---
@router.post("/accounts", response_model=AccountResponse, status_code=201)
def create_account(account_in: AccountCreate, db: Session = Depends(get_db)):
    # Si esta cuenta nace como principal, destildamos a las demás
    if account_in.is_main:
        db.query(Account).update({Account.is_main: False})

    db_account = Account(**account_in.model_dump())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

@router.get("/accounts", response_model=List[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return db.query(Account).filter(Account.is_active == True).all()

@router.patch("/accounts/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, account_in: AccountUpdate, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")
    
    update_data = account_in.model_dump(exclude_unset=True)
    
    # Si esta cuenta se vuelve la principal, destildamos a las demás
    if update_data.get("is_main") == True:
        db.query(Account).update({Account.is_main: False})
        
    for key, value in update_data.items():
        setattr(db_account, key, value)
        
    db.commit()
    db.refresh(db_account)
    return db_account

@router.delete("/accounts/{account_id}", status_code=204)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    db_account = db.query(Account).filter(Account.id == account_id).first()
    if not db_account:
        raise HTTPException(status_code=404, detail="Cuenta no encontrada")

    used_by_subscription = db.query(Subscription).filter(
        Subscription.suggested_account_id == account_id,
        Subscription.is_active == True,
    ).first()
    if used_by_subscription:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede desactivar: la suscripción '{used_by_subscription.description}' la usa como cuenta de cobro.",
        )

    used_as_reserve = db.query(Account).filter(
        Account.reserve_account_id == account_id,
        Account.is_active == True,
    ).first()
    if used_as_reserve:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede desactivar: la cuenta '{used_as_reserve.name}' la usa como cuenta de reserva.",
        )

    db_account.is_active = False
    db.commit()
    return None

# --- CATEGORÍAS ---
@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(category_in: CategoryCreate, db: Session = Depends(get_db)):
    db_category = Category(**category_in.model_dump())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).filter(Category.is_active == True).all()

@router.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_in: CategoryUpdate, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    update_data = category_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_category, key, value)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.delete("/categories/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    db_category = db.query(Category).filter(Category.id == category_id).first()
    if not db_category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")

    used_by_subscription = db.query(Subscription).filter(
        Subscription.category_id == category_id,
        Subscription.is_active == True,
    ).first()
    if used_by_subscription:
        raise HTTPException(
            status_code=400,
            detail=f"No se puede desactivar: la suscripción '{used_by_subscription.description}' la usa como categoría.",
        )

    db_category.is_active = False
    db.commit()
    return None

# --- PERSONAS / ENTIDADES EXTERNAS ---
@router.post("/people", response_model=PersonResponse, status_code=201)
def create_person(person_in: PersonCreate, db: Session = Depends(get_db)):
    db_person = Person(**person_in.model_dump())
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return PersonResponse(
        id=db_person.id, name=db_person.name, 
        is_debt_tracker=db_person.is_debt_tracker, 
        is_active=db_person.is_active, balance=Decimal("0.00")
    )

@router.get("/people", response_model=List[PersonResponse])
def list_people(db: Session = Depends(get_db)):
    results = (
        db.query(
            Person.id, Person.name, Person.is_debt_tracker, Person.is_active,
            func.sum(Entry.base_amount).label("balance")
        )
        .outerjoin(Entry, Person.id == Entry.person_id)
        .filter(Person.is_active == True)
        .group_by(Person.id)
        .all()
    )
    return [
        PersonResponse(
            id=r.id, name=r.name, is_debt_tracker=r.is_debt_tracker,
            is_active=r.is_active, balance=r.balance or Decimal("0.00")
        ) for r in results
    ]

@router.patch("/people/{person_id}", response_model=PersonResponse)
def update_person(person_id: int, person_in: PersonUpdate, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    update_data = person_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_person, key, value)
    db.commit()
    db.refresh(db_person)
    balance = db.query(func.sum(Entry.base_amount)).filter(Entry.person_id == person_id).scalar()
    return PersonResponse(
        id=db_person.id, name=db_person.name, is_debt_tracker=db_person.is_debt_tracker,
        is_active=db_person.is_active, balance=balance or Decimal("0.00")
    )

@router.delete("/people/{person_id}", status_code=204)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    db_person.is_active = False
    db.commit()
    return None