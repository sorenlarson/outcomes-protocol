// Outcomes Protocol - Interactive Prototype

// State
const state = {
  currentView: 'catalog',
  selectedCategory: null,
  selectedOutcomeType: null,
  wizardStep: 1,
  config: {
    contextSources: [],
    tools: [],
    successCriteria: {},
    deliveryConstraints: {},
    escalationPolicy: {},
    bidStrategy: {},
    guaranteeTerms: {}
  }
};

// Outcome type data
const outcomeTypes = {
  'customer-service': {
    title: 'Customer Service',
    types: [
      {
        id: 'cs.resolve',
        name: 'Resolve Inquiry',
        description: 'Fully resolve customer inquiry end-to-end. Handles whatever the customer needs: questions, transactions, troubleshooting. AI takes appropriate actions and confirms resolution.',
        avgCost: '$0.45',
        avgTime: '2 min',
        successRate: '94%',
        recommended: true,
        verificationModel: 'capi'
      }
    ]
  },
  'code': {
    title: 'Code',
    types: [
      {
        id: 'code.review',
        name: 'Code Review',
        description: 'Review pull request for bugs, security issues, and improvements. Guaranteed against missed critical issues.',
        avgCost: '$1.50',
        avgTime: '10 min',
        successRate: '91%',
        recommended: true,
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '30 days'
      },
      {
        id: 'code.fix',
        name: 'Bug Fix',
        description: 'Diagnose and fix reported bug. Guaranteed against regression or incomplete fix.',
        avgCost: '$5.00',
        avgTime: '30 min',
        successRate: '85%',
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '30 days'
      }
    ]
  },
  'legal': {
    title: 'Legal',
    types: [
      {
        id: 'legal.review',
        name: 'Contract Review',
        description: 'Review contract for risks, problematic clauses, and compliance issues. Guaranteed against missed material risks.',
        avgCost: '$15.00',
        avgTime: '10 min',
        successRate: '96%',
        recommended: true,
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '2 years'
      },
      {
        id: 'legal.summarize',
        name: 'Contract Summary',
        description: 'Extract and summarize key terms, obligations, deadlines, and renewal dates. Guaranteed against material omissions.',
        avgCost: '$5.00',
        avgTime: '5 min',
        successRate: '98%',
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '1 year'
      },
      {
        id: 'legal.compare',
        name: 'Contract Comparison',
        description: 'Compare contract versions with detailed change summary. Guaranteed against missed material changes.',
        avgCost: '$10.00',
        avgTime: '7 min',
        successRate: '97%',
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '1 year'
      },
      {
        id: 'legal.draft_nda',
        name: 'Draft NDA',
        description: 'Generate Non-Disclosure Agreement from party information. Guaranteed against enforceability defects.',
        avgCost: '$12.00',
        avgTime: '8 min',
        successRate: '94%',
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '2 years'
      },
      {
        id: 'legal.draft_msa',
        name: 'Draft MSA',
        description: 'Generate Master Services Agreement with payment terms and liability caps. Guaranteed against drafting defects.',
        avgCost: '$35.00',
        avgTime: '20 min',
        successRate: '91%',
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '2 years'
      },
      {
        id: 'legal.draft_dpa',
        name: 'Draft DPA',
        description: 'Generate GDPR/CCPA-compliant Data Processing Agreement. Guaranteed against compliance defects.',
        avgCost: '$25.00',
        avgTime: '15 min',
        successRate: '93%',
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '2 years'
      }
    ]
  },
  'medical': {
    title: 'Medical',
    types: [
      {
        id: 'medical.scribe',
        name: 'Clinical Scribing',
        description: 'Generate clinical documentation from patient encounter. Guaranteed against documentation errors.',
        avgCost: '$2.50',
        avgTime: 'Real-time',
        successRate: '98%',
        recommended: true,
        verificationModel: 'guarantee',
        guaranteeClaimWindow: '90 days'
      }
    ]
  }
};

// Buyer-provided context sources (execution engines may use additional resources with costs rolled into outcome price)
const contextSources = {
  'customer-service': [
    { id: 'kb', name: 'Your Knowledge Base', icon: '&#128218;', description: 'help.acme.com - 1,247 articles synced', connected: true },
    { id: 'products', name: 'Your Product Catalog', icon: '&#128230;', description: 'MCP Server: products.acme.internal', connected: true },
    { id: 'crm', name: 'Your CRM', icon: '&#128100;', description: 'MCP Server: crm.acme.internal', connected: true },
    { id: 'orders', name: 'Your Order System', icon: '&#128666;', description: 'MCP Server: orders.acme.internal', connected: true },
    { id: 'policies', name: 'Your Policies', icon: '&#128196;', description: 'Refund policy, shipping terms, warranties', connected: false }
  ],
  'code': [
    { id: 'repo', name: 'Your Repository', icon: '&#128193;', description: 'GitHub: acme/main-app (includes Actions, PRs, Issues)', connected: true },
    { id: 'issues', name: 'Your Issue Tracker', icon: '&#128203;', description: 'Linear workspace: ACME', connected: true },
    { id: 'docs', name: 'Your Documentation', icon: '&#128214;', description: 'Confluence: Engineering space', connected: false },
    { id: 'style', name: 'Your Style Guide', icon: '&#128196;', description: 'ESLint config, coding standards', connected: false }
  ],
  'legal': [
    { id: 'contracts', name: 'Your Contract Repository', icon: '&#128451;', description: 'Ironclad: 2,340 contracts indexed', connected: true },
    { id: 'clauses', name: 'Your Clause Library', icon: '&#128218;', description: 'Your approved clause templates and fallbacks', connected: true },
    { id: 'playbook', name: 'Your Negotiation Playbook', icon: '&#128214;', description: 'Your company positions and red lines', connected: true },
    { id: 'policies', name: 'Your Company Policies', icon: '&#128196;', description: 'Your legal, compliance, and procurement policies', connected: true },
    { id: 'matters', name: 'Matter/Deal Context', icon: '&#128188;', description: 'Link to specific matter or deal', connected: false }
  ],
  'medical': [
    { id: 'ehr', name: 'Your EHR System', icon: '&#127973;', description: 'Epic/Cerner FHIR API (patient context, prior encounters)', connected: true },
    { id: 'templates', name: 'Your Note Templates', icon: '&#128196;', description: 'Your SOAP, H&P, and specialty-specific templates', connected: true },
    { id: 'preferences', name: 'Your Clinician Preferences', icon: '&#128100;', description: 'Documentation style and terminology preferences', connected: true },
    { id: 'protocols', name: 'Your Clinical Protocols', icon: '&#128214;', description: 'Your organization-specific guidelines', connected: false }
  ]
};

