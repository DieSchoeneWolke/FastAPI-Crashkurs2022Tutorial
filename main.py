# https://youtu.be/KXCvIV3yr7c?list=PLhb2CZ9EOUDKQRGd6cSm3Xs-BDRxXk-C8&
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, Field
from jose import jwt
from enum import Enum
from typing import Optional


items = [
    {"name": "Computer", "preis": 1000, "typ": "hardware"},
    {"name": "Monitor", "preis": 800, "typ": "hardware"},
    {"name": "Diablo 3", "preis": 50, "typ": "software"},
    {"name": "Windows", "preis": 90, "typ": "software"}
]


class Type(Enum):
    hardware = "hardware"
    software = "software"


class Item(BaseModel):
    name: str
    preis: int = Field(100, gt=0, lt=2500)
    typ: Type


app = FastAPI()
oauth2_schema = OAuth2PasswordBearer(tokenUrl="login")


@app.post("/login")
async def login(data: OAuth2PasswordRequestForm = Depends()):
    if data.username == "test" and data.password == "test":
        access_token = jwt.encode({"user": data.username}, key="secret")
        return {"access_token": access_token, "token_type": "bearer"}
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Wrong login",
        headers={"WWW-Authenticate": "Bearer"},
    )


class ResponseItem(BaseModel):
    name: str
    typ: Type


@app.get("/items")
async def hello(q: Optional[str] = None):
    if q:
        data = []
        for item in items:
            if item.get("typ") == q:
                data.append(item)
        return data
    return items


@app.get("/items/{item_id}", dependencies=[Depends(oauth2_schema)])
async def read_item(item_id: int):
    try:
        return {"item": items[int(item_id)]}
    except (IndexError, ValueError):
        raise HTTPException(status_code=404, detail="Item not found")


@app.post("/items", response_model=ResponseItem, dependencies=[Depends(oauth2_schema)])
async def create_item(data: Item):
    items.append(data.dict())
    return data


@app.put("/items/{item_id}")
async def change_item(item_id: int, item: Item):
    items[item_id] = item
    return item


@app.delete("/items/{item_id}", dependencies=[Depends(oauth2_schema)])
async def delete_item(item_id: int):
    item = items[item_id]
    items.pop(item_id)
    return {"deleted": item}
