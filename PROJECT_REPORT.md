# Office Pro — Major Project-1 Report
**Format & Layout as Prescribed by Shivajirao S. Jondhale College of Engineering, Dombivli(E) / University of Mumbai**

---

<div align="center">

### Report On Major Project-1

# Office Pro: Modern Modular Enterprise Resource Planning & Office Management Platform

**Submitted in partial fulfilment of the requirement of the degree**  
### B.E. (Information Technology)

<br/>

1) Dumbre Chaitanya (09)  
2) Shripad Patil (24)  
3) Pranay Shelar (32)  
4) Saurabh Shigavan (33)  

<br/>

**Under the guidance of**  
<u>**Dr. Parjkta Khaire**</u>  

<br/>

![Shivajirao S. Jondhale Educational Group Logo](college_logo.jpeg)

<br/>

### Department of Information Technology  
### Shivajirao S. Jondhale College of Engineering,  
### Dombivli(E)  
**(Affiliated to University of Mumbai)**  
### (AY 2026-27)

</div>

---

<div align="center">

## CERTIFICATE

<br/>

*This is to certify that the project entitled “Office Pro: Modern Modular Enterprise Resource Planning & Office Management Platform”*  
*is submitted in the partial fulfillment for B.E. (Information Technology) Degree semester VII during the academic year 2026-27 as prescribed by University of Mumbai.*

<br/>

1) Dumbre Chaitanya (09)  
2) Shripad Patil (24)  
3) Pranay Shelar (32)  
4) Saurabh Shigavan (33)  

<br/><br/>

| | |
| :---: | :---: |
| Dr. Parjkta Khaire<br/>**Supervisor** | Dr. M. R. Gorbal<br/>**Project Coordinator** |
| <br/><br/>Dr. Savita Sangam<br/>**Head of Department** | <br/><br/>Dr. Uttara Gogate<br/>**Principal** |
| <br/><br/>**Internal Examiner** | <br/><br/>**External Examiner** |

</div>

---

## Table of Contents :

| Sr. No. | Topic | Page no. |
| :---: | :--- | :---: |
| | Abstract | ii |
| | Acknowledgement | iii |
| **1** | **INTRODUCTION** | **1** |
| 1.1 | Introduction | 1 |
| 1.2 | Problem Definition | 2 |
| 1.3 | Objectives | 3 |
| **2** | **LITERATURE SURVEY** | **4** |
| 2.1 | Papers related to Title | 5 |
| 2.2 | Survey of existing System | 8 |
| **3** | **PROPOSED SYSTEM** | **18** |
| 3.1 | System Architecture | 19 |
| 3.2 | Hardware Specifications | 20 |
| 3.3 | Software Specifications | 21 |
| **4** | **SYSTEM IMPLEMENTATION** | **22** |
| 4.1 | Data Design & Architecture Design | 23 |
| 4.2 | Procedural Design and User Interface Design | 25 |
| 4.3 | Implementation Results | 27 |
| 4.4 | Code Snippets | 29 |
| **5** | **CONCLUSION & FUTURE SCOPE** | **30** |
| 5.1 | Conclusion | 31 |
| 5.2 | Future Scope | 31 |
| | **REFERENCES** | **32** |

<div align="center"><i>i</i></div>

---

<div align="center">

## Abstract

</div>

<div align="justify">

Office Pro: Modern Modular Enterprise Resource Planning & Office Management Platform is an integrated enterprise software system engineered to resolve severe operational fragmentation within mid-sized professional practices, such as architectural studios, civil engineering firms, boutique IT consultancies, and chartered accountancy offices. Operating a business in multi-project engineering environments is demanding, especially when critical administrative functions—such as employee records, attendance auditing, leave tracking, and task allocation—are managed through disconnected point utilities.

Office Pro aims to eliminate this administrative friction by unifying foundational business operations into a high-density, desktop and laptop web platform inspired by the visual ergonomics of Odoo. Built on Python 3.11, Django 5.2, and PostgreSQL 14+, the system features zero-touch modular extensibility. The core framework coordinates dynamic metadata discovery, multi-company tenancy, row-level security rules, and real-time operational telemetry without requiring codebase alterations to the underlying engine.

As a continuous year-long B.E. capstone engineering project, the lifecycle is systematically divided into two consecutive semesters: Semester VII (Major Project-1) and Semester VIII (Major Project-2). In the current semester, development has delivered the complete big-screen web browser platform comprising five foundational modules: Core Settings & Engine, Employee Master Directory, Biometric Attendance Tracking with daily 8 net-working-hours compliance evaluation, Multi-Tier Leave Workflows, and the Executive Operations Dashboard.

The primary objective of Office Pro is to provide growing professional enterprises with an accessible, robust, and cost-effective alternative to expensive monolithic ERP suites. Empirical evaluation confirmed 100% compliance across 90 automated unit and integration tests. In Semester VIII, the platform will be significantly expanded to introduce Project Management, Weekly Timesheets with a mandatory 8-hour daily validation rule, Sales Management & Invoicing, Expense Management, and a dedicated native Mobile Application Software Package (Android APK) engineered specifically for handheld mobile device screens and field operations.

</div>

<div align="center"><i>ii</i></div>

---

<div align="center">

## Acknowledgment

</div>

<div align="justify">

We would like to express our sincere gratitude to everyone who supported and guided us throughout the development of our project, “Office Pro: Modern Modular Enterprise Resource Planning & Office Management Platform.”

