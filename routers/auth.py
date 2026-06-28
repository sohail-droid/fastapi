from datetime import timedelta
import datetime

from time import timezone
from typing_extensions import deprecated
from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from typing import Annotated
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError #jwt = secret + alg

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'f2e9a7377cecf398b0026ae08b7e623d9171529cbce6c1f48359d56dd054979b'   #openssl rand -hex 32
ALGORITHIM = 'HS256'


bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenurl='auth/stoken')  #this url sent by client 


# CreateUserRequest (Pydantic model)
# Defines the shape of incoming request data.                           <<----
# Validates the JSON body sent by the client.
# Ensures things like: username is a string, password is required, etc.
# Example: FastAPI automatically parses the request body into this model:
# json
# {
#   "username": "abc",
#   "email": "abc@example.com",
#   "password": "secret"
# }
# → becomes a CreateUserRequest object with those attributes.

class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name : str
    last_name: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    #this is a session object that will be used to interact with the database When you call db = SessionLocal()
    # you're opening a temporary connection handle to your database.
    db = SessionLocal()    
    try:
        yield db #this will yield the database session object to the caller.
    finally:
        db.close() #this will close the database session object after the caller is done with it.


db_dependency = Annotated[Session, Depends(get_db)]
# db_dependency = Session = Depends(get_db) is the same as db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user_creds(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHIM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithims=[ALGORITHIM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate the user")
        return {'username': username, 'id': user_id}

    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate the user")




@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest): 

    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )

    # return create_user_model
    db.add(create_user_model)   #I want this object inserted into the DB it queues the object for persistence in queue
    db.commit()                  #Inserted here  success







#user authenticate and authorize (token)

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],db: db_dependency):
    user = authenticate_user_creds(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="could not validate the user")

    token = create_access_token(user.username, user.id, timedelta(minutes=20))

    return {'access_token':token, 'token_type': 'bearer'}