// Agent resources - capabilities the execution engine provides (not buyer-controlled)
// These are always available and costs are rolled into the outcome price
const agentResources = {
  'customer-service': [],
  'code': [
    { id: 'lsp', name: 'Language Server Protocol', description: 'Code intelligence and analysis' },
    { id: 'static_analysis', name: 'Static Analysis Tools', description: 'Security and quality scanning' }
  ],
  'legal': [
    { id: 'lexis_nexis', name: 'Lexis Nexis', description: 'Legal research and case law' },
    { id: 'sec_edgar', name: 'SEC EDGAR', description: 'Public company filings' },
    { id: 'westlaw', name: 'Westlaw', description: 'Legal precedent database' },
    { id: 'contract_standards', name: 'Contract Standards DB', description: 'Industry-standard clause language' }
  ],
  'medical': [
    { id: 'uptodate', name: 'UpToDate', description: 'Clinical decision support' },
    { id: 'icd10', name: 'ICD-10 Database', description: 'Diagnosis code reference' },
    { id: 'cpt', name: 'CPT Code Database', description: 'Procedure code reference' },
    { id: 'drug_interactions', name: 'Drug Interaction DB', description: 'Medication safety checks' }
  ]
};

// Vertical-specific tools (buyer-controlled actions only)
const verticalTools = {
  'customer-service': {
    readOnly: [
      { id: 'order_status', name: 'Look up order status', checked: true },
      { id: 'product_availability', name: 'Check product availability', checked: true },
      { id: 'customer_history', name: 'View customer history', checked: true },
      { id: 'search_kb', name: 'Search knowledge base', checked: true }
    ],
    writeActions: [
      { id: 'refund', name: 'Process refund', checked: true, hasConfig: true, configLabel: 'Max amount:', configValue: '50', configUnit: 'USD' },
      { id: 'discount', name: 'Apply discount code', checked: true, hasConfig: true, configLabel: 'Allowed codes:', configValue: 'SORRY10, LOYALTY15', configUnit: '' },
      { id: 'cancel', name: 'Cancel order', checked: false, warning: 'High impact action - requires approval' }
    ]
  },
  'code': {
    readOnly: [
      { id: 'read_files', name: 'Read repository files', checked: true },
      { id: 'view_history', name: 'View git history and blame', checked: true },
      { id: 'check_ci', name: 'Check CI/CD status', checked: true },
      { id: 'search_code', name: 'Search codebase', checked: true }
    ],
    writeActions: [
      { id: 'comment', name: 'Post review comments', checked: true, hasConfig: false },
      { id: 'suggest', name: 'Suggest code changes', checked: true, hasConfig: false },
      { id: 'approve', name: 'Approve pull request', checked: false, hasConfig: true, configLabel: 'Auto-approve if:', configValue: 'no critical issues', configUnit: '' },
      { id: 'commit', name: 'Create commits', checked: false, warning: 'Allows direct code changes' }
    ]
  },
  'legal': {
    readOnly: [
      { id: 'search_your_contracts', name: 'Search your contract repository', checked: true },
      { id: 'read_your_playbook', name: 'Read your negotiation playbook', checked: true },
      { id: 'read_your_policies', name: 'Read your company policies', checked: true }
    ],
    writeActions: [
      { id: 'upload_document', name: 'Upload to your document system', checked: true, hasConfig: false },
      { id: 'send_review', name: 'Route to your legal team', checked: false, hasConfig: true, configLabel: 'Route to:', configValue: 'legal-review@acme.com', configUnit: '' },
      { id: 'update_matter', name: 'Update matter status', checked: false, warning: 'Modifies your matter management system' }
    ]
  },
  'medical': {
    readOnly: [
      { id: 'patient_context', name: 'Access patient context from your EHR', checked: true },
      { id: 'prior_encounters', name: 'Reference prior encounters', checked: true },
      { id: 'your_templates', name: 'Use your note templates', checked: true }
    ],
    writeActions: [
      { id: 'save_draft', name: 'Save draft to your EHR', checked: true, hasConfig: false },
      { id: 'route_review', name: 'Route for physician review', checked: true, hasConfig: true, configLabel: 'Route to:', configValue: 'attending physician', configUnit: '' }
    ]
  }
};