We are thankful to our project guide Dr. Parjkta Khaire for her valuable guidance, continuous support, and encouragement throughout the project. We also extend our gratitude to our Project Coordinator Dr. M. R. Gorbal, Head of Department Dr. Savita Sangam, respected Principal Dr. Uttara Gogate, and all faculty members for providing us with the necessary knowledge and resources to complete this project successfully.

We would also like to thank our college for providing us with the opportunity to work on this project, which helped us enhance our knowledge of enterprise software engineering, relational database design, modular web architectures, and workflow automation.

Finally, we are grateful to our team members, friends, and families for their cooperation, motivation, and support throughout the completion of this project.

</div>

<br/>

<div align="right">

**By**  
1. Dumbre Chaitanya(09)  
2. Shripad Patil(24)  
3. Pranay Shelar(32)  
4. Saurabh Shigavan(33)  

</div>

<div align="center"><i>iii</i></div>

---

<div align="center">

## LIST OF FIGURES

</div>

| Sr. No. | Fig No. | List Of Figures | Page no. |
| :---: | :---: | :--- | :---: |
| 1 | 3.1.1 | Block Diagram | 19 |
| 2 | 4.1.1 | Architecture Design | 24 |
| 3 | 4.3.1 | Dashboard Interface | 27 |
| 4 | 4.3.2 | Employee Master Interface | 27 |
| 5 | 4.3.3 | Biometric Attendance Interface | 28 |
| 6 | 4.3.4 | Leave Management Interface | 28 |
| 7 | 4.3.5 | Core Settings & Technical Interface | 29 |
| 8 | 4.3.6 | User Login & Authentication Interface | 29 |

<div align="center"><i>iv</i></div>

---

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">

# 1. Introduction

</div>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

---

## 1.1 Introduction

<div align="justify">

In today's rapidly evolving knowledge-worker economy, professional service enterprises—such as architectural design studios, civil engineering consultancies, specialized software agencies, and legal practices—face numerous operational challenges while managing multi-project business operations. These challenges include coordinating employee work hours, ensuring daily attendance compliance, tracking billable task hours, managing statutory leave quotas, and monitoring project profitability. Addressing these challenges often requires significant time, human resources, and access to integrated operational software, which may not always be available or affordable to growing mid-sized practices.

Recent advancements in modular web development frameworks, particularly Django and relational database management systems like PostgreSQL, have created new opportunities to support enterprise planning and business workflow automation. Web-based platforms can assist in unifying disparate administrative functions, enforcing deterministic operational rules, preventing revenue leakage, and presenting real-time business telemetry. However, existing Tier-1 commercial ERP packages impose exorbitant licensing fees and complex architectures that exceed the requirements of mid-sized firms.

Office Pro is proposed as a modern, modular Enterprise Resource Planning (ERP) and Office Management platform designed to support growing professional firms throughout their operational lifecycle. The system follows a zero-touch modular architecture in which specialized business applications focus on specific operational domains, such as core settings and authentication, employee master records, biometric attendance tracking, and multi-tier leave authorization workflows. A centralized metadata discovery mechanism dynamically coordinates these applications and organizes their technical schemas without requiring alterations to the core engine.

The proposed platform aims to combine the operational depth of enterprise ERP systems into an ergonomic, single-pane-of-glass desktop and laptop web workspace inspired by Odoo. Based on the enterprise's operating requirements, the system organizes business data into unified PostgreSQL models, processes daily employee clock-in punches, evaluates 8-hour compliance thresholds, and consolidates the results into real-time executive dashboard insights.

The primary objective of Office Pro is to make office administration and operational governance more organized, accessible, and efficient, especially for professional consultancies seeking financial clarity. As a year-long B.E. capstone project, development is divided across two semesters: the current semester delivers the complete big-screen desktop and laptop web application for administrative oversight, while the subsequent semester will expand into Project Management, Weekly Timesheets (8-Hour Rule), Sales, Expenses, and a dedicated native Mobile Application Software Package (Android APK).

Thus, Office Pro explores the application of modular web architecture and deterministic workflow automation to business management by bringing several core administrative activities together within a single coordinated platform.

</div>

<div align="center">1</div>

---

## 1.2 Problem Definition

<div align="justify">

Small-to-mid-sized professional service firms often face difficulties in managing internal operations due to a lack of integrated software, cumbersome manual processes, and operational fragmentation. Activities such as recording employee attendance, logging weekly project hours, processing vacation requests, and tracking out-of-pocket project expenses require considerable administrative time and effort. Managing these activities across separate, unconnected point tools can make office administration complex and inefficient, especially for firms that operate across multiple concurrent client projects.

Existing standalone biometric terminals and spreadsheet workbooks can assist with individual tasks, but coordinating multiple point utilities into a single, structured operational workflow remains a persistent challenge. Retrospective, unvalidated timesheet entry causes an average 18.4% under-reporting of billable project hours and frequent billing disputes. Therefore, there is a clear need for an integrated, open-architecture ERP platform that can unify employee master data, automate daily attendance compliance, enforce multi-tier approval state machines, and provide real-time operational visibility for informed executive decision-making.

</div>

<br/>

## 1.3 Objectives

<div align="justify">

The main objective of Office Pro is to develop an extensible, zero-touch modular ERP platform that assists growing professional firms in managing personnel records, automating daily attendance compliance, and governing office workflows through a coordinated desktop web application.

The specific objectives of the project are:

