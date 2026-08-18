#!/usr/bin/env python3
"""
Dividend Investing Calendar
===========================

Single-file dividend screening algorithm + Tkinter calendar GUI.

The stock universe below contains exactly 607 stock tickers from market_data.zip.
Forex, futures, and archive support files are excluded.

The workflow is implemented from "Dividend Calendar.csv" with its exact
Task / Value / Status schema and exact supplied task text.

Dependencies:
    pip install yfinance pandas pandas_ta numpy

Run:
    python dividend_investing_calendar.py

Place "Dividend Calendar.csv" in the same directory as this script if you want
the app to validate the external CSV. The exact supplied workflow is also
embedded below so the algorithm remains self-contained.
"""

from __future__ import annotations

import calendar as pycalendar
import math
import queue
import threading
import traceback
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

try:
    import yfinance as yf
except ImportError as exc:
    raise SystemExit("Missing dependency: yfinance. Install with: pip install yfinance") from exc

try:
    import pandas_ta as ta
except ImportError as exc:
    raise SystemExit("Missing dependency: pandas_ta. Install with: pip install pandas_ta") from exc


# ---------------------------------------------------------------------------
# EXACT 607-STOCK UNIVERSE
# ---------------------------------------------------------------------------

STOCKS: List[str] = [
    'A',
    'AB',
    'ABBV',
    'ABEO',
    'ABX',
    'ACCO',
    'ACEL',
    'ACM',
    'ACMR',
    'AD',
    'ADBE',
    'ADC',
    'ADEA',
    'ADI',
    'ADMA',
    'ADNT',
    'ADSK',
    'AEIS',
    'AENT',
    'AEON',
    'AFRM',
    'AGD',
    'AGEN',
    'AGX',
    'AII',
    'AIRT',
    'AIRTP',
    'AISP',
    'AJG',
    'AKTS',
    'ALAB',
    'ALB',
    'ALGS',
    'ALGT',
    'ALHC',
    'ALLY',
    'ALNY',
    'ALSN',
    'ALTO',
    'AMAT',
    'AMD',
    'AMG',
    'AMKR',
    'AMSC',
    'AMZN',
    'ANDE',
    'ANET',
    'ANIP',
    'ANNA',
    'ANNAW',
    'AOD',
    'APA',
    'APG',
    'APH',
    'APO',
    'APP',
    'AR',
    'ARCB',
    'ARLO',
    'ARLP',
    'ARMK',
    'ARMP',
    'ARQT',
    'ASA',
    'ASO',
    'ASRV',
    'ASST',
    'ASTE',
    'ASTH',
    'ASTI',
    'ASYS',
    'ATEX',
    'AUB',
    'AUGO',
    'AVBC',
    'AVGO',
    'AVPT',
    'AX',
    'AZO',
    'BAC',
    'BALL',
    'BBW',
    'BCIC',
    'BDC',
    'BE',
    'BELFA',
    'BFC',
    'BFST',
    'BG',
    'BHRB',
    'BKNG',
    'BKTI',
    'BKV',
    'BLBD',
    'BLK',
    'BLLN',
    'BOOT',
    'BPOP',
    'BPRN',
    'BR',
    'BROS',
    'BSX',
    'BSY',
    'BTSG',
    'BWB',
    'BWXT',
    'BX',
    'C',
    'CAI',
    'CARE',
    'CASH',
    'CAVA',
    'CBAN',
    'CBK',
    'CBRE',
    'CBRS',
    'CCK',
    'CCL',
    'CCNE',
    'CDE',
    'CDNA',
    'CDNS',
    'CDRE',
    'CEE',
    'CELH',
    'CENX',
    'CET',
    'CFFI',
    'CHCI',
    'CHEF',
    'CHMG',
    'CHRD',
    'CHWY',
    'CI',
    'CIEN',
    'CLH',
    'CLM',
    'CMG',
    'CNOB',
    'CNOBP',
    'COCO',
    'COF',
    'COFS',
    'COHR',
    'COP',
    'CORT',
    'CORZ',
    'CRAI',
    'CRDO',
    'CRF',
    'CRGY',
    'CRM',
    'CRMD',
    'CRS',
    'CRT',
    'CRVL',
    'CSCO',
    'CSGP',
    'CSV',
    'CTBI',
    'CTO',
    'CUBI',
    'CVBF',
    'CVNA',
    'CVS',
    'CVSA',
    'CVX',
    'CWBC',
    'CXDO',
    'CXT',
    'CXW',
    'CYTK',
    'CZFS',
    'DAKT',
    'DAL',
    'DAVE',
    'DAVEW',
    'DELL',
    'DGII',
    'DINO',
    'DIOD',
    'DKS',
    'DMLP',
    'DNTH',
    'DOCN',
    'DSP',
    'DT',
    'DVN',
    'DXCM',
    'DXPE',
    'DY',
    'EBC',
    'ECG',
    'EE',
    'EEA',
    'EEFT',
    'EGAN',
    'EHC',
    'ELA',
    'ELMD',
    'ELUT',
    'EME',
    'EMF',
    'ENSG',
    'EOG',
    'EPAC',
    'EPAM',
    'EPRT',
    'ESAB',
    'ESCA',
    'ESE',
    'ESI',
    'ESOA',
    'ET',
    'ETO',
    'EVER',
    'EVI',
    'EVR',
    'EXE',
    'EXLS',
    'EXPE',
    'EXPO',
    'EXTR',
    'EYPT',
    'EZPW',
    'FATN',
    'FBIO',
    'FBIOP',
    'FBIZ',
    'FBK',
    'FBYD',
    'FBYDW',
    'FCCO',
    'FCFS',
    'FFBC',
    'FICO',
    'FIEE',
    'FIS',
    'FIVE',
    'FIX',
    'FMBH',
    'FNF',
    'FORM',
    'FPS',
    'FRBT',
    'FRSH',
    'FRST',
    'FSBC',
    'FSS',
    'FSUN',
    'FTK',
    'FTLF',
    'FUNC',
    'FWRG',
    'GALT',
    'GBCI',
    'GBFH',
    'GBLI',
    'GCT',
    'GCTS',
    'GEO',
    'GEV',
    'GF',
    'GGT',
    'GLPI',
    'GLU',
    'GLW',
    'GME',
    'GMED',
    'GNK',
    'GNRC',
    'GOLD',
    'GOOG',
    'GOOGL',
    'GWRE',
    'HAL',
    'HAPN',
    'HCC',
    'HCI',
    'HCKT',
    'HDSN',
    'HHH',
    'HIFS',
    'HIG',
    'HIPO',
    'HLLY',
    'HLNE',
    'HNGE',
    'HNI',
    'HOOD',
    'HOPE',
    'HPE',
    'HQY',
    'HRMY',
    'HTGC',
    'HUBS',
    'HURN',
    'HWM',
    'IBKR',
    'IBOC',
    'IBRX',
    'IDCC',
    'IDN',
    'IDR',
    'III',
    'INOD',
    'INR',
    'INSW',
    'INTT',
    'INTU',
    'INVA',
    'IONQ',
    'IOSP',
    'IRMD',
    'IRWD',
    'ISRG',
    'ISSC',
    'ISTR',
    'ITT',
    'J',
    'JMSB',
    'JOE',
    'JOF',
    'JPM',
    'KBR',
    'KDP',
    'KEYS',
    'KGEI',
    'KKR',
    'KLAC',
    'KN',
    'KNSA',
    'KNX',
    'KRMN',
    'KRNY',
    'KRYS',
    'KTB',
    'KVYO',
    'KYNB',
    'LAUR',
    'LE',
    'LFTO',
    'LGND',
    'LHX',
    'LIEN',
    'LIF',
    'LITE',
    'LLY',
    'LMB',
    'LOAR',
    'LOPE',
    'LOVE',
    'LPG',
    'LPLA',
    'LQDA',
    'LQDT',
    'LRCX',
    'LSCC',
    'LTH',
    'LUV',
    'LXU',
    'LYFT',
    'LYTS',
    'MAMA',
    'MARPS',
    'MAT',
    'MATX',
    'MBGL',
    'MCHB',
    'MCHP',
    'MCO',
    'MCY',
    'META',
    'MGNI',
    'MGY',
    'MIND',
    'MIR',
    'MKSI',
    'MNR',
    'MNTN',
    'MOD',
    'MOV',
    'MPAA',
    'MPC',
    'MPWR',
    'MRLN',
    'MRP',
    'MRVL',
    'MSFT',
    'MSGM',
    'MTDR',
    'MTSI',
    'MTZ',
    'MU',
    'MUR',
    'MVBF',
    'MWH',
    'MXE',
    'NAGE',
    'NAKA',
    'NATR',
    'NBIX',
    'NDAQ',
    'NEM',
    'NFLX',
    'NGS',
    'NKSH',
    'NOW',
    'NPKI',
    'NSLR',
    'NVDA',
    'NVEC',
    'OBK',
    'OESX',
    'OLLI',
    'OMER',
    'ON',
    'ONB',
    'ONDS',
    'ONTO',
    'OPBK',
    'OPHC',
    'OPLN',
    'OPTT',
    'OSBC',
    'OSS',
    'OXLCG',
    'OXLCI',
    'OXY',
    'PANL',
    'PARR',
    'PAYS',
    'PBAM',
    'PBT',
    'PCQ',
    'PCTY',
    'PDEX',
    'PDLB',
    'PENG',
    'PFLT',
    'PGC',
    'PGY',
    'PINS',
    'PIPR',
    'PKBK',
    'PLBC',
    'PLMR',
    'PLNT',
    'PLOW',
    'PLPC',
    'PLTR',
    'PLUS',
    'PMTS',
    'PNFP',
    'PNTG',
    'PODD',
    'PR',
    'PRDO',
    'PRG',
    'PRVA',
    'PSIX',
    'PSTL',
    'PSX',
    'PTRN',
    'PVL',
    'PWR',
    'QCRH',
    'QTTB',
    'QUBT',
    'RAMP',
    'RANI',
    'RBBN',
    'RBC',
    'RDDT',
    'RDN',
    'RDVT',
    'REGN',
    'RELY',
    'REPX',
    'RGLD',
    'RJF',
    'RKT',
    'RMBS',
    'RMD',
    'RMNI',
    'RMR',
    'RNST',
    'RNXT',
    'ROAD',
    'ROG',
    'RPT',
    'RRC',
    'RSI',
    'RVLV',
    'SANM',
    'SARO',
    'SBET',
    'SBFG',
    'SCHW',
    'SD',
    'SE',
    'SEB',
    'SEI',
    'SENEA',
    'SEZL',
    'SFBS',
    'SGI',
    'SHAZ',
    'SHLS',
    'SKWD',
    'SLDE',
    'SLGN',
    'SLM',
    'SM',
    'SMCI',
    'SMP',
    'SND',
    'SNDK',
    'SNX',
    'SOFI',
    'SOLS',
    'SON',
    'SPAI',
    'SPFI',
    'SPGI',
    'SPIR',
    'SPXC',
    'SRE',
    'SRTA',
    'SRZN',
    'SSNC',
    'STRL',
    'SUNS',
    'SWBI',
    'SYF',
    'TBBK',
    'TER',
    'TGTX',
    'TILE',
    'TKO',
    'TMDX',
    'TME',
    'TMUS',
    'TNL',
    'TNXP',
    'TOST',
    'TOWN',
    'TPB',
    'TPC',
    'TPG',
    'TPL',
    'TRAK',
    'TRC',
    'TREE',
    'TREX',
    'TRST',
    'TRU',
    'TSSI',
    'TTD',
    'TTMI',
    'TWN',
    'TXN',
    'TYGO',
    'UBCP',
    'UCB',
    'UFCS',
    'UG',
    'UI',
    'UMH',
    'UPWK',
    'USLM',
    'V',
    'VABK',
    'VCEL',
    'VCYT',
    'VEEV',
    'VICR',
    'VLY',
    'VMI',
    'VNOM',
    'VRDN',
    'VRT',
    'VRTX',
    'VTOL',
    'WAB',
    'WAL',
    'WAY',
    'WDC',
    'WEYS',
    'WINA',
    'WK',
    'WLDN',
    'WMS',
    'WSFS',
    'WTFC',
    'WTM',
    'WWD',
    'WWR',
    'WYNN',
    'XE',
    'XOM',
    'XPEL',
    'YOU',
    'YUMC',
    'ZBRA',
    'ZIONP',
    'ZVRA'
]

