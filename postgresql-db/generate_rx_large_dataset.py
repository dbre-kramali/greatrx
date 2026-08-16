import random
import datetime
import psycopg2

# ---------- CONFIGURE YOUR CONNECTION HERE ----------
DB_HOST = "your-rds-endpoint.amazonaws.com"
DB_PORT = 5432
DB_NAME = "your_db_name"
DB_USER = "your_db_user"
DB_PASSWORD = "your_db_password"
# ---------------------------------------------------

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
conn.autocommit = True
cur = conn.cursor()

def rand_date(start_year=2024, end_year=2026):
    start = datetime.date(start_year, 1, 1)
    end = datetime.date(end_year, 12, 31)
    delta = (end - start).days
    return start + datetime.timedelta(days=random.randint(0, delta))

def rand_datetime():
    d = rand_date()
    return datetime.datetime(d.year, d.month, d.day,
                             random.randint(8, 17),
                             random.choice([0, 15, 30, 45]))

# -----------------------
# 1. Insert Payers
# -----------------------
payers = [
    ("BlueCross NC", "Commercial", "800-555-1001", "Durham, NC"),
    ("Aetna Health", "Commercial", "800-555-1002", "Hartford, CT"),
    ("United Healthcare", "Commercial", "800-555-1003", "Minnetonka, MN"),
    ("Cigna", "Commercial", "800-555-1004", "Bloomfield, CT"),
    ("Medicare", "Medicare", "800-633-4227", "Baltimore, MD"),
    ("Medicaid NC", "Medicaid", "800-555-2001", "Raleigh, NC"),
    ("Humana", "Commercial", "800-555-3001", "Louisville, KY"),
    ("Kaiser Permanente", "Commercial", "800-555-4001", "Oakland, CA"),
    ("Self-Pay", "Self-Pay", "000-000-0000", "N/A"),
    ("Tricare", "Government", "800-555-5001", "Falls Church, VA")
]

print("Inserting payers...")
for p in payers:
    cur.execute("""
        INSERT INTO rx.payer (payer_name, payer_type, phone, address)
        VALUES (%s, %s, %s, %s)
    """, p)

# -----------------------
# 2. Insert Doctors
# -----------------------
doctor_first = ["Emily","Michael","Christopher","Ashley","Daniel","Sarah","Joshua","Olivia",
                "Andrew","Hannah","Jacob","Madison","Ethan","Ava","Logan","Grace","Ryan",
                "Chloe","Nathan","Lily"]

doctor_last = ["Henderson","Turner","Bennett","Coleman","Foster","Mitchell","Parker",
               "Reynolds","Sullivan","Brooks","Morgan","Price","Hayes","Long","Fisher",
               "Stevens","Warren","Hughes","Bryant","Gibson"]

specialties = [
    "Internal Medicine","Pediatrics","Cardiology","Dermatology","Orthopedics",
    "Family Medicine","Endocrinology","OB/GYN","Neurology","ENT",
    "Gastroenterology","Pulmonology","Rheumatology","Psychiatry","Urology",
    "Nephrology","General Surgery","Allergy & Immunology","Hematology",
    "Infectious Disease"
]

clinics = [
    "Triangle Care Clinic","Family Health Center","HeartCare NC","SkinWell Clinic",
    "OrthoPlus","CareFirst","Metabolic Center","Women Health NC","NeuroCare",
    "Ear Nose Throat NC","GI Center","LungCare","Joint Relief Clinic","MindWell",
    "UroCare","Kidney Center","Surgical Associates","Allergy Relief NC",
    "BloodCare","ID Specialists"
]

print("Inserting doctors...")
for i in range(200):
    fn = doctor_first[i % len(doctor_first)]
    ln = doctor_last[i % len(doctor_last)]
    spec = specialties[i % len(specialties)]
    clinic = clinics[i % len(clinics)]
    npi = f"NPI{9001 + i:04d}"
    cur.execute("""
        INSERT INTO rx.doctor (npi, first_name, last_name, specialty, clinic_name)
        VALUES (%s, %s, %s, %s, %s)
    """, (npi, fn, ln, spec, clinic))

