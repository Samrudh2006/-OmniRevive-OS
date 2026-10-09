import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';

/// Represents a queued offline payment/mandate recovery attempt
class QueuedOfflinePayment {
  final String id;
  final String merchantId;
  final double amountInr;
  final String customerVpa;
  final String failureReason;
  final DateTime queuedAt;
  bool isSynced;
  String syncStatus;

  QueuedOfflinePayment({
    required this.id,
    required this.merchantId,
    required this.amountInr,
    required this.customerVpa,
    required this.failureReason,
    required this.queuedAt,
    this.isSynced = false,
    this.syncStatus = 'PENDING_OFFLINE_QUEUE',
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'merchantId': merchantId,
    'amountInr': amountInr,
    'customerVpa': customerVpa,
    'failureReason': failureReason,
    'queuedAt': queuedAt.toIso8601String(),
    'isSynced': isSynced,
    'syncStatus': syncStatus,
  };
}

/// Manages offline transaction caching, biometrics-backed verification,
/// and automatic cloud synchronization upon reconnection.
class OfflineMandateService {
  static final OfflineMandateService _instance = OfflineMandateService._internal();
  factory OfflineMandateService() => _instance;
  OfflineMandateService._internal() {
    _seedMockOfflineQueue();
  }

  final List<QueuedOfflinePayment> _queue = [];
  bool _isOnline = true;
  final _syncStreamController = StreamController<List<QueuedOfflinePayment>>.broadcast();

  Stream<List<QueuedOfflinePayment>> get queueStream => _syncStreamController.stream;
  List<QueuedOfflinePayment> get currentQueue => List.unmodifiable(_queue);
  bool get isOnline => _isOnline;

  void _seedMockOfflineQueue() {
    _queue.addAll([
      QueuedOfflinePayment(
        id: 'off_tx_90124',
        merchantId: 'merchant_swiggy_delhi',
        amountInr: 450.0,
        customerVpa: 'rahul.verma@okhdfcbank',
        failureReason: 'GATEWAY_TIMEOUT_OFFLINE_CACHED',
        queuedAt: DateTime.now().subtract(const Duration(minutes: 12)),
      ),
      QueuedOfflinePayment(
        id: 'off_tx_90125',
        merchantId: 'merchant_zomato_blr',
        amountInr: 1290.0,
        customerVpa: 'priya.s@icici',
        failureReason: 'NETWORK_DROP_DURING_2FA',
        queuedAt: DateTime.now().subtract(const Duration(minutes: 5)),
      ),
    ]);
  }

  void setNetworkStatus(bool online) {
    _isOnline = online;
    if (online) {
      syncPendingQueue();
    }
  }

  void enqueuePayment({
    required String merchantId,
    required double amountInr,
    required String customerVpa,
    required String failureReason,
  }) {
    final item = QueuedOfflinePayment(
      id: 'off_tx_${DateTime.now().millisecondsSinceEpoch.toString().substring(7)}',
      merchantId: merchantId,
      amountInr: amountInr,
      customerVpa: customerVpa,
      failureReason: failureReason,
      queuedAt: DateTime.now(),
    );
    _queue.insert(0, item);
    _syncStreamController.add(_queue);
  }

  Future<bool> authenticateBiometricsAndRetry(String paymentId) async {
    // Simulates local hardware secure biometric authentication (FaceID / Fingerprint)
    await Future.delayed(const Duration(milliseconds: 600));
    final index = _queue.indexWhere((item) => item.id == paymentId);
    if (index != -1) {
      _queue[index].syncStatus = 'BIOMETRIC_VERIFIED_RETRYING';
      _syncStreamController.add(_queue);
      
      // Simulate UPI intent execution
      await Future.delayed(const Duration(milliseconds: 900));
      _queue[index].isSynced = true;
      _queue[index].syncStatus = 'RECOVERED_SUCCESS_UPI_INTENT';
      _syncStreamController.add(_queue);
      return true;
    }
    return false;
  }

  Future<int> syncPendingQueue() async {
    int syncedCount = 0;
    for (var item in _queue) {
      if (!item.isSynced) {
        item.syncStatus = 'SYNCING_WITH_OMNIREVIVE_CLOUD';
        _syncStreamController.add(_queue);
        await Future.delayed(const Duration(milliseconds: 400));
        item.isSynced = true;
        item.syncStatus = 'RECOVERED_VIA_BACKGROUND_WORKER';
        syncedCount++;
      }
    }
    _syncStreamController.add(_queue);
    return syncedCount;
  }
}
