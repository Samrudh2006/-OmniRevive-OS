import 'package:flutter/material.dart';

class AuditScreen extends StatelessWidget {
  const AuditScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    final List<Map<String, String>> blocks = [
      {
        'index': '#1842',
        'event': 'PAYMENT_RECOVERY_DISPATCHED',
        'hash': '0x9f82...1a3b',
        'prevHash': '0x7c41...8e21',
        'rail': 'JUSPAY_HYPERSDK',
        'status': 'VERIFIED'
      },
      {
        'index': '#1841',
        'event': 'CEDAR_POLICY_PASSED_RS204',
        'hash': '0x7c41...8e21',
        'prevHash': '0x3a19...99dc',
        'rail': 'POLICY_GATEWAY',
        'status': 'VERIFIED'
      },
      {
        'index': '#1840',
        'event': 'WEIBULL_WINDOW_CALIBRATED',
        'hash': '0x3a19...99dc',
        'prevHash': '0x110e...44f2',
        'rail': 'SURVIVAL_ENGINE',
        'status': 'VERIFIED'
      },
    ];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.between,
            children: [
              const Text(
                'SHA-256 Merkle Ledger',
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
                  'Chain Intact',
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF00D285)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'Tamper-evident cryptographic sequential hash chain securing all recovery decisions.',
            style: TextStyle(
              fontSize: 12,
              color: isDark ? Colors.grey[400] : const Color(0xFF64748B),
            ),
          ),
          const SizedBox(height: 16),

          // Merkle Block List
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: blocks.length,
            itemBuilder: (context, index) {
              final b = blocks[index];

              return Container(
                margin: const EdgeInsets.only(bottom: 12),
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: isDark ? const Color(0xFF071328) : Colors.white,
                  borderRadius: BorderRadius.circular(14),
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
                        Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                              decoration: BoxDecoration(
                                color: Colors.blue.withOpacity(0.15),
                                borderRadius: BorderRadius.circular(6),
                              ),
                              child: Text(
                                b['index']!,
                                style: const TextStyle(
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                  fontFamily: 'monospace',
                                  color: Color(0xFF0C6CF2),
                                ),
                              ),
                            ),
                            const SizedBox(width: 8),
                            Text(
                              b['event']!,
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                            ),
                          ],
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: const Color(0xFF00D285).withOpacity(0.12),
                            borderRadius: BorderRadius.circular(6),
                          ),
                          child: Text(
                            b['status']!,
                            style: const TextStyle(
                              fontSize: 9,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF00D285),
                            ),
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          'Merkle Root: ${b['hash']}',
                          style: TextStyle(
                            fontSize: 10,
                            fontFamily: 'monospace',
                            color: isDark ? Colors.grey[400] : const Color(0xFF64748B),
                          ),
                        ),
                        Text(
                          'Rail: ${b['rail']}',
                          style: TextStyle(
                            fontSize: 10,
                            color: isDark ? Colors.grey[500] : const Color(0xFF64748B),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
    );
  }
}