# -----------------------
# 3. Insert Patients
# -----------------------
first_names = ["Jessica","Brandon","Tyler","Megan","Zachary","Lauren","Jason","Brittany",
               "Dylan","Rachel","Kevin","Samantha","Justin","Courtney","Eric","Amber",
               "Shawn","Kaitlyn","Patrick","Brooke","Cameron","Haley","Trevor","Morgan",
               "Evan","Sydney","Blake","Kelsey","Austin","Shelby","Vanessa","Jenna",
               "Cole","Madeline","Grant","Paige","Spencer","Lindsey","Garrett","Allison",
               "Chase","Erin","Mitchell","Kayla","Derek","Jillian","Wesley","Taylor",
               "Connor","Natalie"]

last_names = ["Miller","Smith","Johnson","Davis","Brown","Wilson","Moore","Taylor",
              "Anderson","Thomas","Jackson","White","Harris","Martin","Thompson","Garcia",
              "Martinez","Robinson","Clark","Rodriguez","Lewis","Lee","Walker","Hall",
              "Allen","Young","Hernandez","King","Wright","Lopez","Hill","Scott",
              "Green","Adams","Baker","Nelson","Carter","Mitchell","Perez","Roberts",
              "Turner","Phillips","Campbell","Parker","Evans","Edwards","Collins",
              "Stewart","Morris","Rogers"]

print("Inserting patients...")
for i in range(500):
    fn = first_names[i % len(first_names)]
    ln = last_names[i % len(last_names)]
    dob = rand_date(1960, 2005)
    gender = random.choice(["Male","Female"])
    phone = f"919-555-{1000+i:04d}"
    email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
    mrn = f"MRN{1000+i}"
    cur.execute("""
        INSERT INTO rx.patient (mrn, first_name, last_name, date_of_birth, gender, phone, email)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (mrn, fn, ln, dob, gender, phone, email))

# -----------------------
# FETCH REAL IDs
# -----------------------
cur.execute("SELECT patient_id FROM rx.patient")
patient_ids = [row[0] for row in cur.fetchall()]

cur.execute("SELECT doctor_id FROM rx.doctor")
doctor_ids = [row[0] for row in cur.fetchall()]

# -----------------------
# 4. Insert Encounters (FK-safe)
# -----------------------
print("Inserting encounters...")
for i in range(2000):
    pid = random.choice(patient_ids)
    did = random.choice(doctor_ids)
    dt = rand_datetime()
    etype = random.choice(["Office Visit","Telehealth","Urgent Care"])
    reason = random.choice(["Routine checkup","Hypertension follow-up","Diabetes management",
                            "Acute infection","Medication review","Lab results discussion"])
    cur.execute("""
        INSERT INTO rx.encounter (patient_id, doctor_id, encounter_date, encounter_type, reason, status)
        VALUES (%s, %s, %s, %s, %s, 'COMPLETED')
    """, (pid, did, dt, etype, reason))

# Fetch encounter IDs
cur.execute("SELECT encounter_id, patient_id, doctor_id FROM rx.encounter")
encounters = cur.fetchall()

# -----------------------
# 5. Insert Prescriptions (FK-safe)
# -----------------------
print("Inserting prescriptions...")
for enc_id, pid, did in encounters:
    rxnum = f"RX-2026-{enc_id:04d}"
    wdate = rand_date()
    status = random.choice(["ACTIVE","EXPIRED"])
    notes = random.choice(["Routine visit","Follow-up","New diagnosis","Medication adjustment"])
    cur.execute("""
        INSERT INTO rx.prescription (rx_number, patient_id, doctor_id, written_date, status, notes)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (rxnum, pid, did, wdate, status, notes))

# Fetch prescription IDs
cur.execute("SELECT prescription_id FROM rx.prescription")
prescription_ids = [row[0] for row in cur.fetchall()]

