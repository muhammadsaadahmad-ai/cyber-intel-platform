from sqlalchemy import (create_engine, Column, Integer, String,
                        DateTime, Text, Boolean, Float)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config4 import DATABASE_URL

Base    = declarative_base()
engine  = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

class PlatformEvent(Base):
    __tablename__ = "events"
    id            = Column(Integer, primary_key=True)
    timestamp     = Column(DateTime, default=datetime.utcnow)
    source        = Column(String(50))   # phase1 / phase2 / phase3
    event_type    = Column(String(50))
    severity      = Column(String(20))
    description   = Column(Text)
    mitre_id      = Column(String(20))
    mitre_name    = Column(String(100))

class ThreatHunt(Base):
    __tablename__ = "threat_hunts"
    id            = Column(Integer, primary_key=True)
    timestamp     = Column(DateTime, default=datetime.utcnow)
    hypothesis    = Column(String(100))
    findings      = Column(Text)
    status        = Column(String(20), default="open")
    analyst_notes = Column(Text)

class TabletopSession(Base):
    __tablename__ = "tabletop_sessions"
    id            = Column(Integer, primary_key=True)
    timestamp     = Column(DateTime, default=datetime.utcnow)
    scenario_name = Column(String(100))
    severity      = Column(String(20))
    completed     = Column(Boolean, default=False)
    notes         = Column(Text)

def init_db():
    Base.metadata.create_all(engine)
    print("[+] Unified platform database initialized.")
