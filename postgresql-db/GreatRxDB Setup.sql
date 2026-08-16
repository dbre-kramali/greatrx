CREATE SCHEMA rx;


-- PATIENT
CREATE TABLE rx.patient (
    patient_id      SERIAL PRIMARY KEY,
    mrn             VARCHAR(20) UNIQUE NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    date_of_birth   DATE NOT NULL,
    gender          VARCHAR(10),
    phone           VARCHAR(20),
    email           VARCHAR(100)
);

-- DOCTOR
CREATE TABLE rx.doctor (
    doctor_id       SERIAL PRIMARY KEY,
    npi             VARCHAR(20) UNIQUE NOT NULL,
    first_name      VARCHAR(50) NOT NULL,
    last_name       VARCHAR(50) NOT NULL,
    specialty       VARCHAR(100),
    clinic_name     VARCHAR(100)
);

-- DRUG
CREATE TABLE rx.drug (
    drug_id         SERIAL PRIMARY KEY,
    rxnorm_code     VARCHAR(30),
    name            VARCHAR(100) NOT NULL,
    strength        VARCHAR(50),
    form            VARCHAR(50),
    manufacturer    VARCHAR(100)
);

-- PRESCRIPTION
CREATE TABLE rx.prescription (
    prescription_id SERIAL PRIMARY KEY,
    rx_number       VARCHAR(30) UNIQUE NOT NULL,
    patient_id      INT NOT NULL REFERENCES rx.patient(patient_id),
    doctor_id       INT NOT NULL REFERENCES rx.doctor(doctor_id),
    written_date    DATE NOT NULL,
    status          VARCHAR(20) DEFAULT 'ACTIVE',
    notes           TEXT
);

-- PRESCRIPTION ITEM
CREATE TABLE rx.prescription_item (
    prescription_item_id SERIAL PRIMARY KEY,
    prescription_id      INT NOT NULL REFERENCES rx.prescription(prescription_id) ON DELETE CASCADE,
    drug_id              INT NOT NULL REFERENCES rx.drug(drug_id),
    dosage               VARCHAR(50),
    frequency            VARCHAR(50),
    duration_days        INT,
    route                VARCHAR(50),
    instructions         TEXT
);


CREATE TABLE rx.encounter (
    encounter_id      SERIAL PRIMARY KEY,
    patient_id        INT NOT NULL REFERENCES rx.patient(patient_id),
    doctor_id         INT NOT NULL REFERENCES rx.doctor(doctor_id),
    encounter_date    TIMESTAMP NOT NULL,
    encounter_type    VARCHAR(50),     -- Office Visit, Telehealth, Urgent Care
    reason            TEXT,
    status            VARCHAR(20) DEFAULT 'COMPLETED'
);


CREATE TABLE rx.payer (
    payer_id      SERIAL PRIMARY KEY,
    payer_name    VARCHAR(100) NOT NULL,
    payer_type    VARCHAR(50),     -- Commercial, Medicare, Medicaid, Self-Pay
    phone         VARCHAR(20),
    address       TEXT
);


CREATE TABLE rx.claim (
    claim_id         SERIAL PRIMARY KEY,
    encounter_id     INT NOT NULL REFERENCES rx.encounter(encounter_id),
    payer_id         INT NOT NULL REFERENCES rx.payer(payer_id),
    claim_number     VARCHAR(40) UNIQUE NOT NULL,
    claim_date       DATE NOT NULL,
    total_amount     NUMERIC(10,2),
    status           VARCHAR(20) DEFAULT 'SUBMITTED',  -- Submitted, Paid, Denied, Pending
    notes            TEXT
);


CREATE TABLE rx.claim_line (
    claim_line_id    SERIAL PRIMARY KEY,
    claim_id         INT NOT NULL REFERENCES rx.claim(claim_id) ON DELETE CASCADE,
    cpt_code         VARCHAR(10) NOT NULL,
    description      VARCHAR(200),
    quantity         INT DEFAULT 1,
    charge_amount    NUMERIC(10,2) NOT NULL,
    allowed_amount   NUMERIC(10,2),
    status           VARCHAR(20) DEFAULT 'PENDING'   -- Paid, Denied, Adjusted
);


CREATE TABLE rx.payment (
    payment_id       SERIAL PRIMARY KEY,
    claim_id         INT NOT NULL REFERENCES rx.claim(claim_id),
    payment_date     DATE NOT NULL,
    paid_amount      NUMERIC(10,2) NOT NULL,
    adjustment_amount NUMERIC(10,2),
    patient_responsibility NUMERIC(10,2),
    payment_method   VARCHAR(50),   -- EFT, Check, Credit
    reference_number VARCHAR(50)
);


/*
DELETE FROM rx.prescription_item;
DELETE FROM rx.prescription;
DELETE FROM rx.claim_line;
DELETE FROM rx.payment;
DELETE FROM rx.claim;
DELETE FROM rx.encounter;
DELETE FROM rx.drug;
DELETE FROM rx.payer;
DELETE FROM rx.doctor;
DELETE FROM rx.patient;
*/