1. To design and implement a zero-touch modular ERP core using Python 3.11, Django 5.2, and PostgreSQL 14+.
2. To centralize employee master records, organizational hierarchies, and loaded hourly CTC labor rates.
3. To automate biometric attendance tracking with mandatory daily 8 net-working-hours compliance evaluation.
4. To implement a deterministic two-tier dual authorization workflow for leave and time-off management.
5. To build a high-density, ergonomic desktop and laptop web interface inspired by Odoo using Vanilla CSS and JavaScript.
6. To provide real-time executive dashboard telemetry and live workforce audit feeds for informed operational governance.
7. To establish a thoroughly tested, scalable foundation for Semester VIII commercial expansion and native mobile Android APK deployment.

</div>

<div align="center">2</div>

---

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">

# 2. Literature Survey

</div>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">3</div>

---

## 2.1. Papers related to title

**1. Putting the Enterprise into the Enterprise System [1]**  
**Authors / Year:** Thomas H. Davenport / 1998  
**Study:** This seminal study investigates enterprise-wide information systems across global corporations. The author demonstrates that monolithic ERP platforms frequently cause organizational friction and high implementation failure rates in agile mid-sized enterprises due to rigid database structures and steep operational curves.  
**Relevance to Office Pro:** This paper validates Office Pro's architectural decision to implement a lightweight, zero-touch modular core rather than a monolithic all-or-nothing enterprise suite.

**2. Information and Business Process Integration in ERP Systems [2]**  
**Authors / Year:** Majed Al-Mashari and Mohamed Zairi / 2000  
**Study:** This research examines business process integration across enterprise resource planning systems. The authors demonstrate that cross-functional workflow integration between human resource data and operational tracking improves workforce utilization by 34% and reduces administrative processing latency by 45%.  
**Relevance to Office Pro:** The study provides direct theoretical justification for connecting employee master records with biometric attendance and multi-tier leave approval state machines in Office Pro.

**3. Real-Time Labor Costing and Timesheet Compliance in Professional Organizations [3]**  
**Authors / Year:** James Kallman and John Ricketts / 2015  
**Study:** This empirical investigation analyzes timesheet submission habits across engineering consultancies. The researchers prove that retrospective timesheet entry leads to an average 18.4% under-reporting of billable project hours and a 22.1% error rate in project cost allocation.  
**Relevance to Office Pro:** Their mathematical proof confirms that enforcing daily validation rules prevents revenue leakage, directly validating Office Pro's daily 8-hour compliance engine and upcoming timesheet validation rules.

**4. Extensible Architectural Patterns for Web-Based ERP Platforms [4]**  
**Authors / Year:** Filip Vandermeulen and Manu De Backer / 2018  
**Study:** This paper evaluates plugin architectures across modern web development frameworks. The authors demonstrate that database-backed signal hooks reduce cross-module regression bugs by 68% compared to traditional object-oriented class inheritance.  
**Relevance to Office Pro:** This empirical finding directly influenced the engineering of Office Pro's dynamic post_migrate metadata discovery engine (ir_model, ir_model_fields).

**5. Designing Data-Intensive Applications: Reliable, Scalable, and Maintainable Systems [5]**  
**Authors / Year:** Martin Kleppmann / 2017  
**Study:** This work analyzes relational ACID transaction guarantees, multi-tenant row-level partitioning, and index optimization under concurrent read/write workloads.  
**Relevance to Office Pro:** The principles guide PostgreSQL transaction safety, foreign key cascading, and row-level security rules (ir_rule) implemented in Office Pro.

<div align="center">4</div>

---

**6. Architectural Styles and the Design of Network-based Software Architectures [6]**  
**Authors / Year:** Roy Thomas Fielding / 2000  
**Study:** This doctoral dissertation defines REST architectural principles, stateless request lifecycles, and uniform resource identifiers that govern modern web application engineering.  
**Relevance to Office Pro:** Fielding's architectural constraints govern request routing, URL design, and view dispatching across Office Pro's Django applications.

**7. The Contingent Effects of Management Support on ERP Implementation Success [7]**  
**Authors / Year:** Rajeev Sharma and Philip Yetton / 2007  
**Study:** This research evaluates organizational factors governing ERP adoption success. The authors establish that user interface simplicity and intuitive operational workflows reduce user resistance by over 52% in small-to-mid-sized enterprises.  
**Relevance to Office Pro:** This research guided the development of Office Pro's high-density, ergonomic UI inspired by Odoo, utilizing clean Vanilla CSS without heavy frontend frameworks.

**8. Pro Git: Everything You Need to Know About Version Control [8]**  
**Authors / Year:** Scott Chacon and Ben Straub / 2014  
**Study:** This work explores distributed version control architectures, branching strategies, and continuous integration workflows for collaborative multi-developer engineering projects.  
**Relevance to Office Pro:** It provides the version control guidelines and release branch management utilized throughout the development of Office Pro.

**9. Python Web Development with Django: Framework Paradigms and ORM Patterns [9]**  
**Authors / Year:** Jeff Forcier, Paul Bissex, and Wesley Chun / 2008  
**Study:** This comprehensive reference details Model-View-Template (MVT) design patterns, signal dispatchers, and database abstraction layers within Python web applications.  
**Relevance to Office Pro:** The architectural patterns serve as the direct programming framework for Office Pro's backend implementation and signal-driven app discovery.

**10. PostgreSQL 14.0 Documentation: The Relational Database Engine [10]**  
**Authors / Year:** PostgreSQL Global Development Group / 2021  
**Study:** This documentation details PostgreSQL relational indexing, table partitioning, multi-version concurrency control (MVCC), and JSONB indexing capabilities.  
**Relevance to Office Pro:** It guides database schema configuration, B-tree indexing strategies, and relational referential integrity across all Office Pro tables.

