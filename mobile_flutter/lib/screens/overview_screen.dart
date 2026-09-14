import 'package:flutter/material.dart';

class OverviewScreen extends StatelessWidget {
  const OverviewScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Top Recovery KPI Banner
          Container(
            padding: const EdgeInsets.all(20),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: isDark
                    ? [const Color(0xFF0C2340), const Color(0xFF071328)]
                    : [const Color(0xFFE8F2FE), const Color(0xFFF4F8FE)],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
              borderRadius: BorderRadius.circular(20),
              border: Border.all(
                color: isDark ? const Color(0xFF1E3A6A) : const Color(0xFFBFDBFE),
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.between,
                  children: [
                    Row(
                      children: [
                        Container(
                          width: 8,
                          height: 8,
                          decoration: const BoxDecoration(
                            color: Color(0xFF00D285),
                            shape: BoxShape.circle,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(
                          'LIVE RECOVERY ENGINE',
                          style: TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            letterSpacing: 1.1,
                            color: isDark ? const Color(0xFF38BDF8) : const Color(0xFF0C6CF2),
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: const Color(0xFF00D285).withOpacity(0.15),
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: const Color(0xFF00D285).withOpacity(0.4)),
                      ),
                      child: const Text(
                        '18.4ms SLA',
                        style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF00D285)),
                      ),
                    ),
                  ],
                ),
                const SizedBox(height: 12),
                const Text(
                  '₹4,25,840',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.w900,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'Recovered across 1,842 failure events (78.39% Success Rate)',
                  style: TextStyle(
                    fontSize: 12,
                    color: isDark ? Colors.grey[400] : const Color(0xFF475569),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 20),
          const Text(
            'Core Control Plane Invariants',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 12),

          // 4 Grid KPI Cards
          GridView.count(
            crossAxisCount: 2,
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            crossAxisSpacing: 12,
            mainAxisSpacing: 12,
            childAspectRatio: 1.25,
            children: [
              _buildMetricCard(
                title: 'CAS MUTEX GATE',
                value: '0.23ms',
                subtitle: 'Zero Double-Debits',
                icon: Icons.lock_clock,
                accentColor: const Color(0xFF0C6CF2),
                isDark: isDark,
              ),
              _buildMetricCard(
                title: 'WEIBULL HAZARD',
                value: 'β = 0.74',
                subtitle: 'Dynamic Retries',
                icon: Icons.timeline,
                accentColor: const Color(0xFF00D285),
                isDark: isDark,
              ),
              _buildMetricCard(
                title: 'CEDAR ZERO-TRUST',
                value: '100% Safe',
                subtitle: 'RBI / TRAI Guard',
                icon: Icons.shield,
                accentColor: const Color(0xFF7C3AED),
                isDark: isDark,
              ),
              _buildMetricCard(
                title: 'MERKLE CHAIN',
                value: '465+ Tests',
                subtitle: 'SHA-256 Verified',
                icon: Icons.verified_user,
                accentColor: const Color(0xFFD97706),
                isDark: isDark,
              ),
            ],
          ),

          const SizedBox(height: 24),
          Row(
            mainAxisAlignment: MainAxisAlignment.between,
            children: [
              const Text(
                'Active Payment Rails Telemetry',
                style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
              ),
              Text(
                '18/18 Online',
                style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.green[500]),
              ),
            ],
          ),
          const SizedBox(height: 12),

          // Rail status list
          _buildRailTile('Juspay HyperSDK', '18.4ms Switch', '99.98% Health', isDark),
          _buildRailTile('PhonePe UPI 2.0', '12.1ms Intent', '100% Health', isDark),
          _buildRailTile('CRED High-Ticket', '22.0ms Auto-Route', '99.95% Health', isDark),
          _buildRailTile('Cashfree Payouts', '16.5ms Mutex', '100% Health', isDark),
          _buildRailTile('Razorpay Core', '14.2ms Direct', '99.99% Health', isDark),
        ],
      ),
    );
  }

  Widget _buildMetricCard({
    required String title,
    required String value,
    required String subtitle,
    required IconData icon,
    required Color accentColor,
    required bool isDark,
  }) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF071328) : Colors.white,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark ? const Color(0xFF142442) : const Color(0xFFE2E8F0),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                title,
                style: TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.bold,
                  letterSpacing: 0.8,
                  color: isDark ? Colors.grey[400] : const Color(0xFF64748B),
                ),
              ),
              Icon(icon, size: 16, color: accentColor),
            ],
          ),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.w900,
              color: accentColor,
            ),
          ),
          Text(
            subtitle,
            style: TextStyle(
              fontSize: 10,
              color: isDark ? Colors.grey[500] : const Color(0xFF64748B),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRailTile(String name, String latency, String health, bool isDark) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      decoration: BoxDecoration(
        color: isDark ? const Color(0xFF071328) : Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: isDark ? const Color(0xFF142442) : const Color(0xFFE2E8F0),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.between,
        children: [
          Row(
            children: [
              Container(
                width: 6,
                height: 6,
                decoration: const BoxDecoration(
                  color: Color(0xFF00D285),
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 10),
              Text(
                name,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ],
          ),
          Row(
            children: [
              Text(
                latency,
                style: TextStyle(
                  fontSize: 11,
                  fontFamily: 'monospace',
                  color: isDark ? const Color(0xFF38BDF8) : const Color(0xFF0C6CF2),
                ),
              ),
              const SizedBox(width: 8),
              Text(
                health,
                style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Color(0xFF00D285)),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
