"""
RazorRevive B2B Conversational Autonomous Agent
==============================================
Interactive terminal dialogue agent for enterprise B2B accounts receivable.
Evaluates natural speech input, extracts entities (TDS, GSTIN, UTR, PTP),
enforces policy guardrails, and drives the deterministic B2B state machine.
"""

import os
import sys
import time

# Ensure repository root is in python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from backend.app.b2b.voice_agent import B2BVoiceDialogueEngine, VoiceDialogueTurnRequest
from backend.app.b2b.state_machine import b2b_fsm

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

BANNER = f"""{MAGENTA}{BOLD}
========================================================================================
   ____                                          _             _               _   
  |  _ \ __ _ _______  _ __ _ __   __ _ _   _   / \   __ _ ___(_)_ __  ___ ___| |_ 
  | |_) / _` |_  / _ \| '__| '_ \ / _` | | | | / _ \ / _` / __| | '_ \/ __/ _ \ __|
  |  _ < (_| |/ / (_) | |  | |_) | (_| | |_| |/ ___ \ (_| \__ \ | | | \__ \  __/ |_ 
  |_| \_\__,_/___\___/|_|  | .__/ \__,_|\__, /_/   \_\__, |___/_|_| |_|___/\___|\__|
                           |_|          |___/        |___/                         
       B2B AUTONOMOUS CONVERSATIONAL AGENT // VOICE & WHATSAPP DIALOGUE v2.0
========================================================================================{RESET}
{DIM}[NLP Intent Engine]  |  [Deterministic Policy Guardrails]  |  [FSM Durability]{RESET}
"""

SAMPLE_PROMPTS = [
    ("1", "TDS Deduction", "Humne 10% TDS deduct kiya hai Section 194J ke tehat, revised link bhejiye."),
    ("2", "UTR Confirmation", "Payment already transfer kar diya hai NEFT se, UTR number AXIS984729103 hai."),
    ("3", "GSTIN Correction", "Invoice pe GST update kar do, hamara valid GSTIN hai 29AABCU9603R1Z2."),
    ("4", "Legal Escalation", "Aapka service kharab hai, ye cheating hai, main lawyer ko bol raha hu court jayenge."),
    ("5", "Promise To Pay", "Abhi accounts closed hai, hum next Friday tak pakka clear kar denge.")
]

def main():
    os.system("cls" if os.name == "nt" else "clear")
    print(BANNER)
    
    invoice_id = "INV_ENTERPRISE_998"
    invoice_amount = 85000.0
    session_id = f"CALL_SES_{int(time.time())}"
    
    # Initialize state
    b2b_fsm.reset_state(invoice_id, "OVERDUE")
    
    print(f"{YELLOW}{BOLD}>>> [ACTIVE CALL SESSION CONTEXT]{RESET}")
    print(f"  • {BOLD}Invoice ID:{RESET}     {CYAN}{invoice_id}{RESET}")
    print(f"  • {BOLD}Total Due:{RESET}      {GREEN}INR {invoice_amount:,.2f}{RESET}")
    print(f"  • {BOLD}Initial FSM:{RESET}    {RED}{b2b_fsm.get_state(invoice_id)}{RESET}")
    print(f"  • {BOLD}Session ID:{RESET}     {DIM}{session_id}{RESET}")
    print(f"{DIM}----------------------------------------------------------------------------------------{RESET}")
    print(f"{BOLD}Try speaking or typing your customer response.{RESET}")
    print(f"{DIM}Quick Sample Prompts to test:{RESET}")
    for key, label, prompt_text in SAMPLE_PROMPTS:
        print(f"  [{CYAN}{key}{RESET}] {BOLD}{label}:{RESET} \"{prompt_text}\"")
    print(f"{DIM}(Type 1-5 for quick prompts, or type ANY sentence naturally in Hinglish/English. Type 'exit' to quit){RESET}")
    print(f"{DIM}----------------------------------------------------------------------------------------{RESET}\n")
    
    while True:
        try:
            user_input = input(f"{YELLOW}{BOLD}[CUSTOMER]:{RESET} ").strip()
        except (KeyboardInterrupt, EOFError):
            break
            
        if not user_input or user_input.lower() in ["exit", "quit", "q"]:
            print(f"\n{DIM}Ending session. Goodbye!{RESET}")
            break
            
        # Check quick menu shorthand
        for key, label, prompt_text in SAMPLE_PROMPTS:
            if user_input == key:
                user_input = prompt_text
                print(f"{DIM}>>> Selected Quick Prompt: \"{user_input}\"{RESET}")
                break
                
        req = VoiceDialogueTurnRequest(
            call_session_id=session_id,
            invoice_id=invoice_id,
            customer_speech_text=user_input,
            customer_phone="+919876543210",
            invoice_amount=invoice_amount
        )
        
        t_start = time.perf_counter()
        resp = B2BVoiceDialogueEngine.process_customer_turn(req)
        latency = (time.perf_counter() - t_start) * 1000
        
        # Display Agent Turn Details
        print(f"\n{CYAN}{BOLD}[AI AGENT SPEECH]:{RESET} {BOLD}\"{resp.agent_speech_response}\"{RESET}")
        print(f"   {BLUE}✦ Intent Detected:{RESET}      {BOLD}{resp.intent_detected}{RESET}")
        print(f"   {MAGENTA}✦ Action Executed:{RESET}      {BOLD}{resp.action_taken}{RESET}")
        print(f"   {GREEN}✦ FSM Current State:{RESET}    {BOLD}{resp.fsm_current_state}{RESET} {DIM}(State-Machine Verified){RESET}")
        
        if resp.mutation_proposal:
            prop = resp.mutation_proposal
            print(f"   {YELLOW}✦ Policy Mutation:{RESET}      Mutated '{prop.field_to_mutate}' from {prop.old_value} ➔ {BOLD}{prop.new_value}{RESET}")
            print(f"   {GREEN}✦ Policy Compliance:{RESET}    Approved: {prop.approved_by_policy} | Zero-Hallucination Guardrail Active")
            
        if resp.should_escalate_to_human:
            print(f"   {RED}{BOLD}🚨 ESCALATED TO CFO:{RESET} {RED}Legal/Dispute flag raised. Autonomous mutations locked.{RESET}")
            
        print(f"   {DIM}⏱ Decision Latency: {latency:.2f} ms{RESET}\n")

if __name__ == "__main__":
    main()
