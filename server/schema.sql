
-- Common columns used across all tables:
-- Id: TEXT(18) primary key (Salesforce-like 18-char id)
-- CreatedDate: DATETIME default CURRENT_TIMESTAMP
-- LastModifiedDate: DATETIME updated via trigger
-- DeletedAt: DATETIME NULL for soft-deletes

PRAGMA foreign_keys = ON;

-- Use default expressions for Id generation: 9 random bytes -> 18 hex chars

-- customers table
CREATE TABLE IF NOT EXISTS customers (
  Id TEXT PRIMARY KEY NOT NULL DEFAULT (upper(hex(randomblob(9)))),
  Name VARCHAR(120) NOT NULL,
  Phone VARCHAR(20) UNIQUE,
  Balance NUMERIC(10,2) DEFAULT 0.00,
  Notes TEXT,
  Disabled BOOLEAN DEFAULT 0,
  CreatedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  LastModifiedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  DeletedAt DATETIME
);

CREATE TRIGGER IF NOT EXISTS customers_update_lastmodified
AFTER UPDATE ON customers
FOR EACH ROW WHEN (NEW.LastModifiedDate = OLD.LastModifiedDate)
BEGIN
  UPDATE customers SET LastModifiedDate = CURRENT_TIMESTAMP WHERE Id = OLD.Id;
END;

-- credithistory table
CREATE TABLE IF NOT EXISTS credithistory (
  Id TEXT PRIMARY KEY NOT NULL DEFAULT (upper(hex(randomblob(9)))),
  CustomerId TEXT NOT NULL,
  Type TEXT CHECK (Type IN ('credit','debit')) NOT NULL,
  Amount NUMERIC(10,2) NOT NULL,
  ModeOfPayment TEXT CHECK (ModeOfPayment IN ('bill','cash','upi','cheque','neft')) NOT NULL,
  PreviousBalance NUMERIC(10,2) DEFAULT 0.00,
  CreatedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  LastModifiedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  DeletedAt DATETIME,
  FOREIGN KEY (CustomerId) REFERENCES customers(Id)
);

CREATE INDEX IF NOT EXISTS idx_credithistory_customerid ON credithistory(CustomerId);

CREATE TRIGGER IF NOT EXISTS credithistory_update_lastmodified
AFTER UPDATE ON credithistory
FOR EACH ROW WHEN (NEW.LastModifiedDate = OLD.LastModifiedDate)
BEGIN
  UPDATE credithistory SET LastModifiedDate = CURRENT_TIMESTAMP WHERE Id = OLD.Id;
END;

-- globals table
CREATE TABLE IF NOT EXISTS globals (
  Id TEXT PRIMARY KEY NOT NULL DEFAULT (upper(hex(randomblob(9)))),
  Key VARCHAR(64) UNIQUE NOT NULL,
  Value VARCHAR(256),
  CreatedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  LastModifiedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  DeletedAt DATETIME
);

CREATE TRIGGER IF NOT EXISTS globals_update_lastmodified
AFTER UPDATE ON globals
FOR EACH ROW WHEN (NEW.LastModifiedDate = OLD.LastModifiedDate)
BEGIN
  UPDATE globals SET LastModifiedDate = CURRENT_TIMESTAMP WHERE Id = OLD.Id;
END;

-- goldcertificate table
CREATE TABLE IF NOT EXISTS goldcertificate (
  Id TEXT PRIMARY KEY NOT NULL DEFAULT (upper(hex(randomblob(9)))),
  CustomerId TEXT,
  Status TEXT CHECK (Status IN ('pending','completed','cancelled')) DEFAULT 'pending',
  Data TEXT,
  ModeOfPayment TEXT CHECK (ModeOfPayment IN ('bill','cash','upi','cheque','neft')),
  Total NUMERIC(10,2) DEFAULT 0.00,
  GST NUMERIC(10,2) DEFAULT 0.00,
  GSTBillNumber VARCHAR(32),
  TotalTax NUMERIC(10,2) DEFAULT 0.00,
  CreatedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  LastModifiedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  DeletedAt DATETIME,
  FOREIGN KEY (CustomerId) REFERENCES customers(Id)
);

CREATE INDEX IF NOT EXISTS idx_goldcertificate_customerid ON goldcertificate(CustomerId);

CREATE TRIGGER IF NOT EXISTS goldcertificate_update_lastmodified
AFTER UPDATE ON goldcertificate
FOR EACH ROW WHEN (NEW.LastModifiedDate = OLD.LastModifiedDate)
BEGIN
  UPDATE goldcertificate SET LastModifiedDate = CURRENT_TIMESTAMP WHERE Id = OLD.Id;
END;