// Vertical-specific success criteria
const successCriteria = {
  'customer-service': {
    // For cAPI-verified outcomes like CS, success is defined by a single criterion
    // with enrichment signals for optimization
    successDefinition: 'Inquiry resolved without escalation and without customer reopening within 7 days',
    enrichmentSignals: [
      { id: 'csat', name: 'Customer Satisfaction (CSAT)', description: 'If customer provides rating', checked: true },
      { id: 'handle_time', name: 'Handle Time', description: 'Total conversation duration', checked: true },
      { id: 'outcome_value', name: 'Outcome Value', description: 'Value of transaction (order saved, upsell)', checked: false }
    ]
  },
  'code': {
    // Guarantee-backed: agent affirms completion, guarantee covers defects
    successDefinition: 'Agent affirms the work is complete. Guarantee covers defects discovered later.',
    // Coverage varies by outcome type
    guaranteeCoverageByType: {
      'code.review': [
        { id: 'missed_critical', name: 'Missed Critical Bug', description: 'Critical bug in reviewed code found in production' },
        { id: 'missed_security', name: 'Missed Security Vulnerability', description: 'CVE or exploit in reviewed code' },
        { id: 'false_approval', name: 'False Approval', description: 'Approved PR that should have been blocked' }
      ],
      'code.fix': [
        { id: 'incomplete', name: 'Incomplete Fix', description: 'Original bug still reproducible' },
        { id: 'regression', name: 'Regression', description: 'Fix introduced new bugs' },
        { id: 'wrong_cause', name: 'Wrong Root Cause', description: 'Fix addressed symptom, not cause' }
      ]
    }
  },
  'legal': {
    // Guarantee-backed: agent affirms completion, guarantee covers defects
    successDefinition: 'Agent affirms the work is complete. Guarantee covers defects discovered later.',
    // Coverage varies by outcome type
    guaranteeCoverageByType: {
      'legal.review': [
        { id: 'missed_risk', name: 'Missed Material Risk', description: 'Material risk in reviewed contract caused harm' },
        { id: 'missed_clause', name: 'Missed Problematic Clause', description: 'Problematic clause not flagged caused harm' },
        { id: 'wrong_assessment', name: 'Incorrect Risk Assessment', description: 'Risk level materially understated' }
      ],
      'legal.summarize': [
        { id: 'missed_term', name: 'Missed Key Term', description: 'Material term omitted from summary' },
        { id: 'missed_deadline', name: 'Missed Deadline', description: 'Critical deadline not captured' },
        { id: 'wrong_interpretation', name: 'Misinterpretation', description: 'Term meaning materially misstated' }
      ],
      'legal.compare': [
        { id: 'missed_change', name: 'Missed Material Change', description: 'Significant change between versions not identified' },
        { id: 'wrong_implication', name: 'Wrong Risk Implication', description: 'Change implications materially misstated' }
      ],
      'legal.draft_nda': [
        { id: 'unenforceable', name: 'Unenforceable Provision', description: 'Key provision unenforceable in jurisdiction' },
        { id: 'missing_protection', name: 'Missing Protection', description: 'Standard protection omitted' },
        { id: 'drafting_error', name: 'Drafting Error', description: 'Error in language caused unintended interpretation' }
      ],
      'legal.draft_msa': [
        { id: 'unenforceable', name: 'Unenforceable Provision', description: 'Key provision unenforceable in jurisdiction' },
        { id: 'missing_protection', name: 'Missing Protection', description: 'Standard commercial protection omitted' },
        { id: 'ambiguous_terms', name: 'Ambiguous Terms', description: 'Ambiguity caused dispute or harm' }
      ],
      'legal.draft_dpa': [
        { id: 'compliance_gap', name: 'Compliance Gap', description: 'Missing required GDPR/CCPA provision' },
        { id: 'inadequate_safeguards', name: 'Inadequate Safeguards', description: 'Data protection measures insufficient' },
        { id: 'regulatory_violation', name: 'Regulatory Violation', description: 'DPA failed regulatory scrutiny' }
      ]
    }
  },
  'medical': {
    // Guarantee-backed: agent affirms completion, guarantee covers documentation defects
    successDefinition: 'Agent affirms documentation is complete. Guarantee covers documentation errors discovered later.',
    guaranteeCoverageByType: {
      'medical.scribe': [
        { id: 'factual_error', name: 'Factual Documentation Error', description: 'Wrong medication, dosage, or clinical fact documented' },
        { id: 'omission', name: 'Critical Omission', description: 'Material information from encounter not documented' },
        { id: 'misattribution', name: 'Misattribution', description: 'Statement attributed to wrong party (patient, provider, family)' },
        { id: 'coding_error', name: 'Coding Error', description: 'Incorrect codes affecting reimbursement (if coding included)' }
      ]
    },
    notCovered: [
      'Clinical judgment errors (documentation was accurate but clinical decision was wrong)',
      'Downstream treatment decisions based on the note',
      'Patient harm from treatment (not documentation)',
      'Malpractice claims against the provider'
    ]
  }
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initOutcomeCards();
  initWizard();
  initCostInput();
  initStrategyCards();
  initRadioGroups();
  initDashboardFilters();
  initDocsNavigation();
});

// Dashboard metrics data by outcome type
const dashboardMetrics = {
  'all': {
    outcomes: '1,847',
    outcomesChange: '+12%',
    spend: '$4,012',
    spendChange: '-3%',
    success: '94.2%',
    successChange: '+1.5%',
    avgCost: '$4.88',
    avgCostTarget: 'Target: $5.00',
    avgLatency: '47s',
    avgLatencyTarget: 'Target: 60s',
    escalation: '5.8%',
    escalationChange: '-0.5%'
  },
  'cs.resolve': {
    outcomes: '1,201',
    outcomesChange: '+18%',
    spend: '$1,802',
    spendChange: '-5%',
    success: '96.1%',
    successChange: '+2.1%',
    avgCost: '$0.42',
    avgCostTarget: 'Target: $0.50',
    avgLatency: '32s',
    avgLatencyTarget: 'Target: 45s',
    escalation: '4.2%',
    escalationChange: '-0.8%'
  },
  'code.review': {
    outcomes: '372',
    outcomesChange: '+8%',
    spend: '$1,204',
    spendChange: '+2%',
    success: '91.4%',
    successChange: '+0.5%',
    avgCost: '$3.24',
    avgCostTarget: 'Target: $3.50',
    avgLatency: '127s',
    avgLatencyTarget: 'Target: 180s',
    escalation: '8.1%',
    escalationChange: '-0.3%'
  },
  'legal.review': {
    outcomes: '189',
    outcomesChange: '+5%',
    spend: '$820',
    spendChange: '-8%',
    success: '97.4%',
    successChange: '+1.2%',
    avgCost: '$12.50',
    avgCostTarget: 'Target: $15.00',
    avgLatency: '245s',
    avgLatencyTarget: 'Target: 300s',
    escalation: '2.6%',
    escalationChange: '-0.4%'
  },
  'medical.scribe': {
    outcomes: '85',
    outcomesChange: '+22%',
    spend: '$186',
    spendChange: '+12%',
    success: '98.8%',
    successChange: '+0.3%',
    avgCost: '$2.19',
    avgCostTarget: 'Target: $2.50',
    avgLatency: '18s',
    avgLatencyTarget: 'Target: 30s',
    escalation: '1.2%',
    escalationChange: '-0.1%'
  }
};

function initDashboardFilters() {
  const chips = document.querySelectorAll('.type-chip');
  chips.forEach(chip => {
    chip.addEventListener('click', () => {
      chips.forEach(c => c.classList.remove('active'));
      chip.classList.add('active');
      updateDashboardMetrics(chip.dataset.type);
    });
  });
}