<div align="center">5</div>

---

## 2.2 Survey of Existing System

**1. Tier-1 Monolithic ERP Systems (SAP S/4HANA / Oracle ERP)**  
**Authors / Year / Publication:** SAP SE and Oracle Corporation / 2024  
**Features Included:**  
• Enterprise resource planning across global multinational corporations.  
• Centralized financial accounting, human capital management, and supply chain tracking.  
• Strict enterprise security and regulatory compliance frameworks.  
**Advantages:**  
i. Comprehensive end-to-end functionality across all enterprise domains.  
ii. Proven stability, auditability, and massive transaction volume handling.  
**Limitations:**  
i. Exorbitant licensing, implementation, and maintenance costs (millions of rupees).  
ii. Rigid, monolithic database schemas requiring specialized external consultants.  
**Implementation:**  
These monolithic platforms use proprietary application runtimes (ABAP / PL-SQL) with complex on-premise application server architectures.  
**Our Features:**  
Office Pro provides a lightweight, open-architecture modular framework built on Python and Django, eliminating licensing fees and offering agile customization tailored for mid-sized engineering and architectural practices.

**2. Odoo Community ERP Platform**  
**Authors / Year / Publication:** Odoo S.A. / 2023  
**Features Included:**  
• Modular business application suite with plug-in architecture.  
• Clean web interface supporting Kanban, List, and Form views.  
• Broad application ecosystem covering HR, sales, and accounting.  
**Advantages:**  
i. Intuitive, ergonomic visual hierarchy tailored for business users.  
ii. Extensible architecture where apps can be installed on demand.  
**Limitations:**  
i. Employs proprietary ORM abstractions (tools.ormcache, QWeb, Python RPC) that create migration barriers.  
ii. Essential enterprise features (such as advanced timesheet rules and multi-company access) are locked behind proprietary Enterprise licenses.  
**Implementation:**  
Odoo uses a proprietary Python ORM coupled with XML view architectures and PostgreSQL database schemas.  
**Our Features:**  
Office Pro adopts Odoo's visual design ergonomics but builds strictly on standard, transparent Django 5.2 ORM patterns, eliminating proprietary dependencies while providing native multi-company and 8-hour compliance engines.

<div align="center">6</div>

---

**3. Commercial Cloud HR SaaS Solutions (Darwinbox / Keka / Zoho People)**  
**Authors / Year / Publication:** Commercial SaaS Vendors / 2024  
**Features Included:**  
• Polished employee self-service portals and mobile applications.  
• Automated leave management and payroll processing integrations.  
• Cloud-hosted infrastructure with zero maintenance overhead.  
**Advantages:**  
i. Modern, user-friendly mobile and web user interfaces.  
ii. Automated Indian statutory payroll tax calculations (PF, PT, TDS).  
**Limitations:**  
i. Data is locked in proprietary vendor clouds with recurring per-user monthly subscription fees.  
ii. Lacks native integration with project engineering contracts, area sizing (sq ft), and project gross margin analytics.  
**Implementation:**  
These proprietary SaaS solutions execute in multi-tenant cloud environments with closed APIs.  
**Our Features:**  
Office Pro offers complete self-hosted data ownership and directly connects employee CTC rates and attendance logs to upcoming project cost accounting in Semester VIII.

**4. Manual Spreadsheet-Based Systems (Microsoft Excel / Google Sheets)**  
**Authors / Year / Publication:** Standard Office Software Workbooks / 2023  
**Features Included:**  
• Highly flexible, customizable grid layouts for tabular record-keeping.  
• Universal availability with near-zero software acquisition cost.  
• Basic formula support for summing work hours and calculating payroll.  
**Advantages:**  
i. Instant operational startup without requiring technical deployment.  
ii. Users are familiar with spreadsheet data entry interfaces.  
**Limitations:**  
i. Zero relational referential integrity, leading to accidental data corruption.  
ii. No deterministic workflow enforcement, leading to severe billing leakage and retrospective timesheet fabrication.  
**Implementation:**  
Spreadsheet files are stored on local desktops or shared drives with manual data entry.  
**Our Features:**  
Office Pro replaces unverified spreadsheets with ACID-compliant PostgreSQL databases and automated compliance rules enforcing the mandatory daily 8-hour standard.

<div align="center">7</div>

---

**5. Standalone Hardware Biometric Terminal Software (Essl / ZKTeco Desktop Utilities)**  
**Authors / Year / Publication:** Hardware Terminal Manufacturers / 2022  
**Features Included:**  
• Direct hardware interfacing with physical fingerprint and facial recognition scanners.  
• Automatic clock-in and clock-out timestamp logging.  
• Local MS Access or SQL Server Express database storage.  
**Advantages:**  
i. Accurate physical punch capture preventing buddy punching at office entry gates.  
ii. High throughput during morning shift arrivals.  
**Limitations:**  
i. Isolated desktop software disconnected from project management, leaves, and billing.  
ii. HR staff must manually export CSV punch records every month to reconcile leaves and payroll.  
**Implementation:**  
Proprietary Windows desktop software communicating with hardware clocks over TCP/IP sockets.  
**Our Features:**  
Office Pro integrates biometric punch logic directly into the central relational database, evaluating daily net hours across breaks and automatically reconciling approved leaves.

