/**
 * Office Pro - Enterprise ERP & Office Management Platform
 * Client-side Presentation & Interactive Dummy Engine (No DB Required)
 */

// Initial Seed State
const INITIAL_DATA = {
  theme: 'default',
  debugMode: false,
  currentUser: {
    name: 'Admin User (Director)',
    role: 'System Administrator & Executive Approver',
    email: 'admin@officepro.internal',
    avatar: 'AD',
    company: 'Office Pro Headquarters (Mumbai)'
  },
  employees: [
    {
      id: 'EMP001',
      name: 'Alex Morgan',
      avatarLetter: 'A',
      avatarColor: '#b45309',
      role: 'Executive Director',
      dept: 'Executive Management',
      tag: 'Director',
      email: 'alex.morgan@officepro.internal',
      phone: '+91 98765 43210',
      mobile: '+91 98765 43210',
      hireDate: 'Apr 1',
      online: true,
      hourlyCtc: 2500,
      reportingManager: 'None (Board of Directors)',
      timesheetApprover: 'Self',
      leaveL1: 'Self',
      leaveL2: 'Self',
      expenseL1: 'Self',
      expenseL2: 'Finance Head',
      status: 'Active',
      branch: 'Mumbai HQ'
    },
    {
      id: 'EMP002',
      name: 'David Miller',
      avatarLetter: 'D',
      avatarColor: '#15803d',
      role: 'Managing Partner',
      dept: 'Executive Management',
      tag: 'Director',
      email: 'david.miller@officepro.internal',
      phone: '+91 98765 43211',
      mobile: '+91 98765 43211',
      hireDate: 'Apr 1',
      online: true,
      hourlyCtc: 2400,
      reportingManager: 'None (Board of Directors)',
      timesheetApprover: 'Self',
      leaveL1: 'Self',
      leaveL2: 'Self',
      expenseL1: 'Self',
      expenseL2: 'Finance Head',
      status: 'Active',
      branch: 'Mumbai HQ'
    },
    {
      id: 'EMP003',
      name: 'Ramesh Patil',
      avatarLetter: 'R',
      avatarColor: '#0284c7',
      role: 'Principal Architect & PM',
      dept: 'Engineering & Architecture',
      tag: 'Manager',
      email: 'ramesh.patil@officepro.internal',
      phone: '+91 98765 43212',
      mobile: '+91 98765 43212',
      hireDate: 'Apr 1',
      online: true,
      hourlyCtc: 1200,
      reportingManager: 'Alex Morgan',
      timesheetApprover: 'Alex Morgan',
      leaveL1: 'Alex Morgan',
      leaveL2: 'David Miller',
      expenseL1: 'Alex Morgan',
      expenseL2: 'David Miller',
      status: 'Active',
      branch: 'Pune Branch'
    },
    {
      id: 'EMP004',
      name: 'Priya Sharma',
      avatarLetter: 'P',
      avatarColor: '#7e22ce',
      role: 'Senior Project Engineer',
      dept: 'Structural Design',
      tag: 'Manager',
      email: 'priya.sharma@officepro.internal',
      phone: '+91 98765 43213',
      mobile: '+91 98765 43213',
      hireDate: 'Apr 1',
      online: false,
      hourlyCtc: 850,
      reportingManager: 'Ramesh Patil',
      timesheetApprover: 'Ramesh Patil',
      leaveL1: 'Ramesh Patil',
      leaveL2: 'Alex Morgan',
      expenseL1: 'Ramesh Patil',
      expenseL2: 'Alex Morgan',
      status: 'Active',
      branch: 'Pune Branch'
    },
    {
      id: 'EMP005',
      name: 'Amit Verma',
      avatarLetter: 'A',
      avatarColor: '#059669',
      role: 'Junior Site Engineer',
      dept: 'Site Operations & Execution',
      tag: 'Employee',
      email: 'amit.verma@officepro.internal',
      phone: '+91 98765 43214',
      mobile: '+91 98765 43214',
      hireDate: 'May 15',
      online: true,
      hourlyCtc: 450,
      reportingManager: 'Ramesh Patil',
      timesheetApprover: 'Ramesh Patil',
      leaveL1: 'Ramesh Patil',
      leaveL2: 'Alex Morgan',
      expenseL1: 'Ramesh Patil',
      expenseL2: 'Alex Morgan',
      status: 'Active',
      branch: 'Pune Branch'
    },
    {
      id: 'EMP006',
      name: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#be123c',
      role: 'HR Officer',
      dept: 'Human Resources',
      tag: 'Employee',
      email: 'anjali.desai@officepro.internal',
      phone: '+91 98765 43215',
      mobile: '+91 98765 43215',
      hireDate: 'Apr 1',
      online: true,
      hourlyCtc: 600,
      reportingManager: 'Alex Morgan',
      timesheetApprover: 'Alex Morgan',
      leaveL1: 'Alex Morgan',
      leaveL2: 'David Miller',
      expenseL1: 'Alex Morgan',
      expenseL2: 'David Miller',
      status: 'Active',
      branch: 'Mumbai HQ'
    },
    {
      id: 'EMP007',
      name: 'Elena Rostova',
      avatarLetter: 'E',
      avatarColor: '#ea580c',
      role: 'Lead UI/UX Designer',
      dept: 'UI/UX & Graphics',
      tag: 'Employee',
      email: 'elena.rostova@officepro.internal',
      phone: '+91 98765 43216',
      mobile: '+91 98765 43216',
      hireDate: 'Jun 1',
      online: false,
      hourlyCtc: 750,
      reportingManager: 'Ramesh Patil',
      timesheetApprover: 'Ramesh Patil',
      leaveL1: 'Ramesh Patil',
      leaveL2: 'Alex Morgan',
      expenseL1: 'Ramesh Patil',
      expenseL2: 'Alex Morgan',
      status: 'Active',
      branch: 'Mumbai HQ'
    },
    {
      id: 'EMP008',
      name: 'Lucas Vance',
      avatarLetter: 'L',
      avatarColor: '#0f766e',
      role: 'Senior QA Engineer',
      dept: 'Quality Assurance & Testing',
      tag: 'Employee',
      email: 'lucas.vance@officepro.internal',
      phone: '+91 98765 43217',
      mobile: '+91 98765 43217',
      hireDate: 'Apr 1',
      online: true,
      hourlyCtc: 700,
      reportingManager: 'Sarah Connor',
      timesheetApprover: 'Sarah Connor',
      leaveL1: 'Sarah Connor',
      leaveL2: 'David Miller',
      expenseL1: 'Sarah Connor',
      expenseL2: 'David Miller',
      status: 'Active',
      branch: 'Pune Branch'
    },
    {
      id: 'EMP009',
      name: 'Sarah Connor',
      avatarLetter: 'S',
      avatarColor: '#4338ca',
      role: 'Senior Systems Architect',
      dept: 'Odoo Technical Systems',
      tag: 'Manager',
      email: 'sarah.connor@officepro.internal',
      phone: '+91 98765 43218',
      mobile: '+91 98765 43218',
      hireDate: 'May 1',
      online: true,
      hourlyCtc: 1100,
      reportingManager: 'Alex Morgan',
      timesheetApprover: 'Alex Morgan',
      leaveL1: 'Alex Morgan',
      leaveL2: 'David Miller',
      expenseL1: 'Alex Morgan',
      expenseL2: 'David Miller',
      status: 'Active',
      branch: 'Mumbai HQ'
    },
    {
      id: 'EMP010',
      name: 'Michael Scott',
      avatarLetter: 'M',
      avatarColor: '#854d0e',
      role: 'Regional Operations Lead',
      dept: 'Site Operations & Execution',
      tag: 'Manager',
      email: 'michael.scott@officepro.internal',
      phone: '+91 98765 43219',
      mobile: '+91 98765 43219',
      hireDate: 'Apr 1',
      online: false,
      hourlyCtc: 950,
      reportingManager: 'David Miller',
      timesheetApprover: 'David Miller',
      leaveL1: 'David Miller',
      leaveL2: 'Alex Morgan',
      expenseL1: 'David Miller',
      expenseL2: 'Alex Morgan',
      status: 'Active',
      branch: 'Pune Branch'
    },
    {
      id: 'EMP011',
      name: 'Robert Davis',
      avatarLetter: 'R',
      avatarColor: '#334155',
      role: 'Financial Controller',
      dept: 'Accounting & Finance',
      tag: 'Manager',
      email: 'robert.davis@officepro.internal',
      phone: '+91 98765 43220',
      mobile: '+91 98765 43220',
      hireDate: 'Apr 1',
      online: true,
      hourlyCtc: 1300,
      reportingManager: 'David Miller',
      timesheetApprover: 'David Miller',
      leaveL1: 'David Miller',
      leaveL2: 'Alex Morgan',
      expenseL1: 'David Miller',
      expenseL2: 'Alex Morgan',
      status: 'Active',
      branch: 'Mumbai HQ'
    },
    {
      id: 'EMP012',
      name: 'Tara Mehta',
      avatarLetter: 'T',
      avatarColor: '#10b981',
      role: 'BIM Modeling Specialist',
      dept: 'Engineering & Architecture',
      tag: 'Employee',
      email: 'tara.mehta@officepro.internal',
      phone: '+91 98765 43221',
      mobile: '+91 98765 43221',
      hireDate: 'Jul 10',
      online: true,
      hourlyCtc: 550,
      reportingManager: 'Ramesh Patil',
      timesheetApprover: 'Ramesh Patil',
      leaveL1: 'Ramesh Patil',
      leaveL2: 'Alex Morgan',
      expenseL1: 'Ramesh Patil',
      expenseL2: 'Alex Morgan',
      status: 'Active',
      branch: 'Pune Branch'
    }
  ],
  departments: [
    { id: 'dept_eng', name: 'Engineering & Architecture', manager: 'Ramesh Patil', company: 'Office Pro Solutions Ltd', count: 4, color: '#0284c7' },
    { id: 'dept_str', name: 'Structural Design', manager: 'Priya Sharma', company: 'Office Pro Solutions Ltd', count: 3, color: '#7e22ce' },
    { id: 'dept_site', name: 'Site Operations & Execution', manager: 'Michael Scott', company: 'Office Pro Solutions Ltd', count: 3, color: '#d97706' },
    { id: 'dept_hr', name: 'Human Resources', manager: 'Anjali Desai', company: 'Office Pro Solutions Ltd', count: 2, color: '#be123c' },
    { id: 'dept_acc', name: 'Accounting & Finance', manager: 'Robert Davis', company: 'Office Pro Solutions Ltd', count: 3, color: '#4f46e5' },
    { id: 'dept_tech', name: 'Odoo Technical Systems', manager: 'Sarah Connor', company: 'Office Pro Solutions Ltd', count: 4, color: '#059669' },
    { id: 'dept_ui', name: 'UI/UX & Graphics', manager: 'Elena Rostova', company: 'Office Pro Solutions Ltd', count: 2, color: '#ea580c' },
    { id: 'dept_qa', name: 'Quality Assurance & Testing', manager: 'Lucas Vance', company: 'Office Pro Solutions Ltd', count: 3, color: '#0f766e' }
  ],
  projects: [
    {
      id: 'PRJ/2026/001',
      name: 'Tech Park Phase 2 Commercial Complex',
      client: 'Apex Realty Developers',
      areaSqFt: 45000,
      leader: 'Ramesh Patil',
      billingPolicy: 'Milestone-Based',
      budgetHours: 640,
      loggedHours: 412,
      totalBudget: 1850000,
      invoicedAmount: 1100000,
      hsnSac: '998311 (Architectural Services)',
      gstRate: 18,
      status: 'In Progress',
      milestones: [
        { name: 'Schematic Design & Approval', pct: 20, amount: 370000, status: 'Invoiced & Paid' },
        { name: 'Structural Detailed Drawings', pct: 40, amount: 740000, status: 'Invoiced & Paid' },
        { name: 'MEP & Facade Integration', pct: 25, amount: 462500, status: 'In Progress' },
        { name: 'Final Handover & As-Built', pct: 15, amount: 277500, status: 'Pending' }
      ]
    },
    {
      id: 'PRJ/2026/002',
      name: 'Metro Station Canopy & Entry Plaza',
      client: 'State Urban Transit Corp',
      areaSqFt: 18500,
      leader: 'Priya Sharma',
      billingPolicy: 'Timesheet-Based',
      budgetHours: 320,
      loggedHours: 240,
      totalBudget: 950000,
      invoicedAmount: 580000,
      hsnSac: '998312 (Civil Engineering)',
      gstRate: 18,
      status: 'In Progress',
      milestones: []
    },
    {
      id: 'PRJ/2026/003',
      name: 'Corporate Tower Corporate Interior',
      client: 'FinTech Hub Ltd',
      areaSqFt: 60000,
      leader: 'Ramesh Patil',
      billingPolicy: 'Lumpsum Fee',
      budgetHours: 800,
      loggedHours: 510,
      totalBudget: 2400000,
      invoicedAmount: 1600000,
      hsnSac: '998311 (Architectural Services)',
      gstRate: 18,
      status: 'In Progress',
      milestones: []
    }
  ],
  projectStages: {
    notStarted: [
      { id: 'PRJ004', name: 'Enterprise Marketing Suite', sprintsCount: 1, leader: 'Alex Morgan', avatar: 'V', avatarColor: '#0d9488' },
      { id: 'PRJ005', name: 'Enterprise Sales Portal', sprintsCount: 0, leader: 'David Miller', avatar: 'V', avatarColor: '#0d9488' }
    ],
    inProgress: [
      { id: 'PRJ007', name: 'AI-Engine Architecture', sprintsCount: 1, leader: 'Michael Scott', avatar: 'M', avatarColor: '#7c3aed' },
      { id: 'PRJ010', name: 'Quality Assurance Suite', sprintsCount: 2, leader: 'Alex Morgan', avatar: 'V', avatarColor: '#0d9488' },
      { id: 'PRJ008', name: 'Internal Infrastructure', sprintsCount: 0, leader: 'Alex Morgan', avatar: 'V', avatarColor: '#0d9488' },
      { id: 'PRJ006', name: 'Smart IoT Wearable', sprintsCount: 2, leader: 'Alex Morgan', avatar: 'V', avatarColor: '#0d9488' },
      { id: 'PRJ011', name: 'Office Pro Cloud ERP', sprintsCount: 2, leader: 'Alex Morgan', avatar: 'V', avatarColor: '#0d9488' },
      { id: 'PRJ012', name: 'Global Media Publications', sprintsCount: 2, leader: 'Sarah Connor', avatar: 'S', avatarColor: '#9333ea' },
      { id: 'PRJ001', name: 'Tech Park Phase 2 Complex', sprintsCount: 2, leader: 'Ramesh Patil', avatar: 'R', avatarColor: '#0284c7' },
      { id: 'PRJ002', name: 'Metro Station Canopy & Plaza', sprintsCount: 1, leader: 'Priya Sharma', avatar: 'P', avatarColor: '#7e22ce' },
      { id: 'PRJ003', name: 'Corporate Tower Interior', sprintsCount: 2, leader: 'Ramesh Patil', avatar: 'R', avatarColor: '#0284c7' },
      { id: 'PRJ013', name: 'Smart Sensor Telemetry Grid', sprintsCount: 1, leader: 'Priya Sharma', avatar: 'P', avatarColor: '#7e22ce' },
      { id: 'PRJ014', name: 'Fleet Asset Tracker Firmware', sprintsCount: 2, leader: 'Alex Morgan', avatar: 'V', avatarColor: '#0d9488' },
      { id: 'PRJ015', name: 'Automated Invoice Gateway', sprintsCount: 1, leader: 'David Miller', avatar: 'D', avatarColor: '#15803d' },
      { id: 'PRJ016', name: 'Mobile Kiosk Client App', sprintsCount: 1, leader: 'Amit Verma', avatar: 'A', avatarColor: '#059669' },
      { id: 'PRJ017', name: 'Biometric Gateway Middleware', sprintsCount: 3, leader: 'Lucas Vance', avatar: 'L', avatarColor: '#0f766e' }
    ],
    finalPhase: [],
    closed: [
      { id: 'PRJ009', name: 'Lead Management Hub', sprintsCount: 0, leader: 'Anjali Desai', avatar: 'A', avatarColor: '#7c3aed' }
    ]
  },
  sprints: {
    active: [
      {
        id: 'SPRISH002',
        code: 'SPRISH002',
        name: 'Smart Wearable Sprint 2',
        project: 'IoT - Smart Wearable',
        dates: 'Oct 1 → Oct 14',
        pct: 0,
        pts: '0.00 / 32.00 pts (32 items)',
        daysLeft: '10 days left',
        status: 'Off track',
        avatar: 'V',
        avatarColor: '#0d9488'
      }
    ],
    planned: [],
    closed: [
      {
        id: 'SPRISH001',
        code: 'SPRISH001',
        name: 'IoT Sprint 1',
        project: 'IoT - Smart Wearable',
        dates: 'Sep 29 → Sep 30',
        pct: 100,
        pts: '17.00 / 17.00 pts (17 items)',
        daysLeft: 'Completed',
        status: 'On track',
        avatar: 'V',
        avatarColor: '#0d9488'
      }
    ]
  },
  userStories: {
    backlogs: [
      { code: 'ISH-STORY-010', title: 'DataNexus -v2 Testing - Open Premises', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488', hasPen: true },
      { code: 'ISH-STORY-007', title: 'DataNexus - V3 [ Internal Discussion ]', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V', 'A'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-009', title: 'Proper Documentation & Workflow Creation', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-021', title: 'Gas - Final Discussion & Gas Type Detections', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' }
    ],
    todo: [
      { code: 'ISH-STORY-034', title: 'Feature List - Final Demo', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-036', title: 'GPS Geo Fence', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-037', title: 'Document for CPE710, EAP610', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-033', title: 'Certificate Process', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-016', title: 'Structural Integrity Verification Phase 1', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-018', title: 'Antenna Impedance Match - Band 3/5', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-020', title: 'Battery Level Indicator Alert Thresholds', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' }
    ],
    inProgress: [
      { code: 'ISH-STORY-011', title: 'Check Battery Life of BLE Indoor Asset', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-008', title: 'Button Glitch - Remove from Helmet', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-014', title: 'Document V2 - Complete Message Flow End To End', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V', 'A'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-004', title: 'Print the Black Flame - Paper for Camera Front Side Hide.', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-001', title: 'BLE Beacon RSSI Distance Calibration', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-002', title: 'MQTT Packet Drop Retry Mechanism', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-003', title: 'Heartbeat Health Ping Optimization', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-005', title: 'Accelerometer Fall Detection Logic', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-006', title: 'Firmware Over-The-Air (FOTA) Bootstrap', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-012', title: 'IMU 6-Axis Axis Remap & Calibration', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-015', title: 'Power Consumption Benchmarking at 3.3V', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-017', title: 'Audio Speaker Filter & Noise Floor Tuning', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-023', title: 'GPS Time Sync vs NTP Epoch Timestamping', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-026', title: 'LED Status Indicator Pulse Modes', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-027', title: 'EEPROM Wear Leveling Driver', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' }
    ],
    onHold: [
      { code: 'ISH-STORY-025', title: 'Circuit Check - EC200U - GSM/GPS', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-024', title: 'Audio & Video Check - EC200U - GSM/GPS', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-022', title: '[ v2 ] - Smart Wearable - upgrade ADXL to BMI270', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V', 'A'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-019', title: 'Voice Feedback Quality', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' },
      { code: 'ISH-STORY-013', title: 'Environmental Chamber Thermal Stress Test', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['V'], avatarColor: '#0d9488' },
      { code: 'ISH-STORY-028', title: 'High-Altitude Pressure Variation Compensation', sprint: '[SPRISH002] Smart Wearable    IoT - Smart Wearable', pts: '1.00 pts', avatars: ['A'], avatarColor: '#10b981' }
    ]
  },
  timesheets: [
    {
      id: 'TS/2026/W40',
      employee: 'Priya Sharma',
      week: 'Week 40 (Sep 29 - Oct 05, 2026)',
      status: 'Submitted',
      submittedAt: 'Oct 02, 2026 14:45',
      approver: 'Ramesh Patil',
      entries: [
        { project: 'Tech Park Phase 2 Commercial Complex', task: 'Facade Wind Load Analysis', mon: 4, tue: 4, wed: 5, thu: 4, fri: 4, sat: 0, sun: 0 },
        { project: 'Metro Station Canopy & Entry Plaza', task: 'Foundation Rebar Detailing', mon: 4, tue: 4, wed: 3, thu: 4, fri: 4, sat: 4, sun: 0 }
      ],
      overtimeClaimed: 4,
      overtimeReason: 'Emergency Transit Authority review for Metro canopy drawings on Saturday'
    }
  ],
  allTimesheets: [
    {
      id: 'TSL001',
      date: 'Oct 3',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Coordination & Review',
      description: 'Coordination for Candidate offers and salary benchmarking',
      salesOrder: '-',
      timeSpent: '00:30',
      status: 'Approved',
      elapsed: '05:25'
    },
    {
      id: 'TSL002',
      date: 'Oct 1',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Candidate Interviews',
      description: 'Coordination with Executive Director for Candidate Interviews, Offers and more',
      salesOrder: '-',
      timeSpent: '01:00',
      status: 'Approved',
      elapsed: '07:55'
    },
    {
      id: 'TSL003',
      date: 'Oct 1',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Meeting with Leads',
      description: 'Coordination and roadmap sync meeting for candidate technical evaluation and assessment',
      salesOrder: '-',
      timeSpent: '00:30',
      status: 'Approved',
      elapsed: '07:54'
    },
    {
      id: 'TSL004',
      date: 'Oct 1',
      employee: 'Michael Scott',
      avatarLetter: 'M',
      avatarColor: '#854d0e',
      project: 'Smart Wearable V2',
      task: 'SKY-AI-RFI Endpoint',
      description: 'Added the new endpoint as per the new Requirement and removed the new bug in edge telemetry',
      salesOrder: 'SO-0089',
      timeSpent: '08:00',
      status: 'Approved',
      elapsed: '08:41'
    },
    {
      id: 'TSL005',
      date: 'Oct 1',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Candidate Interviews',
      description: 'Coordination with Java, Embedded and BD candidates for Negotiation and Interview rounds',
      salesOrder: '-',
      timeSpent: '03:30',
      status: 'Approved',
      elapsed: '06:59'
    },
    {
      id: 'TSL006',
      date: 'Oct 1',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Coordination & Review',
      description: 'Coordination with Tech Lead for LWD and Mail on points discussed during exit formalities',
      salesOrder: '-',
      timeSpent: '00:15',
      status: 'Approved',
      elapsed: '06:57'
    },
    {
      id: 'TSL007',
      date: 'Oct 1',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Team Onboarding',
      description: 'Documentation Handover and developer credential provisioning for new team engineers',
      salesOrder: '-',
      timeSpent: '00:00',
      status: 'Draft',
      elapsed: '00:00'
    },
    {
      id: 'TSL008',
      date: 'Oct 1',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Transit Infrastructure',
      task: 'Team Coordination',
      description: 'Coordination for Transit Project Development Updates and Weekly status for stakeholders',
      salesOrder: 'SO-0042',
      timeSpent: '02:00',
      status: 'Draft',
      elapsed: '00:00'
    },
    {
      id: 'TSL009',
      date: 'Sep 30',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Digital Marketing Suite',
      task: 'Client Coordination',
      description: 'Coordination for Campaign Strategy and Deliverables Approval with design agency',
      salesOrder: 'SO-0015',
      timeSpent: '00:15',
      status: 'Approved',
      elapsed: '06:41'
    },
    {
      id: 'TSL010',
      date: 'Sep 30',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Digital Marketing Suite',
      task: 'Coordination & Review',
      description: 'Coordination for Enterprise Product Video Script and voiceover master recordings',
      salesOrder: '-',
      timeSpent: '00:30',
      status: 'Draft',
      elapsed: '00:00'
    },
    {
      id: 'TSL011',
      date: 'Sep 30',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Candidate Interviews',
      description: 'HR Drive setup within Enterprise Solutions and department folder permissions',
      salesOrder: '-',
      timeSpent: '01:00',
      status: 'Approved',
      elapsed: '06:37'
    },
    {
      id: 'TSL012',
      date: 'Sep 30',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Candidate Interviews',
      description: 'Coordination for BD and Architecture Candidate interview schedule and panel alignment',
      salesOrder: '-',
      timeSpent: '01:00',
      status: 'Approved',
      elapsed: '06:29'
    },
    {
      id: 'TSL013',
      date: 'Sep 30',
      employee: 'Michael Scott',
      avatarLetter: 'M',
      avatarColor: '#854d0e',
      project: 'Smart Wearable V2',
      task: 'SKYSTRUCT Core Engine',
      description: 'Added the new changes to the RFI module and Deployed the Same to staging cluster',
      salesOrder: 'SO-0089',
      timeSpent: '08:00',
      status: 'Approved',
      elapsed: '08:34'
    },
    {
      id: 'TSL014',
      date: 'Sep 29',
      employee: 'Anjali Desai',
      avatarLetter: 'A',
      avatarColor: '#10b981',
      project: 'Operations & HR Admin',
      task: 'Quote Request & Review',
      description: 'Replied to the mail for information and requested the quote for the selected hardware kit',
      salesOrder: '-',
      timeSpent: '02:00',
      status: 'Approved',
      elapsed: '31:57'
    },
    {
      id: 'TSL015',
      date: 'Sep 29',
      employee: 'Priya Sharma',
      avatarLetter: 'P',
      avatarColor: '#7e22ce',
      project: 'Tech Park Phase 2 Complex',
      task: 'Structural Analysis',
      description: 'Facade Wind Load Analysis and finite element model simulations in STAAD Pro',
      salesOrder: 'SO-0021',
      timeSpent: '04:00',
      status: 'Approved',
      elapsed: '08:15'
    },
    {
      id: 'TSL016',
      date: 'Sep 29',
      employee: 'Amit Verma',
      avatarLetter: 'A',
      avatarColor: '#059669',
      project: 'Metro Station Canopy & Plaza',
      task: 'Foundation Detailing',
      description: 'On-site Rebar placement inspection and bar bending schedule verification for footing F-4',
      salesOrder: 'SO-0022',
      timeSpent: '04:00',
      status: 'Approved',
      elapsed: '08:00'
    }
  ],
  attendanceLogs: [
    { date: '2026-10-04 (Today)', in: '09:02 AM', breakOut: '01:00 PM', breakIn: '01:45 PM', out: '--', netHours: '4h 43m (In Progress)', status: 'Present' },
    { date: '2026-10-03 (Fri)', in: '08:55 AM', breakOut: '01:05 PM', breakIn: '01:50 PM', out: '06:15 PM', netHours: '8h 35m', status: 'Compliant' },
    { date: '2026-10-02 (Thu)', in: '09:15 AM', breakOut: '01:00 PM', breakIn: '01:45 PM', out: '05:30 PM', netHours: '7h 30m', status: 'Shortage Alert (<8h)' },
    { date: '2026-10-01 (Wed)', in: '09:00 AM', breakOut: '--', breakIn: '--', out: '--', netHours: '--', status: 'Missing Punch (Regularization Req)' }
  ],
  attendances: [
    { id: 'ATT001', employee: 'Alex Morgan', avatarLetter: 'A', avatarColor: '#b45309', checkIn: 'Oct 1, 9:12 AM', checkOut: 'Oct 1, 9:01 PM', workedHours: '11:09', extraHours: '02:49', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT002', employee: 'David Miller', avatarLetter: 'D', avatarColor: '#15803d', checkIn: 'Sep 30, 7:20 PM', checkOut: 'Oct 1, 10:06 AM', workedHours: '14:45', extraHours: '01:46', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT003', employee: 'Ramesh Patil', avatarLetter: 'R', avatarColor: '#0284c7', checkIn: 'Sep 30, 12:35 PM', checkOut: 'Sep 30, 7:30 PM', workedHours: '06:15', extraHours: '00:00', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT004', employee: 'Priya Sharma', avatarLetter: 'P', avatarColor: '#7e22ce', checkIn: 'Sep 30, 10:36 AM', checkOut: 'Sep 30, 7:45 PM', workedHours: '08:28', extraHours: '00:08', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT005', employee: 'Amit Verma', avatarLetter: 'A', avatarColor: '#059669', checkIn: 'Sep 30, 10:35 AM', checkOut: 'Sep 30, 2:00 PM', workedHours: '03:05', extraHours: '00:00', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT006', employee: 'Anjali Desai', avatarLetter: 'A', avatarColor: '#be123c', checkIn: 'Sep 30, 10:35 AM', checkOut: 'Sep 30, 8:38 PM', workedHours: '09:23', extraHours: '01:03', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT007', employee: 'Elena Rostova', avatarLetter: 'E', avatarColor: '#ea580c', checkIn: 'Sep 30, 10:34 AM', checkOut: 'Sep 30, 7:17 PM', workedHours: '08:03', extraHours: '00:00', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT008', employee: 'Lucas Vance', avatarLetter: 'L', avatarColor: '#0f766e', checkIn: 'Sep 30, 10:30 AM', checkOut: 'Sep 30, 7:15 PM', workedHours: '08:05', extraHours: '00:00', inputModeIn: 'Manual', inputModeOut: 'Manual' },
    { id: 'ATT009', employee: 'Sarah Connor', avatarLetter: 'S', avatarColor: '#4338ca', checkIn: 'Sep 30, 10:26 AM', checkOut: 'Sep 30, 6:40 PM', workedHours: '07:34', extraHours: '00:00', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT010', employee: 'Michael Scott', avatarLetter: 'M', avatarColor: '#854d0e', checkIn: 'Sep 30, 10:21 AM', checkOut: 'Sep 30, 7:24 PM', workedHours: '08:23', extraHours: '00:03', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT011', employee: 'Robert Davis', avatarLetter: 'R', avatarColor: '#334155', checkIn: 'Sep 30, 10:21 AM', checkOut: 'Sep 30, 7:30 PM', workedHours: '08:29', extraHours: '00:09', inputModeIn: 'Biometric', inputModeOut: 'Biometric' },
    { id: 'ATT012', employee: 'Tara Mehta', avatarLetter: 'T', avatarColor: '#10b981', checkIn: 'Sep 30, 10:20 AM', checkOut: 'Sep 30, 7:00 PM', workedHours: '08:00', extraHours: '00:00', inputModeIn: 'Manual', inputModeOut: 'Manual' }
  ],
  biometricDevice: {
    id: 'DEV001',
    name: 'ADMS Device CUB7252300146',
    serialNumber: 'CUB7252300146',
    admsEnabled: true,
    status: 'Push Active',
    lastPush: 'Oct 3, 7:27 PM',
    totalUsers: 31,
    mappedUsers: 30,
    unmappedUsers: 1,
    timezone: 'Asia/Kolkata',
    usedFor: 'Attendance',
    statusCodeBased: false,
    minCheckoutGap: 4.00,
    pushUrl: 'http://connect.officepro.internal/iclock/cdata'
  },
  deviceUsers: [
    { pin: '1', nameOnDevice: 'Alex', employee: 'Alex Morgan', mapped: true },
    { pin: '10', nameOnDevice: 'David', employee: 'David Miller', mapped: true },
    { pin: '11', nameOnDevice: 'Ramesh', employee: 'Ramesh Patil', mapped: true },
    { pin: '12', nameOnDevice: 'Priya', employee: 'Priya Sharma', mapped: true },
    { pin: '13', nameOnDevice: 'Amit', employee: 'Amit Verma', mapped: true },
    { pin: '14', nameOnDevice: 'Anjali', employee: 'Anjali Desai', mapped: true },
    { pin: '15', nameOnDevice: 'Elena', employee: 'Elena Rostova', mapped: true },
    { pin: '16', nameOnDevice: 'Lucas', employee: 'Lucas Vance', mapped: true },
    { pin: '17', nameOnDevice: 'Sarah', employee: 'Sarah Connor', mapped: true },
    { pin: '18', nameOnDevice: 'Michael', employee: 'Michael Scott', mapped: true },
    { pin: '19', nameOnDevice: 'Robert', employee: 'Robert Davis', mapped: true },
    { pin: '20', nameOnDevice: 'Tara', employee: 'Tara Mehta', mapped: true },
    { pin: '99', nameOnDevice: 'Guest_Temp', employee: 'Unmapped Device User', mapped: false }
  ],
  absenceRequests: [
    { id: 'ABS001', employee: 'Amit Verma', type: 'Full Day Request', date: '2026-10-02', status: 'Approved', approver: 'Ramesh Patil', reason: 'Official Municipal Authority visit' },
    { id: 'ABS002', employee: 'Priya Sharma', type: 'Compute Absent Days', date: '2026-09-30', status: 'Computed', approver: 'System Engine', reason: 'Biometric reconciliation' }
  ],
  leaveBalances: {
    vacation: 14,
    sick: 8,
    compensatory: 3.5,
    festival: 10,
    flexible: 2
  },
  leaveRequests: [
    {
      id: 'LV/2026/014',
      employee: 'Amit Verma',
      dept: 'Site Operations & Execution',
      avatarLetter: 'A',
      avatarColor: '#059669',
      type: 'Vacation Leave',
      fromDate: '2026-10-12',
      toDate: '2026-10-14',
      days: 3,
      currentBalance: '14 Days remaining',
      reason: 'Family wedding ceremony in hometown',
      level1Approver: 'Ramesh Patil',
      level1Status: 'Approved',
      level2Approver: 'Executive Approver',
      level2Status: 'Pending Final Signoff',
      overallStatus: 'To Approve'
    },
    {
      id: 'LV/2026/013',
      employee: 'Priya Sharma',
      dept: 'Structural Design',
      avatarLetter: 'P',
      avatarColor: '#7e22ce',
      type: 'Sick Leave',
      fromDate: '2026-09-25',
      toDate: '2026-09-25',
      days: 1,
      currentBalance: '8 Days remaining',
      reason: 'Viral Fever & Medical Rest',
      level1Approver: 'Ramesh Patil',
      level1Status: 'Approved',
      level2Approver: 'Executive Approver',
      level2Status: 'Approved',
      overallStatus: 'Approved'
    },
    {
      id: 'LV/2026/015',
      employee: 'Elena Rostova',
      dept: 'UI/UX & Graphics',
      avatarLetter: 'E',
      avatarColor: '#ea580c',
      type: 'Compensatory Off',
      fromDate: '2026-10-16',
      toDate: '2026-10-16',
      days: 1,
      currentBalance: '3.5 Days remaining',
      reason: 'Comp-off earned against Saturday Metro station canopy sprint',
      level1Approver: 'Ramesh Patil',
      level1Status: 'Pending',
      level2Approver: 'Executive Approver',
      level2Status: 'Pending',
      overallStatus: 'To Approve'
    }
  ],
  leaveAllocations: [
    { id: 'ALC001', employee: 'Priya Sharma', type: 'Compensatory Leave', allocatedDays: 4.0, reason: 'Weekend Overtime (4h Sat review)', status: 'Approved', date: 'Oct 02, 2026' },
    { id: 'ALC002', employee: 'Amit Verma', type: 'Annual Paid Leave Quota', allocatedDays: 18.0, reason: 'FY 2026-27 Annual Statutory Quota', status: 'Approved', date: 'Apr 01, 2026' },
    { id: 'ALC003', employee: 'Elena Rostova', type: 'Compensatory Leave', allocatedDays: 1.0, reason: 'Saturday Sprint Overtime', status: 'To Approve', date: 'Oct 03, 2026' }
  ],

  expenses: [
    {
      id: 'EXP/2026/088',
      employee: 'Amit Verma',
      date: '2026-10-01',
      category: 'Travel & Site Cab',
      amount: 1450,
      taggedTo: 'Project: PRJ/2026/001 (Tech Park Phase 2)',
      description: 'Site inspection transit fare and concrete test lab drop',
      receipt: 'cab_receipt_tax_inv.pdf',
      status: 'Approved by L1 (Ramesh Patil), Pending Finance',
      l1Status: 'Approved',
      l2Status: 'Pending'
    },
    {
      id: 'EXP/2026/087',
      employee: 'Ramesh Patil',
      date: '2026-09-28',
      category: 'Printing & Large Plotting',
      amount: 3200,
      taggedTo: 'Project: PRJ/2026/002 (Metro Station Canopy)',
      description: 'A0 size blueprint plot sets for municipal clearance',
      receipt: 'repro_print_invoice.pdf',
      status: 'Approved & Reimbursed',
      l1Status: 'Approved',
      l2Status: 'Approved'
    }
  ],
  invoices: [
    {
      id: 'INV/2026/0042',
      date: '2026-09-30',
      client: 'Apex Realty Developers',
      project: 'Tech Park Phase 2 Commercial Complex',
      billingType: 'Milestone (Structural Detailed Drawings)',
      baseAmount: 740000,
      hsn: '998311',
      cgst: 66600,
      sgst: 66600,
      totalAmount: 873200,
      status: 'Paid',
      dueDate: '2026-10-15'
    },
    {
      id: 'INV/2026/0043',
      date: '2026-10-02',
      client: 'State Urban Transit Corp',
      project: 'Metro Station Canopy & Entry Plaza',
      billingType: 'Timesheet (Sep 2026 - 120 Approved Hours)',
      baseAmount: 360000,
      hsn: '998312',
      cgst: 32400,
      sgst: 32400,
      totalAmount: 424800,
      status: 'Sent / Pending Payment',
      dueDate: '2026-10-20'
    }
  ],
  webmail: [
    {
      id: 1,
      sender: 'municipal.approvals@mumbai.gov.in',
      senderName: 'BMC Town Planning Dept',
      subject: 'Approval Clearance Granted: Tech Park Phase 2 Layout Plan',
      date: 'Today, 11:30 AM',
      folder: 'inbox',
      unread: true,
      body: 'Dear M/s Office Pro & Apex Realty,\n\nWe are pleased to communicate that the revised schematic layout drawings for Tech Park Phase 2 (Area: 45,000 sq.ft) submitted under File No. TP/2026/8941 have received formal preliminary NOC.\n\nPlease find attached the verified stamping schedule.\n\nRegards,\nTown Planning Officer\nBMC Mumbai'
    },
    {
      id: 2,
      sender: 'accounts@fintechhub.com',
      senderName: 'FinTech Hub Finance Dept',
      subject: 'Payment Advice: Inward Remittance for Corporate HQ Interior Milestone #1',
      date: 'Yesterday, 04:15 PM',
      folder: 'inbox',
      unread: false,
      body: 'Hi Team,\n\nWe have initiated NEFT transfer of INR 9,44,000 against Tax Invoice INV/2026/0038.\nUTR Reference: N2610029871142.\n\nKindly acknowledge receipt.\n\nBest,\nAccounts Payable\nFinTech Hub Ltd.'
    },
    {
      id: 3,
      sender: 'hr@officepro.internal',
      senderName: 'Anjali Desai (HR)',
      subject: 'Reminder: Monday 3:00 PM Timesheet Submission Deadline',
      date: 'Oct 02, 2026',
      folder: 'inbox',
      unread: false,
      body: 'All Team Members,\n\nPlease ensure your weekly timesheets for Week 40 are logged and submitted before Monday 3:00 PM. Note the mandatory 8-hour daily validation rule. Incomplete entries cannot be submitted without justification.\n\nRegards,\nAnjali Desai\nHR Officer'
    }
  ],
  technicalRegistry: {
    models: [
      { key: 'res.users', name: 'User Accounts', module: 'base', table: 'res_users', count: 6 },
      { key: 'res.company', name: 'Companies & Branches', module: 'base', table: 'res_company', count: 2 },
      { key: 'ir.model', name: 'Models Registry', module: 'base', table: 'ir_model', count: 18 },
      { key: 'ir.model.fields', name: 'Fields Catalog', module: 'base', table: 'ir_model_fields', count: 142 },
      { key: 'ir.cron', name: 'Scheduled Cron Jobs', module: 'base', table: 'ir_cron', count: 4 },
      { key: 'ir.rule', name: 'Record Rules (Row Security)', module: 'base', table: 'ir_rule', count: 12 },
      { key: 'ir.model.access', name: 'Model Access Rights', module: 'base', table: 'ir_model_access', count: 24 },
      { key: 'ir.sequence', name: 'Document Sequences', module: 'base', table: 'ir_sequence', count: 8 },
      { key: 'mail.mail', name: 'Webmail Messages', module: 'mail', table: 'mail_mail', count: 3 },
      { key: 'hr.employee', name: 'Employee Master', module: 'employee', table: 'hr_employee', count: 6 },
      { key: 'project.project', name: 'Project Master', module: 'project', table: 'project_project', count: 3 },
      { key: 'project.timesheet', name: 'Weekly Timesheets', module: 'project', table: 'project_timesheet', count: 12 },
      { key: 'hr.attendance', name: 'Attendance & Punches', module: 'attendance', table: 'hr_attendance', count: 156 },
      { key: 'hr.leave', name: 'Leave Allocations & Requests', module: 'leave', table: 'hr_leave', count: 28 },
      { key: 'hr.expense', name: 'Expense Claims', module: 'expense', table: 'hr_expense', count: 45 },
      { key: 'account.invoice', name: 'Customer Invoices', module: 'accounting', table: 'account_invoice', count: 43 }
    ],
    crons: [
      { id: 1, name: 'Timesheet Submission Deadline Monitor', interval: 'Every Monday 15:00', nextRun: '2026-10-06 15:00:00', status: 'Active' },
      { id: 2, name: 'Attendance Net-Hours & Missing Punch Flag', interval: 'Daily 23:59', nextRun: '2026-10-04 23:59:00', status: 'Active' },
      { id: 3, name: 'Monthly Leave Accrual Credit Engine', interval: '1st of Every Month 00:01', nextRun: '2026-11-01 00:01:00', status: 'Active' },
      { id: 4, name: 'Incoming SMTP Webmail Poller', interval: 'Every 5 Minutes', nextRun: '2026-10-04 14:35:00', status: 'Active' }
    ]
  },
  installedModules: [
    {
      id: 'MOD001',
      name: 'HR Employee Analytics',
      key: 'hr_employee_analytics',
      category: 'Human Resources',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Learn More',
      summary: 'Advanced employee workforce distribution, skill matrices, headcount turnover, and real-time CTC labor cost analysis.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'hr'],
      models: ['hr.employee', 'hr.department', 'hr.employee.analytics'],
      status: 'Installed'
    },
    {
      id: 'MOD002',
      name: 'Project Restriction Module',
      key: 'project_restriction_customization',
      category: 'Services & Projects',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Learn More',
      summary: 'Multi-tier project access rules (ir.rule) restricting task visibility to assigned project members and managers.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'project'],
      models: ['project.project', 'project.task', 'ir.rule'],
      status: 'Installed'
    },
    {
      id: 'MOD003',
      name: 'Accounting Customization',
      key: 'accounting_customization',
      category: 'Finance & Accounting',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Module Info',
      summary: 'Statutory GST compliance engine (CGST/SGST/IGST 18%), HSN/SAC automated resolution, and live project gross margin calculation.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'account', 'project'],
      models: ['account.move', 'account.move.line', 'account.tax'],
      status: 'Installed'
    },
    {
      id: 'MOD004',
      name: 'Dashboard Customization',
      key: 'dashboard_customization',
      category: 'Productivity & Dashboard',
      iconType: 'dashboard',
      iconColor: '#f43f5e',
      btnLabel: 'Learn More',
      summary: 'Dynamic executive cockpit with live cashflow burndown, resource capacity charts, and pending multi-tier approval widgets.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'web'],
      models: ['board.board', 'ir.ui.view'],
      status: 'Installed'
    },
    {
      id: 'MOD005',
      name: 'Attendance Customize',
      key: 'attendance_module',
      category: 'Human Resources',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Learn More',
      summary: 'Biometric punch regularization, mandatory 8-hour daily validation rule, and automated comp-off calculation engine.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'hr_attendance'],
      models: ['hr.attendance', 'hr.attendance.overtime'],
      status: 'Installed'
    },
    {
      id: 'MOD006',
      name: 'Login Page Customization',
      key: 'login_page_customization',
      category: 'UI & Customization',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Learn More',
      summary: 'Enterprise-branded single sign-on (SSO) gateway with multi-branch corporate selector and security auditing.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'auth_signup'],
      models: ['res.users', 'res.company'],
      status: 'Installed'
    },
    {
      id: 'MOD007',
      name: 'PropX Lead Integration',
      key: 'email_marketing',
      category: 'Services & Projects',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Module Info',
      summary: 'Automated lead-to-project scope conversion pipeline with built-up area (sq.ft) estimation tools.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'mail', 'project'],
      models: ['crm.lead', 'project.project'],
      status: 'Installed'
    },
    {
      id: 'MOD008',
      name: 'eSSL Biometric Attendance',
      key: 'essl_adms_19',
      category: 'Hardware & Biometrics',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Learn More',
      summary: 'Real-time ADMS Push listener for eSSL/ZKTeco hardware devices over HTTP/HTTPS with auto employee PIN synchronization.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'hr_attendance'],
      models: ['biometric.device', 'biometric.device.user'],
      status: 'Installed'
    },
    {
      id: 'MOD009',
      name: 'HR Leave Report',
      key: 'hr_emp_leave_analytics',
      category: 'Human Resources',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Learn More',
      summary: 'Statutory leave ledger reporting, annual encashment computations, and cross-department absence trends.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'hr_holidays'],
      models: ['hr.leave', 'hr.leave.report'],
      status: 'Installed'
    },
    {
      id: 'MOD010',
      name: 'HR Payroll Leave Summary',
      key: 'hr_payroll_leave_summary',
      category: 'Human Resources',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Learn More',
      summary: 'Monthly payroll integration syncing approved leaves (8h blocks) and unpaid absence deductions into payslips.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'hr_payroll', 'hr_holidays'],
      models: ['hr.payslip', 'hr.leave'],
      status: 'Installed'
    },
    {
      id: 'MOD011',
      name: 'Project Sprints',
      key: 'project_sprint',
      category: 'Services & Projects',
      iconType: 'cube',
      iconColor: '#00a09d',
      btnLabel: 'Module Info',
      summary: 'Agile milestone tracking, weekly sprint planning, and timesheet billability verification.',
      version: '18.0.1.0.0',
      author: 'Office Pro Solutions Ltd',
      dependencies: ['base', 'project', 'hr_timesheet'],
      models: ['project.sprint', 'project.milestone'],
      status: 'Installed'
    }
  ],
  presentationQA: [
    {
      category: '0. 5W1H Foundation',
      q: 'WHAT is this project? (Core Definition & Deliverables)',
      a: 'Office Pro is a modular, enterprise-grade Office Management and ERP platform tailored for architecture, engineering, and consulting firms.\nIt delivers:\n1. Core Engine: Authentication, multi-branch support, dynamic metadata registries (ir.model, ir.fields), cron scheduler (ir.cron), and row-level security (ir.rule).\n2. 6 Integrated Business Modules: Employees, Projects & Timesheets, Biometric Attendance, Leaves, Expenses, Accounting & Invoicing, plus Webmail.\n3. Real-Time Profitability Engine: Calculates live project gross margins by factoring employee hourly CTC labor costs, logged timesheet hours, tagged expenses, and client milestone billing.'
    },
    {
      category: '0. 5W1H Foundation',
      q: 'WHY are we building this project? (Motivation & Problem Statement)',
      a: 'Today companies use 4 to 6 disconnected tools (Excel timesheets, biometric desktop software, WhatsApp leaves, paper expenses, standalone billing software).\nThis causes:\n• Zero real-time visibility into project profitability (managers don\'t know if a project made money until months later).\n• Timesheet billing leakage and fake hours due to lack of daily threshold validation.\n• Operational disconnect where leaves and attendance punches do not sync with payroll or timesheets.\nOffice Pro unifies all operations into a single relational graph with zero-touch modularity at a fraction of standard SAP/Odoo Enterprise costs.'
    },
    {
      category: '0. 5W1H Foundation',
      q: 'HOW are we building it? (Two-Tier Zero-Touch Architecture)',
      a: '• Two-Tier Zero-Touch Engine: Tier 1 (Core base & authentication) handles shared security, metadata registries, and UI layouts. Tier 2 (Business modules) plug in without editing a single line of core code.\n• Dynamic Metadata Discovery: Django post-migrate signals automatically catalogue all models and fields into ir.model and ir.model.fields.\n• Frontend: Pure Vanilla CSS tokens and JavaScript with dynamic theming and Developer Mode (?debug=1) field inspectability.\n• Backend: Python 3.11+, Django ORM, and PostgreSQL with table-level constraints, triggers, and row security rules.'
    },
    {
      category: '0. 5W1H Foundation',
      q: 'WHO are the users & personas of this platform?',
      a: '1. Employees: Log daily timesheets, punch biometrics, apply for leaves/expenses, track compensatory balances.\n2. Project Leaders: Define project scopes (sq.ft), milestones, allocate team hours, and borrow cross-department resources.\n3. Approver Matrix: Level 1 (Direct Reporting Manager) and Level 2 (Executive Management / Finance Head).\n4. HR Administrators: Manage employee master data, Hourly CTC rates, shift timings, and missing punch regularizations.\n5. Billing & Finance: Generate GST invoices (Milestone %, Hourly, Lumpsum) and process expense payouts.\n6. Directors / Partners: Live dashboard of project profitability and resource capacity.'
    },
    {
      category: '0. 5W1H Foundation',
      q: 'WHEN does each business workflow occur? (Operating Cadence)',
      a: '• Daily: Employees punch in/out (system monitors 8 net working hours); project tasks logged in timesheets.\n• Weekly Deadlines: Monday 3:00 PM (Strict timesheet submission deadline with 8-hr daily validation rule); Tuesday 5:00 PM (Manager reviews and approvals).\n• Monthly: 1st of every month at 00:01 (ir.cron automatically credits monthly vacation/sick leave accruals); monthly payroll integrates verified attendance and leaves.\n• Project Milestones: Invoices generated upon deliverable signoff, instantly updating project profitability.'
    },
    {
      category: '0. 5W1H Foundation',
      q: 'WHERE is the engineering innovation & unique value?',
      a: '1. Zero-Touch Modularity: Eliminates cross-developer merge conflicts and allows independent app shipping.\n2. Deterministic 8-Hour Rule & Leave Auto-Sync: Approved leaves automatically inject 8-hr blocks into timesheets.\n3. Automated Cross-Team Resource Loaning: Borrowing an engineer automatically debits the borrowing project with their Hourly CTC.\n4. Real-Time Gross Margin Computation: Revenue - [(Hours × CTC) + Direct Expenses] without batch lag.'
    },
    {
      category: '1. Architecture & Design',
      q: 'Why did you choose a Two-Tier "Zero-Touch" architecture instead of a monolithic single app?',
      a: 'A monolithic approach creates high merge-conflict risk and cross-module regressions when multiple developers work simultaneously. In our Two-Tier architecture:\n• Tier 1 (Core Engine): Provides authentication, metadata registries (ir.model, ir.fields), security row-rules (ir.rule), and unified UI layout widgets.\n• Tier 2 (Business Apps): Webmail, Employee, Project, Attendance, Leave, Expense, Accounting are standalone plug-and-play modules.\nDevelopers can build, migrate, and test their own business app without altering any core files. When migrated, post-migrate signals automatically catalogue models and fields into ir.* registries.'
    },
    {
      category: '1. Architecture & Design',
      q: 'What is the purpose of the Odoo-inspired ir.* (Information Repository) metadata tables?',
      a: 'The ir.* tables (ir.model, ir.model.fields, ir.ui.view, ir.rule, ir.cron, ir.sequence) turn static code into runtime-inspectable metadata.\n1. Dynamic Many2One Autocomplete: The Many2One widget dynamically queries ir.model to resolve relations without hardcoding.\n2. Developer Mode (?debug=1): Hovering on any field instantly shows its technical model name, field key, and DB type.\n3. Dynamic Row-Level Security (ir.rule): Allows domain-based permission filters without writing repetitive custom SQL.'
    },
    {
      category: '2. Project & Timesheet Engine',
      q: 'Explain the mandatory 8-Hour Daily Validation rule and how leaves are synchronized.',
      a: 'To guarantee strict ERP billing integrity and payroll compliance:\n• Timesheet validation blocks submission if any regular workday has less than 8 logged hours.\n• If an employee has an approved Leave or Time-Off, our signal handler automatically creates an 8-hour non-project time block in the weekly timesheet grid so the daily threshold is met without manual fudge hours.'
    },
    {
      category: '2. Project & Timesheet Engine',
      q: 'How does the Overtime & Comp-Off policy differentiate between weekdays and weekends?',
      a: '• Weekday Overtime (Mon–Fri): Junior/Mid staff must log at least 3.5 extra hours beyond 8 hours on a task to be eligible for comp-off credit. Senior managers/leaders are not eligible for weekday overtime.\n• Weekend/Holiday Overtime: 100% of verified hours logged on Saturdays, Sundays, or Public Holidays convert 1-to-1 into Compensatory Leave balance upon manager approval.'
    },
    {
      category: '3. Approvals & Multi-Tier Matrix',
      q: 'Why are 2-Level Approvals mandatory for Leave and Expense, and who are the approvers?',
      a: '• Level 1 (Reporting Manager): Validates operational feasibility (e.g., project deadlines, team bandwidth, legitimate receipts).\n• Level 2 (Executive Management / Finance Head): Validates company-wide leave liabilities, financial budgets, and client billability.\nThis prevents unauthorized single-person approvals and enforces strict corporate governance.'
    },
    {
      category: '4. Profitability & Accounting Engine',
      q: 'How is Real-Time Project Profitability calculated in Office Pro?',
      a: 'Real-time project gross margin is computed as:\nProfit = Total Billed / Milestone Revenue - [(Logged Timesheet Hours × Employee Hourly CTC) + Tagged Direct Project Expenses]\nExample for Tech Park Phase 2:\n• Revenue: ₹18,50,000\n• Labor Cost: 412 hrs × Avg CTC (₹850) = ₹3,50,200\n• Tagged Expenses: ₹48,000\n• Gross Profit: ₹14,51,800 (Margin: 78.4%)'
    },
    {
      category: '5. Security & Access Control',
      q: 'What is the difference between Model Access Rights (ir.model.access) and Record Rules (ir.rule)?',
      a: '• ir.model.access (Table Level): Defines standard CRUD permissions (Create, Read, Write, Delete) for a user group on an entire table (e.g., HR Officers can Read/Write hr.employee).\n• ir.rule (Row Level): Enforces row-level domain filters (e.g., ["employee_id.user_id", "=", user.id]) so standard employees only see their own timesheets, salary slips, and attendance punches while Managers see their direct subordinates.'
    }
  ]
};

// Global Store with Auto-Sync & Migration
function loadInitialState() {
  try {
    const saved = localStorage.getItem('office_pro_demo_state');
    if (!saved) return JSON.parse(JSON.stringify(INITIAL_DATA));
    const parsed = JSON.parse(saved);
    const merged = {
      ...INITIAL_DATA,
      ...parsed,
      installedModules: (parsed.installedModules && parsed.installedModules.length > 0) ? parsed.installedModules : JSON.parse(JSON.stringify(INITIAL_DATA.installedModules)),
      allTimesheets: (parsed.allTimesheets && parsed.allTimesheets.length > 0) ? parsed.allTimesheets : JSON.parse(JSON.stringify(INITIAL_DATA.allTimesheets)),
      timesheets: (parsed.timesheets && parsed.timesheets.length > 0) ? parsed.timesheets : JSON.parse(JSON.stringify(INITIAL_DATA.timesheets)),
      projectStages: (parsed.projectStages && parsed.projectStages.inProgress && parsed.projectStages.inProgress.length > 0) ? parsed.projectStages : JSON.parse(JSON.stringify(INITIAL_DATA.projectStages)),
      sprints: (parsed.sprints && parsed.sprints.active && parsed.sprints.active.length > 0) ? parsed.sprints : JSON.parse(JSON.stringify(INITIAL_DATA.sprints)),
      userStories: (parsed.userStories && parsed.userStories.backlogs && parsed.userStories.backlogs.length > 0) ? parsed.userStories : JSON.parse(JSON.stringify(INITIAL_DATA.userStories)),
      employees: (parsed.employees && parsed.employees.length > 0) ? parsed.employees : JSON.parse(JSON.stringify(INITIAL_DATA.employees)),
      departments: (parsed.departments && parsed.departments.length > 0) ? parsed.departments : JSON.parse(JSON.stringify(INITIAL_DATA.departments)),
      attendances: (parsed.attendances && parsed.attendances.length > 0) ? parsed.attendances : JSON.parse(JSON.stringify(INITIAL_DATA.attendances)),
      leaveAllocations: (parsed.leaveAllocations && parsed.leaveAllocations.length > 0) ? parsed.leaveAllocations : JSON.parse(JSON.stringify(INITIAL_DATA.leaveAllocations)),
      timeOffRequests: (parsed.timeOffRequests && parsed.timeOffRequests.length > 0) ? parsed.timeOffRequests : JSON.parse(JSON.stringify(INITIAL_DATA.timeOffRequests)),
      expenses: (parsed.expenses && parsed.expenses.length > 0) ? parsed.expenses : JSON.parse(JSON.stringify(INITIAL_DATA.expenses))
    };
    localStorage.setItem('office_pro_demo_state', JSON.stringify(merged));
    return merged;
  } catch (e) {
    console.warn('Error loading localStorage state, using INITIAL_DATA', e);
    return JSON.parse(JSON.stringify(INITIAL_DATA));
  }
}

let AppState = loadInitialState();

function saveState() {
  localStorage.setItem('office_pro_demo_state', JSON.stringify(AppState));
}

function resetDemoState() {
  localStorage.removeItem('office_pro_demo_state');
  AppState = JSON.parse(JSON.stringify(INITIAL_DATA));
  localStorage.setItem('office_pro_demo_state', JSON.stringify(AppState));
  renderAppView(currentView);
  alert('Demo data state reset to initial master seed successfully!');
}

// Router & View Management
let currentView = 'home';

function navigateTo(viewName, param = null) {
  currentView = viewName;
  closeAllPopovers();
  closeAppSwitcher();
  renderAppView(viewName, param);
}

// Digital Clock in Topbar & Simulator
function initClock() {
  function updateTime() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const clockEls = document.querySelectorAll('.live-clock-display');
    clockEls.forEach(el => el.textContent = timeStr);
  }
  setInterval(updateTime, 1000);
  updateTime();
}

// App Switcher Toggle
function toggleAppSwitcher() {
  if (currentView === 'home') {
    const input = document.getElementById('switcherSearchInput');
    if (input) input.focus();
  } else {
    navigateTo('home');
  }
}

function closeAppSwitcher() {
  // Legacy stub
}

// Live Apps Matrix Search Filter
function filterLandingApps(query) {
  const q = (query || '').toLowerCase().trim();
  const tiles = document.querySelectorAll('#landingAppsGrid .op-app-tile');
  tiles.forEach(tile => {
    const text = tile.innerText.toLowerCase();
    const keywords = (tile.getAttribute('data-keywords') || '').toLowerCase();
    if (!q || text.includes(q) || keywords.includes(q)) {
      tile.style.display = 'flex';
    } else {
      tile.style.display = 'none';
    }
  });
}

function handleLandingSearchKey(e) {
  if (e.key === 'Enter') {
    const visibleTiles = Array.from(document.querySelectorAll('#landingAppsGrid .op-app-tile')).filter(t => t.style.display !== 'none');
    if (visibleTiles.length > 0) {
      visibleTiles[0].click();
    }
  }
}

// Popovers
function togglePopover(popoverId) {
  const popover = document.getElementById(popoverId);
  const isShown = popover.classList.contains('show');
  closeAllPopovers();
  if (!isShown) popover.classList.add('show');
}

function closeAllPopovers() {
  document.querySelectorAll('.op-popover-panel').forEach(p => p.classList.remove('show'));
}

// Theme Switcher
function changeTheme(themeName) {
  AppState.theme = themeName;
  document.body.setAttribute('data-theme', themeName);
  saveState();
}

// Debug Mode Toggle
function toggleDebugMode() {
  AppState.debugMode = !AppState.debugMode;
  document.body.classList.toggle('debug-mode', AppState.debugMode);
  const btn = document.getElementById('debugToggleBtn');
  if (btn) btn.classList.toggle('active', AppState.debugMode);
  saveState();
}

// Main Render Dispatcher
function renderAppView(view, param) {
  const container = document.getElementById('mainContentArea');
  const breadcrumb = document.getElementById('topBreadcrumb');
  
  if (view === 'home') {
    breadcrumb.innerHTML = `<span class="op-breadcrumb-item">Office Pro Dashboard</span>`;
    container.innerHTML = renderHomeDashboard();
    setTimeout(() => {
      const input = document.getElementById('switcherSearchInput');
      if (input) input.focus();
    }, 40);
  } else if (view === 'employee') {
    if (param === 'departments') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('employee')" class="op-breadcrumb-item">Employees</a> &gt; <span class="op-breadcrumb-item">Departments</span>`;
    } else if (param && param.startsWith('EMP')) {
      const e = AppState.employees.find(x => x.id === param);
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('employee')" class="op-breadcrumb-item">Employees</a> &gt; <span class="op-breadcrumb-item">${e ? e.name : param}</span>`;
    } else {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Employees (hr.employee)</span>`;
    }
    container.innerHTML = renderEmployeeView(param);
  } else if (view === 'project') {
    if (param === 'sprints') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('project')" class="op-breadcrumb-item">Projects</a> &gt; <span class="op-breadcrumb-item">Sprints - Smart Transit Infrastructure</span>`;
    } else if (param === 'sprint-board' || param === 'sprint-stories') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('project')" class="op-breadcrumb-item">Projects</a> &gt; <a href="javascript:navigateTo('project', 'sprints')" class="op-breadcrumb-item">Sprints</a> &gt; <span class="op-breadcrumb-item">Transit Infrastructure Sprint 2</span>`;
    } else if (param === 'pending-approvals') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('project')" class="op-breadcrumb-item">Projects</a> &gt; <span class="op-breadcrumb-item">Pending Timesheet Approvals</span>`;
    } else if (param && param.startsWith('PRJ')) {
      const p = AppState.projects.find(x => x.id === param);
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('project')" class="op-breadcrumb-item">Projects</a> &gt; <span class="op-breadcrumb-item">${p ? p.name : param}</span>`;
    } else {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Projects &amp; Sprints (project.project)</span>`;
    }
    container.innerHTML = renderProjectView(param);
  } else if (view === 'timesheet') {
    if (param === 'grid') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('timesheet')" class="op-breadcrumb-item">Timesheets</a> &gt; <span class="op-breadcrumb-item">Weekly Timesheet Engine (8-Hour Validation)</span>`;
      container.innerHTML = renderTimesheetWeeklyGridView();
    } else {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Timesheets (account.analytic.line)</span>`;
      container.innerHTML = renderTimesheetView(param);
    }
  } else if (view === 'attendance') {
    if (param === 'biometric' || param === 'biometric-form') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('attendance')" class="op-breadcrumb-item">Attendances</a> &gt; <span class="op-breadcrumb-item">Biometric Devices</span>`;
    } else if (param === 'kiosk') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('attendance')" class="op-breadcrumb-item">Attendances</a> &gt; <span class="op-breadcrumb-item">Kiosk Mode</span>`;
    } else if (param && param.startsWith('absence')) {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('attendance')" class="op-breadcrumb-item">Attendances</a> &gt; <span class="op-breadcrumb-item">Absence Tracking</span>`;
    } else {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Attendances (hr.attendance)</span>`;
    }
    container.innerHTML = renderAttendanceView(param);
  } else if (view === 'leave') {
    if (param === 'my-time-off') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('leave')" class="op-breadcrumb-item">Time Off</a> &gt; <span class="op-breadcrumb-item">My Time Off</span>`;
    } else if (param === 'management-approvals') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('leave')" class="op-breadcrumb-item">Time Off</a> &gt; <span class="op-breadcrumb-item">Management &gt; Time Off</span>`;
    } else if (param === 'management-allocations') {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <a href="javascript:navigateTo('leave')" class="op-breadcrumb-item">Time Off</a> &gt; <span class="op-breadcrumb-item">Management &gt; Allocations</span>`;
    } else {
      breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Time Off Dashboard (hr.leave)</span>`;
    }
    container.innerHTML = renderLeaveView(param);
  } else if (view === 'expense') {
    breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Expense Management (hr.expense)</span>`;
    container.innerHTML = renderExpenseView();
  } else if (view === 'accounting') {
    breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Accounting & Project Profitability</span>`;
    container.innerHTML = renderAccountingView();
  } else if (view === 'mail') {
    breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Webmail Suite (mail.mail)</span>`;
    container.innerHTML = renderMailView(param);
  } else if (view === 'apps') {
    breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Apps</a> &gt; <span class="op-breadcrumb-item">Apps Store & Custom Modules (ir.module.module)</span>`;
    container.innerHTML = renderAppsStoreView();
  } else if (view === 'technical') {
    breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Settings</a> &gt; <span class="op-breadcrumb-item">Technical Metadata Registry (ir.*)</span>`;
    container.innerHTML = renderTechnicalView();
  } else if (view === 'defense') {
    breadcrumb.innerHTML = `<a href="javascript:navigateTo('home')" class="op-breadcrumb-item">Guide & HOD Defense</a> &gt; <span class="op-breadcrumb-item">Presentation Q&A & Viva Cheatsheet</span>`;
    container.innerHTML = renderDefenseView();
  }
}

// -------------------------------------------------------------
// View Renderers
// -------------------------------------------------------------

// 1. Home / Apps Matrix Landing Page
function renderHomeDashboard() {
  return `
    <div class="op-landing-view">
      <!-- Centered App Search Bar -->
      <div class="op-switcher-search">
        <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
        <input type="text" id="switcherSearchInput" placeholder="Search applications, actions, or settings..." autocomplete="off" oninput="filterLandingApps(this.value)" onkeydown="handleLandingSearchKey(event)">
      </div>

      <!-- 11 Apps Grid -->
      <div class="op-apps-grid" id="landingAppsGrid">
        <div class="op-app-tile" onclick="navigateTo('mail')" data-keywords="mail email webmail messages inbox communication smtp">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #0284c7, #0369a1);">
            ✉️
            <span class="op-app-badge-tag">mail</span>
          </div>
          <div class="op-app-name">Webmail</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('employee')" data-keywords="employees hr employee staff directory ctc approver matrix">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #714b67, #583750);">
            👥
            <span class="op-app-badge-tag">hr</span>
          </div>
          <div class="op-app-name">Employees</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('project')" data-keywords="projects project architecture area square feet tasks milestone">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #d97706, #b45309);">
            📊
            <span class="op-app-badge-tag">project</span>
          </div>
          <div class="op-app-name">Projects</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('timesheet')" data-keywords="timesheets timesheet weekly 8-hr 8hr daily log validation hours grid">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #059669, #047857);">
            ⏱️
            <span class="op-app-badge-tag">8-hr</span>
          </div>
          <div class="op-app-name">Timesheets</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('attendance')" data-keywords="attendance punch biometric kiosk net hours regularization logs clock">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #10b981, #059669);">
            🕒
            <span class="op-app-badge-tag">biometric</span>
          </div>
          <div class="op-app-name">Attendance</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('leave')" data-keywords="leaves leave vacation sick comp-off flexible 2-tier approval holiday">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #00a09d, #00817e);">
            🏖️
            <span class="op-app-badge-tag">2-tier</span>
          </div>
          <div class="op-app-name">Leaves</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('expense')" data-keywords="expenses expense claims reimbursement receipts bills overhead claims">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #ea580c, #c2410c);">
            💳
            <span class="op-app-badge-tag">claims</span>
          </div>
          <div class="op-app-name">Expenses</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('accounting')" data-keywords="accounting gst invoice tax profitability gross margin ctc revenue billing finance">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #4f46e5, #4338ca);">
            💰
            <span class="op-app-badge-tag">GST</span>
          </div>
          <div class="op-app-name">Accounting</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('apps')" data-keywords="apps appstore modules addons ir.module.module installed custom store plugins store">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #0f766e, #115e59);">
            📦
            <span class="op-app-badge-tag">11 custom</span>
          </div>
          <div class="op-app-name">Apps</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('technical')" data-keywords="settings technical ir.model ir.cron ir.rule metadata system engine debug">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #334155, #1e293b);">
            ⚙️
            <span class="op-app-badge-tag">ir.*</span>
          </div>
          <div class="op-app-name">Settings</div>
        </div>

        <div class="op-app-tile" onclick="navigateTo('defense')" data-keywords="viva defense guide hod presentation questions 5w1h viva cheat cheat sheet">
          <div class="op-app-icon-box" style="background: linear-gradient(135deg, #9333ea, #7e22ce); border: 2px solid #38bdf8;">
            🎓
            <span class="op-app-badge-tag">Guide/HOD</span>
          </div>
          <div class="op-app-name">Viva Defense</div>
        </div>
      </div>
    </div>
  `;
}

// 2. Employee Module (Kanban Cards Grid, Form Sheet & Departments)
function renderEmployeeView(param = null) {
  if (param === 'departments') {
    return renderEmployeeDepartmentsView();
  }
  if (param && param.startsWith('EMP')) {
    return renderEmployeeDetailView(param);
  }
  return renderEmployeeKanbanView();
}

function renderEmployeeKanbanView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      <div class="op-subbar">
        <span class="op-subbar-item active" onclick="navigateTo('employee')">Employees</span>
        <span class="op-subbar-item" onclick="navigateTo('employee', 'departments')">Departments</span>
        <span class="op-subbar-item" onclick="navigateTo('leave')">Payroll Leave Summary</span>
        <span class="op-subbar-item" onclick="navigateTo('employee', 'EMP001')">Org Chart</span>
        <span class="op-subbar-item" onclick="alert('Reporting: Employee headcount & turnover analytics')">Reporting</span>
        <span class="op-subbar-item" onclick="navigateTo('technical')">Configuration</span>
      </div>

      <!-- Control Bar -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Create New Employee Form Sheet')">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>Employees</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;" title="Employee Settings">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 260px;">
            <span>🔍</span>
            <input type="text" id="employeeSearchInput" placeholder="Search..." oninput="filterEmployeeCards(this.value)">
          </div>
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1-${AppState.employees.length} / ${AppState.employees.length}
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn active" title="Kanban Cards" onclick="navigateTo('employee')">🗂️</button>
            <button class="op-view-btn" title="List Table" onclick="alert('Switching to List Table View')">📋</button>
            <button class="op-view-btn" title="Departments Grid" onclick="navigateTo('employee', 'departments')">🏢</button>
            <button class="op-view-btn" title="Organization Hierarchy" onclick="navigateTo('employee', 'EMP001')">🌳</button>
          </div>
        </div>
      </div>

      <!-- 4-Column Kanban Grid Matching Image 1 -->
      <div class="op-emp-grid" id="employeeKanbanGrid">
        ${AppState.employees.map(e => `
          <div class="op-emp-card" onclick="navigateTo('employee', '${e.id}')">
            <!-- Left Large Avatar Tile -->
            <div class="op-emp-avatar-tile" style="background-color: ${e.avatarColor || '#0284c7'};">
              ${e.avatarLetter || e.name[0]}
            </div>

            <!-- Right Details Info -->
            <div class="op-emp-info">
              <div>
                <div class="op-emp-name-row">
                  <span class="op-emp-name" title="${e.name}">${e.name}</span>
                  <span class="op-presence-dot ${e.online ? 'online' : 'offline'}" title="${e.online ? 'Online / Present' : 'Offline / Off-Hours'}"></span>
                </div>
                <div class="op-emp-meta-row" title="${e.email}">
                  <span>✉️</span>
                  <span style="overflow: hidden; text-overflow: ellipsis;">${e.email}</span>
                </div>
                ${e.phone ? `
                  <div class="op-emp-meta-row">
                    <span>📞</span>
                    <span>${e.phone}</span>
                  </div>
                ` : ''}
                <div class="op-emp-meta-row">
                  <span>💼</span>
                  <span>${e.hireDate || 'Apr 1'}</span>
                </div>
              </div>

              <div style="display: flex; justify-content: space-between; align-items: flex-end;">
                <span class="op-emp-badge">${e.tag || 'Employee'}</span>
                <div class="op-emp-footer-icons">
                  <span class="op-emp-mini-avatar" style="background-color: ${e.avatarColor || '#0284c7'};">${e.avatarLetter || e.name[0]}</span>
                  <span style="font-size: 11px; color: #94a3b8;" title="Schedule Next Activity">🕒</span>
                </div>
              </div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function renderEmployeeDetailView(empId) {
  const emp = AppState.employees.find(e => e.id === empId) || AppState.employees[0];
  const reportingMgr = AppState.employees.find(e => e.name === emp.reportingManager) || { name: 'Alex Morgan (Director)', avatarColor: '#b45309', avatarLetter: 'A' };

  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      <div class="op-subbar">
        <span class="op-subbar-item" onclick="navigateTo('employee')">Employees</span>
        <span class="op-subbar-item" onclick="navigateTo('employee', 'departments')">Departments</span>
        <span class="op-subbar-item" onclick="navigateTo('leave')">Payroll Leave Summary</span>
        <span class="op-subbar-item" onclick="alert('Reporting')">Reporting</span>
        <span class="op-subbar-item" onclick="navigateTo('technical')">Configuration</span>
      </div>

      <!-- Control Bar -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="navigateTo('employee')">← Back to Directory</button>
          <div class="op-control-title" style="font-size: 15px;">
            <a href="javascript:navigateTo('employee')" style="color: var(--primary); text-decoration: none;">Employees</a>
            <span style="color: #94a3b8; margin: 0 4px;">/</span>
            <span style="font-weight: 700;">${emp.name}</span>
            <span style="font-size: 12px; color: #64748b; margin-left: 6px;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <button class="op-btn op-btn-secondary" onclick="alert('Simulation: Launch Plan wizard initialized for ${emp.name}')">Launch Plan</button>
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1 / ${AppState.employees.length}
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" onclick="navigateTo('employee')">&lt;</button>
            <button class="op-view-btn" onclick="navigateTo('employee')">&gt;</button>
          </div>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 1fr 340px; gap: 16px;">
        <!-- Left White Sheet Form Card (Image 2) -->
        <div class="op-sheet" style="padding: 24px; margin: 0;">
          
          <!-- Smart Ribbon (7 Buttons Matching Image 2) -->
          <div class="op-smart-ribbon">
            <div class="op-smart-btn" onclick="navigateTo('leave')" title="Time Off Allocation">
              <span class="op-smart-btn-icon" style="color: #6366f1;">📅</span>
              <div class="op-smart-btn-text">
                <span>Time Off</span>
                <span class="op-smart-btn-val">31/38 Days</span>
              </div>
            </div>

            <div class="op-smart-btn" onclick="navigateTo('timesheet')" title="Timesheets Logged">
              <span class="op-smart-btn-icon" style="color: #059669;">⏱️</span>
              <div class="op-smart-btn-text">
                <span>Timesheets</span>
                <span class="op-smart-btn-val">8-Hr Valid</span>
              </div>
            </div>

            <div class="op-smart-btn" title="Monthly Working Hours">
              <span class="op-smart-btn-icon" style="color: #0284c7;">🕒</span>
              <div class="op-smart-btn-text">
                <span>Monthly Hours</span>
                <span class="op-smart-btn-val">160:00</span>
              </div>
            </div>

            <div class="op-smart-btn" title="Connected Contacts">
              <span class="op-smart-btn-icon" style="color: #475569;">👥</span>
              <div class="op-smart-btn-text">
                <span>Contacts</span>
                <span class="op-smart-btn-val">1</span>
              </div>
            </div>

            <div class="op-smart-btn" title="Version History">
              <span class="op-smart-btn-icon" style="color: #475569;">🗂️</span>
              <div class="op-smart-btn-text">
                <span>History</span>
                <span class="op-smart-btn-val">2</span>
              </div>
            </div>

            <div class="op-smart-btn" onclick="navigateTo('leave')" title="Leave Ledger Report">
              <span class="op-smart-btn-icon" style="color: #d97706;">📊</span>
              <div class="op-smart-btn-text">
                <span>Leave Report</span>
              </div>
            </div>

            <div class="op-smart-btn" title="Performance Reviews">
              <span class="op-smart-btn-icon" style="color: #7e22ce;">📈</span>
              <div class="op-smart-btn-text">
                <span>Performance</span>
              </div>
            </div>
          </div>

          <!-- Identity Row (Image 2) -->
          <div style="display: flex; gap: 20px; align-items: flex-start; margin-bottom: 24px;">
            <div class="op-emp-avatar-tile" style="width: 85px; min-width: 85px; height: 85px; border-radius: 8px; background-color: ${emp.avatarColor || '#0284c7'}; font-size: 38px;">
              ${emp.avatarLetter || emp.name[0]}
            </div>

            <div style="flex: 1;">
              <div style="display: flex; justify-content: space-between; align-items: center;">
                <h1 style="font-size: 26px; font-weight: 700; color: var(--text-main); margin-bottom: 6px;">${emp.name}</h1>
                <span style="font-size: 11.5px; background: #f1f5f9; padding: 3px 8px; border-radius: 12px; color: #64748b; font-weight: 600;">
                  ● ${emp.online ? 'Active' : 'Off-Hours'}
                </span>
              </div>

              <div style="display: flex; flex-direction: column; gap: 4px; font-size: 13px; color: #475569;">
                <div>✉️ <a href="mailto:${emp.email}" style="color: var(--primary); text-decoration: none;">${emp.email}</a></div>
                <div>📞 Work Phone: <b>${emp.phone}</b></div>
                <div>📱 Work Mobile: <b>${emp.mobile || emp.phone}</b></div>
              </div>

              <div style="margin-top: 8px;">
                <span class="op-emp-badge" style="background: #fee2e2; color: #991b1b; font-size: 11px; padding: 2px 8px;">${emp.tag || 'Employee'} ✕</span>
              </div>
            </div>
          </div>

          <!-- Tabs (Work, Approvers Matrix & CTC, Personal, Payroll, Settings) -->
          <div class="op-status-pipeline" style="margin-bottom: 20px;">
            <div class="op-pipeline-step active" onclick="switchEmpTab('workTab')">Work</div>
            <div class="op-pipeline-step" onclick="switchEmpTab('approversTab')">Approver Matrix & CTC</div>
            <div class="op-pipeline-step" onclick="switchEmpTab('personalTab')">Personal Info</div>
            <div class="op-pipeline-step" onclick="switchEmpTab('payrollTab')">Payroll & Bank</div>
            <div class="op-pipeline-step" onclick="switchEmpTab('settingsTab')">Settings</div>
          </div>

          <!-- WORK TAB CONTENT -->
          <div id="workTabContent">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px;">
              <!-- Left Column: Work Info -->
              <div>
                <h4 style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase; margin-bottom: 12px;">WORK</h4>
                
                <div class="op-form-group">
                  <label class="op-form-label">Company</label>
                  <input class="op-form-input" value="Office Pro Solutions Ltd" readonly>
                </div>

                <div class="op-form-group">
                  <label class="op-form-label">Department</label>
                  <input class="op-form-input" value="${emp.dept}" readonly>
                </div>

                <div class="op-form-group">
                  <label class="op-form-label">Job Position</label>
                  <input class="op-form-input" value="${emp.role}" readonly>
                </div>

                <div class="op-form-group">
                  <label class="op-form-label">Manager</label>
                  <input class="op-form-input" value="${emp.reportingManager}" readonly>
                </div>

                <div class="op-form-group">
                  <label class="op-form-label">Working Hours</label>
                  <input class="op-form-input" value="Standard 40 hours/week (8 net hrs/day)" readonly>
                </div>
              </div>

              <!-- Right Column: Organization Chart Tree (Image 2) -->
              <div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                  <h4 style="font-size: 12px; font-weight: 700; color: #64748b; text-transform: uppercase;">ORGANIZATION CHART</h4>
                  <a href="javascript:alert('Full Org Tree View')" style="font-size: 11.5px; color: var(--primary); font-weight: 600; text-decoration: none;">🌳 FULL CHART</a>
                </div>

                <div class="op-org-chart">
                  <!-- Level 1: Director -->
                  <div class="op-org-node">
                    <div class="op-org-node-avatar" style="background: #b45309;">A</div>
                    <div>
                      <div style="font-weight: 700; font-size: 13px;">Alex Morgan</div>
                      <div style="font-size: 11px; color: #64748b;">Executive Director</div>
                    </div>
                  </div>

                  <div class="op-org-tree-line"></div>

                  <!-- Level 2: Manager (if not direct) -->
                  ${emp.reportingManager !== 'None (Board of Directors)' && emp.name !== 'Alex Morgan' ? `
                    <div class="op-org-node">
                      <div class="op-org-node-avatar" style="background: ${reportingMgr.avatarColor || '#0284c7'};">
                        ${reportingMgr.avatarLetter || reportingMgr.name[0]}
                      </div>
                      <div>
                        <div style="font-weight: 700; font-size: 13px;">${emp.reportingManager}</div>
                        <div style="font-size: 11px; color: #64748b;">Reporting Manager</div>
                      </div>
                    </div>
                    <div class="op-org-tree-line"></div>
                  ` : ''}

                  <!-- Current Employee Node (Highlighted) -->
                  <div class="op-org-node highlight">
                    <div class="op-org-node-avatar" style="background: ${emp.avatarColor || '#0284c7'};">
                      ${emp.avatarLetter || emp.name[0]}
                    </div>
                    <div>
                      <div style="font-weight: 700; font-size: 13px; color: var(--primary);">${emp.name} (Current)</div>
                      <div style="font-size: 11px; color: #64748b;">${emp.role}</div>
                    </div>
                  </div>
                </div>

                <!-- 2-Tier Approvers & Hourly CTC Callout -->
                <div style="margin-top: 16px; background: #f1f5f9; padding: 12px; border-radius: 6px; border: 1px solid #cbd5e1;">
                  <div style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase;">Real-Time Labor Costing & Approvers</div>
                  <div style="font-size: 15px; font-weight: 700; color: var(--primary); margin: 4px 0;">Hourly CTC: ₹ ${emp.hourlyCtc} / hr</div>
                  <div style="font-size: 11.5px; color: #64748b;">• Timesheet Approver: <b>${emp.timesheetApprover}</b></div>
                  <div style="font-size: 11.5px; color: #64748b;">• 2-Tier Leave: L1 (${emp.leaveL1}) ➔ L2 (${emp.leaveL2})</div>
                  <div style="font-size: 11.5px; color: #64748b;">• 2-Tier Expense: L1 (${emp.expenseL1}) ➔ L2 (${emp.expenseL2})</div>
                </div>
              </div>
            </div>
          </div>

          <div style="margin-top: 20px; padding-top: 16px; border-top: 1px solid var(--border-color); display: flex; justify-content: flex-end; gap: 10px;">
            <button class="op-btn op-btn-secondary" onclick="alert('Simulation: Exporting Master Profile PDF')">📄 Print Master Card</button>
            <button class="op-btn op-btn-primary" onclick="alert('Simulation: Profile changes saved!')">Save Changes</button>
          </div>
        </div>

        <!-- Right Chatter & History Audit Pane (Matching Image 2) -->
        <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 16px;">
          <div style="display: flex; gap: 6px; margin-bottom: 16px;">
            <button class="op-btn op-btn-sm op-btn-primary" onclick="alert('Simulation: Open compose message popup')">Send message</button>
            <button class="op-btn op-btn-sm op-btn-secondary" onclick="alert('Simulation: Add internal audit note')">Log note</button>
            <button class="op-btn op-btn-sm op-btn-secondary" onclick="alert('Simulation: Schedule new activity')">Activity</button>
          </div>

          <div style="border-top: 1px solid #e2e8f0; padding-top: 12px;">
            <div style="font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 10px;">Audit History & Activities</div>

            <div style="display: flex; gap: 10px; margin-bottom: 14px;">
              <div style="width: 28px; height: 28px; border-radius: 4px; background: #059669; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">AD</div>
              <div style="font-size: 12px; color: #475569;">
                <b>Admin User</b> <span style="font-size: 10.5px; color: #94a3b8;">Today, 10:30 AM</span>
                <div>Standard 40 hours/week working schedule verified.</div>
              </div>
            </div>

            <div style="display: flex; gap: 10px; margin-bottom: 14px;">
              <div style="width: 28px; height: 28px; border-radius: 4px; background: #7e22ce; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">HR</div>
              <div style="font-size: 12px; color: #475569;">
                <b>Anjali Desai (HR)</b> <span style="font-size: 10.5px; color: #94a3b8;">Apr 1, 2026</span>
                <div>Employee master profile initialized under <b>${emp.dept}</b>.</div>
              </div>
            </div>

            <div style="display: flex; gap: 10px;">
              <div style="width: 28px; height: 28px; border-radius: 4px; background: #0284c7; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 12px;">SYS</div>
              <div style="font-size: 12px; color: #475569;">
                <b>System Engine</b> <span style="font-size: 10.5px; color: #94a3b8;">Apr 1, 2026</span>
                <div>Biometric punch card and 2-tier approval flow mapped.</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderEmployeeDepartmentsView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      <div class="op-subbar">
        <span class="op-subbar-item" onclick="navigateTo('employee')">Employees</span>
        <span class="op-subbar-item active" onclick="navigateTo('employee', 'departments')">Departments</span>
        <span class="op-subbar-item" onclick="navigateTo('leave')">Payroll Leave Summary</span>
        <span class="op-subbar-item" onclick="alert('Reporting')">Reporting</span>
        <span class="op-subbar-item" onclick="navigateTo('technical')">Configuration</span>
      </div>

      <!-- Control Bar -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Create New Department Wizard')">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>Departments</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 260px;">
            <span>🔍</span>
            <input type="text" placeholder="Search departments...">
          </div>
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1-${AppState.departments.length} / ${AppState.departments.length}
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" title="Employees Kanban" onclick="navigateTo('employee')">🗂️</button>
            <button class="op-view-btn active" title="Departments Grid" onclick="navigateTo('employee', 'departments')">🏢</button>
          </div>
        </div>
      </div>

      <!-- 3-Column Departments Kanban Grid Matching Image 3 -->
      <div class="op-dept-grid">
        ${AppState.departments.map(d => `
          <div class="op-dept-card" style="border-left-color: ${d.color};" onclick="navigateTo('employee')">
            <div>
              <h3 style="font-size: 16px; font-weight: 700; color: var(--text-main); margin-bottom: 8px;">${d.name}</h3>
              <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                <div style="width: 22px; height: 22px; border-radius: 4px; background: ${d.color}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold;">
                  ${d.manager[0]}
                </div>
                <span style="font-size: 13px; font-weight: 600; color: #475569;">${d.manager}</span>
              </div>
              <div style="font-size: 11.5px; color: #64748b;">
                🏢 ${d.company}
              </div>
            </div>

            <div style="margin-top: 14px;">
              <span class="op-btn op-btn-sm op-btn-secondary" style="background: var(--primary-subtle); color: var(--primary); font-weight: bold;">
                ${d.count} Employees
              </span>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function filterEmployeeCards(query) {
  const q = (query || '').toLowerCase().trim();
  const cards = document.querySelectorAll('#employeeKanbanGrid .op-emp-card');
  cards.forEach(card => {
    const text = card.innerText.toLowerCase();
    if (!q || text.includes(q)) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });
}

function switchEmpTab(tabId) {
  alert(`Tab Switch: Viewing ${tabId} details.`);
}

// -------------------------------------------------------------
// 3. Project & Sprints Module (Kanban Stages, Sprints & User Stories)
// -------------------------------------------------------------

function renderProjectView(param = null) {
  if (param === 'sprints') {
    return renderProjectSprintsView();
  }
  if (param === 'sprint-board' || param === 'sprint-stories') {
    return renderSprintUserStoriesBoardView();
  }
  if (param === 'pending-approvals') {
    return renderPendingTimesheetApprovalsView();
  }
  if (param && param.startsWith('PRJ')) {
    return renderProjectDetailView(param);
  }
  return renderProjectKanbanStagesView();
}

function renderProjectSubbar(activeTab = 'projects') {
  return `
    <div class="op-subbar">
      <span class="op-subbar-item ${activeTab === 'projects' ? 'active' : ''}" onclick="navigateTo('project')">Projects</span>
      <span class="op-subbar-item ${activeTab === 'tasks' ? 'active' : ''}" onclick="navigateTo('project', 'sprint-board')">Tasks</span>
      <span class="op-subbar-item ${activeTab === 'sprints' ? 'active' : ''}" onclick="navigateTo('project', 'sprints')">Sprints</span>
      <span class="op-subbar-item" onclick="alert('Project Reporting: Margin analysis, burn rate, and deliverable pacing')">Reporting</span>
      <span class="op-subbar-item ${activeTab === 'pending-approvals' ? 'active' : ''}" style="color: #f59e0b; font-weight: 700;" onclick="navigateTo('project', 'pending-approvals')">⚠️ Pending Timesheet Approvals</span>
      <span class="op-subbar-item" onclick="navigateTo('technical')">Configuration</span>
      <span class="op-subbar-item" onclick="alert('Timesheet Audit Log: 412 entries timestamped and immutable')">Timesheet Audit Log</span>
    </div>
  `;
}

// 3.1 Main Projects Kanban Stages View Matching Image 1
function renderProjectKanbanStagesView() {
  const stages = AppState.projectStages || { notStarted: [], inProgress: [], finalPhase: [], closed: [] };
  const totalProjects = stages.notStarted.length + stages.inProgress.length + stages.finalPhase.length + stages.closed.length;

  return `
    <div style="max-width: 1350px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderProjectSubbar('projects')}

      <!-- Control Bar Matching Image 1 -->
      <div class="op-control-bar" style="margin-bottom: 14px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Create New Project Wizard')">New</button>
          <div class="op-control-title" style="font-size: 16px; display: flex; align-items: center; gap: 6px;">
            <span>Projects</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;" title="Project Settings">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <!-- Search Box with Yellow Filter Chip Matching Image 1 -->
          <div class="op-search-box" style="width: 330px; display: flex; align-items: center; background: #ffffff; padding: 4px 10px; border: 1px solid #cbd5e1; border-radius: 4px;">
            <span class="op-filter-chip">
              ★ My Projects <span class="op-filter-chip-remove" onclick="clearProjectFilter(event)" title="Clear filter">✕</span>
            </span>
            <input type="text" id="projectSearchInput" placeholder="Search..." oninput="filterProjectCards(this.value)" style="border: none; outline: none; background: transparent; flex: 1; font-size: 13px;">
            <span style="color: #64748b; font-size: 10px; margin-left: 4px; cursor: pointer;">▼</span>
          </div>
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1-${totalProjects} / ${totalProjects}
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" onclick="alert('Previous page')">&lt;</button>
            <button class="op-view-btn" onclick="alert('Next page')">&gt;</button>
            <button class="op-view-btn active" title="Kanban Board" onclick="navigateTo('project')">🗂️</button>
            <button class="op-view-btn" title="List View" onclick="navigateTo('project', 'PRJ/2026/001')">📋</button>
            <button class="op-view-btn" title="Calendar View" onclick="navigateTo('leave')">📅</button>
            <button class="op-view-btn" title="Activities View" onclick="togglePopover('activitiesPopover')">⏱️</button>
          </div>
        </div>
      </div>

      <!-- 4-Column Stages Kanban Board Matching Image 1 -->
      <div class="op-kanban-board" id="projectKanbanBoard">
        <!-- Stage 1: Not Started -->
        <div class="op-kanban-column">
          <div class="op-kanban-col-header">
            <span>Not Started (${stages.notStarted.length})</span>
            <div class="op-kanban-col-count">
              <span class="op-kanban-col-add" onclick="alert('Add project in Not Started stage')">+</span>
              <span>${stages.notStarted.length}</span>
            </div>
          </div>
          <div class="op-kanban-col-bar"></div>
          <div class="op-kanban-col-body">
            ${stages.notStarted.map(p => `
              <div class="op-project-kcard" onclick="navigateTo('project', '${p.id === 'PRJ006' ? 'sprints' : p.id}')">
                <div class="op-project-kcard-title">
                  <span style="color: #94a3b8; cursor: pointer;" onclick="event.stopPropagation(); this.style.color = this.style.color === 'rgb(245, 158, 11)' ? '#94a3b8' : '#f59e0b';">☆</span>
                  <span title="${p.name}">${p.name}</span>
                </div>
                <div class="op-project-kcard-footer">
                  <div><b>${p.sprintsCount} Sprints</b> ⏱️</div>
                  <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 20px; height: 20px; border-radius: 50%; background: ${p.avatarColor || '#0d9488'}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">
                      ${p.avatar}
                    </div>
                    <span style="width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid #cbd5e1; background: #fff;"></span>
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Stage 2: In Progress -->
        <div class="op-kanban-column" style="width: 320px; min-width: 320px;">
          <div class="op-kanban-col-header">
            <span>In Progress (${stages.inProgress.length})</span>
            <div class="op-kanban-col-count">
              <span class="op-kanban-col-add" onclick="alert('Add project in In Progress stage')">+</span>
              <span>${stages.inProgress.length}</span>
            </div>
          </div>
          <div class="op-kanban-col-bar"></div>
          <div class="op-kanban-col-body">
            ${stages.inProgress.map(p => `
              <div class="op-project-kcard" onclick="navigateTo('project', '${p.id === 'PRJ006' ? 'sprints' : p.id}')">
                <div class="op-project-kcard-title">
                  <span style="color: ${p.id === 'PRJ007' || p.id === 'PRJ006' ? '#f59e0b' : '#94a3b8'}; cursor: pointer;" onclick="event.stopPropagation(); this.style.color = this.style.color === 'rgb(245, 158, 11)' ? '#94a3b8' : '#f59e0b';">☆</span>
                  <span title="${p.name}">${p.name}</span>
                </div>
                <div class="op-project-kcard-footer">
                  <div><b>${p.sprintsCount} Sprints</b> ⏱️</div>
                  <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 20px; height: 20px; border-radius: 50%; background: ${p.avatarColor || '#0d9488'}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">
                      ${p.avatar}
                    </div>
                    <span style="width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid #cbd5e1; background: #fff;"></span>
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Stage 3: Final Phase -->
        <div class="op-kanban-column">
          <div class="op-kanban-col-header">
            <span>Final Phase (80% Completion) (0)</span>
            <div class="op-kanban-col-count">
              <span class="op-kanban-col-add" onclick="alert('Add project in Final Phase stage')">+</span>
              <span>0</span>
            </div>
          </div>
          <div class="op-kanban-col-bar"></div>
          <div class="op-kanban-col-body" style="display: flex; align-items: center; justify-content: center; color: #94a3b8; font-size: 12px; font-style: italic;">
            No projects in this stage
          </div>
        </div>

        <!-- Stage 4: Closed -->
        <div class="op-kanban-column">
          <div class="op-kanban-col-header">
            <span>Closed (${stages.closed.length})</span>
            <div class="op-kanban-col-count">
              <span class="op-kanban-col-add" onclick="alert('Add project in Closed stage')">+</span>
              <span>${stages.closed.length}</span>
            </div>
          </div>
          <div class="op-kanban-col-bar"></div>
          <div class="op-kanban-col-body">
            ${stages.closed.map(p => `
              <div class="op-project-kcard" onclick="navigateTo('project', '${p.id}')">
                <div class="op-project-kcard-title">
                  <span style="color: #94a3b8; cursor: pointer;" onclick="event.stopPropagation(); this.style.color = this.style.color === 'rgb(245, 158, 11)' ? '#94a3b8' : '#f59e0b';">☆</span>
                  <span title="${p.name}">${p.name}</span>
                </div>
                <div class="op-project-kcard-footer">
                  <div><b>${p.sprintsCount} Sprints</b> ⏱️</div>
                  <div style="display: flex; align-items: center; gap: 6px;">
                    <div style="width: 20px; height: 20px; border-radius: 50%; background: ${p.avatarColor || '#7c3aed'}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">
                      ${p.avatar}
                    </div>
                    <span style="width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid #cbd5e1; background: #fff;"></span>
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;
}

// 3.2 Sprints Kanban View Matching Image 2
function renderProjectSprintsView() {
  const spr = AppState.sprints || { active: [], planned: [], closed: [] };
  return `
    <div style="max-width: 1350px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderProjectSubbar('sprints')}

      <!-- Control Bar with Breadcrumbs Matching Image 2 -->
      <div class="op-control-bar" style="margin-bottom: 14px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Create New Sprint Wizard')">New</button>
          <div class="op-control-title" style="font-size: 15px; display: flex; align-items: center; gap: 4px;">
            <a href="javascript:navigateTo('project')" style="color: var(--primary); text-decoration: none; font-weight: 500;">Projects</a>
            <span style="color: #94a3b8; margin: 0 2px;">/</span>
            <span style="font-weight: 700;">Sprints - IoT - Smart Wearable</span>
            <span style="font-size: 12px; color: #64748b; margin-left: 6px; cursor: pointer;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 280px; display: flex; align-items: center; background: #ffffff; padding: 4px 10px; border: 1px solid #cbd5e1; border-radius: 4px;">
            <span style="color: #94a3b8; margin-right: 6px;">🔍</span>
            <input type="text" placeholder="Search..." style="border: none; outline: none; background: transparent; flex: 1; font-size: 13px;">
            <span style="color: #64748b; font-size: 10px; margin-left: 4px; cursor: pointer;">▼</span>
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn active" title="Sprints Kanban" onclick="navigateTo('project', 'sprints')">🗂️</button>
            <button class="op-view-btn" title="Sprint User Stories" onclick="navigateTo('project', 'sprint-board')">📌</button>
          </div>
        </div>
      </div>

      <!-- Sprints Kanban Columns Matching Image 2 -->
      <div class="op-kanban-board">
        <!-- Active Column -->
        <div class="op-kanban-column" style="width: 380px; min-width: 380px;">
          <div class="op-kanban-col-header">
            <span>Active (${spr.active.length})</span>
            <span class="op-kanban-col-add" onclick="alert('Add Active Sprint')">+</span>
          </div>
          <div class="op-kanban-col-bar"></div>
          <div class="op-kanban-col-body">
            ${spr.active.map(s => `
              <div class="op-sprint-kcard">
                <div class="op-sprint-kcard-header">
                  <span style="font-family: monospace; font-size: 11px; color: #94a3b8;">${s.code}</span>
                  <span style="font-size: 11px; color: #94a3b8;">${s.project}</span>
                </div>
                <div class="op-sprint-kcard-title" onclick="navigateTo('project', 'sprint-board')">
                  ${s.name}
                </div>
                <div class="op-sprint-kcard-dates" style="color: #64748b; font-size: 12px; margin-bottom: 12px;">${s.dates}</div>

                <div class="op-sprint-prog-bar" style="height: 10px; background: #e2e8f0; border-radius: 2px; margin-bottom: 4px;">
                  <div class="op-sprint-prog-fill" style="width: ${s.pct}%; height: 100%;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #64748b; font-weight: 600; margin-bottom: 12px;">
                  <span>${s.pts}</span>
                  <b>${s.pct}%</b>
                </div>

                <div class="op-sprint-badge-row" style="display: flex; gap: 8px; margin-bottom: 14px;">
                  <span class="op-badge-left" style="background: #f59e0b; color: #fff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">${s.daysLeft}</span>
                  <span class="op-badge-offtrack" style="background: #dc2626; color: #fff; font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 4px;">${s.status}</span>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 10px;">
                  <button class="op-btn op-btn-sm op-btn-secondary" style="font-size: 11.5px; padding: 3px 10px;" onclick="navigateTo('project', 'sprint-board')">Edit</button>
                  <div style="width: 22px; height: 22px; border-radius: 4px; background: ${s.avatarColor || '#0d9488'}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold;">
                    ${s.avatar}
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>

        <!-- Planned Column -->
        <div class="op-kanban-column" style="width: 320px; min-width: 320px;">
          <div class="op-kanban-col-header">
            <span>Planned (${spr.planned.length})</span>
            <span class="op-kanban-col-add" onclick="alert('Plan New Sprint')">+</span>
          </div>
          <div class="op-kanban-col-bar"></div>
          <div class="op-kanban-col-body" style="display: flex; align-items: center; justify-content: center; color: #94a3b8; font-size: 12px; font-style: italic;">
            No planned sprints
          </div>
        </div>

        <!-- Closed Column -->
        <div class="op-kanban-column" style="width: 380px; min-width: 380px;">
          <div class="op-kanban-col-header">
            <span>Closed (${spr.closed.length})</span>
            <span class="op-kanban-col-add" onclick="alert('View Closed Sprints')">+</span>
          </div>
          <div class="op-kanban-col-bar"></div>
          <div class="op-kanban-col-body">
            ${spr.closed.map(s => `
              <div class="op-sprint-kcard">
                <div class="op-sprint-kcard-header">
                  <span style="font-family: monospace; font-size: 11px; color: #94a3b8;">${s.code}</span>
                  <span style="font-size: 11px; color: #94a3b8;">${s.project}</span>
                </div>
                <div class="op-sprint-kcard-title" onclick="navigateTo('project', 'sprint-board')">
                  ${s.name}
                </div>
                <div class="op-sprint-kcard-dates" style="color: #64748b; font-size: 12px; margin-bottom: 12px;">${s.dates}</div>

                <div class="op-sprint-prog-bar" style="height: 10px; background: #e2e8f0; border-radius: 2px; margin-bottom: 4px;">
                  <div class="op-sprint-prog-fill" style="width: 100%; height: 100%; background: var(--primary);"></div>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; font-size: 12px; color: #64748b; font-weight: 600; margin-bottom: 12px;">
                  <span>${s.pts}</span>
                  <b style="color: var(--primary);">100 %</b>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 10px;">
                  <button class="op-btn op-btn-sm op-btn-secondary" style="font-size: 11.5px; padding: 3px 10px;" onclick="navigateTo('project', 'sprint-board')">Edit</button>
                  <div style="width: 22px; height: 22px; border-radius: 4px; background: ${s.avatarColor || '#0d9488'}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold;">
                    ${s.avatar}
                  </div>
                </div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    </div>
  `;
}

// 3.3 User Stories Kanban Board Matching Image 3
function renderSprintUserStoriesBoardView() {
  const us = AppState.userStories || { backlogs: [], todo: [], inProgress: [], onHold: [] };
  return `
    <div style="max-width: 1380px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderProjectSubbar('tasks')}

      <!-- Control Bar with Breadcrumbs Matching Image 3 -->
      <div class="op-control-bar" style="margin-bottom: 14px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Create New User Story Wizard')">New</button>
          <div class="op-control-title" style="font-size: 13.5px; display: flex; align-items: center; gap: 4px;">
            <a href="javascript:navigateTo('project')" style="color: var(--primary); text-decoration: none; font-weight: 500;">Projects</a>
            <span style="color: #94a3b8; margin: 0 2px;">/</span>
            <a href="javascript:navigateTo('project', 'sprints')" style="color: var(--primary); text-decoration: none; font-weight: 500;">Sprints - IoT - Smart Wearable</a>
            <span style="color: #94a3b8; margin: 0 2px;">/</span>
            <span style="font-weight: 700;">Smart Wearable</span>
            <span style="font-size: 12px; color: #64748b; margin-left: 6px; cursor: pointer;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 280px; display: flex; align-items: center; background: #ffffff; padding: 4px 10px; border: 1px solid #cbd5e1; border-radius: 4px;">
            <span style="color: #94a3b8; margin-right: 6px;">🔍</span>
            <input type="text" placeholder="Search..." oninput="filterUserStories(this.value)" style="border: none; outline: none; background: transparent; flex: 1; font-size: 13px;">
            <span style="color: #64748b; font-size: 10px; margin-left: 4px; cursor: pointer;">▼</span>
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn active" title="User Stories Board" onclick="navigateTo('project', 'sprint-board')">📌</button>
            <button class="op-view-btn" title="List View" onclick="alert('Switching to List View')">📋</button>
            <button class="op-view-btn" title="Calendar View" onclick="navigateTo('leave')">📅</button>
            <button class="op-view-btn" title="Activities View" onclick="togglePopover('activitiesPopover')">⏱️</button>
          </div>
        </div>
      </div>

      <!-- 4-Column User Stories Agile Board Matching Image 3 -->
      <div class="op-kanban-board" id="userStoriesBoard">
        <!-- Column 1: Backlogs -->
        <div class="op-kanban-column" style="width: 310px; min-width: 310px;">
          <div class="op-kanban-col-header">
            <span>Backlogs (${us.backlogs.length})</span>
            <div class="op-kanban-col-count">
              <span class="op-kanban-col-add" onclick="alert('Add Backlog Story')">+</span>
              <span>${us.backlogs.length}</span>
            </div>
          </div>
          <div class="op-kanban-col-bar cyan"></div>
          <div class="op-kanban-col-body">
            ${us.backlogs.map(s => renderUserStoryCard(s)).join('')}
          </div>
        </div>

        <!-- Column 2: To Do -->
        <div class="op-kanban-column" style="width: 310px; min-width: 310px;">
          <div class="op-kanban-col-header">
            <span>To Do (${us.todo.length})</span>
            <div class="op-kanban-col-count">
              <span class="op-kanban-col-add" onclick="alert('Add To Do Story')">+</span>
              <span>${us.todo.length}</span>
            </div>
          </div>
          <div class="op-kanban-col-bar cyan"></div>
          <div class="op-kanban-col-body">
            ${us.todo.map(s => renderUserStoryCard(s)).join('')}
          </div>
        </div>

        <!-- Column 3: In Progress -->
        <div class="op-kanban-column" style="width: 310px; min-width: 310px;">
          <div class="op-kanban-col-header">
            <span>In Progress (${us.inProgress.length})</span>
            <div class="op-kanban-col-count">
              <span class="op-kanban-col-add" onclick="alert('Add In Progress Story')">+</span>
              <span>${us.inProgress.length}</span>
            </div>
          </div>
          <div class="op-kanban-col-bar cyan"></div>
          <div class="op-kanban-col-body">
            ${us.inProgress.map(s => renderUserStoryCard(s)).join('')}
          </div>
        </div>

        <!-- Column 4: On Hold -->
        <div class="op-kanban-column" style="width: 310px; min-width: 310px;">
          <div class="op-kanban-col-header">
            <span>On Hold (${us.onHold.length})</span>
            <div class="op-kanban-col-count">
              <span class="op-kanban-col-add" onclick="alert('Add On Hold Story')">+</span>
              <span>${us.onHold.length}</span>
            </div>
          </div>
          <div class="op-kanban-col-bar cyan"></div>
          <div class="op-kanban-col-body">
            ${us.onHold.map(s => renderUserStoryCard(s)).join('')}
          </div>
        </div>
      </div>
    </div>
  `;
}

function renderUserStoryCard(s) {
  const avatars = s.avatars || [s.avatar || 'V'];
  return `
    <div class="op-story-kcard" onclick="alert('User Story Details: [${s.code}]\\n${s.title}\\nScope: ${s.sprint}\\nPoints: ${s.pts}')">
      <div class="op-story-kcard-top" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
        <div style="display: flex; align-items: center; gap: 6px;">
          <span class="op-story-pill" style="background: #00a09d; color: #ffffff; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 10px;">User Story</span>
          <span class="op-story-code" style="font-family: monospace; font-size: 11px; color: #64748b;">${s.code}</span>
        </div>
        <span style="font-size: 13px; color: #cbd5e1; cursor: pointer;" title="Select story">☐</span>
      </div>

      <div class="op-story-title" style="font-size: 13px; font-weight: 600; color: #1e293b; margin-bottom: 4px; line-height: 1.35;">${s.title}</div>
      <div class="op-story-scope" style="font-size: 11px; color: #94a3b8; margin-bottom: 10px;">${s.sprint}</div>

      <div class="op-story-kcard-footer" style="display: flex; justify-content: space-between; align-items: center;">
        <div style="display: flex; align-items: center; gap: 8px;">
          <span style="color: #cbd5e1; font-size: 13px; cursor: pointer;" onclick="event.stopPropagation(); this.innerText = this.innerText === '☆☆☆' ? '★☆☆' : this.innerText === '★☆☆' ? '★★☆' : this.innerText === '★★☆' ? '★★★' : '☆☆☆';">☆☆☆</span>
          <span class="op-story-pts" style="border: 1px solid #e2e8f0; border-radius: 4px; padding: 1px 6px; font-size: 11px; color: #475569; font-weight: 600;">${s.pts}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 6px;">
          ${s.hasPen ? `<span style="font-size: 11px; color: #64748b;" title="Edit Story">✏️</span>` : ''}
          ${avatars.map(av => `
            <div style="width: 18px; height: 18px; border-radius: 4px; background: ${av === 'A' ? '#10b981' : (s.avatarColor || '#0d9488')}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold;">
              ${av}
            </div>
          `).join('')}
          <span style="width: 8px; height: 8px; border-radius: 50%; border: 1.5px solid #cbd5e1; background: #fff;"></span>
        </div>
      </div>
    </div>
  `;
}

function filterUserStories(query) {
  const q = (query || '').toLowerCase().trim();
  const cards = document.querySelectorAll('#userStoriesBoard .op-story-kcard');
  cards.forEach(card => {
    const text = card.innerText.toLowerCase();
    if (!q || text.includes(q)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

// 3.4 Pending Timesheet Approvals View
function renderPendingTimesheetApprovalsView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      ${renderProjectSubbar('pending-approvals')}

      <div class="op-control-bar" style="margin-bottom: 14px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="navigateTo('timesheet')">⏱️ Open Weekly Grid</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>⚠️ Pending Timesheet Approvals</span>
            <span class="op-debug-badge">Deadline: Monday 3:00 PM</span>
          </div>
        </div>

        <div class="op-control-right">
          <button class="op-btn op-btn-success" onclick="alert('Batch Approval: All verified Week 40 timesheets signed off by Manager Ramesh Patil.')">✅ Batch Approve All</button>
        </div>
      </div>

      <div class="op-table-card">
        <table class="op-table">
          <thead>
            <tr>
              <th>Timesheet Ref</th>
              <th>Employee</th>
              <th>Period</th>
              <th>Logged Hours</th>
              <th>Overtime / Comp-Off</th>
              <th>8-Hr Rule Compliance</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="font-weight: 700; color: var(--primary);">TS/2026/W40</td>
              <td style="font-weight: 600;">Priya Sharma</td>
              <td>Week 40 (Sep 29 - Oct 05, 2026)</td>
              <td style="font-weight: bold; color: var(--primary);">44h (40h Base + 4h OT)</td>
              <td style="color: #0284c7; font-weight: 600;">+4.0h (Saturday Review)</td>
              <td><span class="op-status-pill op-status-approved">PASSED ✅</span></td>
              <td>
                <button class="op-btn op-btn-sm op-btn-primary" onclick="alert('Timesheet TS/2026/W40 approved by Ramesh Patil!')">Approve</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 3.5 Project Detail Sheet & Sizing
function renderProjectDetailView(selectedId = null) {
  const prj = selectedId ? AppState.projects.find(p => p.id === selectedId) : AppState.projects[0];
  
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderProjectSubbar('projects')}

      <!-- Control Bar -->
      <div class="op-control-bar" style="margin-bottom: 14px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="navigateTo('project')">← Back to Kanban</button>
          <div class="op-control-title" style="font-size: 15px;">
            <a href="javascript:navigateTo('project')" style="color: var(--primary); text-decoration: none;">Projects</a>
            <span style="color: #94a3b8; margin: 0 4px;">/</span>
            <span style="font-weight: 700;">${prj.name}</span>
            <span style="font-size: 12px; color: #64748b; margin-left: 6px;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <button class="op-btn op-btn-secondary" onclick="navigateTo('project', 'sprints')">⚡ Open Sprints</button>
          <button class="op-btn op-btn-secondary" onclick="navigateTo('timesheet')">⏱️ Weekly Timesheet Grid</button>
        </div>
      </div>

      <div style="display: grid; grid-template-columns: 320px 1fr; gap: 20px;">
        <!-- Project List -->
        <div class="op-table-card">
          <div style="padding: 12px 16px; background: #f8fafc; border-bottom: 1px solid var(--border-color); font-weight: bold;">
            Active Projects (${AppState.projects.length})
          </div>
          ${AppState.projects.map(p => `
            <div onclick="navigateTo('project', '${p.id}')" style="padding: 14px 16px; border-bottom: 1px solid var(--border-color); cursor: pointer; background: ${p.id === prj.id ? 'var(--primary-subtle)' : '#fff'};">
              <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 4px;">
                <span style="font-weight: 700; color: var(--primary); font-size: 13px;">${p.id}</span>
                <span class="op-status-pill op-status-approved">${p.billingPolicy}</span>
              </div>
              <div style="font-weight: 600; font-size: 13px; color: var(--text-main); margin-bottom: 2px;">${p.name}</div>
              <div style="font-size: 11.5px; color: var(--text-muted);">${p.client} • <b>${p.areaSqFt.toLocaleString()} sq.ft</b></div>
            </div>
          `).join('')}
        </div>

        <!-- Project Detail Sheet -->
        <div class="op-sheet" style="margin: 0; padding: 24px;">
          <div class="op-sheet-header">
            <div>
              <div style="display: flex; align-items: center; gap: 8px;">
                <h2 class="op-sheet-title">${prj.name}</h2>
                <span class="op-status-pill op-status-approved">${prj.status}</span>
              </div>
              <div class="op-sheet-subtitle">Client: <b>${prj.client}</b> | Lead: <b>${prj.leader}</b></div>
            </div>
            <div style="text-align: right;">
              <span class="op-debug-badge">Code: ${prj.id}</span>
              <div style="font-size: 18px; font-weight: 700; color: #059669; margin-top: 4px;">
                ₹ ${(prj.totalBudget).toLocaleString('en-IN')}
              </div>
            </div>
          </div>

          <!-- Metadata 2-Column Grid -->
          <div class="op-grid-2col" style="margin-bottom: 20px;">
            <div>
              <div class="op-form-group">
                <label class="op-form-label">Built-Up / Scope Area <span class="op-debug-badge">fields.Float(sq_ft)</span></label>
                <input class="op-form-input" value="${prj.areaSqFt.toLocaleString()} sq.ft" readonly>
              </div>
              <div class="op-form-group">
                <label class="op-form-label">Invoicing Policy <span class="op-debug-badge">fields.Selection</span></label>
                <input class="op-form-input" value="${prj.billingPolicy}" readonly>
              </div>
              <div class="op-form-group">
                <label class="op-form-label">Statutory GST & HSN/SAC <span class="op-debug-badge">fields.Char</span></label>
                <input class="op-form-input" value="${prj.hsnSac} @ ${prj.gstRate}% GST" readonly>
              </div>
            </div>

            <div>
              <div class="op-form-group">
                <label class="op-form-label">Hours Budget & Burn Rate <span class="op-debug-badge">project.hours</span></label>
                <div style="margin-bottom: 6px; display: flex; justify-content: space-between; font-size: 12px; font-weight: bold;">
                  <span>Logged: ${prj.loggedHours} hrs</span>
                  <span>Budget: ${prj.budgetHours} hrs</span>
                </div>
                <div style="width: 100%; height: 10px; background: #e2e8f0; border-radius: 5px; overflow: hidden;">
                  <div style="width: ${(prj.loggedHours / prj.budgetHours * 100)}%; height: 100%; background: var(--primary);"></div>
                </div>
              </div>
              <div class="op-form-group">
                <label class="op-form-label">Invoiced Milestone Progress</label>
                <div style="font-size: 14px; font-weight: bold; color: var(--text-main);">
                  ₹ ${prj.invoicedAmount.toLocaleString('en-IN')} / ₹ ${prj.totalBudget.toLocaleString('en-IN')}
                  (${Math.round(prj.invoicedAmount / prj.totalBudget * 100)}% Billed)
                </div>
              </div>
            </div>
          </div>

          <!-- Milestones Table if applicable -->
          ${prj.milestones && prj.milestones.length > 0 ? `
            <h4 style="font-size: 14px; font-weight: 700; margin-bottom: 10px; color: var(--text-main);">
              Milestone Breakdown & Deliverable Schedule
            </h4>
            <div class="op-table-card" style="margin-bottom: 20px;">
              <table class="op-table">
                <thead>
                  <tr>
                    <th>Milestone Stage</th>
                    <th>% Share</th>
                    <th>Fee Amount</th>
                    <th>Invoicing Status</th>
                  </tr>
                </thead>
                <tbody>
                  ${prj.milestones.map(m => `
                    <tr>
                      <td style="font-weight: 600;">${m.name}</td>
                      <td>${m.pct}%</td>
                      <td>₹ ${m.amount.toLocaleString('en-IN')}</td>
                      <td><span class="op-status-pill ${m.status === 'Invoiced & Paid' ? 'op-status-approved' : 'op-status-pending'}">${m.status}</span></td>
                    </tr>
                  `).join('')}
                </tbody>
              </table>
            </div>
          ` : ''}

          <div style="display: flex; justify-content: flex-end; gap: 10px;">
            <button class="op-btn op-btn-secondary" onclick="navigateTo('accounting')">💰 Generate Milestone Invoice</button>
            <button class="op-btn op-btn-primary" onclick="navigateTo('timesheet')">⏱️ Log Daily Timesheets</button>
          </div>
        </div>
      </div>
    </div>
  `;
}

function filterProjectCards(query) {
  const q = (query || '').toLowerCase().trim();
  const cards = document.querySelectorAll('#projectKanbanBoard .op-project-kcard');
  cards.forEach(card => {
    const text = card.innerText.toLowerCase();
    if (!q || text.includes(q)) {
      card.style.display = 'block';
    } else {
      card.style.display = 'none';
    }
  });
}

function clearProjectFilter(e) {
  if (e) e.stopPropagation();
  const input = document.getElementById('projectSearchInput');
  if (input) input.value = '';
  filterProjectCards('');
}

// -------------------------------------------------------------
// 4. Timesheet Engine (All Timesheets List & Weekly 8-Hour Grid)
// -------------------------------------------------------------

function renderTimesheetView(param = null) {
  if (param === 'grid') {
    return renderTimesheetWeeklyGridView();
  }
  return renderTimesheetListView();
}

function renderTimesheetSubbar(activeTab = 'timesheets') {
  return `
    <div class="op-subbar">
      <span class="op-subbar-item ${activeTab === 'timesheets' ? 'active' : ''}" onclick="navigateTo('timesheet')">Timesheets</span>
      <span class="op-subbar-item ${activeTab === 'reporting' ? 'active' : ''}" onclick="alert('Timesheet Reporting: Pivot Matrix by Project, Employee, and Billable Hours')">Reporting</span>
    </div>
  `;
}

// 4.1 All Timesheets Management List View Matching Uploaded Screenshot
function renderTimesheetListView() {
  const list = (AppState.allTimesheets && AppState.allTimesheets.length > 0) ? AppState.allTimesheets : INITIAL_DATA.allTimesheets;
  return `
    <div style="max-width: 1400px; margin: 0 auto;">
      <!-- Odoo Subbar Matching Screenshot -->
      ${renderTimesheetSubbar('timesheets')}

      <!-- Control Bar Matching Uploaded Screenshot -->
      <div class="op-control-bar" style="margin-bottom: 14px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Create New Timesheet Entry Wizard')">New</button>
          <div class="op-control-title" style="font-size: 16px; display: flex; align-items: center; gap: 6px;">
            <span>All Timesheets</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;" title="Timesheet Settings">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <!-- Search Box with Purple Filter Chip matching Screenshot -->
          <div class="op-search-box" style="width: 390px; display: flex; align-items: center; background: #ffffff; padding: 4px 10px; border: 1px solid #cbd5e1; border-radius: 4px;">
            <span style="color: #94a3b8; margin-right: 6px;">🔍</span>
            <span class="op-filter-chip-purple" id="timesheetFilterChip">
              <span class="op-chip-icon">🗂️</span> Project not – Internal or Internal <span class="op-chip-remove" onclick="clearTimesheetFilter(event)" title="Clear filter">✕</span>
            </span>
            <input type="text" id="timesheetSearchInput" placeholder="Search..." oninput="filterTimesheetRows(this.value)" style="border: none; outline: none; background: transparent; flex: 1; font-size: 13px;">
            <span style="color: #64748b; font-size: 10px; margin-left: 4px; cursor: pointer;">▼</span>
          </div>
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1-${list.length} / 1384
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" onclick="alert('Previous page')">&lt;</button>
            <button class="op-view-btn" onclick="alert('Next page')">&gt;</button>
            <button class="op-view-btn active" title="List View" onclick="navigateTo('timesheet')">📋</button>
            <button class="op-view-btn" title="Weekly 8-Hr Grid" onclick="navigateTo('timesheet', 'grid')">⏱️</button>
            <button class="op-view-btn" title="Calendar View" onclick="navigateTo('leave')">📅</button>
            <button class="op-view-btn" title="Kanban View" onclick="navigateTo('project')">🗂️</button>
            <button class="op-view-btn" title="Pivot Matrix View" onclick="alert('Switch to Pivot Matrix View')">📊</button>
            <button class="op-view-btn" title="Graph View" onclick="alert('Switch to Graph Analysis View')">📈</button>
          </div>
        </div>
      </div>

      <!-- Batch Actions Bar (Visible when rows checked) -->
      <div id="timesheetBatchBar" class="op-batch-bar" style="display: none;">
        <div style="font-weight: 700; font-size: 13px; color: #581c87;">
          <span id="selectedTimesheetCount">0</span> timesheet(s) selected
        </div>
        <div style="display: flex; gap: 8px;">
          <button class="op-btn op-btn-sm op-btn-success" onclick="approveSelectedTimesheets()">✅ Approve Selected</button>
          <button class="op-btn op-btn-sm op-btn-danger" onclick="refuseSelectedTimesheets()">❌ Refuse</button>
          <button class="op-btn op-btn-sm op-btn-secondary" onclick="exportTimesheetsCSV()">📤 Export CSV</button>
        </div>
      </div>

      <!-- All Timesheets List Table Matching Screenshot -->
      <div class="op-table-card" style="border-radius: var(--radius-md); overflow: visible;">
        <table class="op-timesheet-list-table" id="allTimesheetsTable">
          <thead>
            <tr>
              <th style="width: 32px; text-align: center;">
                <input type="checkbox" id="selectAllTimesheets" onchange="toggleSelectAllTimesheets(this.checked)">
              </th>
              <th>Date</th>
              <th>Employee</th>
              <th>Project</th>
              <th>Task</th>
              <th>Description</th>
              <th>Sales Order Item</th>
              <th style="text-align: right;">Time Spent</th>
              <th style="text-align: center;">Status</th>
              <th style="text-align: right;">Elapsed at...</th>
              <th style="width: 24px; text-align: center; color: #94a3b8; cursor: pointer;" title="Customize Columns">⇄</th>
            </tr>
          </thead>
          <tbody>
            ${list.map(t => `
              <tr data-id="${t.id}" data-employee="${t.employee}" data-project="${t.project}" data-task="${t.task}" data-desc="${t.description}">
                <td style="text-align: center;">
                  <input type="checkbox" class="timesheet-row-cb" onchange="handleTimesheetRowSelect()">
                </td>
                <td style="font-weight: 600; color: #334155; white-space: nowrap;">${t.date}</td>
                <td>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 18px; height: 18px; border-radius: 3px; background: ${t.avatarColor || '#10b981'}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 10px; font-weight: bold;">
                      ${t.avatarLetter || 'A'}
                    </div>
                    <span style="font-weight: 600; color: #1e293b; white-space: nowrap;">${t.employee}</span>
                  </div>
                </td>
                <td style="color: #0369a1; font-weight: 500; white-space: nowrap;">${t.project}</td>
                <td style="color: #475569; white-space: nowrap;">${t.task}</td>
                <td class="op-desc-cell">
                  <span>${t.description}</span>
                  <div class="op-desc-tooltip">${t.description}</div>
                </td>
                <td style="color: #64748b; font-family: monospace; font-size: 11px;">${t.salesOrder}</td>
                <td style="text-align: right; font-weight: 700; font-family: monospace; color: #1e293b;">${t.timeSpent}</td>
                <td style="text-align: center;">
                  <span class="${t.status === 'Approved' ? 'op-status-badge-approved' : 'op-status-badge-draft'}">${t.status}</span>
                </td>
                <td style="text-align: right; font-family: monospace; color: #64748b;">${t.elapsed}</td>
                <td></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 4.2 Weekly Timesheet 8-Hour Validation Grid Engine
function renderTimesheetWeeklyGridView() {
  return `
    <div style="max-width: 1150px; margin: 0 auto;">
      ${renderTimesheetSubbar('timesheets')}

      <div class="op-control-bar" style="margin-bottom: 16px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-secondary" onclick="navigateTo('timesheet')">← All Timesheets List</button>
          <div class="op-control-title">
            <span>⏱️ Weekly Timesheet Engine</span>
            <span class="op-debug-badge">Rule: Mandatory 8-Hr Daily Minimum</span>
          </div>
        </div>
        <div class="op-control-right">
          <div style="font-size: 12px; color: var(--text-muted);">
            Submission Deadline: <b>Every Monday 3:00 PM</b> | Approval: <b>Tuesday 5:00 PM</b>
          </div>
        </div>
      </div>

      <div class="op-sheet">
        <div class="op-sheet-header">
          <div>
            <h2 class="op-sheet-title">Week 40 Timesheet Submission</h2>
            <div class="op-sheet-subtitle">Employee: <b>Priya Sharma (Senior Project Engineer)</b> | Approver: <b>Ramesh Patil</b></div>
          </div>
          <div style="text-align: right;">
            <span class="op-status-pill op-status-submitted">Submitted</span>
            <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">Auto-locked after submission</div>
          </div>
        </div>

        <!-- Timesheet Interactive Grid -->
        <table class="op-timesheet-grid">
          <thead>
            <tr>
              <th style="text-align: left;">Project & Task Activity</th>
              <th>Mon</th>
              <th>Tue</th>
              <th>Wed</th>
              <th>Thu</th>
              <th>Fri</th>
              <th>Sat (OT)</th>
              <th>Sun</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="text-align: left;">
                <div style="font-weight: 700;">Tech Park Phase 2 Complex</div>
                <div style="font-size: 11px; color: var(--text-muted);">Facade Wind Load Analysis</div>
              </td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="5" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="0" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="0" onchange="recalcTimesheet()"></td>
              <td class="op-timesheet-total-cell">21h</td>
            </tr>
            <tr>
              <td style="text-align: left;">
                <div style="font-weight: 700;">Metro Station Canopy & Plaza</div>
                <div style="font-size: 11px; color: var(--text-muted);">Foundation Rebar Detailing</div>
              </td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="3" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="4" onchange="recalcTimesheet()"></td>
              <td><input class="op-timesheet-input" value="0" onchange="recalcTimesheet()"></td>
              <td class="op-timesheet-total-cell">23h</td>
            </tr>
            <tr style="background: #f8fafc; font-weight: bold;">
              <td style="text-align: left;">Daily Total Logged:</td>
              <td class="op-day-valid">8h ✅</td>
              <td class="op-day-valid">8h ✅</td>
              <td class="op-day-valid">8h ✅</td>
              <td class="op-day-valid">8h ✅</td>
              <td class="op-day-valid">8h ✅</td>
              <td style="color: #0284c7;">4h (OT)</td>
              <td>0h</td>
              <td style="font-size: 16px; color: var(--primary);">44h</td>
            </tr>
            <tr style="background: #f1f5f9; font-size: 11px;">
              <td style="text-align: left; font-weight: bold;">8-Hour Validation Compliance:</td>
              <td style="color: var(--success); font-weight: bold;">PASSED</td>
              <td style="color: var(--success); font-weight: bold;">PASSED</td>
              <td style="color: var(--success); font-weight: bold;">PASSED</td>
              <td style="color: var(--success); font-weight: bold;">PASSED</td>
              <td style="color: var(--success); font-weight: bold;">PASSED</td>
              <td style="color: #0284c7; font-weight: bold;">COMP-OFF</td>
              <td style="color: var(--text-muted);">-</td>
              <td style="color: var(--success); font-weight: bold;">VALIDATED</td>
            </tr>
          </tbody>
        </table>

        <!-- Overtime & Inter-Team Resource Loaning Summary -->
        <div style="margin-top: 20px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 14px;">
            <h4 style="font-size: 12px; font-weight: 700; color: var(--primary); text-transform: uppercase; margin-bottom: 6px;">
              ⚡ Overtime & Comp-Off Policy Engine
            </h4>
            <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 6px;">
              • <b>Weekend Claim:</b> 4 hours logged on Saturday for Metro Canopy review.
            </p>
            <div style="font-size: 12px; font-weight: 600; color: var(--success);">
              +4.0 Hours credited to Compensatory Leave Balance upon Ramesh Patil signoff.
            </div>
          </div>

          <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 14px;">
            <h4 style="font-size: 12px; font-weight: 700; color: var(--primary); text-transform: uppercase; margin-bottom: 6px;">
              🔄 Cross-Team Resource Loaning Routing
            </h4>
            <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 6px;">
              Priya (Structural Design Dept) loaned 23 hrs to Transit Infrastructure.
            </p>
            <div style="font-size: 12px; font-weight: 600; color: var(--primary);">
              Automated Cost Journal: ₹ 19,550 automatically debited to PRJ/2026/002.
            </div>
          </div>
        </div>

        <div style="margin-top: 20px; display: flex; justify-content: flex-end; gap: 10px;">
          <button class="op-btn op-btn-secondary" onclick="alert('Simulation: Re-opening Timesheet for edit')">🔓 Unlock & Edit</button>
          <button class="op-btn op-btn-success" onclick="alert('Timesheet Approved by Manager Ramesh Patil! Status updated in database.')">✅ Approve Timesheet (Manager Sign-Off)</button>
        </div>
      </div>
    </div>
  `;
}

function filterTimesheetRows(query) {
  const q = (query || '').toLowerCase().trim();
  const rows = document.querySelectorAll('#allTimesheetsTable tbody tr');
  rows.forEach(r => {
    const text = r.innerText.toLowerCase();
    if (!q || text.includes(q)) {
      r.style.display = '';
    } else {
      r.style.display = 'none';
    }
  });
}

function clearTimesheetFilter(e) {
  if (e) e.stopPropagation();
  const chip = document.getElementById('timesheetFilterChip');
  if (chip) chip.style.display = 'none';
  const input = document.getElementById('timesheetSearchInput');
  if (input) input.value = '';
  filterTimesheetRows('');
}

function toggleSelectAllTimesheets(checked) {
  const cbs = document.querySelectorAll('#allTimesheetsTable tbody .timesheet-row-cb');
  cbs.forEach(cb => {
    cb.checked = checked;
    const tr = cb.closest('tr');
    if (tr) tr.classList.toggle('selected', checked);
  });
  updateTimesheetBatchBar();
}

function handleTimesheetRowSelect() {
  const cbs = document.querySelectorAll('#allTimesheetsTable tbody .timesheet-row-cb');
  cbs.forEach(cb => {
    const tr = cb.closest('tr');
    if (tr) tr.classList.toggle('selected', cb.checked);
  });
  updateTimesheetBatchBar();
}

function updateTimesheetBatchBar() {
  const selected = document.querySelectorAll('#allTimesheetsTable tbody .timesheet-row-cb:checked').length;
  const bar = document.getElementById('timesheetBatchBar');
  const countEl = document.getElementById('selectedTimesheetCount');
  if (bar && countEl) {
    if (selected > 0) {
      countEl.textContent = selected;
      bar.style.display = 'flex';
    } else {
      bar.style.display = 'none';
    }
  }
}

function approveSelectedTimesheets() {
  const checkedRows = document.querySelectorAll('#allTimesheetsTable tbody tr.selected');
  checkedRows.forEach(tr => {
    const statusCell = tr.querySelector('td:nth-child(9)');
    if (statusCell) {
      statusCell.innerHTML = `<span class="op-status-badge-approved">Approved</span>`;
    }
  });
  alert(`Successfully validated & signed off ${checkedRows.length} timesheet entry(ies)!`);
  toggleSelectAllTimesheets(false);
  const selectAll = document.getElementById('selectAllTimesheets');
  if (selectAll) selectAll.checked = false;
}

function refuseSelectedTimesheets() {
  const checkedRows = document.querySelectorAll('#allTimesheetsTable tbody tr.selected');
  checkedRows.forEach(tr => {
    const statusCell = tr.querySelector('td:nth-child(9)');
    if (statusCell) {
      statusCell.innerHTML = `<span class="op-status-badge-draft">Refused</span>`;
    }
  });
  alert(`Refused ${checkedRows.length} timesheet entry(ies) for revision.`);
  toggleSelectAllTimesheets(false);
  const selectAll = document.getElementById('selectAllTimesheets');
  if (selectAll) selectAll.checked = false;
}

function exportTimesheetsCSV() {
  alert('Exporting filtered timesheets to CSV/XLSX: analytic_lines_export.csv generated successfully.');
}

function recalcTimesheet() {
  alert('Interactive Engine: 8-Hour Daily Validation recalculated dynamically!');
}

// -------------------------------------------------------------
// 5. Attendance Module (List, Biometric Device & Kiosk Mode)
// -------------------------------------------------------------

function renderAttendanceView(param = null) {
  if (param === 'biometric') {
    return renderBiometricDevicesListView();
  }
  if (param === 'biometric-form') {
    return renderBiometricDeviceFormView();
  }
  if (param === 'kiosk') {
    return renderAttendanceKioskView();
  }
  if (param && param.startsWith('absence')) {
    return renderAbsenceTrackingView(param);
  }
  return renderAttendanceListView();
}

function renderAttendanceSubbar(activeTab = 'attendances') {
  return `
    <div class="op-subbar">
      <span class="op-subbar-item ${activeTab === 'attendances' ? 'active' : ''}" onclick="navigateTo('attendance')">Attendances</span>
      <span class="op-subbar-item ${activeTab === 'overview' ? 'active' : ''}" onclick="alert('Attendance Overview Dashboard: 12 Employees Online / 1 On Leave')">Overview</span>
      <div class="op-subbar-dropdown">
        <span class="op-subbar-item ${activeTab === 'management' ? 'active' : ''}">Management ▾</span>
        <div class="op-subbar-dropdown-menu">
          <div class="op-subbar-dropdown-header">Absence Tracking</div>
          <div class="op-subbar-dropdown-item" onclick="navigateTo('attendance', 'absence-fullday')">Full Day Requests</div>
          <div class="op-subbar-dropdown-item" onclick="navigateTo('attendance', 'absence-days')">Absent Days</div>
          <div class="op-subbar-dropdown-item" onclick="navigateTo('attendance', 'absence-compute')">Compute Absent Days</div>
          <div class="op-subbar-dropdown-divider"></div>
          <div class="op-subbar-dropdown-item" onclick="navigateTo('attendance', 'absence-my')">My Absent Days</div>
        </div>
      </div>
      <span class="op-subbar-item ${activeTab === 'kiosk' ? 'active' : ''}" onclick="navigateTo('attendance', 'kiosk')">Kiosk Mode</span>
      <span class="op-subbar-item" onclick="alert('Attendance Reports: Monthly Biometric Log & Overtime Summary')">Reporting</span>
      <span class="op-subbar-item ${activeTab === 'biometric' ? 'active' : ''}" onclick="navigateTo('attendance', 'biometric')">Biometric Device</span>
      <span class="op-subbar-item" onclick="alert('Pending Reviews: 2 Regularization requests awaiting manager signoff')">Pending Reviews</span>
      <span class="op-subbar-item" onclick="navigateTo('technical')">Configuration</span>
    </div>
  `;
}

// 5.1 Main Attendances List View Matching Image 7
function renderAttendanceListView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar with Management Dropdown & Kiosk Mode -->
      ${renderAttendanceSubbar('attendances')}

      <!-- Control Bar Matching Image 7 -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="openManualAttendanceModal()">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>Attendances</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;" title="Attendance Settings">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 260px;">
            <span>🔍</span>
            <input type="text" id="attendanceSearchInput" placeholder="Search..." oninput="filterAttendanceTable(this.value)">
          </div>
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1-${AppState.attendances.length} / 3285
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" onclick="alert('Previous page')">&lt;</button>
            <button class="op-view-btn" onclick="alert('Next page')">&gt;</button>
            <button class="op-view-btn active" title="List View" onclick="navigateTo('attendance')">📋</button>
            <button class="op-view-btn" title="Biometric Devices" onclick="navigateTo('attendance', 'biometric')">🔌</button>
            <button class="op-view-btn" title="Kiosk Simulator" onclick="navigateTo('attendance', 'kiosk')">🕒</button>
          </div>
        </div>
      </div>

      <!-- Attendances Table Card Matching Image 7 -->
      <div class="op-table-card">
        <table class="op-table" id="attendanceListTable">
          <thead>
            <tr>
              <th style="width: 32px;"><input type="checkbox" onclick="toggleSelectAllAttendances(this)"></th>
              <th>Employee</th>
              <th>Check In</th>
              <th>Check Out</th>
              <th>Worked Hours</th>
              <th>Worked Extra Hours</th>
              <th>Input Mode (In)</th>
              <th>Input Mode (Out)</th>
            </tr>
          </thead>
          <tbody>
            ${AppState.attendances.map(a => `
              <tr>
                <td><input type="checkbox" class="att-row-cb"></td>
                <td>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <div style="width: 22px; height: 22px; border-radius: 4px; background: ${a.avatarColor || '#0284c7'}; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold;">
                      ${a.avatarLetter || a.employee[0]}
                    </div>
                    <span style="font-weight: 600; color: #1e293b;">${a.employee}</span>
                  </div>
                </td>
                <td style="color: #475569;">${a.checkIn}</td>
                <td style="color: #475569;">${a.checkOut}</td>
                <td style="font-weight: 700; color: ${a.workedHours.startsWith('03') || a.workedHours.startsWith('06') ? '#d97706' : '#1e293b'};">${a.workedHours}</td>
                <td style="font-weight: 600; color: ${a.extraHours !== '00:00' ? 'var(--primary)' : '#64748b'};">${a.extraHours}</td>
                <td>
                  <span class="op-status-pill ${a.inputModeIn === 'Biometric' ? 'op-status-approved' : 'op-status-pending'}" style="font-size: 11px;">
                    ${a.inputModeIn === 'Biometric' ? '🔒 Biometric' : '✍️ Manual'}
                  </span>
                </td>
                <td>
                  <span class="op-status-pill ${a.inputModeOut === 'Biometric' ? 'op-status-approved' : 'op-status-pending'}" style="font-size: 11px;">
                    ${a.inputModeOut === 'Biometric' ? '🔒 Biometric' : '✍️ Manual'}
                  </span>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 5.2 Biometric Devices List View Matching Image 8
function renderBiometricDevicesListView() {
  const dev = AppState.biometricDevice;
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderAttendanceSubbar('biometric')}

      <!-- Control Bar Matching Image 8 -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Register New ADMS Biometric Device')">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>Biometric Devices</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;" title="Device Settings">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 260px;">
            <span>🔍</span>
            <input type="text" placeholder="Search devices...">
          </div>
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1-1 / 1
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" onclick="alert('Previous page')">&lt;</button>
            <button class="op-view-btn" onclick="alert('Next page')">&gt;</button>
            <button class="op-view-btn" title="Attendances List" onclick="navigateTo('attendance')">📋</button>
            <button class="op-view-btn active" title="Biometric Devices" onclick="navigateTo('attendance', 'biometric')">🔌</button>
          </div>
        </div>
      </div>

      <!-- Biometric Devices Table Matching Image 8 -->
      <div class="op-table-card">
        <table class="op-table">
          <thead>
            <tr>
              <th style="width: 32px;"><input type="checkbox"></th>
              <th>Device Name</th>
              <th>Serial Number</th>
              <th>ADMS Enabled</th>
              <th>Status</th>
              <th>Last Push</th>
              <th>Total Users</th>
              <th>Mapped Users</th>
              <th>Unmapped Users</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td><input type="checkbox"></td>
              <td>
                <a href="javascript:navigateTo('attendance', 'biometric-form')" style="font-weight: 700; color: var(--primary); text-decoration: none; cursor: pointer;">
                  ${dev.name}
                </a>
              </td>
              <td style="font-family: monospace; font-weight: 600;">${dev.serialNumber}</td>
              <td>
                <input type="checkbox" ${dev.admsEnabled ? 'checked' : ''} disabled style="accent-color: var(--primary);">
              </td>
              <td>
                <span style="color: #16a34a; font-weight: 700;">● ${dev.status}</span>
              </td>
              <td style="color: #475569;">${dev.lastPush}</td>
              <td style="font-weight: 600;">${dev.totalUsers}</td>
              <td style="font-weight: 600; color: #16a34a;">${dev.mappedUsers}</td>
              <td style="font-weight: 600; color: #d97706;">${dev.unmappedUsers}</td>
              <td>
                <button class="op-btn op-btn-sm op-btn-secondary" onclick="navigateTo('attendance', 'biometric-form')">
                  🔌 ADMS Info
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 5.3 Biometric Device Form Sheet Matching Images 9 & 10
function renderBiometricDeviceFormView(activeTab = 'deviceUsers') {
  const dev = AppState.biometricDevice;
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderAttendanceSubbar('biometric')}

      <!-- Control Bar with Breadcrumbs Matching Image 9 -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="navigateTo('attendance', 'biometric')">New</button>
          <div class="op-control-title" style="font-size: 15px;">
            <a href="javascript:navigateTo('attendance', 'biometric')" style="color: var(--primary); text-decoration: none;">Biometric Devices</a>
            <span style="color: #94a3b8; margin: 0 4px;">/</span>
            <span style="font-weight: 700;">${dev.name}</span>
            <span style="font-size: 12px; color: #64748b; margin-left: 6px;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1 / 1
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" onclick="navigateTo('attendance', 'biometric')">&lt;</button>
            <button class="op-view-btn" onclick="navigateTo('attendance', 'biometric')">&gt;</button>
          </div>
        </div>
      </div>

      <!-- Action Buttons Bar & Status Bar Matching Image 9 -->
      <div style="background: #ffffff; border: 1px solid #e2e8f0; border-radius: 8px 8px 0 0; padding: 10px 16px; display: flex; justify-content: space-between; align-items: center; border-bottom: none;">
        <div style="display: flex; gap: 8px;">
          <button class="op-btn op-btn-sm op-btn-secondary" onclick="alert('ADMS Setup Wizard: Endpoint URL http://connect.officepro.internal/iclock/cdata verified')">🔌 ADMS Setup</button>
          <button class="op-btn op-btn-sm op-btn-secondary" onclick="navigateTo('attendance')">📥 Browse Attendance</button>
          <button class="op-btn op-btn-sm op-btn-secondary" onclick="syncBiometricPunches()">🔄 Sync Attendance</button>
        </div>

        <div class="op-status-pipeline">
          <div class="op-pipeline-step">Waiting</div>
          <div class="op-pipeline-step active">Push Active</div>
        </div>
      </div>

      <!-- Main Form Sheet Matching Images 9 & 10 -->
      <div class="op-sheet" style="border-radius: 0 0 8px 8px; margin: 0; padding: 24px;">
        <h1 style="font-size: 24px; font-weight: 700; color: #1e293b; margin-bottom: 20px;">${dev.name}</h1>

        <!-- 2-Column Fields Grid Matching Image 9 -->
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 24px; margin-bottom: 20px;">
          <!-- Left Column -->
          <div>
            <div class="op-form-group">
              <label class="op-form-label">Serial Number <span title="Hardware serial number">?</span></label>
              <input class="op-form-input" value="${dev.serialNumber}" readonly style="font-family: monospace; font-weight: 600;">
            </div>

            <div class="op-form-group">
              <label class="op-form-label">ADMS Enabled <span title="Real-time push protocol">?</span></label>
              <div>
                <label class="op-switch">
                  <input type="checkbox" checked onchange="alert('ADMS Push stream active.')">
                  <span class="op-slider"></span>
                </label>
              </div>
            </div>

            <div class="op-form-group">
              <label class="op-form-label">Company <span title="Legal entity">?</span></label>
              <input class="op-form-input" value="Office Pro Solutions Ltd" readonly>
            </div>

            <div class="op-form-group">
              <label class="op-form-label">Last Push <span title="Last heartbeat timestamp">?</span></label>
              <input class="op-form-input" value="${dev.lastPush}" readonly style="color: #16a34a; font-weight: 600;">
            </div>
          </div>

          <!-- Right Column -->
          <div>
            <div class="op-form-group">
              <label class="op-form-label">Timezone <span title="Hardware device timezone">?</span></label>
              <input class="op-form-input" value="${dev.timezone}" readonly>
            </div>

            <div class="op-form-group">
              <label class="op-form-label">Used For <span title="Operation purpose">?</span></label>
              <input class="op-form-input" value="${dev.usedFor}" readonly>
            </div>

            <div class="op-form-group">
              <label class="op-form-label">Status Code Based <span title="Use in/out status codes">?</span></label>
              <div>
                <input type="checkbox" disabled>
              </div>
            </div>

            <div class="op-form-group">
              <label class="op-form-label">Min. Checkout Gap (hrs) <span title="Minimum time between punches">?</span></label>
              <input class="op-form-input" value="${dev.minCheckoutGap.toFixed(2)}" readonly>
            </div>
          </div>
        </div>

        <!-- ADMS PUSH URL Banner Matching Image 9 -->
        <div class="op-adms-banner">
          <div class="op-adms-title">Configure this URL on the eSSL device:</div>
          <div class="op-adms-url">${dev.pushUrl}</div>
          <div class="op-adms-help">Device menu: Comm &rarr; ADMS &rarr; Server Address / Port</div>
        </div>

        <!-- Bottom Tabs Matching Images 9 & 10 -->
        <div class="op-status-pipeline" style="margin-bottom: 16px;">
          <div class="op-pipeline-step" onclick="alert('ADMS Settings: Port 80, Keep-alive 30s, Heartbeat interval 60s')">ADMS Settings</div>
          <div class="op-pipeline-step" onclick="alert('Status Codes: 0=CheckIn, 1=CheckOut, 2=BreakOut, 3=BreakIn')">Status Codes</div>
          <div class="op-pipeline-step" onclick="alert('Attendance Data Logs: 3,285 raw biometric punch records synced')">Attendance Data Logs</div>
          <div class="op-pipeline-step active">Device Users</div>
        </div>

        <!-- DEVICE USERS TAB CONTENT Matching Image 10 -->
        <div>
          <!-- Blue Info Alert Box -->
          <div class="op-info-alert">
            <div style="font-weight: 700; margin-bottom: 4px;">How to get users into this list (Office Pro Cloud Server):</div>
            <div><b>1. ADMS Push (recommended):</b> click <i>Request Users from Device</i> below &mdash; the device will upload its full user list on the next heartbeat (~30 s).</div>
            <div><b>2. CSV Import:</b> export the user list from your eSSL desktop software (ZKBioSecurity / iClock) and click <i>Import from CSV</i>.</div>
            <div><b>3. Manual entry:</b> click <i>Add a line</i> in the table below and type the PIN and name directly.</div>
          </div>

          <!-- Action Buttons Row Matching Image 10 -->
          <div style="display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap;">
            <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="requestUsersFromDevice()">📥 Request Users from Device (ADMS)</button>
            <button class="op-btn op-btn-warning" style="background: #f59e0b; color: #fff;" onclick="resetStamp()">Reset Stamp</button>
            <button class="op-btn op-btn-secondary" onclick="importFromCSV()">📁 Import from CSV</button>
            <button class="op-btn op-btn-secondary" onclick="autoMapEmployees()">⚡ Auto Map Employees</button>
          </div>

          <!-- User Counts Row Matching Image 10 -->
          <div style="display: flex; gap: 24px; font-size: 13px; margin-bottom: 14px; padding-bottom: 10px; border-bottom: 1px solid #e2e8f0;">
            <div>Total Users <span title="Total registered users">?</span>: <b>${dev.totalUsers}</b></div>
            <div>Mapped Users <span title="Users linked to an employee">?</span>: <b style="color: #16a34a;">${dev.mappedUsers}</b></div>
            <div>Unmapped Users <span title="Users requiring mapping">?</span>: <b style="color: #d97706;">${dev.unmappedUsers}</b></div>
          </div>

          <!-- Mapping Table Matching Image 10 -->
          <table class="op-table">
            <thead>
              <tr>
                <th style="width: 120px;">Device PIN</th>
                <th>Name on Device</th>
                <th>Odoo Employee</th>
                <th style="width: 90px; text-align: center;">Mapped</th>
                <th style="width: 60px; text-align: center;">Action</th>
              </tr>
            </thead>
            <tbody>
              ${AppState.deviceUsers.map(u => `
                <tr>
                  <td style="font-family: monospace; font-weight: bold;">${u.pin}</td>
                  <td style="font-weight: 600;">${u.nameOnDevice}</td>
                  <td style="color: ${u.mapped ? 'var(--primary)' : '#94a3b8'}; font-weight: ${u.mapped ? '600' : 'normal'};">
                    ${u.employee}
                  </td>
                  <td style="text-align: center;">
                    <input type="checkbox" ${u.mapped ? 'checked' : ''} disabled style="accent-color: var(--primary);">
                  </td>
                  <td style="text-align: center;">
                    <button class="op-btn op-btn-sm" style="background: transparent; color: #ef4444; padding: 2px 6px;" onclick="alert('Simulation: Unlink PIN ${u.pin}')" title="Delete User Mapping">🗑️</button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>

          <div style="margin-top: 12px;">
            <a href="javascript:alert('Simulation: Add new PIN line to device mapping')" style="font-size: 13px; color: var(--primary); font-weight: 600; text-decoration: none;">
              + Add a line
            </a>
          </div>
        </div>
      </div>
    </div>
  `;
}

// 5.4 Kiosk Mode Terminal Simulator
function renderAttendanceKioskView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Subbar -->
      ${renderAttendanceSubbar('kiosk')}

      <div class="op-kiosk-view">
        <div class="op-kiosk-card">
          <div style="font-size: 13px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1px;">
            🏢 Office Pro &bull; Biometric Attendance Terminal
          </div>
          <div class="op-kiosk-clock live-clock-display">--:--:--</div>
          
          <div style="margin-bottom: 16px;">
            <label style="font-size: 12px; font-weight: 600; color: #475569; display: block; margin-bottom: 6px;">Select Employee or Enter PIN:</label>
            <select id="kioskEmployeeSelect" class="op-form-input" style="font-size: 14px; font-weight: 600;" onchange="updateKioskPin(this.value)">
              ${AppState.employees.map(e => `
                <option value="${e.id}">${e.name} (${e.role})</option>
              `).join('')}
            </select>
          </div>

          <div class="op-kiosk-pin-display" id="kioskPinDisplay">••••</div>

          <!-- Numpad -->
          <div class="op-kiosk-numpad">
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('1')">1</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('2')">2</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('3')">3</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('4')">4</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('5')">5</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('6')">6</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('7')">7</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('8')">8</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('9')">9</button>
            <button class="op-kiosk-num-btn" onclick="clearKioskPin()" style="color: #ef4444;">C</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('0')">0</button>
            <button class="op-kiosk-num-btn" onclick="pressKioskKey('⌫')">⌫</button>
          </div>

          <!-- Punch Actions -->
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 14px;">
            <button class="op-btn op-btn-primary" style="padding: 14px; font-size: 15px; font-weight: 700; background: #10b981;" onclick="submitKioskPunch('Check In')">
              🟢 Check In
            </button>
            <button class="op-btn op-btn-primary" style="padding: 14px; font-size: 15px; font-weight: 700; background: #ef4444;" onclick="submitKioskPunch('Check Out')">
              🔴 Check Out
            </button>
          </div>

          <div style="display: flex; justify-content: center; gap: 12px; font-size: 12px; color: #64748b;">
            <span>Terminal: <b>CUB7252300146 (Mumbai HQ)</b></span>
            <span>&bull;</span>
            <span style="color: #10b981; font-weight: bold;">● ADMS Push Active</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

// 5.5 Absence Tracking Sub-views
function renderAbsenceTrackingView(type) {
  const title = type === 'absence-fullday' ? 'Full Day Requests' : type === 'absence-days' ? 'Absent Days' : type === 'absence-compute' ? 'Compute Absent Days' : 'My Absent Days';
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      ${renderAttendanceSubbar('management')}

      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Create Absence Request')">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>Absence Tracking &gt; ${title}</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 260px;">
            <span>🔍</span>
            <input type="text" placeholder="Search requests...">
          </div>
        </div>
      </div>

      <div class="op-table-card">
        <table class="op-table">
          <thead>
            <tr>
              <th>Request ID</th>
              <th>Employee</th>
              <th>Absence Type</th>
              <th>Date</th>
              <th>Approver</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${AppState.absenceRequests.map(r => `
              <tr>
                <td style="font-weight: 700; color: var(--primary);">${r.id}</td>
                <td style="font-weight: 600;">${r.employee}</td>
                <td>${r.type}</td>
                <td>${r.date}</td>
                <td>${r.approver}</td>
                <td><span class="op-status-pill op-status-approved">${r.status}</span></td>
                <td><button class="op-btn op-btn-sm op-btn-secondary" onclick="alert('Viewing absence details for ${r.employee}')">Review</button></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// Helper handlers for Attendance App
function filterAttendanceTable(query) {
  const q = (query || '').toLowerCase().trim();
  const rows = document.querySelectorAll('#attendanceListTable tbody tr');
  rows.forEach(row => {
    const text = row.innerText.toLowerCase();
    if (!q || text.includes(q)) {
      row.style.display = '';
    } else {
      row.style.display = 'none';
    }
  });
}

function toggleSelectAllAttendances(masterCb) {
  document.querySelectorAll('.att-row-cb').forEach(cb => cb.checked = masterCb.checked);
}

function requestUsersFromDevice() {
  alert('ADMS Command Dispatched: [CMD_REQUEST_USERS] sent to device CUB7252300146.\nDevice will upload full user roster on next heartbeat (~30s).');
}

function resetStamp() {
  alert('Biometric Stamp Reset: Hardware operational timestamp pointer reset to 0.');
}

function importFromCSV() {
  alert('CSV User Importer: Ready to parse exported eSSL / ZKBioSecurity user roster.');
}

function autoMapEmployees() {
  alert('Auto-Mapping Engine: All 12 employee names fuzzy matched against Biometric Device PINs with 100% confidence!');
}

function syncBiometricPunches() {
  alert('ADMS Cloud Poller: Checking for newly arrived punch logs from CUB7252300146... 0 pending logs. System synchronized in real time.');
}

function openManualAttendanceModal() {
  alert('Manual Attendance Entry Wizard:\n• Select Employee\n• Check In / Check Out Timestamps\n• Justification note (tagged as Manual input mode)');
}

let kioskCurrentPin = '1234';
function pressKioskKey(key) {
  if (key === '⌫') {
    kioskCurrentPin = kioskCurrentPin.slice(0, -1);
  } else {
    if (kioskCurrentPin.length < 6) kioskCurrentPin += key;
  }
  const el = document.getElementById('kioskPinDisplay');
  if (el) el.textContent = '•'.repeat(kioskCurrentPin.length) || '----';
}

function clearKioskPin() {
  kioskCurrentPin = '';
  const el = document.getElementById('kioskPinDisplay');
  if (el) el.textContent = '----';
}

function updateKioskPin(empId) {
  clearKioskPin();
}

function submitKioskPunch(action) {
  const select = document.getElementById('kioskEmployeeSelect');
  const empName = select ? select.options[select.selectedIndex].text.split('(')[0].trim() : 'Alex Morgan';
  const now = new Date();
  const timeStr = now.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit', hour12: true });
  const dateStr = now.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  
  // Add record to state
  AppState.attendances.unshift({
    id: 'ATT' + Date.now(),
    employee: empName,
    avatarLetter: empName[0],
    avatarColor: '#0284c7',
    checkIn: `${dateStr}, ${timeStr}`,
    checkOut: action === 'Check Out' ? `${dateStr}, ${timeStr}` : '--',
    workedHours: action === 'Check Out' ? '08:15' : 'In Progress',
    extraHours: '00:00',
    inputModeIn: 'Biometric',
    inputModeOut: action === 'Check Out' ? 'Biometric' : '--'
  });
  saveState();
  
  alert(`✅ Biometric Punch Recorded!\n\nEmployee: ${empName}\nAction: ${action}\nTime: ${dateStr}, ${timeStr}\nTerminal: CUB7252300146 (Push Active)\n\nAttendance ledger updated dynamically.`);
  clearKioskPin();
}

// -------------------------------------------------------------
// 6. Leave / Time Off Module (Calendar, Approvals & Allocations)
// -------------------------------------------------------------

function renderLeaveView(param = null) {
  if (param === 'my-time-off') {
    return renderMyTimeOffListView();
  }
  if (param === 'management-approvals') {
    return renderLeaveManagementApprovalsView();
  }
  if (param === 'management-allocations') {
    return renderLeaveManagementAllocationsView();
  }
  return renderTimeOffCalendarDashboardView();
}

function renderLeaveSubbar(activeTab = 'calendar') {
  return `
    <div class="op-subbar">
      <span class="op-subbar-item ${activeTab === 'calendar' ? 'active' : ''}" onclick="navigateTo('leave')">Time Off</span>
      <span class="op-subbar-item ${activeTab === 'my-time' ? 'active' : ''}" onclick="navigateTo('leave', 'my-time-off')">My Time</span>
      <span class="op-subbar-item" onclick="alert('Time Off Overview')">Overview</span>
      <div class="op-subbar-dropdown">
        <span class="op-subbar-item ${activeTab === 'management' ? 'active' : ''}">
          Management ▾ <span style="font-size: 10px; background: rgba(255,255,255,0.2); padding: 1px 5px; border-radius: 3px;">Manager</span>
        </span>
        <div class="op-subbar-dropdown-menu">
          <div class="op-subbar-dropdown-header">Approvals & Allocations</div>
          <div class="op-subbar-dropdown-item" onclick="navigateTo('leave', 'management-approvals')">Time Off (Approvals)</div>
          <div class="op-subbar-dropdown-item" onclick="navigateTo('leave', 'management-allocations')">Allocations</div>
        </div>
      </div>
      <span class="op-subbar-item" onclick="alert('Leave Reports & Monthly Accruals')">Reporting</span>
      <span class="op-subbar-item" onclick="navigateTo('technical')">Configuration</span>
    </div>
  `;
}

// 6.1 Time Off Monthly Calendar Dashboard Matching Image 1
function renderTimeOffCalendarDashboardView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderLeaveSubbar('calendar')}

      <!-- Control Bar Matching Image 1 -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="openLeaveApplyModal()">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>Time Off</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div style="display: flex; align-items: center; gap: 8px; font-weight: 700; font-size: 14px; color: #334155;">
            <button class="op-view-btn" onclick="alert('Previous Month')">&lt;</button>
            <span>October 2026</span>
            <button class="op-view-btn" onclick="alert('Next Month')">&gt;</button>
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" onclick="alert('Day View')">Day</button>
            <button class="op-view-btn" onclick="alert('Week View')">Week</button>
            <button class="op-view-btn active" title="Month Calendar" onclick="navigateTo('leave')">Month</button>
            <button class="op-view-btn" title="My Time Off List" onclick="navigateTo('leave', 'my-time-off')">📋</button>
            <button class="op-view-btn" title="Management Approvals" onclick="navigateTo('leave', 'management-approvals')">⚡</button>
          </div>
        </div>
      </div>

      <!-- Balance Ledger KPI Cards -->
      <div class="op-kpi-grid" style="margin-bottom: 16px;">
        <div class="op-kpi-card">
          <div class="op-kpi-icon" style="background: #e0f2fe; color: #0284c7;">🌴</div>
          <div class="op-kpi-info">
            <h4>Vacation Leave</h4>
            <div class="val">${AppState.leaveBalances.vacation} Days</div>
          </div>
        </div>
        <div class="op-kpi-card">
          <div class="op-kpi-icon" style="background: #fee2e2; color: #ef4444;">🏥</div>
          <div class="op-kpi-info">
            <h4>Sick Leave</h4>
            <div class="val">${AppState.leaveBalances.sick} Days</div>
          </div>
        </div>
        <div class="op-kpi-card">
          <div class="op-kpi-icon" style="background: #d1fae5; color: #059669;">⚡</div>
          <div class="op-kpi-info">
            <h4>Comp-Off Balance</h4>
            <div class="val">${AppState.leaveBalances.compensatory} Days</div>
          </div>
        </div>
        <div class="op-kpi-card">
          <div class="op-kpi-icon" style="background: #fef3c7; color: #d97706;">🎉</div>
          <div class="op-kpi-info">
            <h4>Festival / Flexi</h4>
            <div class="val">${AppState.leaveBalances.festival + AppState.leaveBalances.flexible} Days</div>
          </div>
        </div>
      </div>

      <!-- Monthly Calendar Grid Matching Image 1 -->
      <div class="op-cal-container">
        <div class="op-cal-header">
          <div>SUN</div>
          <div>MON</div>
          <div>TUE</div>
          <div>WED</div>
          <div>THU</div>
          <div>FRI</div>
          <div>SAT</div>
        </div>

        <div class="op-cal-grid">
          <!-- Week 1: Sep 27 - Oct 3 -->
          <div class="op-cal-cell other-month weekend"><div class="op-cal-cell-day">27</div></div>
          <div class="op-cal-cell other-month"><div class="op-cal-cell-day">28</div></div>
          <div class="op-cal-cell other-month"><div class="op-cal-cell-day">29</div></div>
          <div class="op-cal-cell other-month"><div class="op-cal-cell-day">30</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">1</div></div>
          <div class="op-cal-cell">
            <div class="op-cal-cell-day">2</div>
            <span class="op-cal-badge holiday" title="Public Holiday">🔴 Gandhi Jayanti</span>
          </div>
          <div class="op-cal-cell weekend"><div class="op-cal-cell-day">3</div></div>

          <!-- Week 2: Oct 4 - Oct 10 -->
          <div class="op-cal-cell weekend today">
            <div class="op-cal-cell-day">4</div>
            <span class="op-cal-badge compoff" title="Present / Active">● Today (Shift)</span>
          </div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">5</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">6</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">7</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">8</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">9</div></div>
          <div class="op-cal-cell weekend">
            <div class="op-cal-cell-day">10</div>
            <span class="op-cal-badge holiday" title="Company Holiday">🔵 2nd Saturday</span>
          </div>

          <!-- Week 3: Oct 11 - Oct 17 -->
          <div class="op-cal-cell weekend"><div class="op-cal-cell-day">11</div></div>
          <div class="op-cal-cell">
            <div class="op-cal-cell-day">12</div>
            <span class="op-cal-badge vacation" onclick="navigateTo('leave', 'management-approvals')" title="Amit Verma - Vacation">🌴 Amit (Vacation)</span>
          </div>
          <div class="op-cal-cell">
            <div class="op-cal-cell-day">13</div>
            <span class="op-cal-badge vacation" onclick="navigateTo('leave', 'management-approvals')" title="Amit Verma - Vacation">🌴 Amit (Vacation)</span>
          </div>
          <div class="op-cal-cell">
            <div class="op-cal-cell-day">14</div>
            <span class="op-cal-badge vacation" onclick="navigateTo('leave', 'management-approvals')" title="Amit Verma - Vacation">🌴 Amit (Vacation)</span>
          </div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">15</div></div>
          <div class="op-cal-cell">
            <div class="op-cal-cell-day">16</div>
            <span class="op-cal-badge compoff" onclick="navigateTo('leave', 'management-approvals')" title="Elena Rostova - Comp-Off">⚡ Elena (Comp-Off)</span>
          </div>
          <div class="op-cal-cell weekend"><div class="op-cal-cell-day">17</div></div>

          <!-- Week 4: Oct 18 - Oct 24 -->
          <div class="op-cal-cell weekend"><div class="op-cal-cell-day">18</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">19</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">20</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">21</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">22</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">23</div></div>
          <div class="op-cal-cell weekend">
            <div class="op-cal-cell-day">24</div>
            <span class="op-cal-badge holiday" title="Public Holiday">🔴 Dussehra</span>
          </div>

          <!-- Week 5: Oct 25 - Oct 31 -->
          <div class="op-cal-cell weekend"><div class="op-cal-cell-day">25</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">26</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">27</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">28</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">29</div></div>
          <div class="op-cal-cell"><div class="op-cal-cell-day">30</div></div>
          <div class="op-cal-cell weekend">
            <div class="op-cal-cell-day">31</div>
            <span class="op-cal-badge holiday" title="Company Holiday">🔵 4th Saturday</span>
          </div>
        </div>
      </div>
    </div>
  `;
}

// 6.2 My Time Off List View Matching Image 2
function renderMyTimeOffListView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderLeaveSubbar('my-time')}

      <!-- Control Bar -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="openLeaveApplyModal()">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>My Time Off</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 260px;">
            <span>🔍</span>
            <input type="text" placeholder="Search my requests...">
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" title="Calendar" onclick="navigateTo('leave')">📅</button>
            <button class="op-view-btn active" title="List" onclick="navigateTo('leave', 'my-time-off')">📋</button>
          </div>
        </div>
      </div>

      <!-- My Time Off List Table Matching Image 2 -->
      <div class="op-table-card">
        <table class="op-table">
          <thead>
            <tr>
              <th>Time Off Type</th>
              <th>Description</th>
              <th>Start Date</th>
              <th>End Date</th>
              <th>Duration (Days)</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            ${AppState.leaveRequests.map(r => `
              <tr>
                <td style="font-weight: 700; color: var(--primary);">${r.type}</td>
                <td>${r.reason}</td>
                <td>${r.fromDate}</td>
                <td>${r.toDate}</td>
                <td style="font-weight: bold;">${r.days} days</td>
                <td>
                  <span class="op-status-pill ${r.overallStatus === 'Approved' ? 'op-status-approved' : 'op-status-pending'}">
                    ${r.overallStatus}
                  </span>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 6.3 Management > Time Off Approvals Matching Image 3
function renderLeaveManagementApprovalsView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderLeaveSubbar('management')}

      <!-- Control Bar -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="openLeaveApplyModal()">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>Management &gt; Time Off Approvals</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 260px;">
            <span>🔍</span>
            <input type="text" placeholder="Search requests to approve...">
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" title="Calendar" onclick="navigateTo('leave')">📅</button>
            <button class="op-view-btn active" title="Approvals Kanban" onclick="navigateTo('leave', 'management-approvals')">🗂️</button>
            <button class="op-view-btn" title="Allocations" onclick="navigateTo('leave', 'management-allocations')">⚡</button>
          </div>
        </div>
      </div>

      <!-- 3-Column Approval Cards with TO APPROVE Ribbon Banner Matching Image 3 -->
      <div class="op-approval-grid">
        ${AppState.leaveRequests.map(r => `
          <div class="op-approval-card">
            ${r.overallStatus === 'To Approve' ? `
              <div class="op-ribbon-to-approve">To Approve</div>
            ` : ''}

            <div class="op-approval-card-body">
              <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 12px;">
                <div style="width: 38px; height: 38px; border-radius: 6px; background: ${r.avatarColor || '#0284c7'}; color: #fff; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 16px;">
                  ${r.avatarLetter || r.employee[0]}
                </div>
                <div>
                  <div style="font-size: 15px; font-weight: 700; color: var(--text-main);">${r.employee}</div>
                  <div style="font-size: 11.5px; color: #64748b;">${r.dept || 'Engineering'}</div>
                </div>
              </div>

              <div style="margin-bottom: 10px;">
                <div style="font-size: 13px; font-weight: 700; color: var(--primary);">${r.type}</div>
                <div style="font-size: 12px; color: #475569; margin: 2px 0;">📅 ${r.fromDate} &rarr; ${r.toDate} (<b>${r.days} Days</b>)</div>
                <div style="font-size: 12px; color: #64748b; font-style: italic;">"${r.reason}"</div>
              </div>

              <div style="background: #f8fafc; padding: 6px 10px; border-radius: 4px; border: 1px solid #e2e8f0; font-size: 11.5px; color: #475569;">
                ● Balance: <b>${r.currentBalance}</b>
              </div>
            </div>

            <div class="op-approval-card-actions">
              ${r.overallStatus === 'To Approve' ? `
                <button class="op-btn op-btn-sm op-btn-primary" style="background: var(--primary); flex: 1;" onclick="validateLeaveApproval('${r.id}')">Validate</button>
                <button class="op-btn op-btn-sm op-btn-secondary" style="color: #ef4444; flex: 1;" onclick="refuseLeaveApproval('${r.id}')">Refuse</button>
              ` : `
                <span style="color: #16a34a; font-weight: 700; font-size: 12px;">✓ Approved & Synced to Timesheets</span>
              `}
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

// 6.4 Management > Allocations Matching Image 4
function renderLeaveManagementAllocationsView() {
  return `
    <div style="max-width: 1250px; margin: 0 auto;">
      <!-- Odoo Subbar -->
      ${renderLeaveSubbar('management')}

      <!-- Control Bar -->
      <div class="op-control-bar" style="margin-bottom: 12px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="alert('Simulation: Create New Leave Allocation Wizard')">New</button>
          <div class="op-control-title" style="font-size: 16px;">
            <span>Management &gt; Allocations</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <div class="op-search-box" style="width: 260px;">
            <span>🔍</span>
            <input type="text" placeholder="Search allocations...">
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" title="Calendar" onclick="navigateTo('leave')">📅</button>
            <button class="op-view-btn" title="Approvals" onclick="navigateTo('leave', 'management-approvals')">🗂️</button>
            <button class="op-view-btn active" title="Allocations" onclick="navigateTo('leave', 'management-allocations')">⚡</button>
          </div>
        </div>
      </div>

      <!-- Allocations Table Matching Image 4 -->
      <div class="op-table-card">
        <table class="op-table">
          <thead>
            <tr>
              <th>Allocation ID</th>
              <th>Employee</th>
              <th>Allocation Type</th>
              <th>Allocated Days</th>
              <th>Source / Justification</th>
              <th>Effective Date</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${AppState.leaveAllocations.map(a => `
              <tr>
                <td style="font-weight: 700; color: var(--primary);">${a.id}</td>
                <td style="font-weight: 600;">${a.employee}</td>
                <td>${a.type}</td>
                <td style="font-weight: bold; color: #16a34a;">+${a.allocatedDays} d</td>
                <td>${a.reason}</td>
                <td>${a.date}</td>
                <td><span class="op-status-pill ${a.status === 'Approved' ? 'op-status-approved' : 'op-status-pending'}">${a.status}</span></td>
                <td>
                  ${a.status === 'To Approve' ? `
                    <button class="op-btn op-btn-sm op-btn-primary" style="background: var(--primary);" onclick="approveAllocation('${a.id}')">Validate</button>
                  ` : `
                    <span style="color: #64748b; font-size: 12px;">Processed</span>
                  `}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function validateLeaveApproval(reqId) {
  const req = AppState.leaveRequests.find(r => r.id === reqId);
  if (req) {
    req.overallStatus = 'Approved';
    req.level1Status = 'Approved';
    req.level2Status = 'Approved';
    saveState();
    renderAppView('leave', 'management-approvals');
    alert(`Leave Approved: ${req.id} for ${req.employee} validated successfully!\nAutomatically synced 8h/day non-project block into weekly timesheets.`);
  }
}

function refuseLeaveApproval(reqId) {
  const req = AppState.leaveRequests.find(r => r.id === reqId);
  if (req) {
    req.overallStatus = 'Refused';
    saveState();
    renderAppView('leave', 'management-approvals');
    alert(`Leave Refused: ${req.id} rejected.`);
  }
}

function approveAllocation(alcId) {
  const alc = AppState.leaveAllocations.find(a => a.id === alcId);
  if (alc) {
    alc.status = 'Approved';
    saveState();
    renderAppView('leave', 'management-allocations');
    alert(`Allocation Approved: ${alc.id} (+${alc.allocatedDays} days) credited to ${alc.employee}.`);
  }
}

function openLeaveApplyModal() {
  alert('Leave Application Wizard:\n• Select Leave Type (Vacation, Sick, Comp-Off)\n• Start Date & End Date (Backdated entries blocked)\n• Automated balance deduction check\n• 2-Tier approval chain: L1 (Reporting Manager) ➔ L2 (Executive Approver)');
}

// 7. Expense Management
function renderExpenseView() {
  return `
    <div style="max-width: 1100px; margin: 0 auto;">
      <div class="op-control-bar" style="margin-bottom: 16px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <div class="op-control-title">
            <span>💳 Expense Management & Reimbursements</span>
            <span class="op-debug-badge">Model: hr.expense</span>
          </div>
          <button class="op-btn op-btn-primary" onclick="alert('Simulation: Create Expense Claim with Receipt Attachment')">+ Submit Expense</button>
        </div>
      </div>

      <div class="op-table-card">
        <div style="padding: 14px 18px; background: #f8fafc; border-bottom: 1px solid var(--border-color); font-weight: bold; display: flex; justify-content: space-between;">
          <span>Employee Out-of-Pocket Claims</span>
          <span style="font-size: 12px; color: var(--text-muted);">Cost Allocation: Company Overhead vs Direct Project Tagging</span>
        </div>
        <table class="op-table">
          <thead>
            <tr>
              <th>Claim Ref</th>
              <th>Employee</th>
              <th>Date</th>
              <th>Category</th>
              <th>Cost Tagging</th>
              <th>Amount</th>
              <th>Receipt</th>
              <th>Approval Flow</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            ${AppState.expenses.map(e => `
              <tr>
                <td style="font-weight: 700; color: var(--primary);">${e.id}</td>
                <td style="font-weight: 600;">${e.employee}</td>
                <td>${e.date}</td>
                <td>${e.category}</td>
                <td><span style="font-size: 11px; background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-weight: 600;">${e.taggedTo}</span></td>
                <td style="font-weight: 700; color: var(--text-main);">₹ ${e.amount.toLocaleString('en-IN')}</td>
                <td><a href="javascript:alert('Previewing Receipt: ${e.receipt}')" style="color: var(--primary); font-weight: 600; text-decoration: none;">📎 View Bill</a></td>
                <td><span class="op-status-pill ${e.l2Status === 'Approved' ? 'op-status-approved' : 'op-status-pending'}">${e.status}</span></td>
                <td>
                  ${e.l2Status === 'Pending' ? `
                    <button class="op-btn op-btn-sm op-btn-success" onclick="approveExpenseL2('${e.id}')">Finance Release</button>
                  ` : `<span style="color: var(--success); font-weight: bold;">✓ Paid</span>`}
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function approveExpenseL2(id) {
  const exp = AppState.expenses.find(e => e.id === id);
  if (exp) {
    exp.l2Status = 'Approved';
    exp.status = 'Approved & Reimbursed';
    saveState();
    renderAppView('expense');
    alert(`Expense Claim ${id} approved by Finance! Journal entry debited to project.`);
  }
}

// 8. Accounting & Project Profitability Engine
function renderAccountingView() {
  return `
    <div style="max-width: 1100px; margin: 0 auto;">
      <div class="op-control-bar" style="margin-bottom: 16px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <div class="op-control-title">
            <span>💰 Accounting, GST Invoicing & Project Profitability</span>
            <span class="op-debug-badge">Model: account.invoice</span>
          </div>
          <button class="op-btn op-btn-primary" onclick="alert('Simulation: Open Tax Invoice Generator Wizard')">+ Create Tax Invoice</button>
        </div>
      </div>

      <!-- Profitability Summary Hero Card -->
      <div style="background: #ffffff; border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 24px; margin-bottom: 24px; box-shadow: var(--shadow-sm);">
        <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 12px; color: var(--text-main);">
          📈 Real-Time Project Gross Margin & Profitability Engine
        </h3>
        <p style="font-size: 13px; color: var(--text-muted); margin-bottom: 16px;">
          Calculated dynamically as: <b>Gross Profit = Invoiced Revenue - [(Logged Timesheet Hours × Employee Hourly CTC) + Direct Tagged Expenses]</b>
        </p>

        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;">
          <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px;">
            <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">PRJ/2026/001: Tech Park Phase 2</div>
            <div style="font-size: 20px; font-weight: 700; color: #059669; margin: 4px 0;">₹ 14,51,800 Margin</div>
            <div style="font-size: 12px; color: var(--text-muted);">Revenue: ₹18.5L | Labor Cost: ₹3.50L | Expense: ₹48K</div>
            <div style="margin-top: 8px; font-size: 11px; font-weight: bold; color: var(--success);">78.4% Profit Margin</div>
          </div>

          <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px;">
            <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">PRJ/2026/002: Metro Station Canopy</div>
            <div style="font-size: 20px; font-weight: 700; color: #059669; margin: 4px 0;">₹ 7,16,000 Margin</div>
            <div style="font-size: 12px; color: var(--text-muted);">Revenue: ₹9.5L | Labor Cost: ₹2.04L | Expense: ₹30K</div>
            <div style="margin-top: 8px; font-size: 11px; font-weight: bold; color: var(--success);">75.3% Profit Margin</div>
          </div>

          <div style="background: #f8fafc; border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 16px;">
            <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">PRJ/2026/003: Corporate HQ Interior</div>
            <div style="font-size: 20px; font-weight: 700; color: #059669; margin: 4px 0;">₹ 19,10,000 Margin</div>
            <div style="font-size: 12px; color: var(--text-muted);">Revenue: ₹24.0L | Labor Cost: ₹4.33L | Expense: ₹57K</div>
            <div style="margin-top: 8px; font-size: 11px; font-weight: bold; color: var(--success);">79.5% Profit Margin</div>
          </div>
        </div>
      </div>

      <!-- Invoices Ledger -->
      <div class="op-table-card">
        <div style="padding: 14px 18px; background: #f8fafc; border-bottom: 1px solid var(--border-color); font-weight: bold;">
          Customer Tax Invoices (GST & HSN Compliant)
        </div>
        <table class="op-table">
          <thead>
            <tr>
              <th>Invoice #</th>
              <th>Date</th>
              <th>Client</th>
              <th>Project & Billing Type</th>
              <th>Taxable Base</th>
              <th>GST (18%)</th>
              <th>Total (INR)</th>
              <th>Status</th>
              <th>Print</th>
            </tr>
          </thead>
          <tbody>
            ${AppState.invoices.map(inv => `
              <tr>
                <td style="font-weight: 700; color: var(--primary);">${inv.id}</td>
                <td>${inv.date}</td>
                <td style="font-weight: 600;">${inv.client}</td>
                <td>
                  <div style="font-size: 12px; font-weight: 600;">${inv.project}</div>
                  <div style="font-size: 11px; color: var(--text-muted);">${inv.billingType}</div>
                </td>
                <td>₹ ${inv.baseAmount.toLocaleString('en-IN')}</td>
                <td style="font-size: 11px;">CGST: ₹${inv.cgst.toLocaleString('en-IN')}<br>SGST: ₹${inv.sgst.toLocaleString('en-IN')}</td>
                <td style="font-weight: 700; color: #059669;">₹ ${inv.totalAmount.toLocaleString('en-IN')}</td>
                <td><span class="op-status-pill ${inv.status === 'Paid' ? 'op-status-approved' : 'op-status-pending'}">${inv.status}</span></td>
                <td><button class="op-btn op-btn-sm op-btn-secondary" onclick="alert('Simulation: Generating GST Compliant PDF for ${inv.id}')">📄 PDF</button></td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

// 9. Webmail Suite 3-Pane View
function renderMailView(selectedId = 1) {
  const mail = AppState.webmail.find(m => m.id == selectedId) || AppState.webmail[0];
  
  return `
    <div class="op-mail-container">
      <!-- Pane 1: Folders Sidebar -->
      <div class="op-mail-folders">
        <button class="op-btn op-btn-primary" style="margin-bottom: 12px;" onclick="alert('Simulation: Open Webmail Composer')">
          ✏️ Compose
        </button>
        <div class="op-mail-folder-item active">
          <span>📥 Inbox</span>
          <span style="background: var(--primary); color: white; border-radius: 10px; font-size: 10px; padding: 1px 6px;">1</span>
        </div>
        <div class="op-mail-folder-item">
          <span>⭐ Starred</span>
        </div>
        <div class="op-mail-folder-item">
          <span>📤 Sent</span>
        </div>
        <div class="op-mail-folder-item">
          <span>📝 Drafts</span>
        </div>
        <div class="op-mail-folder-item">
          <span>🗑️ Trash</span>
        </div>
      </div>

      <!-- Pane 2: Messages List -->
      <div class="op-mail-list">
        <div style="padding: 10px 14px; background: #f8fafc; border-bottom: 1px solid var(--border-color); font-weight: bold; font-size: 12px;">
          All Messages (mail.mail)
        </div>
        ${AppState.webmail.map(m => `
          <div class="op-mail-item ${m.id == mail.id ? 'selected' : ''} ${m.unread ? 'unread' : ''}" onclick="navigateTo('mail', ${m.id})">
            <div style="display: flex; justify-content: space-between; margin-bottom: 2px;">
              <span style="font-weight: 700; font-size: 12.5px;">${m.senderName}</span>
              <span style="font-size: 10.5px; color: var(--text-muted);">${m.date}</span>
            </div>
            <div class="op-mail-subject" style="font-size: 12px; margin-bottom: 4px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              ${m.subject}
            </div>
            <div style="font-size: 11px; color: var(--text-muted); overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
              ${m.body.substring(0, 60)}...
            </div>
          </div>
        `).join('')}
      </div>

      <!-- Pane 3: Reading Pane -->
      <div class="op-mail-preview">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; padding-bottom: 16px; border-bottom: 1px solid var(--border-color); margin-bottom: 16px;">
          <div>
            <h2 style="font-size: 18px; font-weight: 700; margin-bottom: 6px; color: var(--text-main);">${mail.subject}</h2>
            <div style="font-size: 12.5px; color: var(--text-muted);">
              From: <b>${mail.senderName}</b> &lt;${mail.sender}&gt;
            </div>
          </div>
          <div style="font-size: 12px; color: var(--text-muted);">${mail.date}</div>
        </div>

        <div style="white-space: pre-wrap; font-size: 13.5px; line-height: 1.6; color: var(--text-main); flex: 1;">
${mail.body}
        </div>

        <div style="margin-top: 20px; padding-top: 14px; border-top: 1px solid var(--border-color); display: flex; gap: 8px;">
          <button class="op-btn op-btn-secondary" onclick="alert('Simulation: Reply to ${mail.sender}')">↩️ Reply</button>
          <button class="op-btn op-btn-secondary" onclick="alert('Simulation: Forward email')">↪️ Forward</button>
        </div>
      </div>
    </div>
  `;
}

// 10. Technical Subsystem (ir.* Registry & Crons)
function renderTechnicalView() {
  return `
    <div style="max-width: 1100px; margin: 0 auto;">
      <div class="op-control-bar" style="margin-bottom: 16px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <div class="op-control-title">
            <span>⚙️ Technical Metadata & Runtime Engine</span>
            <span class="op-debug-badge">Developer Mode (?debug=1)</span>
          </div>
        </div>
        <div class="op-control-right">
          <button class="op-btn op-btn-primary" onclick="alert('Signal Trigger: Auto-syncing Django models into ir.model & ir.model.fields')">🔄 Run Model Discovery Sync</button>
        </div>
      </div>

      <!-- Cron Jobs Section -->
      <div class="op-sheet" style="margin-bottom: 24px;">
        <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 6px; color: var(--text-main);">
          ⏱️ Scheduled Cron Actions (ir.cron)
        </h3>
        <p style="font-size: 12.5px; color: var(--text-muted); margin-bottom: 16px;">
          Background jobs executing automated sequence number generators, timesheet deadline audits, and leave accruals.
        </p>

        <table class="op-table">
          <thead>
            <tr>
              <th>Cron Action Name</th>
              <th>Execution Interval</th>
              <th>Next Scheduled Run</th>
              <th>State</th>
              <th>Manual Trigger</th>
            </tr>
          </thead>
          <tbody>
            ${AppState.technicalRegistry.crons.map(c => `
              <tr>
                <td style="font-weight: 700;">${c.name}</td>
                <td>${c.interval}</td>
                <td style="font-family: monospace; font-size: 12px;">${c.nextRun}</td>
                <td><span class="op-status-pill op-status-approved">${c.status}</span></td>
                <td>
                  <button class="op-btn op-btn-sm op-btn-secondary" onclick="runCronManually('${c.name}')">▶ Run Manually</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>

      <!-- Models Registry (ir.model) -->
      <div class="op-sheet">
        <h3 style="font-size: 16px; font-weight: 700; margin-bottom: 6px; color: var(--text-main);">
          🗃️ Models Registry (ir.model & ir.model.fields)
        </h3>
        <p style="font-size: 12.5px; color: var(--text-muted); margin-bottom: 16px;">
          Registered database models catalogued dynamically during Django migrations.
        </p>

        <table class="op-table">
          <thead>
            <tr>
              <th>Model Key (_name)</th>
              <th>Description</th>
              <th>Module</th>
              <th>PostgreSQL Table</th>
              <th>Records</th>
            </tr>
          </thead>
          <tbody>
            ${AppState.technicalRegistry.models.map(m => `
              <tr>
                <td style="font-weight: 700; color: var(--primary); font-family: monospace;">${m.key}</td>
                <td style="font-weight: 600;">${m.name}</td>
                <td><span class="op-status-pill op-status-draft">${m.module}</span></td>
                <td style="font-family: monospace; font-size: 12px;">${m.table}</td>
                <td style="font-weight: bold;">${m.count}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    </div>
  `;
}

function runCronManually(name) {
  alert(`Triggered Cron Job: [${name}] executed successfully! System log updated.`);
}

// -------------------------------------------------------------
// 10. Apps Store & Custom Modules (ir.module.module)
// -------------------------------------------------------------
function renderAppsStoreView() {
  const modules = (AppState.installedModules && AppState.installedModules.length > 0) ? AppState.installedModules : INITIAL_DATA.installedModules;
  return `
    <div style="max-width: 1350px; margin: 0 auto;">
      <!-- Odoo Subbar Matching Screenshot -->
      <div class="op-subbar">
        <span class="op-subbar-item active" onclick="navigateTo('apps')">Apps</span>
        <span class="op-subbar-item" onclick="alert('Update Apps List: Scanning filesystem addons directory... 11 custom modules verified.')">Update Apps List</span>
        <span class="op-subbar-item" onclick="alert('Apply Scheduled Upgrades: Checking database migration triggers... 0 pending upgrades.')">Apply Scheduled Upgrades</span>
        <span class="op-subbar-item" onclick="alert('Import Module: Upload ZIP package wizard initialized.')">Import Module</span>
      </div>

      <!-- Control Bar Matching Screenshot -->
      <div class="op-control-bar" style="margin-bottom: 14px; border-radius: var(--radius-md);">
        <div class="op-control-left">
          <div class="op-control-title" style="font-size: 16px;">
            <span>Apps</span>
            <span style="font-size: 12px; color: #64748b; cursor: pointer;" title="Apps Configuration">⚙️</span>
          </div>
        </div>

        <div class="op-control-right">
          <!-- Search Box with Yellow Filter Chip matching Screenshot -->
          <div class="op-search-box" style="width: 320px; display: flex; align-items: center; background: #ffffff; padding: 4px 10px;">
            <span class="op-filter-chip">
              ★ Office Pro <span class="op-filter-chip-remove" onclick="clearAppFilter(event)" title="Clear filter">✕</span>
            </span>
            <input type="text" id="appsSearchInput" placeholder="Search..." oninput="filterModuleCards(this.value)" style="border: none; outline: none; background: transparent; flex: 1; font-size: 13px;">
          </div>
          <div style="font-size: 12px; color: var(--text-muted); font-weight: 600;">
            1-${modules.length} / ${modules.length}
          </div>
          <div class="op-view-switcher">
            <button class="op-view-btn" onclick="alert('Previous page')">&lt;</button>
            <button class="op-view-btn" onclick="alert('Next page')">&gt;</button>
            <button class="op-view-btn active" title="Kanban Cards Grid" onclick="navigateTo('apps')">🗂️</button>
            <button class="op-view-btn" title="List View" onclick="alert('Switch to Module List Table View')">📋</button>
          </div>
        </div>
      </div>

      <!-- Main Layout with Left Sidebar & 4-Column Module Cards Grid -->
      <div class="op-apps-store-layout">
        <!-- Left Category Sidebar -->
        <div class="op-apps-sidebar">
          <div class="op-apps-sidebar-header">Categories</div>
          <div class="op-apps-category-item active" onclick="filterModuleCategory('All', this)">
            <span>All</span>
            <span class="op-apps-category-count">${modules.length}</span>
          </div>
          <div class="op-apps-category-item" onclick="filterModuleCategory('Human Resources', this)">
            <span>Human Resources</span>
            <span class="op-apps-category-count">4</span>
          </div>
          <div class="op-apps-category-item" onclick="filterModuleCategory('Services & Projects', this)">
            <span>Services & Projects</span>
            <span class="op-apps-category-count">3</span>
          </div>
          <div class="op-apps-category-item" onclick="filterModuleCategory('Finance & Accounting', this)">
            <span>Accounting</span>
            <span class="op-apps-category-count">1</span>
          </div>
          <div class="op-apps-category-item" onclick="filterModuleCategory('Hardware & Biometrics', this)">
            <span>Hardware & ADMS</span>
            <span class="op-apps-category-count">1</span>
          </div>
          <div class="op-apps-category-item" onclick="filterModuleCategory('Productivity & Dashboard', this)">
            <span>Dashboard</span>
            <span class="op-apps-category-count">1</span>
          </div>
          <div class="op-apps-category-item" onclick="filterModuleCategory('UI & Customization', this)">
            <span>UI Customization</span>
            <span class="op-apps-category-count">1</span>
          </div>
        </div>

        <!-- 4-Column Module Cards Grid Matching Screenshot -->
        <div class="op-module-grid" id="appsModuleGrid">
          ${modules.map(m => `
            <div class="op-module-card" data-category="${m.category}" data-key="${m.key}">
              <!-- Module Icon SVG matching screenshot -->
              <div class="op-module-icon-wrap">
                ${m.iconType === 'dashboard' ? `
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none">
                    <rect x="2" y="3" width="9" height="5" rx="1" fill="#f43f5e" />
                    <rect x="13" y="3" width="9" height="9" rx="1" fill="#f59e0b" />
                    <rect x="2" y="10" width="9" height="11" rx="1" fill="#38bdf8" />
                    <rect x="13" y="14" width="9" height="7" rx="1" fill="#10b981" />
                  </svg>
                ` : `
                  <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#00a09d" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"></path>
                    <polyline points="3.27 6.96 12 12.01 20.73 6.96"></polyline>
                    <line x1="12" y1="22.08" x2="12" y2="12"></line>
                  </svg>
                `}
              </div>

              <!-- Module Card Info -->
              <div class="op-module-card-content">
                <div>
                  <div class="op-module-card-header">
                    <div class="op-module-title" title="${m.name}">${m.name}</div>
                    <button class="op-module-kebab" onclick="openModuleKebabMenu('${m.key}')" title="Module Options">⋮</button>
                  </div>
                  <div class="op-module-key" title="${m.key}">${m.key}</div>
                </div>

                <button class="op-module-action-btn" onclick="openModuleInfoModal('${m.key}')">
                  ${m.btnLabel || 'Learn More'}
                </button>
              </div>
            </div>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- Module Info Modal Container -->
    <div id="moduleInfoModalContainer"></div>
  `;
}

function filterModuleCards(query) {
  const q = (query || '').toLowerCase().trim();
  const cards = document.querySelectorAll('#appsModuleGrid .op-module-card');
  cards.forEach(card => {
    const text = card.innerText.toLowerCase();
    const key = (card.getAttribute('data-key') || '').toLowerCase();
    if (!q || text.includes(q) || key.includes(q)) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });
}

function filterModuleCategory(cat, el) {
  document.querySelectorAll('.op-apps-category-item').forEach(item => item.classList.remove('active'));
  if (el) el.classList.add('active');
  const cards = document.querySelectorAll('#appsModuleGrid .op-module-card');
  cards.forEach(card => {
    const cardCat = card.getAttribute('data-category');
    if (cat === 'All' || cardCat === cat) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });
}

function clearAppFilter(e) {
  if (e) e.stopPropagation();
  const input = document.getElementById('appsSearchInput');
  if (input) input.value = '';
  filterModuleCards('');
}

function openModuleKebabMenu(key) {
  const mod = (AppState.installedModules || []).find(m => m.key === key);
  if (!mod) return;
  alert(`Module Action: [${mod.name}]\n• Technical Key: ${mod.key}\n• State: Installed\n• Version: ${mod.version}\n\nActions:\n[1] Check for Updates\n[2] Module Info\n[3] Re-install Manifest`);
}

function openModuleInfoModal(key) {
  const mod = (AppState.installedModules || []).find(m => m.key === key);
  if (!mod) return;
  const container = document.getElementById('moduleInfoModalContainer');
  if (!container) return;

  container.innerHTML = `
    <div class="op-modal-overlay" onclick="closeModuleInfoModal(event)">
      <div class="op-modal-box" onclick="event.stopPropagation()">
        <div class="op-modal-header">
          <div style="display: flex; align-items: center; gap: 10px;">
            <div style="font-size: 24px;">📦</div>
            <div>
              <h3 style="font-size: 16px; font-weight: 700; color: #1e293b; margin: 0;">${mod.name}</h3>
              <div style="font-family: monospace; font-size: 12px; color: #e11d48;">${mod.key} &bull; v${mod.version}</div>
            </div>
          </div>
          <button class="op-btn op-btn-sm" style="background: transparent; font-size: 18px; padding: 2px 8px;" onclick="closeModuleInfoModal()">&times;</button>
        </div>

        <div class="op-modal-body">
          <div style="margin-bottom: 16px;">
            <span class="op-status-pill op-status-approved" style="font-weight: 700;">● Installed &amp; Active</span>
            <span class="op-status-pill op-status-pending" style="margin-left: 6px;">License: LGPL-3</span>
            <span class="op-status-pill op-status-draft" style="margin-left: 6px;">Category: ${mod.category}</span>
          </div>

          <div style="font-size: 13.5px; color: #334155; line-height: 1.6; margin-bottom: 18px;">
            ${mod.summary}
          </div>

          <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 14px; margin-bottom: 16px;">
            <h4 style="font-size: 12px; font-weight: 700; text-transform: uppercase; color: #64748b; margin-bottom: 8px;">Technical Manifest Details</h4>
            <div style="display: grid; grid-template-columns: 140px 1fr; gap: 6px; font-size: 12.5px;">
              <div style="color: #64748b;">Author:</div>
              <div style="font-weight: 600;">${mod.author}</div>
              <div style="color: #64748b;">Dependencies:</div>
              <div><code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 11px;">${mod.dependencies.join(', ')}</code></div>
              <div style="color: #64748b;">Models Introduced:</div>
              <div><code style="background: #e2e8f0; padding: 2px 6px; border-radius: 4px; font-size: 11px;">${mod.models.join(', ')}</code></div>
            </div>
          </div>
        </div>

        <div class="op-modal-footer">
          <button class="op-btn op-btn-secondary" onclick="alert('Checking manifest updates for ${mod.key}... Up to date.')">🔄 Check Updates</button>
          <button class="op-btn op-btn-primary" style="background: var(--primary);" onclick="closeModuleInfoModal()">Close</button>
        </div>
      </div>
    </div>
  `;
}

function closeModuleInfoModal(e) {
  const container = document.getElementById('moduleInfoModalContainer');
  if (container) container.innerHTML = '';
}

// 11. Guide & HOD Defense Center
function renderDefenseView() {
  return `
    <div style="max-width: 1100px; margin: 0 auto;">
      <div class="op-defense-card" style="background: linear-gradient(135deg, #1e293b, #0f172a); color: white;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
          <h2 style="font-size: 22px; font-weight: 700; color: #38bdf8;">🎓 Project Guide & HOD Defense Hub</h2>
          <span style="background: rgba(56, 189, 248, 0.2); color: #38bdf8; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: bold;">
            Monday Presentation Cheatsheet
          </span>
        </div>
        <p style="font-size: 13.5px; opacity: 0.9; max-width: 800px; line-height: 1.6;">
          This presentation hub prepares you for all high-probability architectural, technical, mathematical, and edge-case questions that your Project Guide and HOD may ask during your presentation.
        </p>
      </div>

      <!-- Category Filter Tabs -->
      <div style="display: flex; gap: 8px; margin-bottom: 16px; overflow-x: auto;">
        <button class="op-btn op-btn-primary" onclick="filterDefenseCategory('All')">All Topics</button>
        <button class="op-btn op-btn-secondary" style="background: #e0f2fe; color: #0369a1; font-weight: bold;" onclick="filterDefenseCategory('5W1H')">🌟 5W1H Foundation (WHAT, WHY, HOW, WHEN)</button>
        <button class="op-btn op-btn-secondary" onclick="filterDefenseCategory('Architecture')">Architecture & Zero-Touch</button>
        <button class="op-btn op-btn-secondary" onclick="filterDefenseCategory('Timesheet')">Timesheet & 8-Hr Rule</button>
        <button class="op-btn op-btn-secondary" onclick="filterDefenseCategory('Approvals')">2-Tier Approvals</button>
        <button class="op-btn op-btn-secondary" onclick="filterDefenseCategory('Accounting')">Profitability & Accounting</button>
        <button class="op-btn op-btn-secondary" onclick="filterDefenseCategory('Security')">Security & Record Rules</button>
      </div>

      <!-- Q&A Accordion -->
      <div id="qaAccordionList">
        ${AppState.presentationQA.map((qa, idx) => `
          <div class="op-qa-item ${idx === 0 ? 'open' : ''}">
            <div class="op-qa-question" onclick="toggleQA(this)">
              <div style="display: flex; align-items: center; gap: 10px;">
                <span style="background: var(--primary-subtle); color: var(--primary); padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">
                  ${qa.category}
                </span>
                <span>${qa.q}</span>
              </div>
              <span class="qa-arrow">▼</span>
            </div>
            <div class="op-qa-answer">
              <div style="font-size: 13.5px; color: var(--text-main); white-space: pre-wrap; line-height: 1.6;">${qa.a}</div>
            </div>
          </div>
        `).join('')}
      </div>
    </div>
  `;
}

function toggleQA(el) {
  const item = el.parentElement;
  item.classList.toggle('open');
}

function filterDefenseCategory(cat) {
  const items = document.querySelectorAll('.op-qa-item');
  items.forEach(item => {
    if (cat === 'All' || item.innerText.includes(cat)) {
      item.style.display = 'block';
    } else {
      item.style.display = 'none';
    }
  });
}

// Initial Load Handler
window.addEventListener('DOMContentLoaded', () => {
  initClock();
  if (AppState.theme) changeTheme(AppState.theme);
  if (AppState.debugMode) {
    document.body.classList.add('debug-mode');
    const btn = document.getElementById('debugToggleBtn');
    if (btn) btn.classList.add('active');
  }
  renderAppView('home');
});
