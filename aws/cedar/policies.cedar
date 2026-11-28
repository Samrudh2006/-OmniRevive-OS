// ==============================================================================
// AWS CEDAR ZERO-TRUST AUTHORIZATION POLICIES
// Target: OmniRevive-OS Banking SRE & Autonomous Invoice Recovery Engine
// Specification: Cedar Policy Language v3.0 (Amazon Web Services)
// ==============================================================================

// POLICY 1: SRE Admin Authorization for Banking Switch Circuit Breaker Overrides
// Ensures only verified SRE Engineers can trip or reset NPCI bank switches (e.g. SBI, HDFC)
permit (
    principal in Role::"SRE_Admin",
    action in [Action::"TripCircuitBreaker", Action::"ResetCircuitBreaker"],
    resource is BankingSwitch
)
when {
    context.mfa_verified == true &&
    context.system_risk_score <= 85
};

// POLICY 2: B2B Voice Agent & Finance Officer GSTIN Tax Invoice Mutation Policy
// Permitted only when mutation difference is within authorized compliance limits (< INR 5,00,000)
permit (
    principal in [Role::"Finance_Officer", Agent::"BedrockVoiceAgent"],
    action in [Action::"MutateInvoiceGSTIN", Action::"ApprovePTP"],
    resource is B2BInvoice
)
when {
    context.proposed_gstin like "??[A-Z0-9]*" &&
    context.invoice_amount <= 500000 &&
    context.regulatory_compliance == "GST_RULE_46"
};

// POLICY 3: Autonomous Voice Turn Execution & Live Email Dispatch
permit (
    principal in [Agent::"BedrockVoiceAgent", Role::"SRE_Admin"],
    action in [Action::"ExecuteVoiceDialogueTurn", Action::"DispatchTaxInvoiceEmail"],
    resource is B2BInvoice
);

// POLICY 4: Universal Immutability Guard for Recovery Audit Trail
// Forbids any deletion or truncation of the SQLite/DynamoDB audit log under any circumstance
forbid (
    principal,
    action in [Action::"DeleteAuditRecord", Action::"TruncateAuditLog"],
    resource is AuditLog
);

// POLICY 5: Fast-Loop Recovery Engine Mandate & Payment Link Execution Policy
// Ensures only authorized agents (FastLoopRecoveryEngine, SRE_Admin) can execute mandate recoveries
permit (
    principal in [Agent::"FastLoopRecoveryEngine", Role::"SRE_Admin"],
    action in [Action::"ExecuteMandateRecovery", Action::"DispatchRecoveryLink"],
    resource is RecoveryWorkflow
)
when {
    context.amount_inr <= 500000 &&
    context.cedar_kill_switch == false
};
