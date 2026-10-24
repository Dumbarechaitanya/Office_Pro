# Office Pro — Master Project Defense & Guide / HOD Viva Questionnaire

**Project Title:** Office Pro: Modern Modular Enterprise Resource Planning & Office Management Platform  
**Academic Year:** 2026-27 | **Class:** B.E. Information Technology (Semester VII)  
**Institution:** Shivajirao S. Jondhale College of Engineering, Dombivli(E) (Affiliated to University of Mumbai)  
**Supervisor / Project Guide:** Dr. Parjkta Khaire  
**Project Coordinator:** Dr. M. R. Gorbal | **Head of Department:** Dr. Savita Sangam | **Principal:** Dr. Uttara Gogate  

**Project Team Members:**
1. **Dumbre Chaitanya** (Roll No: 09) - *System Architecture, Foundations & Core Settings*
2. **Shripad Patil** (Roll No: 24) - *Operational Workflows, Employee Master & Attendance*
3. **Pranay Shelar** (Roll No: 32) - *Leave Subsystems, Zero-Touch Discovery & Security*
4. **Saurabh Shigavan** (Roll No: 33) - *Executive Dashboard, UI/UX Engineering & Live Defense*

---

## Table of Contents

1. [Team Presentation Speaking Division (4 Team Members)](#1-team-presentation-speaking-division-4-team-members)
2. [The Foundational 5W: WHAT, WHY, HOW, WHO, WHEN](#2-the-foundational-5w-what-why-how-who-when)
   - 2.1 [WHAT is this Project?](#21-what-is-this-project)
   - 2.2 [WHY are we building this Project?](#22-why-are-we-building-this-project-problem-statement)
   - 2.3 [HOW does it work -  (High-Level Design)](#23-how-does-it-work-high-level-design)
   - 2.4 [WHO uses the System -  (User Personas)](#24-who-uses-the-system-user-roles)
   - 2.5 [WHEN do key actions happen -  (Operational Schedule)](#25-when-do-key-actions-happen-schedule--deadlines)
3. [Business Modules & Operational Rules](#3-business-modules--operational-rules)
   - 3.1 [Employee Directory & Approver Matrix](#31-employee-directory--approver-matrix)
   - 3.2 [Projects & Mandatory 8-Hour Timesheet Rule](#32-projects--mandatory-8-hour-timesheet-rule)
   - 3.3 [Attendance & 8 Net-Hours Tracking](#33-attendance--8-net-hours-tracking)
   - 3.4 [Leave / Time Off & 2-Tier Approvals](#34-leave--time-off--2-tier-approvals)
   - 3.5 [Expense Claims & Project Cost Tagging](#35-expense-claims--project-cost-tagging)
   - 3.6 [Invoicing, 3 Billing Policies & Real-Time Project Profitability](#36-invoicing-3-billing-policies--real-time-project-profitability)
4. [Technical Architecture & Subsystems Engine (Deep Dive)](#4-technical-architecture--subsystems-engine-deep-dive)
   - 4.1 [Two-Tier Zero-Touch Modularity](#41-two-tier-zero-touch-modularity)
   - 4.2 [Dynamic Metadata Discovery (ir.model & ir.model.fields)](#42-dynamic-metadata-discovery-irmodel--irmodelfields)
   - 4.3 [Background Scheduler Engine (ir.cron)](#43-background-scheduler-engine-ircron)
   - 4.4 [Security Engine: Table Access vs Row-Level Rules (ir.rule)](#44-security-engine-table-access-vs-row-level-rules-irrule)
   - 4.5 [Developer Mode ( - =1) & Runtime Theming](#45-developer-mode-debug1--runtime-theming)
5. [Top Practical Questions Your Guide / HOD May Ask](#5-top-practical-questions-your-guide--hod-may-ask)
6. [5-Minute Step-by-Step Live Platform Presentation Script](#6-5-minute-step-by-step-live-platform-presentation-script)

---

## 1. Team Presentation Speaking Division (4 Team Members)

To give a smooth, well-coordinated group presentation on Monday, divide the topics among your **4 team members** as follows:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                        OFFICE PRO 4-MEMBER PRESENTATION PLAN                           │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 👤 DUMBRE CHAITANYA (09) - (Intro & Foundation) - Time: ~1.2 Mins                      │
│ • Section 2.1: WHAT is Office Pro -  (Scope & 6 Business Modules)                        │
│ • Section 2.2: WHY this Project? (Spreadsheet chaos, no real-time profit visibility)  │
│ • Section 2.3: HOW it works (High-level 2-tier design, Django + PostgreSQL)            │
│ • Section 2.4: WHO uses it (Roles: Staff, Project Leaders, Approvers, HR, Finance)    │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 👤 SHRIPAD PATIL (24) - (Operational Schedule & Core Modules) - Time: ~1.5 Mins        │
│ • Section 2.5: WHEN key actions happen (Monday 3PM deadline, Tuesday approvals)        │
│ • Section 3.1: Employee Master & Hourly Labor Rate Setup                               │
│ • Section 3.2: Projects, Area (sq.ft) & Mandatory 8-Hour Daily Timesheet Rule          │
│ • Section 3.3: Attendance & 8 Net-Hours Rule (Punches, Breaks, Missing logs)           │
│ • Section 3.4: Leave / Time Off & 2-Tier Approvals (Manager ➔ Executive)              │
│ • Section 3.5: Expense Claims & Project Cost Tagging                                   │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 👤 PRANAY SHELAR (32) - (Financial Engine & Technical Subsystems) - Time: ~1.5 Mins    │
│ • Section 3.6: Invoicing (3 Billing Policies: Milestone, Timesheet, Lumpsum)           │
│ • Section 3.6: Real-Time Project Profitability Mathematical Model                      │
│ • Section 4.1: Zero-Touch Modularity (How Django apps plug in without core edits)      │
│ • Section 4.2: Dynamic Metadata Engine (ir.model & ir.model.fields auto-discovery)    │
│ • Section 4.3: Background Cron Jobs (ir.cron) & Row-Level Security (ir.rule)           │
│ • Section 4.4: Developer Mode ( - =1) & Dynamic UI Theme Tokens                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ 👤 SAURABH SHIGAVAN (33) - (Live Platform Walkthrough & Q&A Defense) - Time: ~1.0 Min  │
│ • Live Interactive Screen Walkthrough (Navigating the live platform in browser)        │
│ • Co-answering Guide/HOD practical questions with the team                             │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. The Foundational 5W: WHAT, WHY, HOW, WHO, WHEN

### 2.1 WHAT is this Project?
* **Plain English Definition:** **Office Pro** is an all-in-one web-based ERP and Office Management platform built for project-based companies (architects, civil engineers, software firms, and consultants).
* **What does it contain - **
  1. **Employee Management**: Staff profiles, Hourly CTC costing rates, and multi-level approver matrices.
  2. **Projects & Timesheets**: Project sizing (in sq. ft.), milestone schedules, and an 8-hour daily timesheet validation engine.
  3. **Biometric Attendance**: Digital punch simulation (In/Out/Break) and 8 net-hours daily compliance.
  4. **Leave / Time Off**: Real-time balances (Vacation, Sick, Comp-off) and 2-level approvals.
  5. **Expense Claims**: Out-of-pocket bills tagged to company overhead or specific client projects.
  6. **Accounting & Invoicing**: GST-compliant tax invoices (Milestone, Timesheet, Lumpsum) and **Real-Time Project Profitability** tracking.
  7. **Webmail**: Integrated internal email client.

---

### 2.2 WHY are we building this Project? (Problem Statement)
* **The Problem Today:**
  - Most medium-sized companies use 4 to 5 separate tools: Excel for timesheets, biometric desktop software for attendance, WhatsApp/Email for leave requests, paper bills for expenses, and standalone accounting software.
* **The 3 Main Pain Points Solved:**
  1. **No Real-Time Profitability**: Management cannot see if a project is profitable until months after it finishes because employee hourly salary costs and expenses are not linked to client billing.
  2. **Timesheet Guesswork**: Employees log fake hours at the end of the month. Office Pro requires **at least 8 hours logged per workday** before submitting.
  3. **No Integration**: Leaves don't sync with timesheets, and biometric punch data doesn't sync with payroll.
* **Why not standard Odoo or SAP - **
  - Commercial ERPs are too heavy, rigid, and expensive. Office Pro provides tailored operational rules with lightweight deployment.

---

### 2.3 HOW does it work -  (Simple Architecture)
* **Two Simple Layers:**
  1. **Core Base**: Provides user login, company branches, security rules, and user-friendly Odoo-style themes (Purple, Slate, Ocean, Emerald).
  2. **Business Modules**: Each module (Employee, Project, Attendance, Leave, Expense, Accounting) operates independently and connects together smoothly.
* **Technology Used**: **Python & Django** for the backend logic, **PostgreSQL** for the database, and **Clean HTML/CSS/JavaScript** for the fast, modern frontend.

---

### 2.4 WHO uses the System -  (User Roles)
1. **Employees**: Punch in/out, log daily project task hours, submit weekly timesheets before Monday 3:00 PM, and apply for leaves/expenses.
2. **Project Leaders**: Create projects, set area (sq. ft.), assign milestone budgets, borrow team members, and approve team timesheets by Tuesday 5:00 PM.
3. **Approvers (L1 Manager & L2 Executive Management)**: Review and approve leave/expense claims with 2-tier authorization.
4. **HR Administrator**: Manage employee master profiles, set Hourly CTC rates, and handle attendance regularizations.
5. **Billing & Finance Team**: Generate GST tax invoices, process expense payouts, and view real-time project profitability.
6. **Executive Directors / Managing Partners**: View company-wide project profit margins and team bandwidth.

---

### 2.5 WHEN do key actions happen -  (Schedule & Deadlines)
* **Daily**:
  - Staff Punch In / Break / Punch Out (system monitors 8 net working hours).
  - Staff log hours against project tasks.
* **Weekly Deadlines**:
  - **Every Monday at 3:00 PM**: Strict employee timesheet submission deadline (system blocks submission if any day has less than 8 hours).
  - **Every Tuesday at 5:00 PM**: Manager timesheet review & sign-off deadline.
* **Monthly**:
  - **1st of every month**: System automatically credits monthly Vacation and Sick leave balances.
* **Project Milestones**:
  - When a deliverable is completed, the billing officer issues a GST tax invoice, and the system automatically recalculates project gross profit.

---

## 3. Business Modules & Core Rules (Plain English)

### 3.1 Employee Directory & Approver Matrix
- **Hourly Labor Cost (CTC)**: Every employee has an hourly rate (e.g., Senior Architect: ₹1,200/hr, Junior Engineer: ₹450/hr). This allows the system to calculate exact project costs in real-time.
- **2-Tier Approver Matrix**:
  - **Timesheet Approver**: Direct manager signs off on weekly hours.
  - **Leave Approvers**: Level 1 (Direct Reporting Manager) ➔ Level 2 (Executive Management / Director).
  - **Expense Approvers**: Level 1 (Direct Reporting Manager) ➔ Level 2 (Finance Head / Executive Management).

### 3.2 Projects & Mandatory 8-Hour Timesheet Rule
- **Project Scope**: Tracks project code, built-up area (e.g., 45,000 sq.ft), budget hours, and billing policy (Milestone %, Hourly, or Lumpsum).
- **Mandatory 8-Hour Daily Rule**:
  - Employees must log **at least 8 hours for each workday (Monday to Friday)**.
  - The system will not allow timesheets to be submitted if any workday has less than 8 hours logged.
- **Overtime & Comp-Off Policy**:
  - **Weekdays (Mon–Fri)**: Staff must work at least **3.5 extra hours** beyond the standard 8 hours on a task to qualify for comp-off credit. (Senior managers are not eligible for weekday overtime).
  - **Weekends & Holidays**: 100% of verified hours worked on Saturdays, Sundays, or holidays convert 1-to-1 into Compensatory Leave balance upon manager approval.
- **Inter-Team Resource Borrowing**:
  - When a Project Leader borrows an engineer from another department, their hours and salary cost automatically route to the borrowing project.

### 3.3 Attendance & 8 Net-Hours Tracking
- Tracks daily punches: **Punch In**, **Break Out**, **Break In**, **Punch Out**.
- **Net Hours Calculation**:
  - Net Working Hours = (Punch Out Time - Punch In Time) - Total Break Duration.
  - System verifies if the employee completed 8 net working hours.
- **Missing Punches**: If an employee forgets to punch out, the system flags it and allows the employee to submit an **Attendance Regularization Request** to their manager.

### 3.4 Leave / Time Off & 2-Tier Approvals
- **Leave Types**: Vacation Leave, Sick Leave, Festival Holidays, Flexible Holidays, and Comp-Off (earned from overtime).
- **Backdated Leave Block**: Employees cannot apply for past dates without Admin approval.
- **Automatic Timesheet Sync**: When a leave is approved, the system automatically adds an 8-hour block to the employee's timesheet so they satisfy the daily 8-hour rule without manual entry.

### 3.5 Expense Claims & Project Cost Tagging
- Employees submit out-of-pocket bills (Travel, Site Food, Equipment, Printing).
- **Cost Tagging**: Expenses can be charged to general **Company Overhead** or tagged directly to a **Project** (e.g. Tech Park Phase 2).
- Follows 2-tier approval (Employee ➔ Manager ➔ Finance). Tagged project expenses directly debit the project budget.

### 3.6 Invoicing, 3 Billing Policies & Real-Time Project Profitability
*(Spoken by YOU)*

#### A. 3 Invoicing Policies Supported:
1. **Milestone-Based Billing**: Invoicing is triggered when specific project deliverables/stages are completed.
   - *Example:* For a ₹20 Lakh project: 20% (₹4 Lakhs) on Concept Approval, 40% (₹8 Lakhs) on Structural Drawings, 40% (₹8 Lakhs) on Final Handover.
2. **Timesheet-Based Billing (Hourly / Time & Materials)**: Invoicing is calculated directly from approved team hours multiplied by the client hourly billing rate.
   - *Example:* 120 approved team hours × ₹3,000/hr billing rate = **₹3.60 Lakhs invoice**.
3. **Lumpsum Billing (Fixed Fee)**: A pre-agreed fixed total project contract fee billed in scheduled periodic installments.
   - *Example:* A ₹24 Lakhs contract billed in **4 equal quarterly installments of ₹6 Lakhs each**, regardless of hours worked.

#### B. Real-Time Project Profitability Model (Plain English):
- **Project Gross Profit** = Total Invoiced Revenue - [(Logged Timesheet Hours × Employee Hourly Rate) + Direct Tagged Project Expenses]
- **Gross Profit Margin %** = (Project Gross Profit / Total Invoiced Revenue) × 100
- **Real-World Example:** If Tech Park Phase 2 invoices ₹18.50 Lakhs revenue, labor cost is ₹3.50 Lakhs (412 hours worked), and direct site expenses are ₹48,000:
  - **Gross Profit** = ₹18,50,000 - (₹3,50,200 + ₹48,000) = **₹14,51,800 (78.4% Margin)**

---

## 4. Technical Architecture & Subsystems Engine (Deep Dive)
*(Spoken by YOU)*

### 4.1 Two-Tier Zero-Touch Modularity
* **How it works:**
  - **Tier 1 (`base`, `authentication`)**: Provides shared database models (`res_users`, `res_company`), dynamic metadata registries, security middleware, and frontend layout templates.
  - **Tier 2 (Business Modules: `employee`, `project`, `attendance`, `leave`, `expense`, `accounting`, `mail`)**: Each app lives in its own directory with its own models, views, and URLs.
* **Why -Zero-Touch|— ** Multiple developers can build, migrate, and test independent business apps without modifying a single line of core framework code, eliminating merge conflicts and regressions.

### 4.2 Dynamic Metadata Discovery (`ir.model` & `ir.model.fields`)
* When `python manage.py migrate` is executed, Django triggers a `post_migrate` signal.
* The system uses `django.apps.apps.get_models()` to inspect all registered models and automatically synchronizes them into `ir.model` and `ir.model.fields`.
* This enables runtime inspectability and allows our Many2One dropdown widgets to dynamically search any table without hardcoding.

### 4.3 Background Scheduler Engine (`ir.cron`)
* Background jobs are scheduled and monitored through the `ir.cron` database table without requiring heavy external brokers like Redis/Celery for small-to-medium deployments.
* **Key Automated Jobs:**
  1. *Timesheet Deadline Monitor*: Runs every Monday at 15:00 to lock unsubmitted sheets.
  2. *Attendance Auditor*: Runs daily at 23:59 to flag missing punch-outs and evaluate the 8 net-hours rule.
  3. *Leave Accrual Engine*: Runs on the 1st of every month at 00:01 to credit monthly leave balances.
* In Developer Mode, administrators have a **Run Manually** trigger for instant execution and testing.

### 4.4 Security Engine: Table Access vs Row-Level Rules (`ir.rule`)
* **`ir.model.access` (Table Level)**: Grants CRUD permissions (Create, Read, Write, Delete) for an entire table to specific user groups (e.g. HR Officers can Read/Write `hr.employee`).
* **`ir.rule` (Row-Level Security / RLS)**: Enforces domain-level SQL filters so users only access authorized rows. For example, a standard employee has a rule `[('user_id', '=', user.id)]`, restricting them to seeing only their own timesheets, salary slips, and attendance punches.

### 4.5 Developer Mode (` - =1`) & Runtime Theming
* When Developer Mode is enabled via ` - =1`, form elements display interactive technical badges (` - `) revealing model names, field types (`VARCHAR`, `INTEGER`, `DECIMAL`, `FK`), and database columns.
* Frontend styling is built with **Vanilla CSS Custom Properties (Variables)**, enabling instant live switching between themes (Odoo Purple, Dark Slate, Ocean Blue, Emerald Green) with zero bundle rebuilds.

---

## 5. Top Practical Questions Your Guide / HOD May Ask

#### Q1: What is the main purpose of this project - 
**Answer:** To replace multiple disconnected tools (Excel sheets, WhatsApp messages, paper bills, biometric apps) with one integrated ERP where timesheets, attendance, leaves, expenses, and client billing automatically calculate real-time project profitability.

#### Q2: How does the system prevent fake or incomplete timesheets - 
**Answer:** Through our **Mandatory 8-Hour Daily Validation Rule**. An employee cannot click Submit on Monday 3:00 PM if any regular workday has less than 8 logged hours. If the employee was on approved leave, the system automatically inserts an 8-hour block.

#### Q3: What happens if an employee tries to log overlapping hours - 
**Answer:** The system blocks double-booking. If an employee logs Task A from 10:00 AM to 1:00 PM and tries to log Task B from 12:00 PM to 3:00 PM, the system rejects it because the same hour (12:00 PM to 1:00 PM) cannot be billed twice.

#### Q4: Why are 2-Level Approvals used for leaves and expenses - 
**Answer:** 
- **Level 1 (Reporting Manager):** Checks operational feasibility (deadlines, project workload, valid receipts).
- **Level 2 (Executive Management / Finance Head):** Ensures company-wide financial control, leave liability balance, and client billing alignment.

#### Q5: How is Project Profitability calculated in real-time - 
**Answer:**
Project Profit = Client Invoiced Amount - [(Logged Timesheet Hours × Employee Hourly Rate) + Direct Project Expenses]
This allows managers to see project profit margins immediately as work is logged rather than waiting for month-end accounting reports.

#### Q6: Explain the difference between Milestone, Timesheet, and Lumpsum invoicing.
**Answer:**
- **Milestone-Based:** Billed upon reaching deliverable stages (e.g. 20% on concept, 40% on drawings).
- **Timesheet-Based:** Billed on actual approved hours worked multiplied by the client hourly rate.
- **Lumpsum:** Fixed contract amount billed in scheduled periodic installments.

#### Q7: What is the difference between `ir.model.access` and `ir.rule` - 
**Answer:**
- `ir.model.access` controls broad table-level CRUD permissions for groups.
- `ir.rule` enforces fine-grained row-level security filters (e.g. employees only see their own timesheets, while managers see their direct reports).

#### Q8: How is the system kept fast and secure - 
**Answer:**
- **Security:** Protected against SQL injection using Django's ORM and CSRF validation on all requests.
- **Speed:** Built using lightweight Vanilla CSS and JavaScript with fast database queries, ensuring near-instant page load times.

---

## 6. 5-Minute Step-by-Step Live Platform Presentation Script

Use this exact walkthrough flow when presenting the live interactive platform to your Guide and HOD:

| Time | Speaker | Screen / Action | What to Say & Demonstrate |
|---|---|---|---|
| **0:00 - 1:15** | **Dumbre Chaitanya (09)** | **Home Dashboard & Foundation (2.1 - 2.4)** | -Good morning respected Guide and HOD. Today we present **Office Pro**, our modular ERP platform. Currently, companies struggle with 4 to 5 disconnected tools—Excel sheets, biometric desktop software, WhatsApp leaves, and paper bills. In Office Pro, we unify all operations with a clean Two-Tier architecture using Python Django, PostgreSQL, and Odoo-inspired UI.||
| **1:15 - 2:30** | **Shripad Patil (24)** | **Operational Rules & Modules (2.5 & 3.1 - 3.5)** | -In Employee Directory, each staff member has an **Hourly Labor Rate (CTC)** and a **2-Tier Approver Matrix**. In Projects, we enforce our **Mandatory 8-Hour Daily Timesheet Rule** (blocking submission if any workday has $<8$ hours). Approved leaves automatically sync as 8-hour blocks. In Attendance, we track daily punches, breaks, and verify 8 net working hours.||
| **2:30 - 4:00** | **Pranay Shelar (32)** | **Financials & Technical Engine (3.6 & 4.1 - 4.5)** | -In Invoicing, we support **Milestone, Timesheet hourly, and Lumpsum** billing. Our **Real-Time Project Profitability Engine** calculates: Invoiced Revenue minus Labor Costs and Tagged Expenses (e.g. Tech Park Phase 2 shows a ₹14.51 Lakh margin / 78.4% profit).<br><br>Technically, our **Zero-Touch Modularity** allows independent Django apps to auto-register into `ir.model` on migration. We implement `ir.cron` background schedulers, row security (`ir.rule`), and Developer Mode (` - =1`) for live field inspectability.||
| **4:00 - 5:00** | **Saurabh Shigavan (33)** | **Live Interactive System Presentation** | -Let us now demonstrate the live interactive platform on screen...|*(Member presents the live running application in the browser at http://127.0.0.1:8000, displaying the live UI, theme switching, timesheet grid validation, and executive sign-off).* |