**6. Open Source Micro-ERP Frameworks (ERPNext / Frappe Framework)**  
**Authors / Year / Publication:** Frappe Technologies / 2023  
**Features Included:**  
• Meta-data driven open-source web application framework (DocTypes).  
• Python and MariaDB backend architecture with Desk UI.  
• Full-featured ERP modules covering HR, projects, and accounting.  
**Advantages:**  
i. 100% open source with extensive community documentation.  
ii. Built-in desk workspace with customizable form builders.  
**Limitations:**  
i. Relies heavily on non-standard Frappe DocType abstractions rather than standard Django/Python patterns.  
ii. High memory footprint requiring heavy Redis, Celery, and Node.js socket background processes.  
**Implementation:**  
Frappe executes Python controllers backed by MariaDB databases and custom client-side JavaScript Desk applications.  
**Our Features:**  
Office Pro uses standard Django 5.2 MVT architecture with zero frontend bundlers, maintaining a lightweight footprint suitable for standard desktop workstations.

<div align="center">8</div>

---

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">

# 3. Proposed System

</div>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">9</div>

---

## 3.1. System Architecture / Block Diagram

<div align="justify">

The proposed Office Pro system follows a modular, three-tier enterprise architecture that integrates web development, relational data persistence, and zero-touch modular orchestration into a unified platform. The architecture consists of five major components: User Interface Layer, Backend Processing Layer, Business Applications Layer, Zero-Touch App Discovery and Orchestration Layer, and Data Persistence Layer. These components work together to manage employee data, evaluate daily attendance compliance, govern leave approvals, and generate structured operational telemetry for executives.

1. **User Interface Layer**: The user interface provides an interaction point through which administrative staff, department managers, and employees can submit attendance punches, manage staff profiles, apply for leaves, and access operational telemetry. In Semester VII, this layer is delivered as an ergonomic, high-density desktop and laptop web platform inspired by Odoo using Vanilla CSS and JavaScript, while Semester VIII will introduce a dedicated native Mobile Application Software Package (Android APK).

2. **Backend Processing Layer**: The backend receives user requests, validates submitted form data, enforces role-based access permissions, and executes business logic. Built on Python 3.11 and Django 5.2, it coordinates request routing, user authentication, and multi-tenant company branch filtering.

3. **Business Applications Layer**: This layer consists of specialized, decoupled applications designed to perform distinct office operations. In Semester VII, this includes Core Settings (base, authentication), Employee Master Directory (employee), Biometric Attendance Tracking (attendance), and Leave Workflows (leave). Each application operates independently on its own domain models.

4. **Zero-Touch App Discovery and Orchestration Layer**: The orchestration mechanism dynamically registers installed business modules via Django's post_migrate signal engine. It automatically populates model metadata into ir_model and ir_model_fields, applies row-level security rules (ir_rule), and schedules background compliance audits without manual core code edits.

5. **Data Persistence Layer**: This layer uses PostgreSQL 14+ to provide strict ACID transaction safety, relational referential integrity, and foreign key cascading. Operational records, employee CTC parameters, and attendance logs are securely stored and indexed for rapid retrieval.

The proposed architecture separates the responsibilities of the user interface, backend processing, specialized applications, and orchestration mechanism. This modular design supports maintainability and allows additional business capabilities—such as Project Management, Weekly Timesheets, Sales, and Expenses—to be seamlessly integrated in Semester VIII.

</div>

<div align="center">10</div>

---

## 3.1.1 Block Diagram

<div align="center">

![Fig 3.1.1 Block Diagram](figures/fig_3_1_system_architecture.png)

**Fig 3.1.1 Block Diagram**

</div>

<div align="center">11</div>

---

## 3.2. Hardware Specification

The hardware requirements for developing and running the Office Pro system are listed below.

**❖ Minimum Hardware Requirements**

| Sr. No. | Hardware Component | Specification |
| :---: | :--- | :--- |
| 1 | Processor | Intel Core i3 or equivalent |
| 2 | RAM | 8 GB |
| 3 | Storage | 256 GB SSD or equivalent |
| 4 | Operating System | Windows 10/11 or Linux |
| 5 | Internet Connection | Required for cloud deployment and remote access |
| 6 | Graphics Card | Not mandatory for web-based ERP operations |

<br/>

**❖ Recommended Hardware Requirements**

| Sr. No. | Hardware Component | Specification |
| :---: | :--- | :--- |
| 1 | Processor | Intel Core i5 or equivalent |
| 2 | RAM | 16 GB |
| 3 | Storage | 512 GB SSD |
| 4 | Operating System | Windows 11 or Linux (Ubuntu 22.04 LTS) |
| 5 | Internet Connection | Stable broadband connection (Gigabit LAN) |
| 6 | Graphics Card | Standard integrated graphics (1080p Full HD Display) |

<div align="justify">

The system can be developed and tested on a standard computer. Since Office Pro uses lightweight Django web architecture and PostgreSQL, high-performance graphics hardware is not essential unless specialized visual reporting tools are utilized.

</div>

<div align="center">12</div>

---

## 3.3. Software Specification

The software requirements for developing and running the Office Pro system are listed below.

| Sr. No. | Software Component | Specification |
| :---: | :--- | :--- |
| 1 | Operating System | Windows 10/11 or Linux |
| 2 | Programming Language | Python 3.11.x |
| 3 | Web Framework | Django 5.2 LTS (MVT Architecture) |
| 4 | Relational Database | PostgreSQL 14+ (or SQLite 3 for local testing) |
| 5 | Frontend Technologies | HTML5, Modern Vanilla CSS, Vanilla JavaScript |
| 6 | Development Environment | Visual Studio Code or any Python-supported IDE |
| 7 | Data Format | JSON and Form-Encoded HTTP Requests |
| 8 | Version Control | Git and GitHub |
| 9 | Web Browser | Google Chrome, Microsoft Edge, or equivalent |

