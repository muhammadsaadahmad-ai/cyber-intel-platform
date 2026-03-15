import os, sys

# Point to your phase 1, 2, 3 project directories
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
PHASE1_DIR  = os.path.expanduser("~/osint-threat-intel")
PHASE2_DIR  = os.path.expanduser("~/network-anomaly-detector")
PHASE3_DIR  = os.path.expanduser("~/redteam-toolkit")

# Add all phase dirs to path so we can import their modules
for d in [PHASE1_DIR, PHASE2_DIR, PHASE3_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

DATABASE_URL = "sqlite:///database/platform.db"
DASHBOARD_PORT = 5002

THREAT_HUNT_QUERIES = {
    "lateral_movement": {
        "description": "Detect lateral movement via SMB/RDP anomalies",
        "ports":       [445, 3389],
        "keywords":    ["smb", "rdp", "pass-the-hash", "psexec", "wmi"]
    },
    "c2_beaconing": {
        "description": "Detect C2 beaconing patterns",
        "ports":       [80, 443, 8080, 8443],
        "keywords":    ["beacon", "c2", "callback", "cobalt", "empire"]
    },
    "data_exfiltration": {
        "description": "Detect potential data exfiltration",
        "ports":       [21, 22, 53, 80, 443],
        "keywords":    ["exfil", "upload", "dns tunnel", "large transfer"]
    },
    "credential_access": {
        "description": "Detect credential harvesting attempts",
        "ports":       [22, 389, 636, 3306],
        "keywords":    ["brute", "spray", "mimikatz", "credential", "dump"]
    }
}

TABLETOP_SCENARIOS = [
    {
        "id":       1,
        "name":     "Ransomware Attack",
        "severity": "critical",
        "phases":   ["Recon", "Initial Access", "Execution",
                     "Persistence", "Exfiltration", "Impact"],
        "mitre":    ["T1566", "T1059", "T1486", "T1041"],
        "questions": [
            "How did the attacker gain initial access?",
            "What data was exfiltrated before encryption?",
            "How would you isolate affected systems?",
            "What is the recovery time objective (RTO)?",
            "How do you prevent reinfection?"
        ]
    },
    {
        "id":       2,
        "name":     "APT Intrusion",
        "severity": "high",
        "phases":   ["Recon", "Weaponisation", "Delivery",
                     "Exploitation", "C2", "Actions on Objectives"],
        "mitre":    ["T1592", "T1190", "T1071", "T1041"],
        "questions": [
            "What intelligence did the attacker gather in recon?",
            "Which vulnerability was exploited for initial access?",
            "How long was the attacker present before detection?",
            "What lateral movement techniques were used?",
            "How do you attribute the attack to a threat actor?"
        ]
    },
    {
        "id":       3,
        "name":     "Insider Threat",
        "severity": "high",
        "phases":   ["Reconnaissance", "Privilege Abuse",
                     "Data Staging", "Exfiltration"],
        "mitre":    ["T1078", "T1083", "T1074", "T1048"],
        "questions": [
            "What behavioural indicators preceded the incident?",
            "Which data was accessed outside normal patterns?",
            "How would DLP controls have helped?",
            "What is your insider threat detection policy?",
            "How do you balance monitoring with privacy?"
        ]
    },
    {
        "id":       4,
        "name":     "Zero-Day Exploit",
        "severity": "critical",
        "phases":   ["Discovery", "Weaponisation",
                     "Exploitation", "Persistence", "Impact"],
        "mitre":    ["T1190", "T1210", "T1543", "T1486"],
        "questions": [
            "How do you detect exploitation of an unknown vulnerability?",
            "What compensating controls apply before a patch exists?",
            "How do you communicate a zero-day to leadership?",
            "What is your emergency patching procedure?",
            "How do you assess blast radius?"
        ]
    }
]