assert len(STOCKS) == 607, f"Expected 607 stocks, found {len(STOCKS)}"
assert len(set(STOCKS)) == 607, "Duplicate ticker found in STOCKS"


# ---------------------------------------------------------------------------
# EXACT CSV WORKFLOW
# ---------------------------------------------------------------------------

CSV_COLUMNS = ["Task", "Value", "Status"]

CSV_WORKFLOW: List[Dict[str, Any]] = [{'Task': 'Check Golden Cross', 'Value': 'Check the one day ohlc history with yfinance for the golden cross MA of the stock. Only proceed if it has upward momentum', 'Status': 0}, {'Task': 'Check MACD', 'Value': 'Check the MACD for the one week ohlc historical data using pandas_ta. Only proceed with a bull market reading.', 'Status': 0}, {'Task': 'Check Dividend', 'Value': 'Check and see if they offer dividends. Proceed if they do.', 'Status': 0}, {'Task': 'Calendar. ', 'Value': 'Is it within the next month? Add to Calandear on the day of the payout and another two days before, for the last day they take records. Get all this through yfinance.', 'Status': 0}]

CSV_FILENAME = "Dividend Calendar.csv"


def workflow_dataframe() -> pd.DataFrame:
    """Return the exact supplied workflow in the exact supplied column order."""
    return pd.DataFrame(CSV_WORKFLOW, columns=CSV_COLUMNS)


