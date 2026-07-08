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

class ApprovalAction(BaseModel):
    application_id: int

@app.post("/admin/approve")
def approve_application(action: ApprovalAction):
    conn=get_db_connection()
    cursor=conn.cursor()

    cursor.execute("""
    select property_id, applicant_name from applications
    where application_id=%s and status='Pending';"""
    , (action.application_id,))
    app_record=cursor.fetchone()

    if not app_record:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404,detail="Pending application record not found")
    
    pid = app_record['property_id']
    name = app_record['applicant_name']
    
    cursor.execute("UPDATE applications SET status = 'Approved' WHERE application_id = %s;", (action.application_id,))
    cursor.execute("UPDATE properties SET status = 'Full' WHERE property_id = %s;", (pid,))
    cursor.execute("""
        INSERT INTO tenants (property_id, tenant_name, payment_status)
        VALUES (%s, %s, 'Unpaid');
    """, (pid, name))
    conn.commit()
    
    cursor.close()
    conn.close()
    return {"message": f"Success! {name} has been approved and moved to active tenants."}

@app.get("/admin/applications")
def get_pending_applications():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
       SELECT 
        a.application_id, 
        a.applicant_name, 
        a.contact_email, 
        a.status, 
        p.address AS property_address,
        p.city AS property_city
        FROM applications a 
        INNER JOIN properties p ON a.property_id = p.property_id
        WHERE a.status = 'Pending' 
        ORDER BY a.application_id ASC;
        """)
        
    pending_apps = cursor.fetchall()
    cursor.close()
    conn.close()
    return {'pending_applications': pending_apps}
     
    