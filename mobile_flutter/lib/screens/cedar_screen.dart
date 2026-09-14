import 'package:flutter/material.dart';

class CedarScreen extends StatelessWidget {
  const CedarScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.between,
            children: [
              const Text(
                'AWS Cedar Policy Engine',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFF00D285).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF00D285).withOpacity(0.3)),
                ),
                child: const Text(
                  '100% Policy Safe',
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF00D285)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'Zero-trust deterministic policy gatekeeper enforcing RBI, TRAI, and CFO approval invariants.',
            style: TextStyle(
              fontSize: 12,
              color: isDark ? Colors.grey[400] : const Color(0xFF64748B),
            ),
          ),
          const SizedBox(height: 16),

          // Policy Card 1: TRAI Quiet Hours
          _buildPolicyCard(
            title: 'POL-01: TRAI Quiet Hours Enforcer',
            rule: 'permit(principal, action == Action::"SendVoiceSMS", resource) when { context.time >= 09:00 && context.time <= 21:00 };',
            status: 'ACTIVE • ZERO VIOLATIONS',
            statusColor: const Color(0xFF00D285),
            isDark: isDark,
          ),

          // Policy Card 2: CFO High-Value Gate
          _buildPolicyCard(
            title: 'POL-02: CFO Dual-Key High-Ticket Gate',
            rule: 'forbid(principal, action == Action::"MutateInvoice", resource) unless { context.amount < 50000 || principal.hasDualKeyApproval };',
            status: 'GUARDED • ₹50k+ THRESHOLD',
            statusColor: const Color(0xFF0C6CF2),
            isDark: isDark,
          ),

          // Policy Card 3: Max Retry Clamp
          _buildPolicyCard(
            title: 'POL-03: Max Retry Limit Boundary',
            rule: 'forbid(principal, action == Action::"ExecuteRetry", resource) when { resource.retry_count >= 3 };',
            status: 'ACTIVE • NO CHOKING',
            statusColor: const Color(0xFF7C3AED),
            isDark: isDark,
          ),
        ],
      ),
    );
  }

  Widget _buildPolicyCard({
    required String title,
    required String rule,
    required String status,
    required Color statusColor,
    required bool isDark,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 14),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF071328) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark ? const Color(0xFF142442) : const Color(0xFFE2E8F0),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.between,
            children: [
              Text(
                title,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.12),
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  status,
                  style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: statusColor),
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF030712) : const Color(0xFFF1F5F9),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: isDark ? const Color(0xFF1E293B) : const Color(0xFFE2E8F0),
              ),
            ),
            child: Text(
              rule,
              style: TextStyle(
                fontFamily: 'monospace',
                fontSize: 10.5,
                color: isDark ? const Color(0xFF38BDF8) : const Color(0xFF0F172A),
              ),
            ),
          ),
        ],
      ),
    );
  }
}