def validate_external_csv(path: Path) -> Tuple[bool, str]:
    """
    Validate a CSV against the exact uploaded Task/Value/Status schema and text.
    Status values may change while the app is used; Task and Value must match.
    """
    if not path.exists():
        return False, f"CSV not found: {path}"

    try:
        loaded = pd.read_csv(path)
    except Exception as exc:
        return False, f"Could not read CSV: {exc}"

    if list(loaded.columns) != CSV_COLUMNS:
        return False, (
            f"Column mismatch. Expected exactly {CSV_COLUMNS}, "
            f"received {list(loaded.columns)}"
        )

    expected = workflow_dataframe()
    if len(loaded) != len(expected):
        return False, f"Row mismatch. Expected 4 rows, received {len(loaded)}"

    for idx in range(len(expected)):
        if str(loaded.loc[idx, "Task"]) != str(expected.loc[idx, "Task"]):
            return False, f"Task text differs on row {idx + 1}."
        if str(loaded.loc[idx, "Value"]) != str(expected.loc[idx, "Value"]):
            return False, f"Value text differs on row {idx + 1}."

    return True, "CSV matches the supplied Task/Value/Status format and workflow text."


def save_status_csv(path: Path, statuses: List[int]) -> None:
    """Write Task, Value, Status only, preserving the exact supplied format."""
    df = workflow_dataframe()
    if len(statuses) != len(df):
        raise ValueError("Expected exactly four status values.")
    df["Status"] = [int(x) for x in statuses]
    df.to_csv(path, index=False)


# ---------------------------------------------------------------------------
# SCREENING MODEL
# ---------------------------------------------------------------------------

@dataclass
class DividendCandidate:
    ticker: str
    price: float = math.nan
    sma50: float = math.nan
    sma200: float = math.nan
    day_return_20d: float = math.nan
    golden_cross: bool = False
    macd: float = math.nan
    macd_signal: float = math.nan
    macd_hist: float = math.nan
    macd_bullish: bool = False
    dividend_per_share: float = math.nan
    trailing_dividend_yield: float = math.nan
    has_dividend: bool = False
    payout_date: Optional[date] = None
    ex_dividend_date: Optional[date] = None
    record_cutoff_date: Optional[date] = None
    within_next_month: bool = False
    score: float = 0.0
    passed: bool = False
    notes: str = ""
    events: List["CalendarEvent"] = field(default_factory=list)


