# Office Pro — Interactive Presentation Demo (Zero-DB Setup)

This folder contains the self-contained, standalone interactive presentation demo of **Office Pro** prepared for your **Project Guide and HOD Presentation on Monday**.

---

## 🚀 How to Launch the Demo (2 Easy Ways)

### Option 1: Direct Double-Click (Zero Setup, No Commands)
1. Navigate to `d:\Office_Pro\Office_Pro\demo\` in Windows File Explorer.
2. Double-click **`index.html`**.
3. It will open instantly in Google Chrome, Microsoft Edge, or any modern web browser.
4. **No database, no Python environment, no server commands required!**

### Option 2: Run via Local Python Web Server (Optional)
If you want to run it via an HTTP server URL:
```bash
# In PowerShell / Command Prompt:
cd d:\Office_Pro\Office_Pro\demo
python -m http.server 8080
```
Then open: [http://localhost:8080](http://localhost:8080) in your browser.

---

## 🎯 Key Presentation Highlights to Show Your Guide & HOD

1. **Top Navbar & Dynamic Themes**:
   - Live theme switching (Odoo Purple, Dark Slate, Ocean Blue, Emerald Green).
   - Live server clock and branch switcher.
   - Conversations and Activities popover badges.
   - **Developer Mode Toggle (`?debug=1`)**: Hovering on form fields reveals technical metadata (`ir.model`, `ir.model.fields`).

2. **Employee Directory (`hr.employee`)**:
   - Master staff records with **Hourly CTC Rate** (powers real-time project profitability).
   - **Multi-Level Approver Matrix** (Timesheet Approver, Leave L1/L2, Expense L1/L2).

3. **Project & Sizing Management (`project.project`)**:
   - Scope / Built-up area in **sq. ft.** (e.g. 45,000 sq.ft).
   - Invoicing policy selector (Milestone %, Timesheet hourly billing, Lumpsum fee).
   - Statutory GST tax mapping (18% GST with SAC 998311).

4. **Weekly Timesheet Engine (`project.timesheet`)**:
   - **Mandatory 8-Hour Daily Validation Rule**: Monday–Friday daily threshold checks.
   - **Leave Auto-Synchronization**: Approved leaves automatically reflect as 8-hour daily blocks.
   - **Overtime & Comp-Off Policy**: Weekday 3.5h threshold vs Weekend 100% comp-off credit.
   - **Cross-Team Resource Loaning**: Automatic cost routing to borrowing project.

5. **Attendance Tracking & Punch Simulator (`hr.attendance`)**:
   - Real-time digital biometric punch terminal (Punch In, Break Out, Punch Out).
   - Net 8-hour compliance calculation and missing punch regularization flow.

5. **Leave & Time Off (`hr.leave`)**:
   - Vacation, Sick, Comp-off, Festival, and Flexible leave balances.
   - **2-Tier Approval Flow**: Level 1 (Reporting Manager) -> Level 2 (Executive Approver sign-off).
   - Backdated leave block safeguard.

6. **Expense Management (`hr.expense`)**:
   - Out-of-pocket claims with receipt previews.
   - Cost allocation toggle: Company Overhead vs Project Tagging.

7. **Accounting & Real-Time Project Profitability (`account.invoice`)**:
   - GST-compliant invoice generation (CGST + SGST / IGST).
   - Real-time gross profit calculation:  
     `Project Gross Profit = Total Invoiced Revenue - [(Logged Timesheet Hours × Employee Hourly Rate) + Direct Tagged Project Expenses]`
   - Tech Park Phase 2 demonstrates a ₹14.51 Lakh gross margin (78.4% profit).

9. **Technical Subsystem & Settings (`ir.*`)**:
   - `ir.model` and `ir.model.fields` metadata catalog.
   - `ir.cron` background schedulers with "Run Manually" button.
   - `ir.rule` (Row-Level Security) and `ir.model.access` permissions.

10. **Guide / HOD Defense Hub (`Viva Q&A`)**:
    - Embedded defense deck in the topbar profile menu with answers to 25+ essential viva questions.
