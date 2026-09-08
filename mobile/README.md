# RazorRevive-OS Mobile (Android APK)

A dedicated, isolated native Android client for **RazorRevive-OS | AI Revenue Recovery Control Plane**.

---

## 📱 Pre-Built APK Location

The compiled Android application package is ready for direct installation:
- **Distribution File**: [`mobile/razorrevive-os.apk`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/mobile/razorrevive-os.apk) (13.38 MB)
- **Gradle Debug Artifact**: [`mobile/app/build/outputs/apk/debug/app-debug.apk`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/mobile/app/build/outputs/apk/debug/app-debug.apk)

---

## 🚀 How to Install

### Option A: Install on Connected Phone or Emulator via ADB
```bash
adb install -r mobile/razorrevive-os.apk
```

### Option B: Sideload onto Android Phone
1. Transfer `mobile/razorrevive-os.apk` to your Android phone via USB, Google Drive, or WhatsApp.
2. Tap the APK in your phone's File Manager and select **Install**.
3. Allow "Install unknown apps" if prompted.

---

## ⚡ Features & Architecture

1. **Complete Codebase Isolation**:
   - Resides strictly in `mobile/` without modifying any backend APIs, root scripts, or test suites.
2. **Dual Operation Modes**:
   - **📦 Bundled Offline Mode**: Loads the complete mobile-optimized control plane UI directly from internal Android assets (`file:///android_asset/www/index.html`) without requiring internet connection.
   - **💻 Android Emulator Sync**: One-tap connection to your local backend on `http://10.0.2.2:8000`.
   - **🌐 Production Cloud**: Connects to the live Render deployment (`https://razorpay-target-0-1percent.onrender.com`).
   - **✏️ Custom LAN IP**: Configure your computer's local Wi-Fi IP (e.g. `http://192.168.1.50:8000`) for real-time testing on physical devices.
3. **Voice Engine & WebAudio Support**:
   - Pre-configured with `RECORD_AUDIO` and `MODIFY_AUDIO_SETTINGS` permissions.
   - `WebChromeClient` auto-grants WebRTC audio capture so the B2B Hinglish Voice STT microphone runs without blocking.
4. **Official Razorpay Branding**:
   - Razorpay dark navy `#0c2340` status bar and corporate theme.
   - Electric lightning vector launcher icon.

---

## 🛠️ How to Rebuild the APK

To rebuild the APK at any time:
```cmd
cd mobile
build_apk.bat
```
or with Gradle:
```cmd
cd mobile
gradlew.bat assembleDebug
```