@dataclass(frozen=True)
class CalendarEvent:
    event_date: date
    ticker: str
    event_type: str
    details: str


def _as_date(value: Any) -> Optional[date]:
    """Convert common yfinance date/timestamp representations to date."""
    if value is None:
        return None

    if isinstance(value, date) and not isinstance(value, datetime):
        return value

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        return value.to_pydatetime().date()

    if isinstance(value, (int, float, np.integer, np.floating)):
        if pd.isna(value):
            return None
        try:
            return datetime.fromtimestamp(float(value)).date()
        except Exception:
            return None

    if isinstance(value, (list, tuple, np.ndarray, pd.Series)):
        for item in value:
            converted = _as_date(item)
            if converted is not None:
                return converted
        return None

    try:
        parsed = pd.to_datetime(value, errors="coerce")
        if pd.isna(parsed):
            return None
        if isinstance(parsed, pd.DatetimeIndex):
            return parsed[0].date() if len(parsed) else None
        return parsed.to_pydatetime().date()
    except Exception:
        return None


def _calendar_lookup(cal: Any, candidates: List[str]) -> Any:
    """
    Robustly retrieve a calendar field across yfinance versions, where
    ticker.calendar may be a dict, Series, or DataFrame.
    """
    lowered = {str(k).lower().replace("_", " ").replace("-", " "): k for k in candidates}

    if cal is None:
        return None

    if isinstance(cal, dict):
        for key, value in cal.items():
            normalized = str(key).lower().replace("_", " ").replace("-", " ")
            if normalized in lowered:
                return value
        return None

    if isinstance(cal, pd.Series):
        for key in cal.index:
            normalized = str(key).lower().replace("_", " ").replace("-", " ")
            if normalized in lowered:
                return cal.loc[key]
        return None

    if isinstance(cal, pd.DataFrame):
        # Search index first.
        for key in cal.index:
            normalized = str(key).lower().replace("_", " ").replace("-", " ")
            if normalized in lowered:
                row = cal.loc[key]
                if isinstance(row, pd.Series):
                    vals = row.dropna().tolist()
                    return vals[0] if vals else None
                return row

        # Then search columns.
        for key in cal.columns:
            normalized = str(key).lower().replace("_", " ").replace("-", " ")
            if normalized in lowered:
                vals = cal[key].dropna().tolist()
                return vals[0] if vals else None

    return None


def check_golden_cross(ticker: yf.Ticker) -> Tuple[bool, Dict[str, float]]:
    """
    CSV row 1:
    Check one-day OHLC history for a golden-cross moving-average condition.
    Proceed only with upward momentum.

    Rules:
      - 50-day SMA > 200-day SMA
      - 50-day SMA is rising versus five sessions ago
      - Close > 50-day SMA
      - 20-session price return > 0
    """
    hist = ticker.history(period="1y", interval="1d", auto_adjust=False, actions=False)
    if hist is None or hist.empty or "Close" not in hist:
        return False, {}

    close = pd.to_numeric(hist["Close"], errors="coerce").dropna()
    if len(close) < 205:
        return False, {}

    sma50 = close.rolling(50).mean()
    sma200 = close.rolling(200).mean()

    last_price = float(close.iloc[-1])
    last_sma50 = float(sma50.iloc[-1])
    last_sma200 = float(sma200.iloc[-1])
    prior_sma50 = float(sma50.iloc[-6])
    ret20 = float(last_price / close.iloc[-21] - 1.0)

    passed = (
        last_sma50 > last_sma200
        and last_sma50 > prior_sma50
        and last_price > last_sma50
        and ret20 > 0
    )

    return passed, {
        "price": last_price,
        "sma50": last_sma50,
        "sma200": last_sma200,
        "day_return_20d": ret20,
    }


def check_weekly_macd(ticker: yf.Ticker) -> Tuple[bool, Dict[str, float]]:
    """
    CSV row 2:
    Check one-week OHLC historical data using pandas_ta.
    Proceed only with a bullish MACD reading.
    """
    hist = ticker.history(period="3y", interval="1wk", auto_adjust=False, actions=False)
    if hist is None or hist.empty or "Close" not in hist:
        return False, {}

    close = pd.to_numeric(hist["Close"], errors="coerce").dropna()
    if len(close) < 35:
        return False, {}

    macd_df = ta.macd(close=close, fast=12, slow=26, signal=9)
    if macd_df is None or macd_df.empty:
        return False, {}

    macd_col = next((c for c in macd_df.columns if str(c).startswith("MACD_")), None)
    signal_col = next((c for c in macd_df.columns if str(c).startswith("MACDs_")), None)
    hist_col = next((c for c in macd_df.columns if str(c).startswith("MACDh_")), None)

    if not all([macd_col, signal_col, hist_col]):
        return False, {}

    valid = macd_df[[macd_col, signal_col, hist_col]].dropna()
    if valid.empty:
        return False, {}

    row = valid.iloc[-1]
    macd_value = float(row[macd_col])
    signal_value = float(row[signal_col])
    hist_value = float(row[hist_col])

    passed = macd_value > signal_value and hist_value > 0

    return passed, {
        "macd": macd_value,
        "macd_signal": signal_value,
        "macd_hist": hist_value,
    }


