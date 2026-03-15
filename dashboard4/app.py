from flask import Flask, render_template_string, jsonify
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.unified_models import Session, PlatformEvent, ThreatHunt, TabletopSession

app = Flask(__name__)

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CyberOps Platform — Capstone</title>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
<style>
:root{--bg:#020508;--panel:#050a0f;--border:#0d2233;--border2:#1a4a6b;
  --blue:#00aaff;--blue2:#0077cc;--blue3:#004a80;--dim:#1a3a4a;
  --red:#ff2a2a;--amber:#ffaa00;--green:#00ff88;--text:#b0e8ff;--muted:#3a6a7a;}
*{margin:0;padding:0;box-sizing:border-box;}
body{background:var(--bg);color:var(--text);font-family:'Share Tech Mono',monospace;min-height:100vh;}
body::before{content:'';position:fixed;top:0;left:0;width:100%;height:100%;
  background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,170,255,0.008) 2px,rgba(0,170,255,0.008) 4px);
  pointer-events:none;z-index:0;}
.scan{position:fixed;top:0;left:0;width:100%;height:2px;
  background:linear-gradient(90deg,transparent,rgba(0,170,255,0.3),transparent);
  animation:scan 5s linear infinite;pointer-events:none;z-index:999;}
@keyframes scan{from{top:0}to{top:100vh}}
.wrap{position:relative;z-index:1;padding:20px 24px;max-width:1400px;margin:0 auto;}
.hdr{display:flex;align-items:center;justify-content:space-between;
  border-bottom:1px solid var(--border2);padding-bottom:14px;margin-bottom:22px;}
.hdr-left{display:flex;align-items:center;gap:18px;}
.logo{width:52px;height:52px;border:1px solid var(--blue3);display:flex;
  align-items:center;justify-content:center;font-family:'Orbitron',monospace;
  font-weight:900;font-size:14px;color:var(--blue);position:relative;
  animation:pb 3s ease-in-out infinite;}
.logo::before{content:'';position:absolute;top:-4px;left:-4px;right:-4px;bottom:-4px;
  border:1px solid var(--blue3);opacity:0.3;}
@keyframes pb{0%,100%{border-color:var(--blue3)}50%{border-color:var(--blue2);box-shadow:0 0 16px rgba(0,170,255,0.2)}}
.title h1{font-family:'Orbitron',monospace;font-size:14px;font-weight:700;
  color:var(--blue);letter-spacing:3px;text-transform:uppercase;}
.title p{font-size:10px;color:var(--muted);letter-spacing:2px;margin-top:3px;}
.live{display:inline-flex;align-items:center;gap:7px;font-size:10px;color:var(--blue2);letter-spacing:2px;}
.dot{width:7px;height:7px;border-radius:50%;background:var(--blue);animation:blink 1.2s infinite;}
@keyframes blink{0%,100%{opacity:1}50%{opacity:0.15}}
.ts-clock{font-size:10px;color:var(--muted);margin-top:5px;letter-spacing:1px;}

/* Phase badges */
.phases{display:flex;gap:10px;margin-bottom:22px;}
.phase-badge{flex:1;border:1px solid var(--border2);background:var(--panel);
  padding:14px;text-align:center;position:relative;overflow:hidden;}
.phase-badge::before{content:'';position:absolute;top:0;left:0;width:100%;height:3px;}
.pb1::before{background:#00ff88;}.pb2::before{background:#00aaff;}.pb3::before{background:#ff6644;}
.pb-label{font-size:9px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;}
.pb-name{font-family:'Orbitron',monospace;font-size:11px;font-weight:700;color:var(--text);}
.pb-status{font-size:9px;margin-top:6px;}
.pb1 .pb-status{color:#00ff88;}.pb2 .pb-status{color:#00aaff;}.pb3 .pb-status{color:#ff6644;}

/* Stats grid */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:22px;}
.stat{border:1px solid var(--border);background:var(--panel);padding:16px 18px;position:relative;overflow:hidden;}
.stat::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:var(--blue3);}
.stat.sr::before{background:var(--red);}.stat.sa::before{background:var(--amber);}.stat.sg::before{background:var(--green);}
.sl{font-size:9px;color:var(--muted);letter-spacing:2px;text-transform:uppercase;margin-bottom:10px;}
.sn{font-family:'Orbitron',monospace;font-size:32px;font-weight:700;color:var(--blue);line-height:1;}
.stat.sr .sn{color:var(--red);}.stat.sa .sn{color:var(--amber);}.stat.sg .sn{color:var(--green);}
.ss{font-size:9px;color:var(--dim);margin-top:8px;}