// Docs navigation
function initDocsNavigation() {
  const navItems = document.querySelectorAll('.docs-nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const section = item.dataset.section;

      // Update nav active state
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      // Update section visibility
      document.querySelectorAll('.docs-section').forEach(s => s.classList.remove('active'));
      const targetSection = document.getElementById(`section-${section}`);
      if (targetSection) {
        targetSection.classList.add('active');
        // Scroll to top of content
        targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }
    });
  });
}

function updateDashboardMetrics(outcomeType) {
  const metrics = dashboardMetrics[outcomeType];
  if (!metrics) return;

  document.getElementById('metric-outcomes').textContent = metrics.outcomes;
  document.getElementById('metric-spend').textContent = metrics.spend;
  document.getElementById('metric-success').textContent = metrics.success;
  document.getElementById('metric-avg-cost').textContent = metrics.avgCost;
  document.getElementById('metric-avg-cost-target').textContent = metrics.avgCostTarget;
  document.getElementById('metric-avg-latency').textContent = metrics.avgLatency;
  document.getElementById('metric-avg-latency-target').textContent = metrics.avgLatencyTarget;
  document.getElementById('metric-escalation').textContent = metrics.escalation;

  // Update change indicators
  const outcomesChangeEl = document.getElementById('metric-outcomes-change');
  outcomesChangeEl.textContent = metrics.outcomesChange;
  outcomesChangeEl.className = 'metric-change ' + (metrics.outcomesChange.startsWith('+') ? 'positive' : 'negative');

  const spendChangeEl = document.getElementById('metric-spend-change');
  spendChangeEl.textContent = metrics.spendChange;
  spendChangeEl.className = 'metric-change ' + (metrics.spendChange.startsWith('-') ? 'positive' : 'negative');

  const successChangeEl = document.getElementById('metric-success-change');
  successChangeEl.textContent = metrics.successChange;
  successChangeEl.className = 'metric-change ' + (metrics.successChange.startsWith('+') ? 'positive' : 'negative');

  const escalationChangeEl = document.getElementById('metric-escalation-change');
  escalationChangeEl.textContent = metrics.escalationChange;
  escalationChangeEl.className = 'metric-change ' + (metrics.escalationChange.startsWith('-') ? 'positive' : 'negative');
}

// Navigation
function initNavigation() {
  const navItems = document.querySelectorAll('.nav-item');
  navItems.forEach(item => {
    item.addEventListener('click', (e) => {
      e.preventDefault();
      const view = item.dataset.view;
      showView(view);
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');
    });
  });
}

function showView(viewId) {
  const views = document.querySelectorAll('.view');
  views.forEach(v => v.classList.remove('active'));
  const targetView = document.getElementById(`view-${viewId}`);
  if (targetView) {
    targetView.classList.add('active');
    state.currentView = viewId;
  }
}

// Outcome Cards
function initOutcomeCards() {
  const cards = document.querySelectorAll('.outcome-card');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      const category = card.dataset.category;
      state.selectedCategory = category;
      showOutcomeTypes(category);
    });
  });

  // Back buttons
  document.querySelectorAll('.back-button').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.dataset.back;
      if (target === 'catalog') {
        showView('catalog');
      } else if (target === 'outcome-types') {
        showView('outcome-types');
      }
    });
  });
}

function showOutcomeTypes(category) {
  const data = outcomeTypes[category];
  if (!data) return;

  document.getElementById('category-title').textContent = data.title;

  const container = document.getElementById('outcome-types-container');
  container.innerHTML = data.types.map(type => `
    <div class="outcome-type-item ${type.recommended ? 'selected' : ''}" data-type="${type.id}" data-verification="${type.verificationModel || 'capi'}">
      <input type="radio" name="outcome-type" ${type.recommended ? 'checked' : ''}>
      <div class="outcome-type-content">
        <div class="outcome-type-header">
          <span class="outcome-type-name">${type.name}</span>
          ${type.recommended ? '<span class="recommended-badge">Recommended</span>' : ''}
          <span class="verification-badge ${type.verificationModel === 'guarantee' ? 'guarantee' : 'capi'}">${type.verificationModel === 'guarantee' ? '🛡️ Guarantee-Backed' : '📊 cAPI-Verified'}</span>
        </div>
        <p class="outcome-type-desc">${type.description}</p>
        <div class="outcome-type-stats">
          <span>Avg. cost: ${type.avgCost}</span>
          <span>Avg. time: ${type.avgTime}</span>
          ${type.verificationModel === 'guarantee' ? `<span>Claim window: ${type.guaranteeClaimWindow || '30 days'}</span>` : `<span>Success: ${type.successRate}</span>`}
        </div>
      </div>
    </div>
  `).join('');

  // Add click handlers
  container.querySelectorAll('.outcome-type-item').forEach(item => {
    item.addEventListener('click', () => {
      container.querySelectorAll('.outcome-type-item').forEach(i => i.classList.remove('selected'));
      item.classList.add('selected');
      item.querySelector('input').checked = true;
      state.selectedOutcomeType = item.dataset.type;
    });
  });

  // Add continue button
  if (!container.querySelector('.continue-btn')) {
    const continueBtn = document.createElement('button');
    continueBtn.className = 'btn-primary continue-btn';
    continueBtn.textContent = 'Continue';
    continueBtn.style.marginTop = '24px';
    continueBtn.addEventListener('click', () => {
      showView('wizard');
      state.wizardStep = 1;
      updateWizardStep();
    });
    container.appendChild(continueBtn);
  }

  showView('outcome-types');
}

// Wizard
function initWizard() {
  const backBtn = document.getElementById('wizard-back');
  const nextBtn = document.getElementById('wizard-next');

  backBtn.addEventListener('click', () => {
    if (state.wizardStep > 1) {
      state.wizardStep--;
      updateWizardStep();
    } else {
      showView('outcome-types');
    }
  });

  nextBtn.addEventListener('click', () => {
    if (state.wizardStep < 6) {
      state.wizardStep++;
      updateWizardStep();
    } else {
      launchOutcome();
    }
  });
}