-- goldtest table
CREATE TABLE IF NOT EXISTS goldtest (
  Id TEXT PRIMARY KEY NOT NULL DEFAULT (upper(hex(randomblob(9)))),
  CustomerId TEXT,
  Status TEXT CHECK (Status IN ('pending','completed','cancelled')) DEFAULT 'pending',
  Data TEXT,
  ModeOfPayment TEXT CHECK (ModeOfPayment IN ('bill','cash','upi','cheque','neft')),
  Total NUMERIC(10,2) DEFAULT 0.00,
  CreatedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  LastModifiedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  DeletedAt DATETIME,
  FOREIGN KEY (CustomerId) REFERENCES customers(Id)
);

CREATE INDEX IF NOT EXISTS idx_goldtest_customerid ON goldtest(CustomerId);

CREATE TRIGGER IF NOT EXISTS goldtest_update_lastmodified
AFTER UPDATE ON goldtest
FOR EACH ROW WHEN (NEW.LastModifiedDate = OLD.LastModifiedDate)
BEGIN
  UPDATE goldtest SET LastModifiedDate = CURRENT_TIMESTAMP WHERE Id = OLD.Id;
END;

-- photocertificate table
CREATE TABLE IF NOT EXISTS photocertificate (
  Id TEXT PRIMARY KEY NOT NULL DEFAULT (upper(hex(randomblob(9)))),
  CustomerId TEXT,
  Media TEXT,
  Status TEXT CHECK (Status IN ('pending','completed','cancelled')) DEFAULT 'pending',
  Data TEXT,
  ModeOfPayment TEXT CHECK (ModeOfPayment IN ('bill','cash','upi','cheque','neft')),
  Total NUMERIC(10,2) DEFAULT 0.00,
  GST NUMERIC(10,2) DEFAULT 0.00,
  GSTBillNumber VARCHAR(32),
  TotalTax NUMERIC(10,2) DEFAULT 0.00,
  CreatedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  LastModifiedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  DeletedAt DATETIME,
  FOREIGN KEY (CustomerId) REFERENCES customers(Id)
);

CREATE INDEX IF NOT EXISTS idx_photocertificate_customerid ON photocertificate(CustomerId);

CREATE TRIGGER IF NOT EXISTS photocertificate_update_lastmodified
AFTER UPDATE ON photocertificate
FOR EACH ROW WHEN (NEW.LastModifiedDate = OLD.LastModifiedDate)
BEGIN
  UPDATE photocertificate SET LastModifiedDate = CURRENT_TIMESTAMP WHERE Id = OLD.Id;
END;

-- silvercertificate table
CREATE TABLE IF NOT EXISTS silvercertificate (
  Id TEXT PRIMARY KEY NOT NULL DEFAULT (upper(hex(randomblob(9)))),
  CustomerId TEXT,
  Status TEXT CHECK (Status IN ('pending','completed','cancelled')) DEFAULT 'pending',
  Data TEXT,
  ModeOfPayment TEXT CHECK (ModeOfPayment IN ('bill','cash','upi','cheque','neft')),
  Total NUMERIC(10,2) DEFAULT 0.00,
  GST NUMERIC(10,2) DEFAULT 0.00,
  GSTBillNumber VARCHAR(32),
  TotalTax NUMERIC(10,2) DEFAULT 0.00,
  CreatedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  LastModifiedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  DeletedAt DATETIME,
  FOREIGN KEY (CustomerId) REFERENCES customers(Id)
);

CREATE INDEX IF NOT EXISTS idx_silvercertificate_customerid ON silvercertificate(CustomerId);

CREATE TRIGGER IF NOT EXISTS silvercertificate_update_lastmodified
AFTER UPDATE ON silvercertificate
FOR EACH ROW WHEN (NEW.LastModifiedDate = OLD.LastModifiedDate)
BEGIN
  UPDATE silvercertificate SET LastModifiedDate = CURRENT_TIMESTAMP WHERE Id = OLD.Id;
END;

-- weightlosshistory table
CREATE TABLE IF NOT EXISTS weightlosshistory (
  Id TEXT PRIMARY KEY NOT NULL DEFAULT (upper(hex(randomblob(9)))),
  CustomerId TEXT NOT NULL,
  Amount NUMERIC(10,2) NOT NULL,
  ModeOfPayment TEXT CHECK (ModeOfPayment IN ('bill','cash','upi','cheque','neft')) NOT NULL,
  CreatedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  LastModifiedDate DATETIME DEFAULT (CURRENT_TIMESTAMP),
  DeletedAt DATETIME,
  FOREIGN KEY (CustomerId) REFERENCES customers(Id)
);

CREATE INDEX IF NOT EXISTS idx_weightlosshistory_customerid ON weightlosshistory(CustomerId);

CREATE TRIGGER IF NOT EXISTS weightlosshistory_update_lastmodified
AFTER UPDATE ON weightlosshistory
FOR EACH ROW WHEN (NEW.LastModifiedDate = OLD.LastModifiedDate)
BEGIN
  UPDATE weightlosshistory SET LastModifiedDate = CURRENT_TIMESTAMP WHERE Id = OLD.Id;
END;