# -----------------------
# 6. Insert Drugs
# -----------------------
print("Inserting drugs...")
for i in range(300):
    base = drugs[i % len(drugs)]
    rxcode = f"{base[0]}_{i}"
    cur.execute("""
        INSERT INTO rx.drug (rxnorm_code, name, strength, form, manufacturer)
        VALUES (%s, %s, %s, %s, %s)
    """, (rxcode, base[1], base[2], base[3], base[4]))

# Fetch drug IDs
cur.execute("SELECT drug_id FROM rx.drug")
drug_ids = [row[0] for row in cur.fetchall()]

# -----------------------
# 7. Insert Prescription Items (FK-safe)
# -----------------------
print("Inserting prescription items...")
for i in range(6000):
    pid = random.choice(prescription_ids)
    drug = random.choice(drug_ids)
    dosage = random.choice(["1 tablet","2 tablets","1 capsule"])
    freq = random.choice(["QD","BID","TID","Q6H PRN"])
    dur = random.choice([7,14,30,90])
    route = random.choice(["oral","inhalation","injection"])
    instr = random.choice(["Take with water","Take with food","As needed for pain","Take at bedtime"])
    cur.execute("""
        INSERT INTO rx.prescription_item
        (prescription_id, drug_id, dosage, frequency, duration_days, route, instructions)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (pid, drug, dosage, freq, dur, route, instr))

# -----------------------
# 8. Insert Claims (FK-safe)
# -----------------------
cur.execute("SELECT payer_id FROM rx.payer")
payer_ids = [row[0] for row in cur.fetchall()]

print("Inserting claims...")
for enc_id, pid, did in encounters:
    payer = random.choice(payer_ids)
    cnum = f"CLM-2026-{enc_id:04d}"
    cdate = rand_date()
    amt = round(random.uniform(100,500),2)
    status = random.choice(["SUBMITTED","PAID","DENIED","PENDING"])
    notes = random.choice(["Routine claim","Telehealth claim","Follow-up claim"])
    cur.execute("""
        INSERT INTO rx.claim (encounter_id, payer_id, claim_number, claim_date, total_amount, status, notes)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (enc_id, payer, cnum, cdate, amt, status, notes))

# Fetch claim IDs
cur.execute("SELECT claim_id FROM rx.claim")
claim_ids = [row[0] for row in cur.fetchall()]

# -----------------------
# 9. Insert Claim Lines (FK-safe)
# -----------------------
print("Inserting claim lines...")
cpt_codes = ["99213","99214","J1100","87804","93000","81002"]

for i in range(6000):
    cid = random.choice(claim_ids)
    cpt = random.choice(cpt_codes)
    desc = random.choice([
        "Office Visit - Established Patient",
        "Office Visit - Moderate Complexity",
        "Injection - Dexamethasone",
        "Rapid Flu Test",
        "Electrocardiogram",
        "Urinalysis"
    ])
    qty = random.randint(1,3)
    charge = round(random.uniform(50,300),2)
    allowed = round(charge * random.uniform(0.7,1.0),2)
    status = random.choice(["PAID","DENIED","ADJUSTED","PENDING"])
    cur.execute("""
        INSERT INTO rx.claim_line
        (claim_id, cpt_code, description, quantity, charge_amount, allowed_amount, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (cid, cpt, desc, qty, charge, allowed, status))

# -----------------------
# 10. Insert Payments (FK-safe)
# -----------------------
print("Inserting payments...")
for cid in claim_ids:
    pdate = rand_date()
    paid = round(random.uniform(50,400),2)
    adj = round(random.uniform(0,100),2)
    resp = round(random.uniform(0,100),2)
    method = random.choice(["EFT","Check","Credit"])
    ref = f"PMT-{pdate.year}-{cid:04d}"
    cur.execute("""
        INSERT INTO rx.payment
        (claim_id, payment_date, paid_amount, adjustment_amount, patient_responsibility, payment_method, reference_number)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (cid, pdate, paid, adj, resp, method, ref))

print("DONE — All FK-safe data inserted successfully.")

cur.close()
conn.close()