/* Two column layout */
.cols{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin-bottom:20px;}
.sec-hdr{font-family:'Orbitron',monospace;font-size:10px;color:var(--blue2);
  letter-spacing:3px;margin-bottom:10px;}
.sec-hdr::before{content:'> ';color:var(--blue3);}
.tbl-wrap{border:1px solid var(--border);overflow:hidden;}
table{width:100%;border-collapse:collapse;}
thead tr{background:#071218;border-bottom:1px solid var(--border2);}
th{padding:9px 12px;font-size:9px;color:var(--blue3);letter-spacing:2px;
  text-transform:uppercase;text-align:left;font-weight:400;}
tbody tr{border-bottom:1px solid var(--border);transition:background 0.15s;}
tbody tr:hover{background:#071218;}
td{padding:9px 12px;font-size:10px;}
.iv{color:#e0f4ff;font-family:'Share Tech Mono',monospace;}
.mc{color:var(--muted);font-size:10px;}
.badge{display:inline-block;padding:2px 8px;font-size:9px;letter-spacing:1px;border:1px solid;text-transform:uppercase;}
.bh{color:var(--red);border-color:#6b1212;background:#1a0505;}
.bm{color:var(--amber);border-color:#6b4a00;background:#1a1100;}
.bl{color:var(--blue);border-color:#004a6b;background:#00111a;}
.bg{color:var(--green);border-color:#006644;background:#001a11;}
.bp1{color:#00ff88;border-color:#006633;background:#001a0d;}
.bp2{color:#00aaff;border-color:#004a80;background:#00111a;}
.bp3{color:#ff6644;border-color:#803322;background:#1a0a05;}
.empty td{color:var(--muted);text-align:center;padding:24px;font-size:10px;}
.footer{margin-top:18px;padding-top:12px;border-top:1px solid var(--border);
  display:flex;justify-content:space-between;}
.fl{font-size:9px;color:var(--blue3);letter-spacing:2px;}
.fr{font-size:9px;color:var(--dim);}
</style>
</head>
<body>
<div class="scan"></div>
<div class="wrap">

  <div class="hdr">
    <div class="hdr-left">
      <div class="logo">COP</div>
      <div class="title">
        <h1>CyberOps Platform &mdash; Integrated Intel Center</h1>
        <p>CAPSTONE // PHASES 1-3 UNIFIED // ARMY INTELLIGENCE PORTFOLIO</p>
      </div>
    </div>
    <div style="text-align:right">
      <div class="live"><span class="dot"></span>ALL SYSTEMS ACTIVE</div>
      <div class="ts-clock" id="ts">--:--:-- UTC</div>
    </div>
  </div>

  <!-- Phase status -->
  <div class="phases">
    <div class="phase-badge pb1">
      <div class="pb-label">Phase 1</div>
      <div class="pb-name">OSINT + IOC Engine</div>
      <div class="pb-status">{{ p1_count }} IOCs collected</div>
    </div>
    <div class="phase-badge pb2">
      <div class="pb-label">Phase 2</div>
      <div class="pb-name">Anomaly Detector</div>
      <div class="pb-status">{{ p2_count }} alerts imported</div>
    </div>
    <div class="phase-badge pb3">
      <div class="pb-label">Phase 3</div>
      <div class="pb-name">Red Team Toolkit</div>
      <div class="pb-status">{{ p3_count }} CVE findings</div>
    </div>
    <div class="phase-badge" style="border-color:#534AB7;">
      <div class="pb-label" style="color:#7F77DD;">Threat Hunts</div>
      <div class="pb-name" style="color:#AFA9EC;">Hunt Engine</div>
      <div class="pb-status" style="color:#7F77DD;">{{ hunt_count }} hunts run</div>
    </div>
  </div>

  <!-- Stat cards -->
  <div class="stats">
    <div class="stat">
      <div class="sl">Total events</div>
      <div class="sn">{{ total }}</div>
      <div class="ss">all phases combined</div>
    </div>
    <div class="stat sr">
      <div class="sl">Critical / High</div>
      <div class="sn">{{ critical }}</div>
      <div class="ss">immediate action</div>
    </div>
    <div class="stat sa">
      <div class="sl">Tabletop sessions</div>
      <div class="sn">{{ tabletop_count }}</div>
      <div class="ss">exercises completed</div>
    </div>
    <div class="stat sg">
      <div class="sl">MITRE techniques</div>
      <div class="sn">{{ mitre_count }}</div>
      <div class="ss">unique ATT&amp;CK IDs</div>
    </div>
  </div>

  <!-- Two column: events + hunts -->
  <div class="cols">
    <div>
      <div class="sec-hdr">Unified event feed</div>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>Source</th><th>Type</th><th>Severity</th><th>MITRE</th><th>Time</th></tr></thead>
          <tbody>
            {% for e in events %}
            <tr>
              <td>
                {% if e.source == 'phase1' %}<span class="badge bp1">P1</span>
                {% elif e.source == 'phase2' %}<span class="badge bp2">P2</span>
                {% elif e.source == 'phase3' %}<span class="badge bp3">P3</span>
                {% else %}<span class="badge bl">{{ e.source }}</span>{% endif %}
              </td>
              <td class="iv">{{ e.event_type[:18] }}</td>
              <td>
                {% if e.severity in ['critical','high'] %}<span class="badge bh">{{ e.severity }}</span>
                {% elif e.severity == 'medium' %}<span class="badge bm">{{ e.severity }}</span>
                {% else %}<span class="badge bl">{{ e.severity }}</span>{% endif %}
              </td>
              <td class="mc">{{ e.mitre_id }}</td>
              <td class="mc">{{ e.timestamp.strftime('%H:%M:%S') }}</td>
            </tr>
            {% else %}
            <tr class="empty"><td colspan="5">[ NO EVENTS — RUN PIPELINE FIRST ]</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>

    <div>
      <div class="sec-hdr">Threat hunt log</div>
      <div class="tbl-wrap">
        <table>
          <thead><tr><th>Hypothesis</th><th>Status</th><th>Findings</th><th>Time</th></tr></thead>
          <tbody>
            {% for h in hunts %}
            <tr>
              <td class="iv">{{ h.hypothesis[:22] }}</td>
              <td>
                {% if h.status == 'findings' %}<span class="badge bh">FINDINGS</span>
                {% else %}<span class="badge bg">NEGATIVE</span>{% endif %}
              </td>
              <td class="mc">{{ h.analyst_notes[:30] }}</td>
              <td class="mc">{{ h.timestamp.strftime('%H:%M:%S') }}</td>
            </tr>
            {% else %}
            <tr class="empty"><td colspan="4">[ NO HUNTS RUN YET ]</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </div>
  </div>

  <div class="footer">
    <div class="fl">CYBEROPS PLATFORM v1.0 // CAPSTONE // PHASES 1-2-3 UNIFIED</div>
    <div class="fr">PORTFOLIO &mdash; MUHAMMAD SAAD AHMAD</div>
  </div>
</div>

<script>
(function tick(){
  const t=new Date().toUTCString().match(/(\\d{2}:\\d{2}:\\d{2})/);
  if(t) document.getElementById('ts').textContent=t[1]+' UTC';
  setTimeout(tick,1000);
})();
</script>
</body>
</html>"""

@app.route("/")
def index():
    session = Session()
    events  = session.query(PlatformEvent)\
                     .order_by(PlatformEvent.timestamp.desc())\
                     .limit(50).all()
    hunts   = session.query(ThreatHunt)\
                     .order_by(ThreatHunt.timestamp.desc())\
                     .limit(20).all()
    tabs    = session.query(TabletopSession).all()

    total    = session.query(PlatformEvent).count()
    critical = session.query(PlatformEvent)\
                      .filter(PlatformEvent.severity.in_(["critical","high"]))\
                      .count()
    p1_count = session.query(PlatformEvent)\
                      .filter_by(source="phase1").count()
    p2_count = session.query(PlatformEvent)\
                      .filter_by(source="phase2").count()
    p3_count = session.query(PlatformEvent)\
                      .filter_by(source="phase3").count()

    mitre_ids = session.query(PlatformEvent.mitre_id)\
                       .distinct().count()
    session.close()

    return render_template_string(
        TEMPLATE,
        events=events, hunts=hunts,
        total=total, critical=critical,
        p1_count=p1_count, p2_count=p2_count, p3_count=p3_count,
        hunt_count=len(hunts), tabletop_count=len(tabs),
        mitre_count=mitre_ids
    )

@app.route("/api/events")
def api_events():
    session = Session()
    events  = session.query(PlatformEvent)\
                     .order_by(PlatformEvent.timestamp.desc())\
                     .limit(100).all()
    session.close()
    return jsonify([{
        "source": e.source, "type": e.event_type,
        "severity": e.severity, "description": e.description,
        "mitre_id": e.mitre_id, "mitre_name": e.mitre_name,
        "time": str(e.timestamp)
    } for e in events])

def run_dashboard():
    app.run(host="127.0.0.1", port=5002, debug=False)
