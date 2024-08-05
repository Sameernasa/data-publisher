from sqlalchemy.orm import Session
import models, schemas
import json

def get_account(db: Session, account_id: int):
    return db.query(models.Account).filter(models.Account.id == account_id).first()

def get_account_by_email(db: Session, email: str):
    return db.query(models.Account).filter(models.Account.email == email).first()

def create_account(db: Session, account: schemas.AccountCreate):
    db_account = models.Account(email=account.email, account_name=account.account_name, website=account.website)
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account

def get_destinations(db: Session, account_id: int):
    destinations = db.query(models.Destination).filter(models.Destination.account_id == account_id).all()
    for destination in destinations:
        destination.headers = json.loads(destination.headers)  # Deserialize headers
    return destinations

def delete_account(db: Session, account_id: int):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if account:
        db.delete(account)
        db.commit()
    return account

def delete_destination(db: Session, destination_id: int):
    destination = db.query(models.Destination).filter(models.Destination.id == destination_id).first()
    if destination:
        db.delete(destination)
        db.commit()
    return destination