function updateWizardStep() {
  // Update step indicators
  document.querySelectorAll('.wizard-step').forEach((step, index) => {
    step.classList.remove('active', 'completed');
    if (index + 1 < state.wizardStep) {
      step.classList.add('completed');
    } else if (index + 1 === state.wizardStep) {
      step.classList.add('active');
    }
  });

  // Show correct panel
  document.querySelectorAll('.wizard-panel').forEach(panel => {
    panel.classList.remove('active');
    if (parseInt(panel.dataset.panel) === state.wizardStep) {
      panel.classList.add('active');
    }
  });

  // Render dynamic content based on step
  const category = state.selectedCategory;
  if (category) {
    if (state.wizardStep === 1) renderContextSources(category);
    if (state.wizardStep === 2) renderTools(category);
    if (state.wizardStep === 3) renderSuccessCriteria(category);
    if (state.wizardStep === 4) renderDeliveryOptions(category);
    if (state.wizardStep === 6) renderReview(category);
  }

  // Update navigation buttons
  const backBtn = document.getElementById('wizard-back');
  const nextBtn = document.getElementById('wizard-next');

  backBtn.textContent = state.wizardStep === 1 ? 'Cancel' : 'Back';
  nextBtn.textContent = state.wizardStep === 6 ? 'Launch Outcome' : 'Continue';
}