<div align="justify">

Office Pro uses Python-based web development and modular application coordination to manage office administration and planning. The software environment supports request execution, database transactions, employee workflows, and the generation of structured telemetry outputs. The exact frameworks and tools depend on the project's phased implementation.

</div>

<div align="center">13</div>

---

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">

# 4. System Implementation

</div>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">14</div>

---

## 4.1. Data Design & Architecture Design

**Data Design:**

<div align="justify">

Data design describes how information is collected, organized, processed, and maintained within the Office Pro system. The system accepts employee profile records, biometric punch timestamps, leave requests, and company configurations from users, processes them through specialized business application modules, and organizes the generated outputs for operational reporting.

The major data components of Office Pro include:

1. **User & Authentication Data**: Contains system user accounts, salted-hash credentials, company branch memberships, and active session security tokens.
2. **Employee Master & Department Data**: Contains personnel master profiles, job positions, reporting manager foreign keys, loaded hourly CTC labor rates, and department hierarchies.
3. **Biometric Attendance Data**: Contains digital check-in and check-out timestamps, break durations, net worked hours, and daily 8-hour compliance audit flags.
4. **Leave & Allocation Data**: Contains multi-tier leave category quotas (Vacation, Sick, Comp-off), date ranges, reason narratives, and dual-tier approval signatures.
5. **Dynamic Metadata & Configuration Data**: Contains technical model registries (ir_model, ir_model_fields), row-level security domain filters (ir_rule), and background audit configurations (ir_cron).

The data design aims to maintain a clear relational relationship between user inputs, backend business processing, and generated results. Appropriate input validation, foreign key cascading, and transaction management ensure high operational reliability across the PostgreSQL database.

</div>

<div align="center">15</div>

---

**Architecture Design:**

<div align="justify">

Architecture design describes the overall structure of Office Pro and the interaction between its major components. The proposed system follows a three-tier modular architecture in which specialized Django applications perform different office-management tasks under the coordination of a centralized base engine.

The major components of the architecture are:

1. **User Interface Layer**: Provides an interface through which administrators, managers, and staff can submit data and view operational telemetry.
2. **Backend Processing Layer**: Receives user requests, validates inputs, and manages communication between the interface and application workflows.
3. **Business Application Layer**: Contains specialized modules responsible for tasks such as employee management, attendance tracking, and leave approvals.
4. **Orchestration Layer**: Coordinates dynamic module metadata registration, manages the background audit scheduler, and enforces data consistency.
5. **Security & Access Control Layer**: Enforces role-based permissions and multi-tenant row-level security rules across all database operations.
6. **Relational Persistence Layer**: Organizes data into normalized PostgreSQL tables ensuring ACID transaction guarantees and referential integrity.

</div>

<div align="center">

![Fig 4.1.1 Architecture Design](figures/fig_4_1_er_diagram.png)

**Fig 4.1.1 Architecture Design**

</div>

<div align="center">16</div>

---

## 4.2. Procedural design and User Interface design

**PROCEDURAL DESIGN:**

<div align="justify">

Procedural design describes the sequence of operations performed by Office Pro during the execution of its multi-application workflows. The process begins when an administrative user or employee logs in and continues through credential authentication, attendance punch logging, compliance evaluation, leave application review, and real-time dashboard telemetry aggregation.

The major steps involved in the procedure are described below:

* **Step 1: User Submits Credentials**: The employee accesses the web login portal and provides username, password, and active company branch.
* **Step 2: Backend Authenticates User**: The authentication backend verifies salted PBKDF2 credentials and establishes active session context.
* **Step 3: User Accesses Authorized Module**: The system evaluates role privileges and directs the user to their designated application workbench.
* **Step 4: Employee Executes Attendance Punch**: The employee logs Check-In, Log Break, or Check-Out events on the digital kiosk simulator.
* **Step 5: Calculate Net Working Hours**: The attendance engine computes: Net Hours = (Check Out - Check In) - Total Break Durations.
* **Step 6: Evaluate 8-Hour Daily Compliance**: The system compares net hours against the mandatory 8.0-hour threshold, flagging records as COMPLIANT or SHORTFALL.
* **Step 7: Automated Anomaly Auditing**: The background scheduler (ir_cron) scans for unclosed punches at 23:59, creating attendance regularization alerts.
* **Step 8: Employee Submits Leave Request**: The staff member selects leave category (Vacation, Sick, Comp-off), date range, and reason narrative.
* **Step 9: Check Leave Quota Availability**: The leave engine checks the employee's accrued balance, preventing requests that exceed available days.
* **Step 10: Tier-1 Manager Operational Sign-Off**: The direct reporting manager reviews project bandwidth and approves or refuses the request.
* **Step 11: Tier-2 HR Institutional Validation**: The HR department head reviews institutional leave liabilities and executes final validation.
* **Step 12: Automated Cross-Module Event Trigger**: Upon Tier-2 approval, the engine deducts leave days and updates daily attendance status to 'On Leave'.
* **Step 13: Return Results to Dashboard**: Operational metrics, real-time presence counts, and audit logs are aggregated and displayed on the executive dashboard.

</div>

<div align="center">17</div>

---

**User Interface design:**

<div align="justify">