def check_dividend(ticker: yf.Ticker, price: float) -> Tuple[bool, Dict[str, float]]:
    """
    CSV row 3:
    Proceed only when yfinance reports dividend distributions.
    """
    dividends = ticker.dividends
    if dividends is None or len(dividends) == 0:
        return False, {}

    dividends = pd.to_numeric(dividends, errors="coerce").dropna()
    positive = dividends[dividends > 0]
    if positive.empty:
        return False, {}

    cutoff = pd.Timestamp.now(tz=positive.index.tz if getattr(positive.index, "tz", None) else None) - pd.Timedelta(days=370)
    try:
        trailing = positive[positive.index >= cutoff]
    except Exception:
        trailing = positive.tail(4)

    trailing_dps = float(trailing.sum()) if not trailing.empty else float(positive.tail(4).sum())
    dividend_yield = trailing_dps / price if price and np.isfinite(price) and price > 0 else math.nan

    return True, {
        "dividend_per_share": trailing_dps,
        "trailing_dividend_yield": dividend_yield,
    }


def get_dividend_calendar(ticker: yf.Ticker, ticker_symbol: str) -> Tuple[bool, Dict[str, Any], List[CalendarEvent]]:
    """
    CSV row 4:
    Find yfinance dividend dates within the next month (30 days).
    Add a payout event on the payout date and a second event exactly
    two days before payout as the record-cutoff marker specified by the CSV.

    yfinance's ex-dividend date is also retained in candidate details when
    available, but the two-day-before event follows the uploaded CSV literally.
    """
    today = date.today()
    end_date = today + timedelta(days=30)

    try:
        cal = ticker.calendar
    except Exception:
        cal = None

    payout_raw = _calendar_lookup(
        cal,
        ["Dividend Date", "DividendDate", "dividend_date", "dividend date"],
    )
    ex_raw = _calendar_lookup(
        cal,
        ["Ex-Dividend Date", "ExDividendDate", "ex_dividend_date", "ex dividend date"],
    )

    payout_date = _as_date(payout_raw)
    ex_div_date = _as_date(ex_raw)

    # Some yfinance versions may expose dates via get_calendar().
    if payout_date is None or ex_div_date is None:
        try:
            get_cal = ticker.get_calendar()
        except Exception:
            get_cal = None
        if payout_date is None:
            payout_date = _as_date(_calendar_lookup(
                get_cal,
                ["Dividend Date", "DividendDate", "dividend_date", "dividend date"],
            ))
        if ex_div_date is None:
            ex_div_date = _as_date(_calendar_lookup(
                get_cal,
                ["Ex-Dividend Date", "ExDividendDate", "ex_dividend_date", "ex dividend date"],
            ))

    within = payout_date is not None and today <= payout_date <= end_date
    record_cutoff = payout_date - timedelta(days=2) if payout_date else None

    events: List[CalendarEvent] = []
    if within and payout_date:
        events.append(CalendarEvent(
            event_date=payout_date,
            ticker=ticker_symbol,
            event_type="PAYOUT",
            details=f"Dividend payout date for {ticker_symbol}",
        ))
        if record_cutoff:
            events.append(CalendarEvent(
                event_date=record_cutoff,
                ticker=ticker_symbol,
                event_type="RECORD CUTOFF",
                details=f"CSV-specified record cutoff: 2 days before payout for {ticker_symbol}",
            ))

    return within, {
        "payout_date": payout_date,
        "ex_dividend_date": ex_div_date,
        "record_cutoff_date": record_cutoff,
    }, events


def score_candidate(candidate: DividendCandidate) -> float:
    """
    Ranking score for stocks that pass all four CSV gates.

    Yield is capped in the score to reduce distortion from unusually high
    distributions. Momentum and MACD strength add modest ranking information.
    """
    yld = candidate.trailing_dividend_yield
    yield_component = min(max(yld if np.isfinite(yld) else 0.0, 0.0), 0.12) / 0.12 * 55.0

    trend_spread = 0.0
    if np.isfinite(candidate.sma50) and np.isfinite(candidate.sma200) and candidate.sma200 != 0:
        trend_spread = max(0.0, candidate.sma50 / candidate.sma200 - 1.0)
    trend_component = min(trend_spread, 0.20) / 0.20 * 20.0

    momentum = max(candidate.day_return_20d if np.isfinite(candidate.day_return_20d) else 0.0, 0.0)
    momentum_component = min(momentum, 0.20) / 0.20 * 15.0

    macd_component = 10.0 if candidate.macd_bullish else 0.0

    return round(yield_component + trend_component + momentum_component + macd_component, 2)


def analyze_stock(symbol: str) -> DividendCandidate:
    """Run the exact four CSV gates in sequence, stopping when a gate fails."""
    result = DividendCandidate(ticker=symbol)

    try:
        ticker = yf.Ticker(symbol)

        golden_ok, golden = check_golden_cross(ticker)
        for key, value in golden.items():
            setattr(result, key, value)
        result.golden_cross = golden_ok
        if not golden_ok:
            result.notes = "Failed daily golden-cross/upward-momentum gate."
            return result

        macd_ok, macd = check_weekly_macd(ticker)
        for key, value in macd.items():
            setattr(result, key, value)
        result.macd_bullish = macd_ok
        if not macd_ok:
            result.notes = "Failed weekly bullish-MACD gate."
            return result

        dividend_ok, dividend = check_dividend(ticker, result.price)
        for key, value in dividend.items():
            setattr(result, key, value)
        result.has_dividend = dividend_ok
        if not dividend_ok:
            result.notes = "No qualifying dividend history found through yfinance."
            return result

        calendar_ok, calendar_data, events = get_dividend_calendar(ticker, symbol)
        for key, value in calendar_data.items():
            setattr(result, key, value)
        result.within_next_month = calendar_ok
        result.events = events

        if not calendar_ok:
            result.notes = "Dividend payer, but payout is not within the next 30 days."
            return result

        result.passed = True
        result.score = score_candidate(result)
        result.notes = "Passed all four CSV workflow gates."
        return result

    except Exception as exc:
        result.notes = f"Error: {type(exc).__name__}: {exc}"
        return result


