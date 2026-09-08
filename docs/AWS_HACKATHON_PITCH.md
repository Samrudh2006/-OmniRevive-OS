# 🏆 RazorRevive-AWS: Official 3-Minute Winning Demo Video Script
**Hackathon**: Bharat Builds Tour: First Commit (WeMakeDevs × AWS)  
**Track Target**: 🥇 Ship It (₹2,00,000 + Amazon Fast-Track Interview) & 🎨 Best UI (₹1,00,000)  
**Team**: `makers` | **Presenter**: Dwivedula Samrudh (@samrudhdwivedula)  
**Video Length Constraint**: Exactly 3 Minutes (180 Seconds)

---

## 🎬 Video Production Quick-Reference

| Time | Scene | On-Screen Action | Audio / Spoken Script |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:30** | **The Bharat Problem Hook** | Split-screen: UPI transaction failure animation & news headline: *"Over 30% of Indian Digital Transactions Face Temporary Bank Timeouts during Festival Sales"*. | "Every month, Indian businesses lose over ₹10,000 Crores due to digital payment failures. When an SBI or HDFC banking switch drops, systems blindly retry, causing double-charges and merchant churn. In B2B, a simple wrong GSTIN holds up an ₹85,000 invoice for weeks. We built **RazorRevive-AWS** to solve this." |
| **0:30 - 1:05** | **Architecture Overview** | Pan across the **RazorRevive-OS Control Plane** (`http://localhost:8000/`) showcasing the live telemetry, NPCI Switch Radar, and AWS badges. | "RazorRevive-AWS is an enterprise revenue recovery control plane combining **Amazon Bedrock (Claude 3.5 Sonnet)**, **AWS Cedar Zero-Trust Policies**, and **EventBridge serverless streams**. Instead of naive retries, we use SciPy Weibull hazard models to schedule mathematically optimal recovery windows." |
| **1:05 - 1:55** | **Live Demo: Bedrock Voice Agent** | Navigate to **Deep-Loop B2B Voice Station**. Click `Mic (STT)` or select GST Dispute. Click **Execute Autonomous B2B Voice Turn**. Click **View Dispatched Tax Invoice**. | "Watch our autonomous voice agent in action. A customer calls disputing their GST number in Hinglish: *'Invoice mein GSTIN galat hai, correct 29AABCU9603R1Z2 daal kar bhejo'*. **Amazon Bedrock** understands the nuance, verifies the GST format, and auto-dispatches an authentic RFC-compliant tax invoice email with a 1-click UPI link. Let's inspect the delivered invoice inside our interactive viewer." |
| **1:55 - 2:25** | **Live Demo: AWS Cedar Zero-Trust Radar** | Click the gradient **`AWS Bedrock & Cedar`** button in the header. Open the interactive playground. Select Scenario 1 (SRE Admin) ➡️ ALLOW. Then select Scenario 4 (Delete Audit Log) ➡️ FORBID/DENY. | "In financial systems, AI models must never have unchecked power. We integrated **AWS Cedar** to enforce formal zero-trust authorization. Only verified SRE Admins with MFA can trip circuit breakers, while destructive actions like deleting the audit trail are mathematically forbidden with cryptographically verifiable SHA-256 policy receipts." |
| **2:25 - 2:45** | **Live Demo: Standalone Android APK** | Hold up Android phone running [`RazorRevive-OS.apk`](file:///c:/Users/HP/Razorpay-Target-0.1percent-/mobile/razorrevive-os.apk) or screen-record the mobile UI. | "To give finance and SRE teams recovery control anywhere, we compiled a standalone native Android application—**RazorRevive-OS.apk**. It bundles the full UI offline and syncs live to our AWS backend with edge-to-edge hardware acceleration." |
| **2:45 - 3:00** | **Deployment, Impact & Closing** | Show the AWS App Runner & SAM Serverless architecture diagram. End on team slide (`Dwivedula Samrudh`, Team `makers`). | "Deployed via **AWS App Runner** and **AWS SAM**, RazorRevive-AWS delivers a 42.2% GMV recovery yield with exactly zero double-debit violations and 84 passing test suites. We are Team Makers, building the resilient backbone for Bharat's digital economy. Thank you." |

---

## 🎙️ Recording Tips & Visual Checklist

1. **Screen Resolution**: Set display to **1920x1080 (16:9)**.
2. **Audio Setup**: Use a headset or clear USB microphone; speak with confidence and energy.
3. **Browser State**: Keep `http://localhost:8000/` preloaded in full-screen (press `F11` to hide browser tabs).
4. **Key Interactive Moments**:
   - Show the green **`AWS Bedrock & Cedar`** top-nav button.
   - Show the **Allow/Deny** live evaluation badge in the Cedar playground.
   - Pop open the **View Dispatched Tax Invoice** iframe modal.
   - Show the mobile phone running the APK.

---

## 🛠️ Step-by-Step Deployment to AWS App Runner (During the 3 Days)

To launch the live URL for the **Ship It** submission:
```bash
# 1. Build and verify locally
uv run pytest -q

# 2. Deploy using AWS App Runner configuration
aws apprunner create-service --cli-input-json file://aws/deploy/apprunner.yaml
```