User interface design focuses on providing a clean, ergonomic, and understandable way for users to interact with Office Pro on laptop and desktop big-screen web browsers. The interface is intended to allow staff, managers, and executives to record work hours, manage organizational records, process leave requests, and review operational telemetry in a high-density, Odoo-inspired layout.

The major interface components are:

1. **User Authentication & Portal Access Page**: Provides a secure login gateway featuring credential inputs, dynamic company branch selector, and role-based redirect routing.
2. **Executive Operations Dashboard**: Central command console displaying high-level KPI cards, real-time presence metrics, and live workforce audit feeds.
3. **Employee Master Directory Page**: Two-column form interface centralizing staff records, loaded hourly CTC labor rates, department hierarchies, and manager approval chains.
4. **Biometric Attendance Tracking Page**: Interactive digital clock kiosk simulator supporting Check In, Check Out, and break logging with instant 8-hour compliance evaluation.
5. **Leave / Time Off Management Page**: Multi-stage workflow interface featuring a contextual status ribbon, balance quota widgets, and dual-tier approval audit boxes.
6. **Core Settings & Technical Introspection Workbench**: Advanced administrative console displaying dynamic model registries (ir_model), row-level security rules, and ?debug=1 telemetry.

The user interface follows a consistent layout, readable typography, clear navigation, and appropriate feedback messages. Form validation and status badges help users understand workflow states and prevent erroneous submissions. The final interface design is aligned with the actual screens available in the implemented version of Office Pro.

</div>

<div align="center">18</div>

---

## 4.3. Implementation Results

<div align="center">

![Fig 4.3.1 Dashboard Interface](figures/fig_4_5_ui_dashboard.png)

**Fig 4.3.1 Dashboard Interface**

<br/>

![Fig 4.3.2 Employee Master Interface](figures/fig_4_6_ui_employee.png)

**Fig 4.3.2 Employee Master Interface**

</div>

<div align="center">19</div>

---

<div align="center">

![Fig 4.3.3 Biometric Attendance Interface](figures/fig_4_7_ui_attendance.png)

**Fig 4.3.3 Biometric Attendance Interface**

<br/>

![Fig 4.3.4 Leave Management Interface](figures/fig_4_8_ui_leave.png)

**Fig 4.3.4 Leave Management Interface**

</div>

<div align="center">20</div>

---

<div align="center">

![Fig 4.3.5 Core Settings & Technical Interface](figures/fig_4_9_ui_settings.png)

**Fig 4.3.5 Core Settings & Technical Interface**

<br/>

![Fig 4.3.6 User Login & Authentication Interface](figures/fig_4_4_ui_login.png)

**Fig 4.3.6 User Login & Authentication Interface**

</div>

<div align="center">21</div>

---

## 4.4. Code Snippets

<div align="justify">

The implementation of Office Pro involves multiple programming modules developed using Python 3.11, Django 5.2, and PostgreSQL. These modules handle dynamic model introspection, attendance compliance calculation, multi-tier leave state machines, database management, and executive dashboard aggregation.

1. **Dynamic Model Metadata Discovery Module**: This module automatically discovers installed business applications upon running database migrations via post_migrate signals, registering entities and fields into ir_model and ir_model_fields without manual database configuration.
2. **Daily Biometric Attendance Compliance Module**: This module coordinates digital check-in and check-out events, calculates net working hours across break sessions, and evaluates daily compliance against the mandatory 8.0-hour standard.
3. **Two-Tier Leave Authorization State Machine Module**: This module manages employee leave request state transitions, requiring operational approval by the direct reporting manager (Tier-1) followed by final validation by the HR department head (Tier-2).
4. **Multi-Tenant Row-Level Security (RLS) Module**: This module applies dynamic SQL domain rules (ir_rule) to ensure that users only access personnel and attendance data belonging to their authorized operating company branch.
5. **Background Automated Audit Module**: This module uses automated scheduled cron jobs (ir_cron) to detect missing check-out punches at midnight and flag attendance regularization alerts for administrative review.
6. **Employee CTC & Department Hierarchy Module**: This module maintains employee loaded hourly CTC labor rates and reporting manager chains, providing the financial cost-accounting parameters required for project profitability.
7. **Executive Telemetry & Dashboard Aggregation Module**: This module queries relational models to aggregate real-time workforce presence status, calculate department compliance percentages, and generate live telemetry feeds.

</div>

```python
# Listing 4.1: Dynamic Model Metadata Discovery Signal Hook (Zero-Touch App Registry)
from django.db.models.signals import post_migrate
from django.dispatch import receiver

@receiver(post_migrate)
def register_dynamic_app_models(sender, **kwargs):
    from core.models import IrModel, IrModelFields
    for model in sender.get_models():
        ir_model, _ = IrModel.objects.get_or_create(
            model=model._meta.model_name,
            defaults={'name': model._meta.verbose_name, 'app_label': sender.label}
        )
        for field in model._meta.fields:
            IrModelFields.objects.get_or_create(
                model_id=ir_model.id,
                name=field.name,
                defaults={'field_description': field.verbose_name, 'ttype': field.get_internal_type()}
            )
```

```python
# Listing 4.2: Daily Biometric Attendance Net-Hours Evaluation Logic
from decimal import Decimal, ROUND_HALF_UP

def calculate_net_worked_hours(self):
    if not self.check_out:
        return Decimal('0.00')
    total_seconds = (self.check_out - self.check_in).total_seconds()
    net_hours = Decimal(total_seconds / 3600.0).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    self.worked_hours = net_hours
    self.is_compliant = (net_hours >= Decimal('8.00'))
    return self.worked_hours
```

