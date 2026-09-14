import 'package:flutter/material.dart';

class RailsScreen extends StatefulWidget {
  const RailsScreen({Key? key}) : super(key: key);

  @override
  State<RailsScreen> createState() => _RailsScreenState();
}

class _RailsScreenState extends State<RailsScreen> {
  String _selectedRail = 'juspay';
  bool _isSimulating = false;
  String? _simulationResult;

  final List<Map<String, dynamic>> _rails = [
    {
      'id': 'juspay',
      'name': 'Juspay HyperSDK',
      'tag': '18.4ms Switch',
      'desc': 'Smart dynamic retry orchestrator with 18 bank radar routes.',
      'icon': Icons.swap_horiz,
      'color': Color(0xFF0C6CF2),
    },
    {
      'id': 'phonepe',
      'name': 'PhonePe UPI 2.0',
      'tag': 'UPI Intent',
      'desc': 'Deep-linked 1-click fallback UPI intent QR links for soft declines.',
      'icon': Icons.qr_code_2,
      'color': Color(0xFF6739B7),
    },
    {
      'id': 'cred',
      'name': 'CRED Pay',
      'tag': 'High-Ticket',
      'desc': 'Optimized for ₹50,000+ high-ticket invoice settlements.',
      'icon': Icons.credit_card,
      'color': Color(0xFF1E293B),
    },
    {
      'id': 'cashfree',
      'name': 'Cashfree Auto-Collect',
      'tag': 'B2B Payouts',
      'desc': 'Virtual accounts and instant auto-collect settlement webhook locks.',
      'icon': Icons.account_balance_wallet,
      'color': Color(0xFF00D285),
    },
    {
      'id': 'razorpay',
      'name': 'Razorpay Core 99.99%',
      'tag': 'Standard Core',
      'desc': 'Primary production switch with zero-trust token vault.',
      'icon': Icons.bolt,
      'color': Color(0xFF0284C7),
    },
    {
      'id': 'stripe',
      'name': 'Stripe Global Forex',
      'tag': 'Cross-Border',
      'desc': 'Multi-currency international card token recurring subscriptions.',
      'icon': Icons.public,
      'color': Color(0xFF6366F1),
    },
  ];

  void _simulateRecovery(String railId) {
    setState(() {
      _isSimulating = true;
      _simulationResult = null;
    });

    Future.delayed(const Duration(milliseconds: 600), () {
      setState(() {
        _isSimulating = false;
        _simulationResult = '200 OK • Dispatched via ${railId.toUpperCase()} in 18.2ms. Invariant verified: NO_DOUBLE_DEBIT.';
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Multi-Rail Gateway Switcher',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
          ),
          const SizedBox(height: 4),
          Text(
            'Select and benchmark recovery adapters across India\'s payment infrastructure.',
            style: TextStyle(
              fontSize: 12,
              color: isDark ? Colors.grey[400] : const Color(0xFF64748B),
            ),
          ),
          const SizedBox(height: 16),

          // Rail Cards List
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _rails.length,
            itemBuilder: (context, index) {
              final rail = _rails[index];
              final isSelected = _selectedRail == rail['id'];

              return GestureDetector(
                onTap: () {
                  setState(() => _selectedRail = rail['id']);
                  _simulateRecovery(rail['id']);
                },
                child: Container(
                  margin: const EdgeInsets.only(bottom: 12),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF071328) : Colors.white,
                    borderRadius: BorderRadius.circular(16),
                    border: Border.all(
                      color: isSelected
                          ? const Color(0xFF0C6CF2)
                          : (isDark ? const Color(0xFF142442) : const Color(0xFFE2E8F0)),
                      width: isSelected ? 2 : 1,
                    ),
                    boxShadow: isSelected
                        ? [
                            BoxStyle(
                              color: const Color(0xFF0C6CF2).withOpacity(0.15),
                              blurRadius: 10,
                              offset: const Offset(0, 4),
                            ),
                          ]
                        : null,
                  ),
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(10),
                        decoration: BoxDecoration(
                          color: (rail['color'] as Color).withOpacity(0.15),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Icon(rail['icon'] as IconData, color: rail['color'] as Color, size: 22),
                      ),
                      const SizedBox(width: 14),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.between,
                              children: [
                                Text(
                                  rail['name'],
                                  style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                                ),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                                  decoration: BoxDecoration(
                                    color: Colors.blue.withOpacity(0.1),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    rail['tag'],
                                    style: const TextStyle(
                                      fontSize: 10,
                                      fontWeight: FontWeight.bold,
                                      color: Color(0xFF0C6CF2),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 4),
                            Text(
                              rail['desc'],
                              style: TextStyle(
                                fontSize: 11,
                                color: isDark ? Colors.grey[400] : const Color(0xFF64748B),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),

          if (_isSimulating || _simulationResult != null) ...[
            const SizedBox(height: 12),
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF030712) : const Color(0xFFE0F2FE),
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isDark ? const Color(0xFF1E293B) : const Color(0xFFBAE6FD),
                ),
              ),
              child: Row(
                children: [
                  if (_isSimulating)
                    const SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  else
                    const Icon(Icons.check_circle, color: Color(0xFF00D285), size: 18),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _isSimulating
                          ? 'Dispatching recovery contract via ${_selectedRail.toUpperCase()}...'
                          : _simulationResult!,
                      style: TextStyle(
                        fontSize: 11,
                        fontFamily: 'monospace',
                        color: isDark ? const Color(0xFF38BDF8) : const Color(0xFF0C4A6E),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }
}
