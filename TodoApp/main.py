from fastapi import FastAPI
import models
from database import engine


app = FastAPI()

#this line creates the tables in the database based on the models defined in models.py. 
# It uses the metadata from the Base class to create all tables that are defined as subclasses of Base.
models.Base.metadata.create_all(bind=engine)
models.Base.metadata.create_all(bind=engine)