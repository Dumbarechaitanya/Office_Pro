-- ============================================================
-- Office_Pro ERP — Complete Database Schema
-- PostgreSQL
-- Odoo-inspired foundation (ir_ tables) + business modules
-- All rules enforced at DB level: constraints, triggers, FKs
-- ============================================================

-- ------------------------------------------------------------
-- 0. SHARED FUNCTION: auto-update `updated_at` on every table
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- ============================================================
-- PART A: ODOO-INSPIRED FOUNDATION TABLES (ir_ / res_)
-- ============================================================

-- ------------------------------------------------------------
-- A1. res_groups — permission groups (e.g. HR Manager, Employee)
-- ------------------------------------------------------------
CREATE TABLE res_groups (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_res_groups_updated_at
BEFORE UPDATE ON res_groups
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A2. res_users — login accounts
-- (employee_id FK added later via ALTER, since employee table
--  doesn't exist yet at this point)
-- ------------------------------------------------------------
CREATE TABLE res_users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100) NOT NULL UNIQUE,
    email           VARCHAR(150) NOT NULL UNIQUE,
    password_hash   VARCHAR(255) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_res_users_updated_at
BEFORE UPDATE ON res_users
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE res_company (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(150),
    phone           VARCHAR(20),
    address         TEXT,
    logo_url        VARCHAR(255),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_res_company_updated_at
BEFORE UPDATE ON res_company
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- link users to a company
ALTER TABLE res_users
    ADD COLUMN company_id INTEGER REFERENCES res_company(id) ON DELETE RESTRICT;

CREATE TABLE res_partner (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(150),
    phone           VARCHAR(20),
    address         TEXT,
    is_company      BOOLEAN NOT NULL DEFAULT FALSE,
    parent_id       INTEGER REFERENCES res_partner(id) ON DELETE RESTRICT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_res_partner_updated_at
BEFORE UPDATE ON res_partner
FOR EACH ROW EXECUTE FUNCTION set_updated_at();
-- ------------------------------------------------------------
-- A3. res_users_groups — many-to-many: user <-> group
-- ------------------------------------------------------------
CREATE TABLE res_users_groups (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES res_users(id) ON DELETE RESTRICT,
    group_id        INTEGER NOT NULL REFERENCES res_groups(id) ON DELETE RESTRICT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(user_id, group_id)
);

CREATE TRIGGER trg_res_users_groups_updated_at
BEFORE UPDATE ON res_users_groups
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A4. ir_module — module activation state (Odoo-style)
-- ------------------------------------------------------------
CREATE TABLE ir_module (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    state           VARCHAR(20) NOT NULL DEFAULT 'uninstalled'
                    CHECK (state IN ('uninstalled', 'installed', 'to_upgrade')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_ir_module_updated_at
BEFORE UPDATE ON ir_module
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE ir_ui_menu (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    parent_id       INTEGER REFERENCES ir_ui_menu(id) ON DELETE RESTRICT,
    sequence        INTEGER NOT NULL DEFAULT 10,
    url_path        VARCHAR(255),
    action_model    VARCHAR(100),
    web_icon        VARCHAR(255),
    visibility_group_id INTEGER REFERENCES res_groups(id) ON DELETE RESTRICT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_ir_ui_menu_updated_at
BEFORE UPDATE ON ir_ui_menu
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A5. ir_model — registry of every model/table
--
-- CHANGED: added abstract, transient, is_mail_thread,
-- is_mail_activity, is_mail_blacklist, model_order, state --
-- these back the "New Model" create form and its checkboxes.
-- 'model_order' (not 'order') to avoid the SQL reserved word.
-- 'state' distinguishes rows synced from a real Django model
-- ('base') from rows created via the New Model form ('manual').
-- ------------------------------------------------------------
CREATE TABLE ir_model (
    id                  SERIAL PRIMARY KEY,
    model_name          VARCHAR(100) NOT NULL UNIQUE,
    table_name          VARCHAR(100) NOT NULL,
    module_id           INTEGER REFERENCES ir_module(id) ON DELETE RESTRICT,
    description         VARCHAR(255),
    abstract            BOOLEAN NOT NULL DEFAULT FALSE,
    transient           BOOLEAN NOT NULL DEFAULT FALSE,
    is_mail_thread      BOOLEAN NOT NULL DEFAULT FALSE,
    is_mail_activity    BOOLEAN NOT NULL DEFAULT FALSE,
    is_mail_blacklist   BOOLEAN NOT NULL DEFAULT FALSE,
    model_order         VARCHAR(255) NOT NULL DEFAULT 'id',
    state               VARCHAR(20) NOT NULL DEFAULT 'manual'
                        CHECK (state IN ('base', 'manual')),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_ir_model_updated_at
BEFORE UPDATE ON ir_model
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A5b. ir_filters — saved searches / favorites (Odoo ir.filters
-- equivalent). MOVED here from before ir_model existed: it
-- references ir_model(id), so it must be created after A5.
-- (Original file created this before ir_model, which errors on
-- a fresh run since the referenced table didn't exist yet.)
-- Also added the missing updated_at trigger for consistency
-- with every other table in this schema.
-- ------------------------------------------------------------
CREATE TABLE ir_filters (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    model_id        INTEGER NOT NULL REFERENCES ir_model(id),
    user_id         INTEGER NULL REFERENCES res_users(id),
    domain          JSONB NOT NULL DEFAULT '[]',
    context         JSONB NOT NULL DEFAULT '{}',
    is_default      BOOLEAN NOT NULL DEFAULT FALSE,
    sequence        INTEGER NOT NULL DEFAULT 10,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (model_id, user_id, name)
);

CREATE TRIGGER trg_ir_filters_updated_at
BEFORE UPDATE ON ir_filters
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A6. ir_model_fields — registry of every field on every model
--
-- CHANGED: added relation_model_id -- lets an FK-type field
-- record which model it relates to, so the many2one chip
-- widget knows what to search against.
-- ------------------------------------------------------------
CREATE TABLE ir_model_fields (
    id                  SERIAL PRIMARY KEY,
    model_id            INTEGER NOT NULL REFERENCES ir_model(id) ON DELETE RESTRICT,
    field_name          VARCHAR(100) NOT NULL,
    field_type          VARCHAR(50) NOT NULL
                        CHECK (field_type IN ('VARCHAR','TEXT','INTEGER','DECIMAL','BOOLEAN','DATE','DATETIME','FK')),
    relation_model_id   INTEGER NULL REFERENCES ir_model(id),
    is_required         BOOLEAN NOT NULL DEFAULT FALSE,
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(model_id, field_name)
);

CREATE TRIGGER trg_ir_model_fields_updated_at
BEFORE UPDATE ON ir_model_fields
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A6b. ir_ui_view — registry of views (list/form/kanban/etc)
-- per model. Since views here are real Django templates (not
-- stored XML like Odoo), template_path documents which file
-- backs the view rather than storing an arch.
-- ------------------------------------------------------------
CREATE TABLE ir_ui_view (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    view_type       VARCHAR(20) NOT NULL DEFAULT 'list'
                    CHECK (view_type IN ('list','form','graph','pivot','calendar','kanban','search','qweb','hierarchy','activity')),
    model_id        INTEGER NULL REFERENCES ir_model(id),
    key             VARCHAR(150),
    visibility      VARCHAR(100),
    inherit_id      INTEGER NULL REFERENCES ir_ui_view(id),
    mode            VARCHAR(20) NOT NULL DEFAULT 'primary',
    model_data      VARCHAR(255),
    external_id     VARCHAR(255),
    arch            TEXT,
    template_path   VARCHAR(255),
    priority        INTEGER NOT NULL DEFAULT 16,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_ir_ui_view_updated_at
BEFORE UPDATE ON ir_ui_view
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A7. ir_model_access — CRUD permission matrix per group
-- ------------------------------------------------------------
CREATE TABLE ir_model_access (
    id              SERIAL PRIMARY KEY,
    model_id        INTEGER NOT NULL REFERENCES ir_model(id) ON DELETE RESTRICT,
    group_id        INTEGER NOT NULL REFERENCES res_groups(id) ON DELETE RESTRICT,
    can_read        BOOLEAN NOT NULL DEFAULT TRUE,
    can_write       BOOLEAN NOT NULL DEFAULT FALSE,
    can_create      BOOLEAN NOT NULL DEFAULT FALSE,
    can_delete      BOOLEAN NOT NULL DEFAULT FALSE,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(model_id, group_id)
);

CREATE TRIGGER trg_ir_model_access_updated_at
BEFORE UPDATE ON ir_model_access
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A8. ir_rule — simplified row-level security rules
-- ------------------------------------------------------------
CREATE TABLE ir_rule (
    id                SERIAL PRIMARY KEY,
    model_id          INTEGER NOT NULL REFERENCES ir_model(id) ON DELETE RESTRICT,
    group_id          INTEGER REFERENCES res_groups(id) ON DELETE RESTRICT,  -- NULL = applies to everyone
    rule_name         VARCHAR(150) NOT NULL,
    condition_field   VARCHAR(100) NOT NULL,
    condition_value   VARCHAR(100) NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at        TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_ir_rule_updated_at
BEFORE UPDATE ON ir_rule
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- A9. ir_sequence — auto-numbering (e.g. EMP0001, INV0001)
-- ------------------------------------------------------------
CREATE TABLE ir_sequence (
    id              SERIAL PRIMARY KEY,
    code            VARCHAR(100) NOT NULL UNIQUE,
    prefix          VARCHAR(20),
    next_number     INTEGER NOT NULL DEFAULT 1 CHECK (next_number > 0),
    padding         INTEGER NOT NULL DEFAULT 4 CHECK (padding > 0),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_ir_sequence_updated_at
BEFORE UPDATE ON ir_sequence
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ============================================================
-- PART B: BUSINESS MODULE TABLES
-- ============================================================

-- ------------------------------------------------------------
-- B1. employee — foundation table, most others depend on this
-- ------------------------------------------------------------
CREATE TABLE employee (
    id              SERIAL PRIMARY KEY,
    employee_code   VARCHAR(20) NOT NULL UNIQUE,
    name            VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL UNIQUE,
    phone           VARCHAR(20),
    department      VARCHAR(100),
    job_title       VARCHAR(100),
    date_joined     DATE NOT NULL,
    manager_id      INTEGER REFERENCES employee(id) ON DELETE RESTRICT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_employee_updated_at
BEFORE UPDATE ON employee
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- Now that employee exists, link res_users to it
ALTER TABLE res_users
    ADD COLUMN employee_id INTEGER REFERENCES employee(id) ON DELETE RESTRICT;


-- ------------------------------------------------------------
-- B2. attendance
-- ------------------------------------------------------------
CREATE TABLE attendance (
    id              SERIAL PRIMARY KEY,
    employee_id     INTEGER NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    date            DATE NOT NULL,
    check_in        TIMESTAMP,
    check_out       TIMESTAMP,
    status          VARCHAR(20) NOT NULL
                    CHECK (status IN ('Present', 'Absent', 'Half Day', 'Late')),
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(employee_id, date),
    CHECK (check_out IS NULL OR check_out > check_in)
);

CREATE TRIGGER trg_attendance_updated_at
BEFORE UPDATE ON attendance
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- B3. leave_type + leave_request
-- ------------------------------------------------------------
CREATE TABLE leave_type (
    id                  SERIAL PRIMARY KEY,
    name                VARCHAR(100) NOT NULL UNIQUE,
    max_days_per_year   INTEGER NOT NULL CHECK (max_days_per_year > 0),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_leave_type_updated_at
BEFORE UPDATE ON leave_type
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE leave_request (
    id              SERIAL PRIMARY KEY,
    employee_id     INTEGER NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    leave_type_id   INTEGER NOT NULL REFERENCES leave_type(id) ON DELETE RESTRICT,
    start_date      DATE NOT NULL,
    end_date        DATE NOT NULL,
    reason          TEXT,
    status          VARCHAR(20) NOT NULL DEFAULT 'Pending'
                    CHECK (status IN ('Pending', 'Approved', 'Rejected')),
    approved_by     INTEGER REFERENCES employee(id) ON DELETE RESTRICT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (end_date >= start_date)
);

CREATE TRIGGER trg_leave_request_updated_at
BEFORE UPDATE ON leave_request
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- B4. project + project_member
-- ------------------------------------------------------------
CREATE TABLE project (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    description     TEXT,
    start_date      DATE NOT NULL,
    end_date        DATE,
    status          VARCHAR(20) NOT NULL DEFAULT 'Not Started'
                    CHECK (status IN ('Not Started', 'In Progress', 'Completed', 'On Hold')),
    manager_id      INTEGER NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TRIGGER trg_project_updated_at
BEFORE UPDATE ON project
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE project_member (
    id              SERIAL PRIMARY KEY,
    project_id      INTEGER NOT NULL REFERENCES project(id) ON DELETE RESTRICT,
    employee_id     INTEGER NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    role            VARCHAR(50) NOT NULL,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE(project_id, employee_id)
);

CREATE TRIGGER trg_project_member_updated_at
BEFORE UPDATE ON project_member
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- B5. timesheet
-- ------------------------------------------------------------
CREATE TABLE timesheet (
    id                  SERIAL PRIMARY KEY,
    employee_id         INTEGER NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    project_id          INTEGER NOT NULL REFERENCES project(id) ON DELETE RESTRICT,
    date                DATE NOT NULL,
    hours_worked        DECIMAL(4,2) NOT NULL CHECK (hours_worked > 0 AND hours_worked <= 24),
    task_description    TEXT,
    status              VARCHAR(20) NOT NULL DEFAULT 'Draft'
                        CHECK (status IN ('Draft', 'Submitted', 'Approved')),
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_timesheet_updated_at
BEFORE UPDATE ON timesheet
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- B6. accounting: account, journal_entry, journal_line
-- ------------------------------------------------------------
CREATE TABLE account (
    id              SERIAL PRIMARY KEY,
    name            VARCHAR(100) NOT NULL UNIQUE,
    account_type    VARCHAR(20) NOT NULL
                    CHECK (account_type IN ('Asset', 'Liability', 'Equity', 'Income', 'Expense')),
    balance         DECIMAL(10,2) NOT NULL DEFAULT 0,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_account_updated_at
BEFORE UPDATE ON account
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE journal_entry (
    id              SERIAL PRIMARY KEY,
    date            DATE NOT NULL,
    reference       VARCHAR(100) NOT NULL UNIQUE,
    description     TEXT,
    created_by      INTEGER NOT NULL REFERENCES employee(id) ON DELETE RESTRICT,
    is_active       BOOLEAN NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TRIGGER trg_journal_entry_updated_at
BEFORE UPDATE ON journal_entry
FOR EACH ROW EXECUTE FUNCTION set_updated_at();

CREATE TABLE journal_line (
    id                  SERIAL PRIMARY KEY,
    journal_entry_id    INTEGER NOT NULL REFERENCES journal_entry(id) ON DELETE RESTRICT,
    account_id           INTEGER NOT NULL REFERENCES account(id) ON DELETE RESTRICT,
    debit                 DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (debit >= 0),
    credit                DECIMAL(10,2) NOT NULL DEFAULT 0 CHECK (credit >= 0),
    is_active             BOOLEAN NOT NULL DEFAULT TRUE,
    created_at            TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMP NOT NULL DEFAULT NOW(),
    CHECK (NOT (debit > 0 AND credit > 0))  -- a line is either a debit or a credit, never both
);

CREATE TRIGGER trg_journal_line_updated_at
BEFORE UPDATE ON journal_line
FOR EACH ROW EXECUTE FUNCTION set_updated_at();


-- ------------------------------------------------------------
-- B7. DOUBLE-ENTRY BOOKKEEPING RULE (DB-enforced)
-- Every journal_entry's total debits must equal total credits.
-- Checked whenever a journal_line is inserted/updated/deleted.
-- ------------------------------------------------------------
CREATE OR REPLACE FUNCTION check_journal_balance()
RETURNS TRIGGER AS $$
DECLARE
    total_debit     DECIMAL(10,2);
    total_credit    DECIMAL(10,2);
    entry_id        INTEGER;
BEGIN
    entry_id := COALESCE(NEW.journal_entry_id, OLD.journal_entry_id);

    SELECT COALESCE(SUM(debit), 0), COALESCE(SUM(credit), 0)
    INTO total_debit, total_credit
    FROM journal_line
    WHERE journal_entry_id = entry_id
      AND is_active = TRUE;

    IF total_debit <> total_credit THEN
        RAISE EXCEPTION 'Journal entry % is unbalanced: total debit (%) does not equal total credit (%)',
            entry_id, total_debit, total_credit;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- NOTE: this trigger checks balance AFTER each line is written.
-- In practice, insert all lines of a journal_entry inside a single
-- transaction (BEGIN ... COMMIT) so the check only matters at commit time,
-- otherwise inserting lines one-by-one will fail on the first (unbalanced) line.
CREATE CONSTRAINT TRIGGER trg_check_journal_balance
AFTER INSERT OR UPDATE OR DELETE ON journal_line
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW EXECUTE FUNCTION check_journal_balance();


-- ============================================================
-- DONE. Run this file top-to-bottom on a fresh database:
--   psql -U your_user -d office_pro_dev -f schema.sql
-- ============================================================