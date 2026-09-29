"""
Soccer Bet Tracker, Analyzer & Predictor
First version - Streamlit app
Built for L - starts with the 20 Sep 2026 Hollywoodbets 41-leg multi as data entry #1
"""

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from pathlib import Path
import json

# -----------------------
# Database setup
# -----------------------
DB_PATH = Path(__file__).parent / "bets.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS bets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_number TEXT,
            bookie TEXT,
            bet_date TEXT,
            stake REAL,
            total_odds REAL,
            potential_payout REAL,
            status TEXT,
            notes TEXT,
            created_at TEXT
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS legs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            bet_id INTEGER,
            league TEXT,
            home_team TEXT,
            away_team TEXT,
            market TEXT,
            selection TEXT,
            odds_fractional TEXT,
            odds_decimal REAL,
            status TEXT,
            result_score TEXT,
            failure_reason TEXT,
            FOREIGN KEY (bet_id) REFERENCES bets (id)
        )
    """)

    conn.commit()
    conn.close()

def insert_first_slip():
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM bets")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    c.execute("""
        INSERT INTO bets (ticket_number, bookie, bet_date, stake, total_odds, potential_payout, status, notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "2083007773891721",
        "Hollywoodbets",
        "2026-09-20",
        2.00,
        8950927.4337199,
        23272411.33,
        "Lost",
        "41-leg multi. First real data entry. 14 losers killed the ticket.",
        datetime.now().isoformat()
    ))
    bet_id = c.lastrowid

    legs = [
        ("Netherlands - Eredivisie", "Feyenoord", "Utrecht", "Full Time", "Feyenoord", "1/4", "Lost"),
        ("Czech Republic - 1. Liga", "Hradec Kralove", "Teplice", "Full Time", "Hradec Kralove", "4/5", "Won"),
        ("Romania - Liga I", "SC FC Voluntari", "FC Universitatea Cluj", "Full Time", "FC Universitatea Cluj", "6/5", "Lost"),
        ("Spain - LaLiga", "Getafe", "Malaga", "Double Chance", "Getafe or Draw", "1/5", "Won"),
        ("Sweden - Allsvenskan", "Kalmar", "Hacken", "Double Chance", "Draw or Hacken", "7/20", "Won"),
        ("Switzerland - Swiss Super League", "Vaduz", "Thun", "Additional Totals", "Under 3.5", "1.03", "Won"),
        ("Sweden - Allsvenskan", "Halmstads BK", "AIK", "Additional Totals", "Under 3.5", "1/2", "Won"),
        ("Austria - Austrian Bundesliga", "Josko Ried", "Wolfsberger", "Double Chance", "Josko Ried or Wolfsberger", "1/4", "Won"),
        ("Austria - Austrian Bundesliga", "Hartberg", "LASK Linz", "Full Time", "LASK Linz", "7/25", "Won"),
        ("Netherlands - Eredivisie", "AZ Alkmaar", "Telstar", "Full Time", "AZ Alkmaar", "2/9", "Lost"),
        ("Netherlands - Eredivisie", "Twente", "PSV", "Full Time", "PSV", "1.06", "Won"),
        ("Ukraine - Premier League", "Karpaty Lviv", "Veres Rivne", "Full Time", "Karpaty Lviv", "2/5", "Lost"),
        ("Poland - Ekstraklasa", "Zaglebie Lubin", "Wisla Plock", "Double Chance", "Zaglebie Lubin or Draw", "7/20", "Lost"),
        ("England - Premier League", "Man City", "Sunderland", "Full Time", "Man City", "1/3", "Lost"),
        ("Italy - Serie A", "Frosinone", "Como 1907", "Full Time", "Como 1907", "9/20", "Won"),
        ("Czech Republic - 1. Liga", "Baumit Jablonec", "Fastav Zlin", "Full Time", "Baumit Jablonec", "9/20", "Lost"),
        ("Italy - Serie B", "Hellas Verona", "Vicenza", "Full Time", "Hellas Verona", "17/20", "Lost"),
        ("Italy - Serie B", "Arezzo", "Sudtirol", "1st Half Totals", "Over 0.5", "1/2", "Won"),
        ("Denmark - Superligaen", "Horsens", "Aarhus", "Additional Totals", "Under 3.5", "2/5", "Won"),
        ("Greece - Greek Super League", "APO Levadiakos FC", "Olympiacos Piraeus", "Full Time", "Olympiacos Piraeus", "1/3", "Lost"),
        ("Turkey - Super Lig", "Fenerbahce Istanbul", "Eyupspor", "Full Time", "Fenerbahce Istanbul", "2/11", "Won"),
        ("Spain - LaLiga", "Atl Madrid", "Real Madrid", "Full Time", "Real Madrid", "19/20", "Won"),
        ("Switzerland - Swiss Super League", "Basel", "St. Gallen", "Double Chance", "Basel or Draw", "11/20", "Lost"),
        ("Sweden - Allsvenskan", "Degerfors IF", "Hammarby IF", "Full Time", "Hammarby IF", "3/10", "Lost"),
        ("Sweden - Allsvenskan", "Mjallby AIF", "GAIS", "Total Corners", "Under 8.5", "1.7", "Won"),
        ("Ukraine - Premier League", "FC Shakhtar Donetsk", "LNZ Cherkasy", "Full Time", "FC Shakhtar Donetsk", "11/20", "Won"),
        ("Croatia - 1. HNL", "Rijeka", "Hajduk Split", "Double Chance", "Rijeka or Hajduk Split", "7/25", "Won"),
        ("Bosnia and Herzegovina - Premijer Liga", "Siroki Brijeg", "Borac Banja", "Full Time", "Borac Banja", "1/2", "Won"),
        ("England - Premier League", "Fulham", "Man Utd", "Double Chance", "Draw or Man Utd", "1/4", "Won"),
        ("Poland - Ekstraklasa", "Jagiellonia Bialystok", "Legia Warszawa", "Total Corners", "Under 7.5", "1.45", "Won"),
        ("Denmark - Superligaen", "Viborg FF", "Nordsjaelland", "MultiGoals", "1-3", "1/2", "Lost"),
        ("Cyprus - 1st Division", "Omonia", "Krasava Eny Ypsonas FC", "Full Time", "AC Omonia Nicosia", "2/11", "Lost"),
        ("Moldova - Divizia Nationala", "FC Sheriff Tiraspol", "FC Balti", "Full Time", "FC Sheriff Tiraspol", "1/25", "Won"),
        ("Spain - LaLiga", "Villarreal", "Levante", "Double Chance", "Villarreal or Draw", "2/14", "Won"),
        ("Greece - Greek Super League", "PAE PS Kalamata", "Panathinaikos Athens", "Full Time", "Panathinaikos Athens", "3/10", "Won"),
        ("Belgium - Pro League", "Club Brugge", "Genk", "Both Teams to Score", "No", "1.4", "Won"),
        ("Turkey - Super Lig", "Goztepe Izmir", "Rizespor", "Totals Away team", "Under 1.5", "3/5", "Won"),
        ("Croatia - 1. HNL", "Dinamo Zagreb", "NK Lokomotiva Zagreb", "Full Time", "Dinamo Zagreb", "1/5", "Lost"),
        ("Poland - Ekstraklasa", "KKS Lech Poznan", "RKS Radomiak Radom", "Full Time", "KKS Lech Poznan", "1/3", "Won"),
        ("Italy - Serie A", "AC Milan", "Lecce", "Full Time", "AC Milan", "1/4", "Won"),
        ("Spain - LaLiga", "Valencia", "Real Sociedad", "Double Chance", "Draw or Real Sociedad", "2/5", "Won"),
    ]

    for leg in legs:
        league, home, away, market, selection, odds_frac, status = leg
        c.execute("""
            INSERT INTO legs (bet_id, league, home_team, away_team, market, selection, odds_fractional, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (bet_id, league, home, away, market, selection, odds_frac, status))

    conn.commit()
    conn.close()

def load_bets():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM bets ORDER BY bet_date DESC", conn)
    conn.close()
    return df

def load_legs(bet_id=None):
    conn = get_connection()
    if bet_id:
        df = pd.read_sql_query("SELECT * FROM legs WHERE bet_id = ? ORDER BY id", conn, params=(bet_id,))
    else:
        df = pd.read_sql_query("SELECT * FROM legs ORDER BY id", conn)
    conn.close()
    return df

def get_stats():
    conn = get_connection()
    bets = pd.read_sql_query("SELECT * FROM bets", conn)
    legs = pd.read_sql_query("SELECT * FROM legs", conn)
    conn.close()

    total_staked = bets["stake"].sum() if not bets.empty else 0
    total_bets = len(bets)
    won_bets = len(bets[bets["status"] == "Won"]) if not bets.empty else 0
    lost_bets = len(bets[bets["status"] == "Lost"]) if not bets.empty else 0

    total_legs = len(legs)
    won_legs = len(legs[legs["status"] == "Won"]) if not legs.empty else 0
    lost_legs = len(legs[legs["status"] == "Lost"]) if not legs.empty else 0

    leg_win_rate = (won_legs / total_legs * 100) if total_legs > 0 else
