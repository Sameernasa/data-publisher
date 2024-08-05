from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import crud, models, schemas
from database import SessionLocal, engine, Base
import httpx
import json

Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/accounts/", response_model=schemas.Account)
def create_account(account: schemas.AccountCreate, db: Session = Depends(get_db)):
    db_account = crud.get_account_by_email(db, email=account.email)
    if db_account:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_account(db=db, account=account)

@app.get("/accounts/{account_id}", response_model=schemas.Account)
def read_account(account_id: int, db: Session = Depends(get_db)):
    db_account = crud.get_account(db, account_id=account_id)
    if db_account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return db_account

@app.delete("/accounts/{account_id}", response_model=schemas.Account)
def delete_account(account_id: int, db: Session = Depends(get_db)):
    account = crud.delete_account(db, account_id=account_id)
    if account is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@app.post("/accounts/{account_id}/destinations/", response_model=schemas.DestinationResponse)
def create_destination_for_account(account_id: int, destination: schemas.DestinationCreate, db: Session = Depends(get_db)):
    db_destination = models.Destination(url=destination.url, http_method=destination.http_method, headers=json.dumps(destination.headers), account_id=account_id)
    db.add(db_destination)
    db.commit()
    db.refresh(db_destination)
    
    return db_destination

@app.get("/accounts/{account_id}/destinations/", response_model=List[schemas.DestinationResponse])
def get_destinations_for_account(account_id: int, db: Session = Depends(get_db)):
    destinations = crud.get_destinations(db, account_id=account_id)
    if not destinations:
        raise HTTPException(status_code=404, detail="Destinations not found")
    # for destination in destinations:
    #     destination.headers = json.loads(destination.headers)  # Deserialize headers before returning
    return destinations

@app.delete("/destinations/{destination_id}", response_model=schemas.DestinationResponse)
def delete_destination(destination_id: int, db: Session = Depends(get_db)):
    destination = crud.delete_destination(db, destination_id=destination_id)
    if destination is None:
        raise HTTPException(status_code=404, detail="Destination not found")
    return destination


@app.post("/server/incoming_data")
async def handle_incoming_data(data: dict, cl_x_token: str = None, db: Session = Depends(get_db)):
    if not cl_x_token:
        return {"detail": "Un Authenticate"}

    account = db.query(models.Account).filter(models.Account.app_secret_token == cl_x_token).first()
    if not account:
        return {"detail": "Un Authenticate"}

    destinations = crud.get_destinations(db, account_id=account.id)
    if not destinations:
        return {"detail": "No destinations found"}

    async with httpx.AsyncClient() as client:
        for destination in destinations:
            headers = json.loads(destination.headers)  # Deserialize headers
            url = destination.url
            method = destination.http_method.lower()

            if method == "get":
                response = await client.get(url, params=data, headers=headers)
            elif method == "post":
                response = await client.post(url, json=data, headers=headers)
            elif method == "put":
                response = await client.put(url, json=data, headers=headers)
            else:
                continue  # Ignore unsupported methods

            if response.status_code != 200:
                return {"detail": f"Failed to send data to {url}"}

    return {"detail": "Data sent successfully"}
