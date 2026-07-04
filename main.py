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
@app.post("/apply")
def apply_to_rent(req: ApplicationRequest):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("select status from properties where property_id=%s;", (req.property_id,))
    property_record = cursor.fetchone()

    if not property_record:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="Property not found")

    if property_record['status'] == 'Full':
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="This property is already occupied")
    
    cursor.execute("""
        INSERT INTO applications (property_id, applicant_name, contact_email, status)
        VALUES (%s, %s, %s, 'Pending') RETURNING application_id;
    """, (req.property_id, req.applicant_name, req.contact_email))

    new_id = cursor.fetchone()['application_id']
    conn.commit()
    cursor.close()
    conn.close()

    return {"message": "Application submitted successfully", "application_id": new_id}