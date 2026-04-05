# here we will trying to create the main engine for our db lets imprt library
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker,declarative_base

# creating the url with user name and password of our db with db name
url_conn = "mysql+pymysql://root:password@localhost/finance_db"


en = create_engine(url_conn,pool_pre_ping=True,echo=True)

sess_loc = sessionmaker(autocommit=False,bind=en,autoflush=False)

base = declarative_base()
