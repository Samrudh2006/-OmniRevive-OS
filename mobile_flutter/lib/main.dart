import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'screens/overview_screen.dart';
import 'screens/rails_screen.dart';
import 'screens/voice_screen.dart';
import 'screens/cedar_screen.dart';
import 'screens/audit_screen.dart';

void main() {
  runApp(const OmniReviveApp());
}

class OmniReviveApp extends StatefulWidget {
  const OmniReviveApp({Key? key}) : super(key: key);

  @override
  State<OmniReviveApp> createState() => _OmniReviveAppState();
}

class _OmniReviveAppState extends State<OmniReviveApp> {
  bool _isDarkMode = true;

  void toggleTheme() {
    setState(() {
      _isDarkMode = !_isDarkMode;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'OmniRevive-OS',
      debugShowCheckedModeBanner: false,
      themeMode: _isDarkMode ? ThemeMode.dark : ThemeMode.light,
      theme: ThemeData(
        brightness: Brightness.light,
        scaffoldBackgroundColor: const Color(0xFFF4F8FE),
        primaryColor: const Color(0xFF0C6CF2),
        colorScheme: const ColorScheme.light(
          primary: Color(0xFF0C6CF2),
          secondary: Color(0xFF00D285),
          surface: Colors.white,
          background: Color(0xFFF4F8FE),
        ),
        textTheme: GoogleFonts.plusJakartaSansTextTheme(ThemeData.light().textTheme),
        cardTheme: CardTheme(
          color: Colors.white,
          elevation: 2,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0xFFD4E5F9), width: 1),
          ),
        ),
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF030816),
        primaryColor: const Color(0xFF0C55EA),
        colorScheme: const ColorScheme.dark(
          primary: Color(0xFF0C55EA),
          secondary: Color(0xFF00D285),
          surface: Color(0xFF071328),
          background: Color(0xFF030816),
        ),
        textTheme: GoogleFonts.plusJakartaSansTextTheme(ThemeData.dark().textTheme),
        cardTheme: CardTheme(
          color: const Color(0xFF071328),
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
            side: const BorderSide(color: Color(0xFF142442), width: 1),
          ),
        ),
      ),
      home: MainNavigationShell(
        isDarkMode: _isDarkMode,
        onToggleTheme: toggleTheme,
      ),
    );
  }
}

class MainNavigationShell extends StatefulWidget {
  final bool isDarkMode;
  final VoidCallback onToggleTheme;

  const MainNavigationShell({
    Key? key,
    required this.isDarkMode,
    required this.onToggleTheme,
  }) : super(key: key);

  @override
  State<MainNavigationShell> createState() => _MainNavigationShellState();
}

class _MainNavigationShellState extends State<MainNavigationShell> {
  int _currentIndex = 0;

  final List<Widget> _screens = const [
    OverviewScreen(),
    RailsScreen(),
    VoiceScreen(),
    CedarScreen(),
    AuditScreen(),
  ];

  @override
  Widget build(BuildContext context) {
    final isDark = widget.isDarkMode;
    return Scaffold(
      appBar: AppBar(
        elevation: 0,
        backgroundColor: isDark ? const Color(0xFF050C1B) : Colors.white,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFF0C6CF2).withOpacity(0.15),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.bolt, color: Color(0xFF0C6CF2), size: 20),
            ),
            const SizedBox(width: 8),
            Text(
              'OmniRevive',
              style: TextStyle(
                fontWeight: FontWeight.w900,
                fontSize: 18,
                color: isDark ? Colors.white : const Color(0xFF0C2340),
              ),
            ),
            Text(
              '-OS',
              style: TextStyle(
                fontWeight: FontWeight.w900,
                fontSize: 18,
                color: isDark ? const Color(0xFF38BDF8) : const Color(0xFF0C6CF2),
              ),
            ),
            const SizedBox(width: 6),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
              decoration: BoxDecoration(
                color: Colors.cyan.withOpacity(0.15),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.cyan.withOpacity(0.4)),
              ),
              child: const Text(
                'v1.1',
                style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold, color: Colors.cyan),
              ),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: Icon(isDark ? Icons.light_mode : Icons.dark_mode, size: 20),
            onPressed: widget.onToggleTheme,
            tooltip: 'Toggle Theme',
          ),
          IconButton(
            icon: const Icon(Icons.notifications_none, size: 20),
            onPressed: () {},
          ),
        ],
      ),
      body: _screens[_currentIndex],
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
          border: Border(
            top: BorderSide(
              color: isDark ? const BorderSide(color: Color(0xFF142442)).color : const Color(0xFFD4E5F9),
              width: 1,
            ),
          ),
        ),
        child: BottomNavigationBar(
          currentIndex: _currentIndex,
          onTap: (index) => setState(() => _currentIndex = index),
          type: BottomNavigationBarType.fixed,
          backgroundColor: isDark ? const Color(0xFF040918) : Colors.white,
          selectedItemColor: const Color(0xFF0C6CF2),
          unselectedItemColor: isDark ? Colors.slate : const Color(0xFF64748B),
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.bold, fontSize: 11),
          unselectedLabelStyle: const TextStyle(fontSize: 10),
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.dashboard_outlined),
              activeIcon: Icon(Icons.dashboard),
              label: 'Overview',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.alt_route_outlined),
              activeIcon: Icon(Icons.alt_route),
              label: 'Rails',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.mic_none_outlined),
              activeIcon: Icon(Icons.mic),
              label: 'Voice AI',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.shield_outlined),
              activeIcon: Icon(Icons.shield),
              label: 'Cedar',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.verified_outlined),
              activeIcon: Icon(Icons.verified),
              label: 'Audit',
            ),
          ],
        ),
      ),
    );
  }
}