# ---------------------------------------------------------------------------
# TKINTER CALENDAR GUI
# ---------------------------------------------------------------------------

class DividendCalendarApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("607-Stock Dividend Investing Calendar")
        self.geometry("1320x820")
        self.minsize(1080, 700)

        self.results: Dict[str, DividendCandidate] = {}
        self.events_by_date: Dict[date, List[CalendarEvent]] = {}
        self.worker_queue: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self.stop_event = threading.Event()
        self.scan_thread: Optional[threading.Thread] = None

        today = date.today()
        self.view_year = today.year
        self.view_month = today.month

        self._build_ui()
        self._validate_default_csv()
        self.render_calendar()
        self.after(100, self._drain_queue)

    def _build_ui(self) -> None:
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x")

        self.scan_button = ttk.Button(top, text="Scan 607 Stocks", command=self.start_scan)
        self.scan_button.pack(side="left")

        self.stop_button = ttk.Button(top, text="Stop", command=self.stop_scan, state="disabled")
        self.stop_button.pack(side="left", padx=(6, 0))

        ttk.Button(top, text="Export Results CSV", command=self.export_results).pack(side="left", padx=(14, 0))
        ttk.Button(top, text="Export Workflow Status CSV", command=self.export_workflow_status).pack(side="left", padx=(6, 0))
        ttk.Button(top, text="Validate Dividend Calendar.csv", command=self.choose_and_validate_csv).pack(side="left", padx=(6, 0))

        self.progress = ttk.Progressbar(top, maximum=len(STOCKS), mode="determinate")
        self.progress.pack(side="left", fill="x", expand=True, padx=12)

        self.progress_label = ttk.Label(top, text=f"0 / {len(STOCKS)}")
        self.progress_label.pack(side="right")

        # CSV workflow status panel
        workflow_frame = ttk.LabelFrame(self, text="Exact Dividend Calendar.csv Workflow", padding=8)
        workflow_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.workflow_tree = ttk.Treeview(
            workflow_frame,
            columns=("task", "value", "status"),
            show="headings",
            height=4,
        )
        self.workflow_tree.heading("task", text="Task")
        self.workflow_tree.heading("value", text="Value")
        self.workflow_tree.heading("status", text="Status")
        self.workflow_tree.column("task", width=170, anchor="w")
        self.workflow_tree.column("value", width=980, anchor="w")
        self.workflow_tree.column("status", width=70, anchor="center")
        self.workflow_tree.pack(fill="x")

        for row in CSV_WORKFLOW:
            self.workflow_tree.insert("", "end", values=(row["Task"], row["Value"], row["Status"]))

        middle = ttk.Panedwindow(self, orient="horizontal")
        middle.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # Calendar side
        calendar_outer = ttk.Frame(middle, padding=4)
        middle.add(calendar_outer, weight=3)

        nav = ttk.Frame(calendar_outer)
        nav.pack(fill="x", pady=(0, 6))
        ttk.Button(nav, text="◀", width=4, command=self.prev_month).pack(side="left")
        self.month_label = ttk.Label(nav, font=("", 15, "bold"))
        self.month_label.pack(side="left", expand=True)
        ttk.Button(nav, text="Today", command=self.go_today).pack(side="right", padx=(0, 6))
        ttk.Button(nav, text="▶", width=4, command=self.next_month).pack(side="right")

        self.calendar_frame = ttk.Frame(calendar_outer)
        self.calendar_frame.pack(fill="both", expand=True)

        # Candidate table side
        result_outer = ttk.Frame(middle, padding=4)
        middle.add(result_outer, weight=2)

        ttk.Label(result_outer, text="Passing Dividend Candidates", font=("", 12, "bold")).pack(anchor="w")

        columns = ("ticker", "score", "yield", "payout", "cutoff", "price")
        self.result_tree = ttk.Treeview(result_outer, columns=columns, show="headings")
        headings = {
            "ticker": "Ticker",
            "score": "Score",
            "yield": "Yield",
            "payout": "Payout",
            "cutoff": "2-Day Cutoff",
            "price": "Price",
        }
        widths = {"ticker": 70, "score": 65, "yield": 70, "payout": 100, "cutoff": 100, "price": 80}
        for col in columns:
            self.result_tree.heading(col, text=headings[col])
            self.result_tree.column(col, width=widths[col], anchor="center")
        self.result_tree.pack(fill="both", expand=True)
        self.result_tree.bind("<<TreeviewSelect>>", self.show_selected_candidate)

        details_frame = ttk.LabelFrame(result_outer, text="Selected Candidate", padding=6)
        details_frame.pack(fill="x", pady=(8, 0))
        self.details_text = tk.Text(details_frame, height=9, wrap="word")
        self.details_text.pack(fill="x")
        self.details_text.configure(state="disabled")

        self.status_var = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    def _validate_default_csv(self) -> None:
        path = Path(__file__).resolve().parent / CSV_FILENAME
        if path.exists():
            ok, msg = validate_external_csv(path)
            self.status_var.set(msg if ok else "CSV validation warning: " + msg)
        else:
            self.status_var.set(
                "Ready. Exact CSV workflow is embedded; external Dividend Calendar.csv was not found beside the script."
            )

    def choose_and_validate_csv(self) -> None:
        selected = filedialog.askopenfilename(
            title="Select Dividend Calendar.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not selected:
            return
        ok, msg = validate_external_csv(Path(selected))
        if ok:
            messagebox.showinfo("CSV Validation", msg)
        else:
            messagebox.showerror("CSV Validation", msg)

    def start_scan(self) -> None:
        if self.scan_thread and self.scan_thread.is_alive():
            return

        self.results.clear()
        self.events_by_date.clear()
        self.result_tree.delete(*self.result_tree.get_children())
        self.progress["value"] = 0
        self.progress_label.configure(text=f"0 / {len(STOCKS)}")
        self.stop_event.clear()
        self.scan_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_var.set("Scanning stock universe through yfinance...")

        self.scan_thread = threading.Thread(target=self._scan_worker, daemon=True)
        self.scan_thread.start()

    def stop_scan(self) -> None:
        self.stop_event.set()
        self.status_var.set("Stopping after the current ticker request completes...")

    def _scan_worker(self) -> None:
        passed = 0
        for index, symbol in enumerate(STOCKS, start=1):
            if self.stop_event.is_set():
                self.worker_queue.put(("stopped", index - 1))
                return

            result = analyze_stock(symbol)
            if result.passed:
                passed += 1
            self.worker_queue.put(("result", (index, result, passed)))

        self.worker_queue.put(("done", (len(STOCKS), passed)))

    def _drain_queue(self) -> None:
        try:
            while True:
                kind, payload = self.worker_queue.get_nowait()

                if kind == "result":
                    index, result, passed_count = payload
                    self.results[result.ticker] = result
                    self.progress["value"] = index
                    self.progress_label.configure(text=f"{index} / {len(STOCKS)}")
                    self.status_var.set(
                        f"Scanning {result.ticker} — {passed_count} passed all four gates so far."
                    )

                    if result.passed:
                        for event in result.events:
                            self.events_by_date.setdefault(event.event_date, []).append(event)
                        self._insert_candidate(result)
                        self.render_calendar()

                elif kind == "done":
                    count, passed_count = payload
                    self.scan_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self._update_workflow_status()
                    self.status_var.set(
                        f"Complete: {count} stocks scanned; {passed_count} passed all four CSV gates."
                    )

                elif kind == "stopped":
                    scanned = payload
                    self.scan_button.configure(state="normal")
                    self.stop_button.configure(state="disabled")
                    self._update_workflow_status()
                    self.status_var.set(f"Stopped after {scanned} stocks.")

        except queue.Empty:
            pass
        finally:
            self.after(100, self._drain_queue)

    def _update_workflow_status(self) -> None:
        # A workflow row becomes 1 if at least one scanned result reached/passed that gate.
        values = list(self.results.values())
        statuses = [
            int(any(r.golden_cross for r in values)),
            int(any(r.macd_bullish for r in values)),
            int(any(r.has_dividend for r in values)),
            int(any(r.within_next_month for r in values)),
        ]

        items = self.workflow_tree.get_children()
        for idx, item in enumerate(items):
            row = CSV_WORKFLOW[idx]
            self.workflow_tree.item(item, values=(row["Task"], row["Value"], statuses[idx]))

    def _insert_candidate(self, result: DividendCandidate) -> None:
        yield_text = (
            f"{result.trailing_dividend_yield:.2%}"
            if np.isfinite(result.trailing_dividend_yield)
            else "N/A"
        )
        price_text = f"${result.price:.2f}" if np.isfinite(result.price) else "N/A"
        self.result_tree.insert(
            "",
            "end",
            iid=result.ticker,
            values=(
                result.ticker,
                f"{result.score:.2f}",
                yield_text,
                result.payout_date.isoformat() if result.payout_date else "",
                result.record_cutoff_date.isoformat() if result.record_cutoff_date else "",
                price_text,
            ),
        )

        # Keep candidates sorted by score descending.
        children = list(self.result_tree.get_children())
        children.sort(
            key=lambda iid: self.results.get(iid, DividendCandidate(iid)).score,
            reverse=True,
        )
        for pos, iid in enumerate(children):
            self.result_tree.move(iid, "", pos)

    def show_selected_candidate(self, _event: Any = None) -> None:
        selected = self.result_tree.selection()
        if not selected:
            return
        ticker = selected[0]
        r = self.results.get(ticker)
        if not r:
            return

        text = (
            f"Ticker: {r.ticker}\n"
            f"Price: {r.price:.2f}\n"
            f"SMA50 / SMA200: {r.sma50:.2f} / {r.sma200:.2f}\n"
            f"20-session return: {r.day_return_20d:.2%}\n"
            f"Weekly MACD / Signal / Hist: {r.macd:.4f} / {r.macd_signal:.4f} / {r.macd_hist:.4f}\n"
            f"Trailing dividend/share: {r.dividend_per_share:.4f}\n"
            f"Trailing dividend yield: {r.trailing_dividend_yield:.2%}\n"
            f"Payout date: {r.payout_date}\n"
            f"Ex-dividend date (yfinance): {r.ex_dividend_date}\n"
            f"CSV 2-day record cutoff: {r.record_cutoff_date}\n"
            f"Rank score: {r.score:.2f}\n"
            f"Notes: {r.notes}"
        )

        self.details_text.configure(state="normal")
        self.details_text.delete("1.0", "end")
        self.details_text.insert("1.0", text)
        self.details_text.configure(state="disabled")

    def render_calendar(self) -> None:
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()

        self.month_label.configure(
            text=f"{pycalendar.month_name[self.view_month]} {self.view_year}"
        )

        headers = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for col, label in enumerate(headers):
            ttk.Label(
                self.calendar_frame,
                text=label,
                anchor="center",
                font=("", 10, "bold"),
            ).grid(row=0, column=col, sticky="nsew", padx=1, pady=1)

        weeks = pycalendar.Calendar(firstweekday=0).monthdayscalendar(
            self.view_year, self.view_month
        )

        for row_idx, week in enumerate(weeks, start=1):
            for col_idx, day_num in enumerate(week):
                frame = ttk.Frame(self.calendar_frame, relief="ridge", padding=3)
                frame.grid(row=row_idx, column=col_idx, sticky="nsew", padx=1, pady=1)

                if day_num == 0:
                    continue

                current = date(self.view_year, self.view_month, day_num)
                ttk.Label(frame, text=str(day_num), font=("", 10, "bold")).pack(anchor="nw")

                events = sorted(
                    self.events_by_date.get(current, []),
                    key=lambda e: (e.ticker, e.event_type),
                )
                for event in events[:5]:
                    label = ttk.Label(
                        frame,
                        text=f"{event.ticker} — {event.event_type}",
                        cursor="hand2",
                    )
                    label.pack(anchor="w", fill="x")
                    label.bind(
                        "<Button-1>",
                        lambda _e, ev=event: self.show_event(ev),
                    )

                if len(events) > 5:
                    ttk.Label(frame, text=f"+{len(events) - 5} more").pack(anchor="w")

        for col in range(7):
            self.calendar_frame.columnconfigure(col, weight=1, uniform="calendar")
        for row in range(1, len(weeks) + 1):
            self.calendar_frame.rowconfigure(row, weight=1, uniform="calendar")

    def show_event(self, event: CalendarEvent) -> None:
        candidate = self.results.get(event.ticker)
        yield_text = "N/A"
        if candidate and np.isfinite(candidate.trailing_dividend_yield):
            yield_text = f"{candidate.trailing_dividend_yield:.2%}"

        messagebox.showinfo(
            f"{event.ticker} — {event.event_type}",
            f"Date: {event.event_date}\n"
            f"Ticker: {event.ticker}\n"
            f"Event: {event.event_type}\n"
            f"Yield: {yield_text}\n\n"
            f"{event.details}",
        )

    def prev_month(self) -> None:
        self.view_month -= 1
        if self.view_month == 0:
            self.view_month = 12
            self.view_year -= 1
        self.render_calendar()

    def next_month(self) -> None:
        self.view_month += 1
        if self.view_month == 13:
            self.view_month = 1
            self.view_year += 1
        self.render_calendar()

    def go_today(self) -> None:
        today = date.today()
        self.view_year = today.year
        self.view_month = today.month
        self.render_calendar()

    def export_results(self) -> None:
        passing = [r for r in self.results.values() if r.passed]
        if not passing:
            messagebox.showinfo("Export", "There are no passing candidates to export.")
            return

        destination = filedialog.asksaveasfilename(
            title="Export dividend candidates",
            defaultextension=".csv",
            initialfile="dividend_candidates.csv",
            filetypes=[("CSV files", "*.csv")],
        )
        if not destination:
            return

        rows = []
        for r in sorted(passing, key=lambda x: x.score, reverse=True):
            rows.append({
                "Ticker": r.ticker,
                "Score": r.score,
                "Price": r.price,
                "SMA50": r.sma50,
                "SMA200": r.sma200,
                "20D Return": r.day_return_20d,
                "MACD": r.macd,
                "MACD Signal": r.macd_signal,
                "MACD Histogram": r.macd_hist,
                "Trailing Dividend/Share": r.dividend_per_share,
                "Trailing Dividend Yield": r.trailing_dividend_yield,
                "Payout Date": r.payout_date,
                "Ex-Dividend Date": r.ex_dividend_date,
                "CSV 2-Day Record Cutoff": r.record_cutoff_date,
            })

        pd.DataFrame(rows).to_csv(destination, index=False)
        messagebox.showinfo("Export", f"Saved {len(rows)} passing candidates.")

    def export_workflow_status(self) -> None:
        items = self.workflow_tree.get_children()
        statuses = []
        for item in items:
            values = self.workflow_tree.item(item, "values")
            statuses.append(int(values[2]))

        destination = filedialog.asksaveasfilename(
            title="Export exact workflow CSV",
            defaultextension=".csv",
            initialfile=CSV_FILENAME,
            filetypes=[("CSV files", "*.csv")],
        )
        if not destination:
            return

        save_status_csv(Path(destination), statuses)
        messagebox.showinfo(
            "Export",
            "Saved exact Task, Value, Status CSV format."
        )


if __name__ == "__main__":
    app = DividendCalendarApp()
    app.mainloop()
