import 'package:flutter/material.dart';

class VoiceScreen extends StatefulWidget {
  const VoiceScreen({Key? key}) : super(key: key);

  @override
  State<VoiceScreen> createState() => _VoiceScreenState();
}

class _VoiceScreenState extends State<VoiceScreen> {
  String _selectedLang = 'telugu';
  bool _isPlaying = false;

  final Map<String, Map<String, String>> _dialogues = {
    'telugu': {
      'title': 'Telugu (తెలుగు)',
      'audioTag': 'te-IN Neural Synthesis',
      'transcript': '"నమస్కారం అండి, మీ ₹85,000 ఇన్‌వాయిస్ చెల్లింపులో GSTIN సరిపోలకపోవడం వల్ల హోల్డ్ అయింది. మేము సరిదిద్దిన ఇన్‌వాయిస్‌ను వాట్సాప్ లింక్ ద్వారా పంపించాము..."',
      'intent': 'GSTIN Mutation Proposed -> PTP Calendar Locked (19th Sept)',
      'fsmState': 'STATE_PTP_CONFIRMED',
    },
    'hindi': {
      'title': 'Hindi (हिंदी)',
      'audioTag': 'hi-IN Neural Synthesis',
      'transcript': '"नमस्ते, आपके ₹42,500 के भुगतान में HDFC स्विच टाइमआउट हुआ था। हमारी AI प्रणाली ने 0.23ms में वैकल्पिक UPI रेल तैयार की है..."',
      'intent': 'Switch Timeout Fallback -> UPI Dynamic QR Auto-Dispatched',
      'fsmState': 'STATE_RETRY_ROUTED',
    },
    'english': {
      'title': 'English (en-IN)',
      'audioTag': 'en-IN Enterprise Tone',
      'transcript': '"Hello CFO, your ₹1,20,000 bulk mandate experienced a soft decline. We have scheduled an optimal Weibull retry window for 11:30 AM."',
      'intent': 'Mandate Churn Avoidance -> Optimal Survival Window Scheduled',
      'fsmState': 'STATE_WINDOW_OPTIMIZED',
    },
  };

  void _togglePlay() {
    setState(() {
      _isPlaying = !_isPlaying;
    });
    if (_isPlaying) {
      Future.delayed(const Duration(seconds: 4), () {
        if (mounted) {
          setState(() {
            _isPlaying = false;
          });
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final dialogue = _dialogues[_selectedLang]!;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.between,
            children: [
              const Text(
                'Voice AI Studio',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: const Color(0xFF7C3AED).withOpacity(0.15),
                  borderRadius: BorderRadius.circular(10),
                  border: Border.all(color: const Color(0xFF7C3AED).withOpacity(0.3)),
                ),
                child: const Text(
                  '180ms Turn Latency',
                  style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Color(0xFF7C3AED)),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            'Autonomous trilingual B2B invoice dispute negotiation and PTP calendar booking.',
            style: TextStyle(
              fontSize: 12,
              color: isDark ? Colors.grey[400] : const Color(0xFF64748B),
            ),
          ),
          const SizedBox(height: 16),

          // Language Selector Tabs
          Row(
            children: ['telugu', 'hindi', 'english'].map((lang) {
              final isSelected = _selectedLang == lang;
              return Expanded(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 3),
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isSelected
                          ? const Color(0xFF7C3AED)
                          : (isDark ? const Color(0xFF071328) : Colors.white),
                      foregroundColor: isSelected
                          ? Colors.white
                          : (isDark ? Colors.grey[300] : const Color(0xFF1E293B)),
                      elevation: isSelected ? 2 : 0,
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(10),
                        side: BorderSide(
                          color: isSelected
                              ? const Color(0xFF7C3AED)
                              : (isDark ? const Color(0xFF142442) : const Color(0xFFE2E8F0)),
                        ),
                      ),
                      padding: const EdgeInsets.symmetric(vertical: 10),
                    ),
                    onPressed: () {
                      setState(() {
                        _selectedLang = lang;
                        _isPlaying = false;
                      });
                    },
                    child: Text(
                      _dialogues[lang]!['title']!,
                      style: const TextStyle(fontSize: 11, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),

          const SizedBox(height: 16),

          // Voice Player Visualizer Card
          Container(
            padding: const EdgeInsets.all(18),
            decoration: BoxDecoration(
              color: isDark ? const Color(0xFF071328) : Colors.white,
              borderRadius: BorderRadius.circular(20),
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
                        CircleAvatar(
                          radius: 20,
                          backgroundColor: const Color(0xFF7C3AED).withOpacity(0.15),
                          child: IconButton(
                            icon: Icon(
                              _isPlaying ? Icons.pause : Icons.play_arrow,
                              color: const Color(0xFF7C3AED),
                              size: 20,
                            ),
                            onPressed: _togglePlay,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              dialogue['audioTag']!,
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13),
                            ),
                            Text(
                              _isPlaying ? 'Playing synthetic audio...' : 'Tap play to synthesize voice',
                              style: TextStyle(
                                fontSize: 11,
                                color: isDark ? Colors.grey[400] : const Color(0xFF64748B),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                    if (_isPlaying)
                      Row(
                        children: List.generate(5, (i) {
                          return Container(
                            margin: const EdgeInsets.symmetric(horizontal: 1.5),
                            width: 3,
                            height: 8.0 + (i % 3) * 6,
                            decoration: BoxDecoration(
                              color: const Color(0xFF7C3AED),
                              borderRadius: BorderRadius.circular(2),
                            ),
                          );
                        }),
                      ),
                  ],
                ),
                const SizedBox(height: 16),

                // Transcript
                Container(
                  padding: const EdgeInsets.all(14),
                  decoration: BoxDecoration(
                    color: const Color(0xFF7C3AED).withOpacity(0.08),
                    borderRadius: BorderRadius.circular(14),
                    border: Border.all(color: const Color(0xFF7C3AED).withOpacity(0.2)),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'REAL-TIME SPEECH STREAM',
                        style: TextStyle(
                          fontSize: 9,
                          fontWeight: FontWeight.bold,
                          letterSpacing: 0.8,
                          color: Color(0xFF7C3AED),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        dialogue['transcript']!,
                        style: const TextStyle(fontSize: 13, height: 1.4, fontWeight: FontWeight.w600),
                      ),
                    ],
                  ),
                ),

                const SizedBox(height: 12),

                // Extracted Intent
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'EXTRACTED INTENT & COMMITMENT',
                            style: TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.grey),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            dialogue['intent']!,
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF00D285),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Text(
                        dialogue['fsmState']!,
                        style: const TextStyle(fontSize: 9, fontWeight: FontWeight.bold, color: Colors.blue),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