// Render context sources for selected vertical
function renderContextSources(category) {
  const sources = contextSources[category];
  const resources = agentResources[category];
  if (!sources) return;

  const container = document.querySelector('[data-panel="1"] .context-sources');
  if (!container) return;

  // Buyer-provided sources
  let html = sources.map(source => `
    <div class="context-source ${source.connected ? 'connected' : ''}">
      <div class="source-header">
        <input type="checkbox" ${source.connected ? 'checked' : ''} data-source="${source.id}">
        <span class="source-icon">${source.icon}</span>
        <span class="source-name">${source.name}</span>
        <span class="source-status ${source.connected ? 'connected' : ''}">${source.connected ? 'Connected' : 'Not configured'}</span>
      </div>
      <div class="source-details">
        <span>${source.description}</span>
      </div>
    </div>
  `).join('') + '<button class="add-source-btn">+ Add Context Source</button>';

  // Agent resources (if any for this vertical)
  if (resources && resources.length > 0) {
    html += `
      <div class="agent-resources-section">
        <h4>Agent Resources <span class="included-badge">Included</span></h4>
        <p class="field-description">The execution engine has access to these resources. Costs are rolled into the outcome price.</p>
        <div class="agent-resources-list">
          ${resources.map(r => `
            <div class="agent-resource-item">
              <span class="resource-name">${r.name}</span>
              <span class="resource-desc">${r.description}</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

// Render tools for selected vertical
function renderTools(category) {
  const tools = verticalTools[category];
  if (!tools) return;

  const container = document.querySelector('[data-panel="2"] .tools-section');
  if (!container) return;

  // Get parent and clear all tool sections
  const parent = container.parentElement;
  parent.querySelectorAll('.tools-section').forEach(s => s.remove());

  // Create read-only section
  const readOnlySection = document.createElement('div');
  readOnlySection.className = 'tools-section';
  readOnlySection.innerHTML = `
    <h3>Read-Only Actions</h3>
    <div class="tools-list">
      ${tools.readOnly.map(tool => `
        <label class="tool-item">
          <input type="checkbox" ${tool.checked ? 'checked' : ''} data-tool="${tool.id}">
          <span>${tool.name}</span>
        </label>
      `).join('')}
    </div>
  `;

  // Create write actions section
  const writeSection = document.createElement('div');
  writeSection.className = 'tools-section';
  writeSection.innerHTML = `
    <h3>Write Actions</h3>
    <div class="tools-list">
      ${tools.writeActions.map(tool => `
        <div class="tool-item-complex">
          <label>
            <input type="checkbox" ${tool.checked ? 'checked' : ''} data-tool="${tool.id}">
            <span>${tool.name}</span>
          </label>
          ${tool.hasConfig ? `
            <div class="tool-config">
              <label>${tool.configLabel} <input type="${tool.configLabel.includes('amount') ? 'number' : 'text'}" value="${tool.configValue}" class="${tool.configLabel.includes('codes') ? 'medium-input' : 'small-input'}"> ${tool.configUnit}</label>
            </div>
          ` : ''}
          ${tool.warning ? `
            <div class="tool-warning">
              <svg viewBox="0 0 24 24" fill="currentColor" width="16" height="16">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-2h2v2zm0-4h-2V7h2v6z"/>
              </svg>
              ${tool.warning}
            </div>
          ` : ''}
        </div>
      `).join('')}
    </div>
  `;

  // Find the wizard description and insert after it
  const description = parent.querySelector('.wizard-description');
  if (description) {
    description.after(readOnlySection);
    readOnlySection.after(writeSection);
  }
}

// Render delivery options for selected vertical
function renderDeliveryOptions(category) {
  const latencyOptions = document.getElementById('latency-options');
  const latencyDesc = document.getElementById('latency-description');
  const handoffDest = document.getElementById('handoff-destination');
  const customerTrigger = document.getElementById('trigger-customer-request');

  if (!latencyOptions) return;

  // Vertical-specific latency options
  const latencyConfigs = {
    'customer-service': {
      description: 'Maximum time for AI to respond to customer messages',
      options: [
        { value: 'streaming', label: 'Streaming', desc: '< 2 seconds - Required for phone/voice', selected: true },
        { value: 'fast', label: 'Fast', desc: '< 5 seconds - Recommended for chat' },
        { value: 'standard', label: 'Standard', desc: '< 15 seconds - Acceptable for email' }
      ],
      showCustomerRequest: true,
      defaultHandoff: 'zendesk'
    },
    'code': {
      description: 'Maximum time to complete review or fix',
      options: [
        { value: 'fast', label: 'Fast', desc: '< 15 minutes - For blocking PRs', selected: true },
        { value: 'standard', label: 'Standard', desc: '< 1 hour - Normal priority' },
        { value: 'relaxed', label: 'Relaxed', desc: '< 4 hours - Non-urgent' }
      ],
      showCustomerRequest: false,
      defaultHandoff: 'github'
    },
    'legal': {
      description: 'Maximum time to complete review or draft',
      options: [
        { value: 'urgent', label: 'Urgent', desc: '< 1 hour - Rush review' },
        { value: 'standard', label: 'Standard', desc: '< 4 hours - Normal priority', selected: true },
        { value: 'relaxed', label: 'Relaxed', desc: '< 24 hours - Non-urgent' }
      ],
      showCustomerRequest: false,
      defaultHandoff: 'slack'
    },
    'medical': {
      description: 'Maximum time to complete documentation',
      options: [
        { value: 'realtime', label: 'Real-time', desc: '< 30 seconds - During encounter', selected: true },
        { value: 'fast', label: 'Fast', desc: '< 5 minutes - Post-encounter' },
        { value: 'standard', label: 'Standard', desc: '< 30 minutes - End of day' }
      ],
      showCustomerRequest: false,
      defaultHandoff: 'webhook'
    }
  };

  const config = latencyConfigs[category] || latencyConfigs['customer-service'];

  // Update description
  if (latencyDesc) {
    latencyDesc.textContent = config.description;
  }

  // Update latency options
  latencyOptions.innerHTML = config.options.map(opt => `
    <label class="radio-item ${opt.selected ? 'selected' : ''}">
      <input type="radio" name="latency" value="${opt.value}" ${opt.selected ? 'checked' : ''}>
      <span class="radio-label">${opt.label}</span>
      <span class="radio-desc">${opt.desc}</span>
    </label>
  `).join('');

  // Re-init radio group click handlers
  latencyOptions.querySelectorAll('.radio-item').forEach(item => {
    item.addEventListener('click', () => {
      latencyOptions.querySelectorAll('.radio-item').forEach(i => i.classList.remove('selected'));
      item.classList.add('selected');
      item.querySelector('input').checked = true;
    });
  });

  // Update customer request trigger visibility
  if (customerTrigger) {
    customerTrigger.style.display = config.showCustomerRequest ? 'flex' : 'none';
  }

  // Update default handoff destination
  if (handoffDest) {
    handoffDest.value = config.defaultHandoff;
  }
}

// Render success criteria for selected vertical
function renderSuccessCriteria(category) {
  const criteria = successCriteria[category];
  if (!criteria) return;

  const panel = document.querySelector('[data-panel="3"]');
  if (!panel) return;

  // Clear existing sections
  panel.querySelectorAll('.criteria-section').forEach(s => s.remove());
  panel.querySelectorAll('.success-definition').forEach(s => s.remove());
  panel.querySelectorAll('.capi-signals').forEach(s => s.remove());

  // Check if this is a cAPI-verified outcome (customer-service style)
  if (criteria.enrichmentSignals) {
    // Success definition section for cAPI-verified
    const definitionSection = document.createElement('div');
    definitionSection.className = 'criteria-section';
    definitionSection.innerHTML = `
      <h3>Success Definition</h3>
      <div class="success-definition">
        <p><strong>${criteria.successDefinition}</strong></p>
        <p class="field-description">You report success or failure via the Conversions API based on what happens after the conversation ends.</p>
      </div>

      <div class="capi-signals">
        <h4>You will report via cAPI:</h4>
        <div class="signal-list">
          <div class="signal-item success">
            <span class="signal-event">outcome.success</span>
            <span class="signal-when">Ticket closed AND no reopen within 7 days</span>
          </div>
          <div class="signal-item failure">
            <span class="signal-event">outcome.failure</span>
            <span class="signal-when">Escalated to human OR customer reopened</span>
          </div>
        </div>
      </div>
    `;

    // Enrichment signals section
    const enrichmentSection = document.createElement('div');
    enrichmentSection.className = 'criteria-section';
    enrichmentSection.innerHTML = `
      <h3>Optional Enrichment Signals</h3>
      <p class="field-description">Report these when available to help optimize provider matching (not required for success).</p>
      <div class="criteria-list">
        ${criteria.enrichmentSignals.map(c => `
          <label class="criterion-item">
            <input type="checkbox" ${c.checked ? 'checked' : ''} data-criterion="${c.id}">
            <span class="criterion-name">${c.name}</span>
            <span class="criterion-desc">${c.description}</span>
          </label>
        `).join('')}
      </div>
    `;

    const description = panel.querySelector('.wizard-description');
    if (description) {
      description.after(definitionSection);
      definitionSection.after(enrichmentSection);
    }
  } else if (criteria.guaranteeCoverage || criteria.guaranteeCoverageByType) {
    // Guarantee-backed outcome (code, legal drafts)
    const definitionSection = document.createElement('div');
    definitionSection.className = 'criteria-section';
    definitionSection.innerHTML = `
      <h3>Completion</h3>
      <div class="success-definition">
        <p><strong>${criteria.successDefinition}</strong></p>
        <p class="field-description">The outcome is delivered when the agent affirms it's complete. You pay on delivery.</p>
      </div>
    `;

    // Get coverage for selected outcome type, or use general coverage
    let coverage = criteria.guaranteeCoverage;
    if (criteria.guaranteeCoverageByType) {
      if (state.selectedOutcomeType && criteria.guaranteeCoverageByType[state.selectedOutcomeType]) {
        coverage = criteria.guaranteeCoverageByType[state.selectedOutcomeType];
      } else {
        // Fall back to first coverage type
        coverage = Object.values(criteria.guaranteeCoverageByType)[0];
      }
    }

    // Get claim window from the selected outcome type
    const outcomeData = outcomeTypes[state.selectedCategory]?.types.find(t => t.id === state.selectedOutcomeType);
    const claimWindow = outcomeData?.guaranteeClaimWindow || '30 days';

    // Guarantee coverage
    const guaranteeSection = document.createElement('div');
    guaranteeSection.className = 'criteria-section';
    guaranteeSection.innerHTML = `
      <h3>Guarantee Coverage</h3>
      <p class="field-description">If defects are discovered within ${claimWindow}, file a claim via the Claims API:</p>
      <div class="criteria-list guarantee-list">
        ${coverage.map(c => `
          <div class="criterion-item guarantee-item">
            <span class="guarantee-icon">&#128737;</span>
            <span class="criterion-name">${c.name}</span>
            <span class="criterion-desc">${c.description}</span>
          </div>
        `).join('')}
      </div>
      <div class="claim-cap-section">
        <label>Maximum Claim Amount</label>
        <p class="field-description">Maximum recovery if defects cause damage. Set based on what's at stake—a $500K contract warrants more coverage than a standard NDA.</p>
        <div class="claim-cap-input-group">
          <span class="currency">$</span>
          <input type="number" value="10000" step="1000" min="100" class="claim-cap-input" id="claim-cap-value">
        </div>
      </div>
      ${criteria.notCovered ? `
        <div class="not-covered-section">
          <h4>Not Covered</h4>
          <ul class="not-covered-list">
            ${criteria.notCovered.map(item => `<li>${item}</li>`).join('')}
          </ul>
        </div>
      ` : ''}
      <div class="claims-api-note">
        <code>POST /v1/claims</code> with <code>guarantee.claim</code> event
      </div>
    `;

    const description = panel.querySelector('.wizard-description');
    if (description) {
      description.after(definitionSection);
      definitionSection.after(guaranteeSection);
    }
  } else if (criteria.required) {
    // Legacy format for other verticals (legal review, medical)
    const requiredSection = document.createElement('div');
    requiredSection.className = 'criteria-section';
    requiredSection.innerHTML = `
      <h3>Required Criteria (all must pass)</h3>
      <div class="criteria-list">
        ${criteria.required.map(c => `
          <div class="criterion-item">
            <input type="checkbox" ${c.checked ? 'checked' : ''} data-criterion="${c.id}">
            <span class="criterion-name">${c.name}</span>
            ${c.hasConfig ? `
              <div class="criterion-config">
                ${c.configType === 'number' ? `
                  <select><option>&ge;</option><option>&gt;</option><option>=</option></select>
                  <input type="number" value="${c.configValue}" ${c.configMin ? `min="${c.configMin}"` : ''} ${c.configMax ? `max="${c.configMax}"` : ''} class="small-input">
                  <span>${c.configLabel}</span>
                ` : `
                  <input type="text" value="${c.configValue}" class="small-input">
                  <span>${c.configLabel}</span>
                `}
              </div>
            ` : `
              <span class="criterion-desc">${c.description}</span>
            `}
          </div>
        `).join('')}
      </div>
    `;

    const optionalSection = document.createElement('div');
    optionalSection.className = 'criteria-section';
    optionalSection.innerHTML = `
      <h3>Optional Criteria (tracked but not required)</h3>
      <div class="criteria-list">
        ${criteria.optional.map(c => `
          <label class="criterion-item">
            <input type="checkbox" ${c.checked ? 'checked' : ''} data-criterion="${c.id}">
            <span class="criterion-name">${c.name}</span>
          </label>
        `).join('')}
      </div>
    `;

    const description = panel.querySelector('.wizard-description');
    if (description) {
      description.after(requiredSection);
      requiredSection.after(optionalSection);
    }
  }
}

// Render review section
function renderReview(category) {
  const panel = document.querySelector('[data-panel="6"]');
  if (!panel) return;

  const outcomeData = outcomeTypes[category];
  const selectedType = outcomeData?.types.find(t => t.id === state.selectedOutcomeType) || outcomeData?.types[0];
  const sources = contextSources[category]?.filter(s => s.connected) || [];
  const tools = verticalTools[category];

  const costInput = document.getElementById('cost-value');
  const budgetInput = document.getElementById('budget-value');
  const cost = parseFloat(costInput?.value) || 0.45;
  const budget = parseFloat(budgetInput?.value) || 5000;
  const estOutcomes = cost > 0 ? Math.round(budget / cost) : 0;

  // Get selected latency SLA
  const latencyRadio = document.querySelector('input[name="latency"]:checked');
  const latencyLabels = {
    'streaming': 'Streaming (< 2 seconds)',
    'fast': 'Fast (< 5 seconds)',
    'standard': 'Standard (< 15 seconds)'
  };
  const latencyLabel = latencyLabels[latencyRadio?.value] || 'Streaming (< 2 seconds)';

  // Determine verification model
  const isGuaranteeBacked = selectedType?.verificationModel === 'guarantee';
  const verificationText = isGuaranteeBacked
    ? `Guarantee-backed (${selectedType?.guaranteeClaimWindow || '30 day'} claim window)`
    : 'cAPI-verified (you report success/failure)';

  const reviewSummary = panel.querySelector('.review-summary');
  if (!reviewSummary) return;

  reviewSummary.innerHTML = `
    <div class="review-section">
      <h3>Outcome</h3>
      <div class="review-item">
        <span class="review-label">Type</span>
        <span class="review-value">${outcomeData?.title || category} - ${selectedType?.name || 'Unknown'}</span>
      </div>
      <div class="review-item">
        <span class="review-label">Verification</span>
        <span class="review-value">${verificationText}</span>
      </div>
    </div>

    <div class="review-section">
      <h3>Context Sources</h3>
      <div class="review-tags">
        ${sources.map(s => `<span class="tag">${s.name}</span>`).join('')}
      </div>
    </div>

    <div class="review-section">
      <h3>Tools</h3>
      <div class="review-tags">
        ${tools?.readOnly.filter(t => t.checked).map(t => `<span class="tag">${t.name}</span>`).join('') || ''}
        ${tools?.writeActions.filter(t => t.checked).map(t => `<span class="tag">${t.name}${t.hasConfig ? ` (${t.configValue} ${t.configUnit})` : ''}</span>`).join('') || ''}
      </div>
    </div>

    <div class="review-section">
      <h3>Success Criteria</h3>
      <p>${isGuaranteeBacked
        ? 'Completion verified at delivery. Defects discovered within claim window covered by guarantee.'
        : 'Inquiry resolved without escalation and without customer reopening within 7 days'}</p>
    </div>

    <div class="review-section">
      <h3>Delivery</h3>
      <div class="review-item">
        <span class="review-label">Response SLA</span>
        <span class="review-value">${latencyLabel}</span>
      </div>
      <div class="review-item">
        <span class="review-label">Escalation</span>
        <span class="review-value">Enabled</span>
      </div>
    </div>

    <div class="review-section highlight">
      <h3>Pricing Summary</h3>
      <div class="review-item">
        <span class="review-label">Strategy</span>
        <span class="review-value">Cost per result goal</span>
      </div>
      <div class="review-item">
        <span class="review-label">Target Cost</span>
        <span class="review-value">$${cost.toFixed(2)}/outcome</span>
      </div>
      <div class="review-item">
        <span class="review-label">Monthly Budget</span>
        <span class="review-value">$${budget.toLocaleString()}</span>
      </div>
      <div class="review-item total">
        <span class="review-label">Est. Outcomes</span>
        <span class="review-value">~${estOutcomes.toLocaleString()}/month</span>
      </div>
    </div>
  `;
}

// Cost Input
function initCostInput() {
  const costInput = document.getElementById('cost-value');
  const bidCapInput = document.getElementById('bid-cap-value');
  const budgetInput = document.getElementById('budget-value');

  if (costInput) {
    costInput.addEventListener('input', () => updateEstimateForStrategy('cost_per_result'));
  }
  if (bidCapInput) {
    bidCapInput.addEventListener('input', () => updateEstimateForStrategy('bid_cap'));
  }
  const roasInput = document.getElementById('roas-value');
  if (roasInput) {
    roasInput.addEventListener('input', () => updateEstimateForStrategy('roas_goal'));
  }
  if (budgetInput) {
    budgetInput.addEventListener('input', () => {
      const selectedStrategy = document.querySelector('input[name="strategy"]:checked')?.value || 'highest_volume';
      updateEstimateForStrategy(selectedStrategy);
    });
  }
}

// Strategy Cards
function initStrategyCards() {
  const cards = document.querySelectorAll('.strategy-card');
  cards.forEach(card => {
    card.addEventListener('click', () => {
      cards.forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      card.querySelector('input').checked = true;

      // Show/hide appropriate config section
      const strategyValue = card.querySelector('input').value;
      document.querySelectorAll('.strategy-config').forEach(config => {
        config.classList.remove('active');
      });
      const targetConfig = document.getElementById(`config-${strategyValue}`);
      if (targetConfig) {
        targetConfig.classList.add('active');
      }

      // Update estimate text based on strategy
      updateEstimateForStrategy(strategyValue);
    });
  });
}

function updateEstimateForStrategy(strategy) {
  const estimate = document.getElementById('estimated-outcomes');
  const budgetInput = document.getElementById('budget-value');
  const budget = parseFloat(budgetInput?.value) || 5000;

  if (strategy === 'highest_volume') {
    estimate.textContent = 'varies by market conditions';
  } else if (strategy === 'cost_per_result') {
    const costInput = document.getElementById('cost-value');
    const cost = parseFloat(costInput?.value) || 0.45;
    if (cost > 0) {
      const outcomes = Math.round(budget / cost);
      estimate.textContent = `~${outcomes.toLocaleString()} outcomes/month`;
    }
  } else if (strategy === 'bid_cap') {
    const bidCapInput = document.getElementById('bid-cap-value');
    const bidCap = parseFloat(bidCapInput?.value) || 1.00;
    if (bidCap > 0) {
      const maxOutcomes = Math.round(budget / bidCap);
      estimate.textContent = `up to ${maxOutcomes.toLocaleString()} outcomes/month (if all at max bid)`;
    }
  } else if (strategy === 'roas_goal') {
    const roasInput = document.getElementById('roas-value');
    const roas = parseFloat(roasInput?.value) || 1.5;
    estimate.textContent = `varies by outcome value (target: $${roas.toFixed(2)} return per $1 spent)`;
  }
}


// Radio Groups
function initRadioGroups() {
  document.querySelectorAll('.radio-group').forEach(group => {
    const items = group.querySelectorAll('.radio-item');
    items.forEach(item => {
      item.addEventListener('click', () => {
        items.forEach(i => i.classList.remove('selected'));
        item.classList.add('selected');
        item.querySelector('input').checked = true;
      });
    });
  });
}

// Launch Outcome
function launchOutcome() {
  const modal = document.getElementById('success-modal');

  // Update modal with correct outcome type
  const category = state.selectedCategory;
  const outcomeData = outcomeTypes[category];
  const selectedType = outcomeData?.types.find(t => t.id === state.selectedOutcomeType) || outcomeData?.types[0];

  const modalText = modal.querySelector('p');
  if (modalText && selectedType) {
    modalText.textContent = `Your ${selectedType.id} outcome is now active and processing requests.`;
  }

  // Update cost estimate
  const costInput = document.getElementById('cost-value');
  const budgetInput = document.getElementById('budget-value');
  const cost = parseFloat(costInput?.value) || 0.45;
  const budget = parseFloat(budgetInput?.value) || 5000;
  const estOutcomes = cost > 0 ? Math.round(budget / cost) : 0;

  const statValues = modal.querySelectorAll('.stat-value');
  if (statValues.length >= 2) {
    statValues[0].textContent = `$${cost.toFixed(2)}`;
    statValues[1].textContent = `~${estOutcomes.toLocaleString()}`;
  }

  modal.classList.add('active');
}

function closeModal() {
  const modal = document.getElementById('success-modal');
  modal.classList.remove('active');
  showView('dashboard');

  // Update nav
  document.querySelectorAll('.nav-item').forEach(item => {
    item.classList.remove('active');
    if (item.dataset.view === 'dashboard') {
      item.classList.add('active');
    }
  });
}

// Make closeModal globally available
window.closeModal = closeModal;

// Copy code to clipboard
const copyIcon = `<svg viewBox="0 0 24 24"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>`;
const checkIcon = `<svg viewBox="0 0 24 24"><polyline points="20 6 9 17 4 12"></polyline></svg>`;

function copyCode(button) {
  const codeBlock = button.previousElementSibling;
  const code = codeBlock.textContent;

  navigator.clipboard.writeText(code).then(() => {
    button.innerHTML = checkIcon;
    button.classList.add('copied');

    setTimeout(() => {
      button.innerHTML = copyIcon;
      button.classList.remove('copied');
    }, 2000);
  }).catch(err => {
    console.error('Failed to copy:', err);
  });
}

// Make copyCode globally available
window.copyCode = copyCode;
