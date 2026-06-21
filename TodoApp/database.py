from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# This is the database URL for SQLite. It will create a file called todos.db in the current directory.
# The three slashes after sqlite: indicate a relative path from the current working directory.
# If you want to store the database file elsewhere, use an absolute path, e.g. 'sqlite:////full/path/to/todos.db'.
SQLALCHEMY_DATABASE_URL = 'sqlite:///./todos.db'

enine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create the SQLAlchemy engine. connect_args is required for SQLite when using multiple threads
# in the same application, such as with FastAPI or other async frameworks.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create a configured "SessionLocal" class used to create new SQLAlchemy session objects.
# autocommit=False means changes are not committed automatically.
# autoflush=False means pending changes are not flushed to the database before queries unless explicitly requested.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative class definitions. Models should inherit from this Base.
Base = declarative_base()