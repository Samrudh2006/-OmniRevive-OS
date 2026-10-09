import 'package:flutter/material.dart';
import '../services/offline_mandate_service.dart';

class RecoveryOfflineScreen extends StatefulWidget {
  const RecoveryOfflineScreen({Key? key}) : super(key: key);

  @override
  State<RecoveryOfflineScreen> createState() => _RecoveryOfflineScreenState();
}

class _RecoveryOfflineScreenState extends State<RecoveryOfflineScreen> {
  final OfflineMandateService _service = OfflineMandateService();
  bool _isOnline = true;
  String _lastNotification = 'Listening for incoming FCM transaction recovery webhooks...';

  void _triggerSimulatedPushAlert() {
    setState(() {
      _lastNotification = '⚡ FCM PUSH [Priority=High]: Tx #TX_9814 failed (HDFC Switch Timeout). Tap to auto-retry via UPI Intent.';
    });
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        backgroundColor: const Color(0xFF0C55EA),
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
        content: Row(
          children: const [
            Icon(Icons.bolt, color: Colors.cyanAccent),
            SizedBox(width: 8),
            Expanded(
              child: Text(
                'FCM Alert: 1-Click UPI Recovery Available',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;

    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Network & Sync Header Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: _isOnline
                      ? [const Color(0xFF072146), const Color(0xFF0C3C78)]
                      : [const Color(0xFF3B1818), const Color(0xFF6B1D1D)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(
                  color: _isOnline ? Colors.blue.withOpacity(0.3) : Colors.red.withOpacity(0.4),
                ),
              ),
              child: Column(
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Row(
                        children: [
                          Icon(
                            _isOnline ? Icons.wifi : Icons.wifi_off,
                            color: _isOnline ? Colors.greenAccent : Colors.redAccent,
                            size: 24,
                          ),
                          const SizedBox(width: 10),
                          Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                _isOnline ? 'NETWORK: ONLINE (4G/5G)' : 'NETWORK: OFFLINE CACHE',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                  fontSize: 14,
                                  color: Colors.white,
                                ),
                              ),
                              Text(
                                _isOnline ? 'Automatic cloud sync enabled' : 'Mandates queued in local secure enclave',
                                style: TextStyle(
                                  fontSize: 11,
                                  color: Colors.white.withOpacity(0.7),
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      Switch(
                        value: _isOnline,
                        activeColor: Colors.greenAccent,
                        onChanged: (val) {
                          setState(() {
                            _isOnline = val;
                            _service.setNetworkStatus(val);
                          });
                        },
                      ),
                    ],
                  ),
                  const Divider(color: Colors.white24, height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      ElevatedButton.icon(
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF0C6CF2),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        onPressed: () async {
                          final count = await _service.syncPendingQueue();
                          setState(() {});
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(content: Text('Successfully reconciled $count offline mandates!')),
                          );
                        },
                        icon: const Icon(Icons.sync, size: 16),
                        label: const Text('Reconcile Cloud', style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold)),
                      ),
                      OutlinedButton.icon(
                        style: OutlinedButton.styleFrom(
                          foregroundColor: Colors.cyanAccent,
                          side: const BorderSide(color: Colors.cyanAccent),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                        ),
                        onPressed: _triggerSimulatedPushAlert,
                        icon: const Icon(Icons.notification_add, size: 16),
                        label: const Text('Simulate FCM', style: TextStyle(fontSize: 12)),
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),

            // Live Push Notification Channel Monitor
            Container(
              padding: const EdgeInsets.all(14),
              decoration: BoxDecoration(
                color: isDark ? const Color(0xFF06152D) : Colors.white,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: const Color(0xFF142E5E)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.notifications_active, color: Colors.amber, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'FCM PUSH NOTIFICATION STREAM',
                          style: TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: Colors.grey),
                        ),
                        const SizedBox(height: 4),
                        Text(
                          _lastNotification,
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: isDark ? Colors.white70 : Colors.black87,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // Section Header
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Queued Offline Mandates & Failures',
                  style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                ),
                Text(
                  '${_service.currentQueue.length} Items',
                  style: const TextStyle(fontSize: 12, color: Colors.blueAccent, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Queue List
            ListView.separated(
              shrinkWrap: true,
              physics: const NeverScrollableScrollPhysics(),
              itemCount: _service.currentQueue.length,
              separatorBuilder: (_, __) => const SizedBox(height: 10),
              itemBuilder: (context, index) {
                final item = _service.currentQueue[index];
                return Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: isDark ? const Color(0xFF071328) : Colors.white,
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(
                      color: item.isSynced ? Colors.green.withOpacity(0.3) : const Color(0xFF1B2D4F),
                    ),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Row(
                            children: [
                              Container(
                                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                                decoration: BoxDecoration(
                                  color: Colors.blue.withOpacity(0.15),
                                  borderRadius: BorderRadius.circular(6),
                                ),
                                child: Text(
                                  item.id,
                                  style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: Colors.blueAccent),
                                ),
                              ),
                              const SizedBox(width: 8),
                              Text(
                                item.merchantId,
                                style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600),
                              ),
                            ],
                          ),
                          Text(
                            'INR ${item.amountInr.toStringAsFixed(2)}',
                            style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w900, color: Colors.greenAccent),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Reason: ${item.failureReason}',
                        style: TextStyle(fontSize: 11, color: isDark ? Colors.white60 : Colors.black54),
                      ),
                      Text(
                        'Payer VPA: ${item.customerVpa}',
                        style: TextStyle(fontSize: 11, color: isDark ? Colors.white60 : Colors.black54),
                      ),
                      const SizedBox(height: 10),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: item.isSynced ? Colors.green.withOpacity(0.15) : Colors.amber.withOpacity(0.15),
                              borderRadius: BorderRadius.circular(6),
                            ),
                            child: Text(
                              item.syncStatus,
                              style: TextStyle(
                                fontSize: 10,
                                fontWeight: FontWeight.bold,
                                color: item.isSynced ? Colors.greenAccent : Colors.amber,
                              ),
                            ),
                          ),
                          if (!item.isSynced)
                            ElevatedButton.icon(
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF00D285),
                                foregroundColor: Colors.black,
                                padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                              ),
                              onPressed: () async {
                                final success = await _service.authenticateBiometricsAndRetry(item.id);
                                setState(() {});
                                if (success) {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('Biometric Verified! UPI Intent Executed.')),
                                  );
                                }
                              },
                              icon: const Icon(Icons.fingerprint, size: 14),
                              label: const Text(
                                'Biometric UPI Retry',
                                style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
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
      ),
    );
  }
}