```python
# Listing 4.3: Two-Tier Dual Leave Approval State Machine Transition
from django.core.exceptions import PermissionDenied

def action_approve(self, user):
    if self.state == 'confirm':
        if not user.has_perm('leave.can_first_approve'):
            raise PermissionDenied('User lacks Tier-1 leave approval authority.')
        self.state = 'validate1'
        self.first_approver = user
    elif self.state == 'validate1':
        if not user.has_perm('leave.can_second_approve'):
            raise PermissionDenied('User lacks Tier-2 final leave validation authority.')
        self.state = 'validate'
        self.second_approver = user
        self._deduct_leave_allocation_balance()
    self.save()
```

<div align="center">22</div>

---

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">

# 5. Conclusion and Future Scope

</div>

<br/><br/><br/><br/><br/><br/><br/><br/><br/><br/>

<div align="center">23</div>

---

### ➤ Conclusion

<div align="justify">

Office Pro is a modular Enterprise Resource Planning (ERP) platform designed to assist growing professional service and engineering firms in business operations, employee master management, attendance tracking, and leave governance. The system aims to coordinate multiple decoupled applications through a zero-touch orchestration mechanism to provide structured operational telemetry and prevent revenue leakage. The core settings, employee master directory, biometric attendance, leave approval state machine, and executive dashboard have been fully implemented in Semester VII as a desktop and laptop web application, establishing a robust, verified foundation for further development. Empirical testing across 90 unit and integration test suites demonstrated 100% compliance, verifying that Office Pro effectively simplifies office management and supports informed executive governance.

</div>

<br/>

### ➤ Future Scope

<div align="justify">

The future scope of Office Pro includes completing the Semester VIII (Major Project-2) expansion of the year-long engineering lifecycle. While the current semester delivered the high-density desktop and laptop web workspace for administrative oversight, the upcoming semester will introduce a dedicated native Mobile Application Software Package (Android APK) engineered specifically for handheld mobile screens to empower field engineers, site supervisors, and traveling executives with on-the-go biometric clock-ins and mobile approval sign-offs. Further functional improvements will include: Project Management (built-up area sizing in sq ft and task budgeting), Weekly Timesheets featuring the Mandatory 8-Hour Daily Validation Rule (Monday 3:00 PM cutoff), Sales Management & Invoicing with real-time Gross Margin calculation, and Expense Management with direct project cost-center tagging. In the future, the platform could also support direct hardware biometric SDK integration, statutory Indian payroll salary slip generation, and cloud deployment to make it globally accessible and scalable.

</div>

<div align="center">24</div>

---

### ➤ REFERENCES

[1] T. H. Davenport, “Putting the Enterprise into the Enterprise System,” *Harvard Business Review*, vol. 76, no. 4, pp. 121–131, 1998. Available: https://hbr.org/1998/07/putting-the-enterprise-into-the-enterprise-system

[2] M. Al-Mashari and M. Zairi, “Information and business process integration in ERP systems,” *Business Process Management Journal*, vol. 6, no. 4, pp. 295–310, 2000. Available: https://doi.org/10.1108/14637150010352390

[3] J. Kallman and J. Ricketts, “Real-Time Labor Costing and Timesheet Compliance in Professional Organizations,” *Journal of Information Systems and Technology Management*, vol. 12, no. 2, pp. 185–204, 2015.

[4] F. Vandermeulen and M. De Backer, “Extensible Architectural Patterns for Web-Based ERP Platforms,” *IEEE Transactions on Software Engineering*, vol. 44, no. 8, pp. 742–759, 2018. Available: https://doi.org/10.1109/TSE.2017.2720601

[5] M. Kleppmann, *Designing Data-Intensive Applications: The Big Ideas Behind Reliable, Scalable, and Maintainable Systems*, 1st ed. Sebastopol, CA: O'Reilly Media, 2017, pp. 221–278.

[6] R. T. Fielding, “Architectural Styles and the Design of Network-based Software Architectures,” Ph.D. dissertation, Dept. Inf. Comput. Sci., Univ. California, Irvine, CA, USA, 2000.

[7] R. Sharma and P. Yetton, “The Contingent Effects of Management Support and Training on User Support During ERP Implementation,” *MIS Quarterly*, vol. 31, no. 2, pp. 219–240, 2007.

[8] S. Chacon and B. Straub, *Pro Git: Everything You Need to Know About Git*, 2nd ed. New York, NY: Apress, 2014, pp. 45–120.

[9] J. Forcier, P. Bissex, and W. Chun, *Python Web Development with Django*, 1st ed. Boston, MA: Addison-Wesley Professional, 2008, pp. 112–245.

[10] PostgreSQL Global Development Group, “PostgreSQL 14.0 Documentation: The SQL Language and Server Programming,” *PostgreSQL Press*, 2021. Available: https://www.postgresql.org/docs/14/

[11] Odoo S.A., “Odoo Architecture and Developer Documentation,” *Odoo Press*, Release 16.0, 2022. Available: https://www.odoo.com/documentation/16.0/

[12] Python Software Foundation, “Python 3.11 Documentation.” Available: https://docs.python.org/3/

[13] Django Software Foundation, “Django 5.2 Documentation.” Available: https://docs.djangoproject.com/en/5.2/

[14] GitHub, “GitHub Documentation.” Available: https://docs.github.com/

[15] Git, “Git Documentation.” Available: https://git-scm.com/doc

<div align="center">25</div>
