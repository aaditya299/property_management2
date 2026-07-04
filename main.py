import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
load_dotenv()
app = FastAPI()
database_url =os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

class ApplicationRequest(BaseModel):
    property_id: int
    applicant_name: str
    contact_email: str

@app.get("/properties")
def get_properties():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("select * from properties order by property_id asc;")
    all_properties = cursor.fetchall()
    cursor.close()
    conn.close()
    return {"properties": all_properties}
