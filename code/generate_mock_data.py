from __future__ import annotations

"""
Education Operations Analytics - Mock Data Generator
====================================================

Purpose
-------
Generate a small but internally coherent synthetic dataset based on:
- 03_数据资产盘点.md (current/raw data assets)
- 04_数据字典.xlsx (standardized target tables + business rules)

Design
------
1. Generate a clean-ish "standardized_truth" layer first.
2. Derive fragmented, inconsistent, partially missing "raw" source tables from it.
3. Inject known data-quality and operational issues for later Python/SQL analysis.

The raw layer intentionally contains problems. Do NOT "fix" them in this script.
The point is to let later ETL / SQL / BI work detect and explain them.

Dependencies
------------
pip install pandas numpy

Run
---
python generate_mock_data.py

Output
------
mock_data/
  raw/
  standardized_truth/
  metadata/
  README_模拟数据说明.md

Notes
-----
- All names, accounts, events, and records are synthetic.
- Timeline spans Mar-2025 to Aug-2026.
- Jun/Jul/Aug-2026 teacher-capacity snapshots show availability compression and a Jul hiring spike.
- The policy/event date used to create the P4 signal is 2026-05-01.
- The generator uses a fixed random seed for reproducibility.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo
import math
import random
import re
from typing import Dict, Iterable, List, Optional, Tuple

import numpy as np
import pandas as pd


# -----------------------------------------------------------------------------
# 1. Configuration
# -----------------------------------------------------------------------------

SEED = 20260822
random.seed(SEED)
RNG = np.random.default_rng(SEED)

BASE_DIR = Path(__file__).resolve().parent / "mock_data"
RAW_DIR = BASE_DIR / "raw"
STD_DIR = BASE_DIR / "standardized_truth"
META_DIR = BASE_DIR / "metadata"
CLASS_RAW_DIR = RAW_DIR / "班课文件"
PRIVATE_RAW_DIR = RAW_DIR / "私教课程文件"
SCHEDULE_RAW_DIR = RAW_DIR / "课程安排表"

START_DATE = pd.Timestamp("2025-03-01")
END_DATE = pd.Timestamp("2026-08-31")
POLICY_CHANGE_DATE = pd.Timestamp("2026-05-01")
HIRING_SPIKE_DATE = pd.Timestamp("2026-07-01")
AVAILABILITY_SNAPSHOT_MONTHS = [
    pd.Timestamp("2026-06-01"),
    pd.Timestamp("2026-07-01"),
    pd.Timestamp("2026-08-01"),
]

# Portfolio-sized but dense enough for time-series, SQL window functions and BI.
N_CUSTOMERS = 520
N_TRIALS = 380
N_TEACHERS_BASE = 20
N_TEACHERS_NEW = 10
N_TEACHERS = N_TEACHERS_BASE + N_TEACHERS_NEW
N_CLASSES = 24
N_PRIVATE_COURSES = 42
N_POSTS = 120

LEVELS = ["A1", "A2", "B1", "B2"]
DELIVERY_MODES = ["线上", "线下"]
COUNTRIES = ["中国", "西班牙", "加拿大", "美国", "澳大利亚", "新加坡", "英国", "德国"]
COUNTRY_TIMEZONES = {
    "中国": "Asia/Shanghai",
    "西班牙": "Europe/Madrid",
    "加拿大": "America/Toronto",
    "美国": "America/Los_Angeles",
    "澳大利亚": "Australia/Sydney",
    "新加坡": "Asia/Singapore",
    "英国": "Europe/London",
    "德国": "Europe/Berlin",
}

STUDENT_NAMES = [
    "Anna", "Lucas", "Luis", "Tommy", "Sofia", "Lucy", "Patrick", "Xuan",
    "Brian", "Tiger", "Larry", "Crystal", "Elva", "Lydia", "Hannah", "Wilson",
    "Jerry", "Jack", "Snow", "Isabela", "Etta", "Alfred", "Elynn", "Lawrence",
    "Mia", "Leo", "Emma", "Noah", "Olivia", "Ethan", "Chloe", "Ryan", "Luna",
    "Daniel", "Ava", "Oscar", "Grace", "Mason", "Ivy", "Henry", "Liam", "Ella",
    "Zoe", "Jason", "Nina", "Eric", "Kevin", "Sarah", "Alice", "David",
]

TEACHER_NAMES = [
    "Pablo", "Claudia", "Sandra", "Elena", "Daniel", "Pilar", "Raul", "Marina",
    "Anna", "Carmen", "Lucia", "Miguel", "Alba", "Javier", "Sara", "Diego",
    "Natalia", "Carlos", "Rocio", "Consuelo",
    "Salma", "Eva", "Juan", "Cecilia", "Mateo", "Irene", "Adrian", "Laura",
    "Fernando", "Beatriz",
]

EMPLOYEES = [
    ("EMP001", "Sofia_Sales", "销售"),
    ("EMP002", "Leo_Sales", "销售"),
    ("EMP003", "Mia_Sales", "销售"),
    ("EMP004", "Cielo_Academic", "教务"),
    ("EMP005", "Iris_Academic", "教务"),
    ("EMP006", "Nora_Academic", "教务"),
    ("EMP007", "Alex_Operations", "运营"),
    ("EMP008", "May_Operations", "运营"),
    ("EMP009", "Eric_Operations", "运营"),
    ("EMP010", "Manager", "管理"),
]

SALES_IDS = [x[0] for x in EMPLOYEES if x[2] == "销售"]
ACADEMIC_IDS = [x[0] for x in EMPLOYEES if x[2] == "教务"]
OPERATOR_IDS = [x[0] for x in EMPLOYEES if x[2] == "运营"]
EMPLOYEE_NAME = {x[0]: x[1] for x in EMPLOYEES}


# -----------------------------------------------------------------------------
# 2. Generic helpers
# -----------------------------------------------------------------------------

def ensure_dirs() -> None:
    for p in [BASE_DIR, RAW_DIR, STD_DIR, META_DIR, CLASS_RAW_DIR, PRIVATE_RAW_DIR, SCHEDULE_RAW_DIR]:
        p.mkdir(parents=True, exist_ok=True)


def id_series(prefix: str, n: int, width: int = 4) -> List[str]:
    return [f"{prefix}{i:0{width}d}" for i in range(1, n + 1)]


def choice(seq, p=None):
    return RNG.choice(seq, p=p).item() if hasattr(RNG.choice(seq, p=p), "item") else RNG.choice(seq, p=p)


def weighted_choice(seq, probs):
    idx = RNG.choice(len(seq), p=np.array(probs, dtype=float) / np.sum(probs))
    return seq[int(idx)]


def random_ts(start: pd.Timestamp, end: pd.Timestamp) -> pd.Timestamp:
    if end <= start:
        return start
    seconds = int((end - start).total_seconds())
    return start + pd.Timedelta(seconds=int(RNG.integers(0, seconds + 1)))


def random_date(start: pd.Timestamp, end: pd.Timestamp) -> pd.Timestamp:
    return random_ts(start.normalize(), end.normalize()).normalize()


def as_iso_date(x) -> Optional[str]:
    if x is None or pd.isna(x):
        return None
    return pd.Timestamp(x).strftime("%Y-%m-%d")


def as_iso_dt(x) -> Optional[str]:
    if x is None or pd.isna(x):
        return None
    return pd.Timestamp(x).strftime("%Y-%m-%d %H:%M:%S")


def month_start(x) -> pd.Timestamp:
    return pd.Timestamp(x).to_period("M").to_timestamp()


def random_clock_hour() -> int:
    return int(choice([9, 10, 11, 14, 15, 16, 17, 18, 19, 20]))


def dirty_date_string(ts: pd.Timestamp) -> str:
    """Create mixed source-style date formats."""
    fmt = weighted_choice(
        ["iso", "slash", "cn", "short"],
        [0.45, 0.25, 0.15, 0.15],
    )
    ts = pd.Timestamp(ts)
    if fmt == "iso":
        return ts.strftime("%Y-%m-%d")
    if fmt == "slash":
        return ts.strftime("%Y/%m/%d")
    if fmt == "cn":
        return f"{ts.year}年{ts.month}月{ts.day}日"
    return ts.strftime("%m/%d/%Y")


def dirty_datetime_string(ts: pd.Timestamp) -> str:
    ts = pd.Timestamp(ts)
    fmt = weighted_choice(["iso", "slash", "cn"], [0.5, 0.3, 0.2])
    if fmt == "iso":
        return ts.strftime("%Y-%m-%d %H:%M")
    if fmt == "slash":
        return ts.strftime("%Y/%m/%d %H:%M")
    return f"{ts.month}月{ts.day}日 {ts.hour}:{ts.minute:02d}"


def mutate_account_name(s: str) -> str:
    r = RNG.random()
    if r < 0.08:
        return " " + s + " "
    if r < 0.13:
        return s.upper()
    if r < 0.18:
        return "@" + s
    return s


def mutate_person_name(s: str) -> str:
    r = RNG.random()
    if r < 0.04:
        return s + " "
    if r < 0.08:
        return s.upper()
    if r < 0.11 and len(s) > 4:
        return s[:-1]  # mild typo
    return s



def department_name_variant(s: str, department: str) -> str:
    """Create stable-ish department-specific naming differences for the same person."""
    base = str(s)
    if department == "销售":
        variants = [base, base.upper(), base.replace("_", " "), base + " "]
        probs = [0.60, 0.10, 0.20, 0.10]
    elif department == "教务":
        variants = [base, base.title(), base.replace("_", ""), base + "（教务）"]
        probs = [0.62, 0.10, 0.18, 0.10]
    elif department == "运营":
        variants = [base, base.lower(), base.replace("_", "-"), base + "_op"]
        probs = [0.62, 0.12, 0.16, 0.10]
    else:
        variants = [base, base.upper(), base + " "]
        probs = [0.75, 0.10, 0.15]
    return weighted_choice(variants, probs)


def department_course_label(clean: str, department: str) -> str:
    mapping = {
        "1V1": {
            "销售": ["VIP一对一", "1对1私教", "一对一"],
            "教务": ["1V1", "一对一", "私教"],
            "运营": ["私教", "单人私教", "1V1"],
        },
        "1V2": {
            "销售": ["1对2", "双人私教", "1V2"],
            "教务": ["1V2", "一对二"],
            "运营": ["私教2人", "1V2"],
        },
        "1V3": {
            "销售": ["1对3", "三人私教", "1V3"],
            "教务": ["1V3", "一对三"],
            "运营": ["私教3人", "1V3"],
        },
        "1V4": {
            "销售": ["1对4", "四人私教", "1V4"],
            "教务": ["1V4", "一对四"],
            "运营": ["私教4人", "1V4"],
        },
        "班课": {
            "销售": ["小班课", "班课", "Group"],
            "教务": ["班课", "小组课"],
            "运营": ["group", "班课"],
        },
    }
    vals = mapping.get(clean, {department: [clean]}).get(department, [clean])
    return choice(vals)


def department_status_label(clean: str, department: str) -> str:
    mapping = {
        "在读": {
            "销售": ["已报名", "成交", "已转化"],
            "教务": ["在读", "上课中", "正常"],
            "运营": ["active", "在读"],
        },
        "暂停": {
            "销售": ["暂缓", "已报名-暂停"],
            "教务": ["暂停", "hold"],
            "运营": ["paused", "暂停"],
        },
        "已停课": {
            "销售": ["未续费", "流失", "结束"],
            "教务": ["已停课", "停课"],
            "运营": ["churned", "停止"],
        },
        "已完成": {
            "销售": ["结课", "完成"],
            "教务": ["已完成", "结课"],
            "运营": ["completed", "完成"],
        },
    }
    return choice(mapping.get(clean, {department: [clean]}).get(department, [clean]))


def teacher_ids_active_on(avail_map: Dict[str, List[dict]], dt: pd.Timestamp) -> List[str]:
    active = []
    d = dt.normalize()
    for teacher_id, slots in avail_map.items():
        for slot in slots:
            ef = pd.Timestamp(slot["effective_from"])
            et = pd.Timestamp(slot["effective_to"])
            if ef <= d <= et:
                active.append(teacher_id)
                break
    return sorted(set(active))


def timezone_local_time(madrid_date: pd.Timestamp, madrid_hour: int, timezone_name: str) -> Tuple[pd.Timestamp, int]:
    """Return the correct local timestamp and UTC offset difference vs Madrid."""
    naive = datetime(
        madrid_date.year, madrid_date.month, madrid_date.day,
        int(madrid_hour), 0, 0,
    )
    madrid = naive.replace(tzinfo=ZoneInfo("Europe/Madrid"))
    local = madrid.astimezone(ZoneInfo(timezone_name))
    madrid_offset = madrid.utcoffset().total_seconds() / 3600
    local_offset = local.utcoffset().total_seconds() / 3600
    return pd.Timestamp(local.replace(tzinfo=None)), int(round(local_offset - madrid_offset))

def course_type_dirty(clean: str) -> str:
    mapping = {
        "1V1": ["一对一", "私教", "单人私教", "1V1"],
        "1V2": ["一对二", "双人私教", "1V2"],
        "1V3": ["一对三", "三人私教", "1V3"],
        "1V4": ["一对四", "四人私教", "1V4"],
        "班课": ["班课", "小班", "group class"],
    }
    return choice(mapping.get(clean, [clean]))


def confirmation_dirty(status: str) -> str:
    mapping = {
        "已确认": ["已确认", "确认", "OK", "done"],
        "待确认": ["待确认", "待定", "pending", "未确认"],
        "冲突": ["冲突", "时间不行", "需重排", "conflict"],
        "取消": ["取消", "cancel", "已取消"],
    }
    return choice(mapping[status])


def write_csv(df: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8-sig")


def pk_unique(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns and df[col].notna().all() and df[col].is_unique


# -----------------------------------------------------------------------------
# 3. Build standardized truth layer
# -----------------------------------------------------------------------------

@dataclass
class TruthTables:
    tables: Dict[str, pd.DataFrame]
    learner_name_by_customer: Dict[str, str]


def build_employees() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "employee_id": eid,
            "employee_name": name,
            "role": role,
            "active_status": "在岗",
        }
        for eid, name, role in EMPLOYEES
    ])



def build_teachers() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Build a long teacher timeline.

    - T001-T020 are the established teacher pool.
    - T021-T030 are concentrated new hires in Jul-2026.
    - Several established teachers exit, with a visible cluster in Jul-Aug 2026.
    """
    teacher_ids = id_series("T", N_TEACHERS, 3)
    established_ids = teacher_ids[:N_TEACHERS_BASE]
    new_ids = teacher_ids[N_TEACHERS_BASE:]

    # A few historical exits + a stronger Jul-Aug exit cluster.
    historical_exit = set(RNG.choice(established_ids, size=2, replace=False).tolist())
    remaining = [t for t in established_ids if t not in historical_exit]
    late_exit = set(RNG.choice(remaining, size=5, replace=False).tolist())
    exit_teachers = historical_exit | late_exit

    teacher_rows = []
    status_rows = []
    status_counter = 1

    for idx, (tid, name) in enumerate(zip(teacher_ids, TEACHER_NAMES[:N_TEACHERS])):
        timezone = weighted_choice(
            ["Europe/Madrid", "America/Managua", "America/Santiago", "Europe/London"],
            [0.68, 0.12, 0.10, 0.10],
        )
        teaching_mode = weighted_choice(["线上", "线下", "线上/线下"], [0.50, 0.15, 0.35])

        if tid in new_ids:
            start_date = random_date(HIRING_SPIKE_DATE, pd.Timestamp("2026-07-20"))
        else:
            # Most established teachers predate the analysis window or joined early in it.
            start_date = random_date(START_DATE, pd.Timestamp("2025-06-30"))

        current_status = "授课中"
        status_rows.append({
            "teacher_status_id": f"TST{status_counter:04d}",
            "teacher_id": tid,
            "status": "授课中",
            "effective_date": as_iso_date(start_date),
            "reason": "新加入教师" if tid in new_ids else None,
        })
        status_counter += 1

        if tid in exit_teachers:
            if tid in historical_exit:
                exit_date = random_date(pd.Timestamp("2025-10-01"), pd.Timestamp("2026-03-31"))
            else:
                exit_date = random_date(pd.Timestamp("2026-07-10"), END_DATE)
            current_status = weighted_choice(["停止授课", "离职"], [0.35, 0.65])
            status_rows.append({
                "teacher_status_id": f"TST{status_counter:04d}",
                "teacher_id": tid,
                "status": current_status,
                "effective_date": as_iso_date(exit_date),
                "reason": None if RNG.random() < 0.42 else choice(
                    ["个人原因", "工作安排", "课程压力", "时间冲突", "工作量过高"]
                ),
            })
            status_counter += 1

        teacher_rows.append({
            "teacher_id": tid,
            "teacher_name": name,
            "timezone": timezone,
            "teaching_mode": teaching_mode,
            "current_status": current_status,
        })

    return pd.DataFrame(teacher_rows), pd.DataFrame(status_rows)


def build_teacher_availability(teachers: pd.DataFrame, teacher_status_history: pd.DataFrame) -> pd.DataFrame:
    """
    Generate recurring availability with explicit effective periods.

    The established teacher pool becomes progressively less available in
    Jun -> Jul -> Aug 2026. A large new-hire cohort appears in Jul 2026.
    """
    rows = []
    counter = 1
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    starts = (
        teacher_status_history[teacher_status_history["status"] == "授课中"]
        .sort_values("effective_date")
        .drop_duplicates("teacher_id")
        .set_index("teacher_id")["effective_date"]
        .map(pd.Timestamp)
        .to_dict()
    )
    exits = (
        teacher_status_history[teacher_status_history["status"].isin(["停止授课", "离职"])]
        .sort_values("effective_date")
        .drop_duplicates("teacher_id", keep="last")
        .set_index("teacher_id")["effective_date"]
        .map(pd.Timestamp)
        .to_dict()
    )

    periods = [
        (START_DATE, pd.Timestamp("2026-05-31"), "baseline"),
        (pd.Timestamp("2026-06-01"), pd.Timestamp("2026-06-30"), "jun"),
        (pd.Timestamp("2026-07-01"), pd.Timestamp("2026-07-31"), "jul"),
        (pd.Timestamp("2026-08-01"), END_DATE, "aug"),
    ]

    for _, teacher in teachers.iterrows():
        tid = teacher["teacher_id"]
        teacher_start = starts.get(tid, START_DATE)
        teacher_exit = exits.get(tid, END_DATE)
        is_new = int(tid[1:]) > N_TEACHERS_BASE

        for p_start, p_end, phase in periods:
            effective_from = max(teacher_start, p_start)
            effective_to = min(teacher_exit, p_end)
            if effective_from > effective_to:
                continue

            # Weekly availability gets tighter for established teachers.
            if is_new:
                if phase == "jul":
                    day_count = int(RNG.integers(4, 7))
                    duration_choices = [4, 5, 6]
                elif phase == "aug":
                    day_count = int(RNG.integers(3, 6))
                    duration_choices = [3, 4, 5]
                else:
                    day_count = int(RNG.integers(3, 5))
                    duration_choices = [3, 4]
            else:
                if phase == "baseline":
                    day_count = int(RNG.integers(4, 7))
                    duration_choices = [4, 5, 6]
                elif phase == "jun":
                    day_count = int(RNG.integers(3, 6))
                    duration_choices = [3, 4]
                elif phase == "jul":
                    day_count = int(RNG.integers(2, 5))
                    duration_choices = [2, 3]
                else:  # Aug
                    day_count = int(RNG.integers(2, 4))
                    duration_choices = [1, 2, 3]

            chosen_days = RNG.choice(weekdays, size=min(day_count, 7), replace=False)
            for weekday in chosen_days:
                start_hour = int(choice([8, 9, 10, 11, 14, 15, 16, 17, 18]))
                duration = int(choice(duration_choices))
                end_hour = min(start_hour + duration, 22)
                rows.append({
                    "availability_id": f"AVL{counter:05d}",
                    "teacher_id": tid,
                    "weekday": weekday,
                    "start_time": f"{start_hour:02d}:00",
                    "end_time": f"{end_hour:02d}:00",
                    "timezone": teacher["timezone"],
                    "effective_from": as_iso_date(effective_from),
                    "effective_to": as_iso_date(effective_to),
                    "status": "有效" if effective_to >= END_DATE else "历史有效",
                })
                counter += 1

    return pd.DataFrame(rows)

def availability_lookup(availability: pd.DataFrame) -> Dict[str, List[dict]]:
    out: Dict[str, List[dict]] = {}
    for _, row in availability.iterrows():
        out.setdefault(row["teacher_id"], []).append(row.to_dict())
    return out


def is_teacher_available(avail_map: Dict[str, List[dict]], teacher_id: str, dt: pd.Timestamp) -> bool:
    for slot in avail_map.get(teacher_id, []):
        if slot["weekday"] != dt.day_name():
            continue
        ef = pd.Timestamp(slot["effective_from"])
        et = pd.Timestamp(slot["effective_to"])
        if not (ef <= dt.normalize() <= et):
            continue
        sh, sm = map(int, slot["start_time"].split(":"))
        eh, em = map(int, slot["end_time"].split(":"))
        mins = dt.hour * 60 + dt.minute
        if sh * 60 + sm <= mins < eh * 60 + em:
            return True
    return False


def next_teacher_available(avail_map: Dict[str, List[dict]], teacher_id: str, from_dt: pd.Timestamp) -> pd.Timestamp:
    # Search next 14 days, hourly, deterministic enough for mock data.
    probe = from_dt.ceil("h")
    for _ in range(14 * 24):
        if is_teacher_available(avail_map, teacher_id, probe):
            return probe
        probe += pd.Timedelta(hours=1)
    # fallback if teacher has no matching future slot
    return from_dt + pd.Timedelta(days=2, hours=1)


def build_accounts_and_posts() -> Tuple[pd.DataFrame, pd.DataFrame]:
    accounts = []
    for i in range(1, 5):
        accounts.append({
            "account_id": f"ACC{i:03d}",
            "account_name": f"SpanishEdu_{i}",
            "platform": "小红书",
            "operator_id": OPERATOR_IDS[(i - 1) % len(OPERATOR_IDS)],
            "active_status": "在用" if i < 4 else "暂停",
        })
    accounts_df = pd.DataFrame(accounts)

    post_rows = []
    post_ids = id_series("POST", N_POSTS, 4)
    titles = ["儿童西语", "DELE备考", "零基础西语", "成人口语", "留学西语", "西语学习方法"]
    for pid in post_ids:
        pub = random_date(START_DATE, END_DATE - pd.Timedelta(days=3))
        account_id = choice(accounts_df["account_id"].tolist())
        operator_id = accounts_df.loc[accounts_df["account_id"] == account_id, "operator_id"].iloc[0]
        impression = int(max(500, RNG.lognormal(mean=8.2, sigma=0.65)))
        click_count = int(max(10, impression * RNG.uniform(0.01, 0.06)))
        post_rows.append({
            "post_id": pid,
            "post_name": f"{choice(titles)}_{pid[-2:]}",
            "publish_date": as_iso_date(pub),
            "account_id": account_id,
            "operator_id": operator_id,
            "impression": impression,
            "click_count": click_count,
            "success_customer_count": 0,  # recomputed after enrollment
        })
    return accounts_df, pd.DataFrame(post_rows)


def build_customers_and_inquiries(posts: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, str]]:
    customer_ids = id_series("CUS", N_CUSTOMERS, 4)
    inquiry_rows = []
    customer_rows = []
    learner_names = {}
    inquiry_counter = 1

    post_ids = posts["post_id"].tolist()
    account_by_post = posts.set_index("post_id")["account_id"].to_dict()

    for i, cid in enumerate(customer_ids):
        base_name = STUDENT_NAMES[i % len(STUDENT_NAMES)]
        learner_name = f"{base_name}_{i+1:03d}"
        learner_names[cid] = learner_name

        first_date = random_date(START_DATE, END_DATE - pd.Timedelta(days=10))
        sales_id = choice(SALES_IDS)
        customer_account = f"user_{i+1:04d}"
        n_interactions = weighted_choice([1, 2, 3], [0.58, 0.30, 0.12])
        last_date = first_date

        for j in range(n_interactions):
            if j > 0:
                last_date = min(END_DATE, last_date + pd.Timedelta(days=int(RNG.integers(2, 45))))
            hour = random_clock_hour()
            inquiry_time = last_date + pd.Timedelta(hours=hour, minutes=int(choice([0, 10, 20, 30, 40, 50])))
            response_minutes = int(max(2, RNG.gamma(2.2, 8.0)))
            # A few very slow responses.
            if RNG.random() < 0.08:
                response_minutes += int(RNG.integers(90, 600))
            response_time = inquiry_time + pd.Timedelta(minutes=response_minutes)
            post_id = choice(post_ids) if RNG.random() < 0.88 else None
            account_id = account_by_post.get(post_id) if post_id else choice(["ACC001", "ACC002", "ACC003", "ACC004"])

            inquiry_rows.append({
                "inquiry_id": f"INQ{inquiry_counter:05d}",
                "customer_id": cid,
                "inquiry_date": as_iso_date(last_date),
                "inquiry_type": weighted_choice(["主动咨询", "被动私信", "主动评论", "回访"], [0.50, 0.18, 0.16, 0.16]),
                "post_id": post_id,
                "account_id": account_id,
                "customer_account": customer_account,
                "inquiry_time": as_iso_dt(inquiry_time),
                "response_time": as_iso_dt(response_time),
                "response_duration": response_minutes,
                "sales_id": sales_id,
                "wechat_status": weighted_choice(["已添加", "未添加", "待添加"], [0.62, 0.25, 0.13]),
                "keyword": weighted_choice(["零基础", "小孩课程", "B2", "DELE", "口语", "留学"], [0.24, 0.22, 0.12, 0.14, 0.18, 0.10]),
                "region": choice(COUNTRIES),
                "remark": None if RNG.random() < 0.75 else "客户希望尽快安排",
            })
            inquiry_counter += 1

        customer_rows.append({
            "customer_id": cid,
            "customer_account": customer_account,
            "source_channel": "小红书",
            "sales_id": sales_id,
            "status": "跟进中",  # updated after trial/enrollment
            "create_date": as_iso_date(first_date),
        })

    return pd.DataFrame(customer_rows), pd.DataFrame(inquiry_rows), learner_names


def phase_conversion_probability(trial_dt: pd.Timestamp) -> float:
    # P4 signal: short-term conversion boost after 2026-05-01, then decline ~2 months later.
    if trial_dt < pd.Timestamp("2026-05-01"):
        return 0.43
    if trial_dt < pd.Timestamp("2026-07-01"):
        return 0.61
    return 0.31



def phase_conflict_probability(trial_dt: pd.Timestamp) -> float:
    # More pressure and less reliable resource confirmation as teacher capacity tightens.
    if trial_dt < pd.Timestamp("2026-05-01"):
        return 0.08
    if trial_dt < pd.Timestamp("2026-06-01"):
        return 0.22
    if trial_dt < pd.Timestamp("2026-07-01"):
        return 0.34
    if trial_dt < pd.Timestamp("2026-08-01"):
        return 0.47
    return 0.56


def build_trials_students_enrollments(
    customers: pd.DataFrame,
    learner_names: Dict[str, str],
    teachers: pd.DataFrame,
    avail_map: Dict[str, List[dict]],
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, Dict[str, str]]:
    trial_rows = []
    student_rows = []
    enrollment_seed = []
    customer_to_student: Dict[str, str] = {}

    n_trials = min(N_TRIALS, len(customers))
    trial_customers = RNG.choice(customers["customer_id"].tolist(), size=n_trials, replace=False).tolist()

    student_counter = 1
    trial_counter = 1

    for cid in trial_customers:
        c = customers.loc[customers["customer_id"] == cid].iloc[0]
        create_dt = pd.Timestamp(c["create_date"])
        max_dt = min(END_DATE, create_dt + pd.Timedelta(days=50))
        preferred = random_ts(create_dt + pd.Timedelta(days=1), max_dt)
        preferred = preferred.normalize() + pd.Timedelta(hours=random_clock_hour())

        eligible = teacher_ids_active_on(avail_map, preferred)
        if not eligible:
            eligible = teachers["teacher_id"].tolist()
        teacher_id = choice(eligible)

        conflict = RNG.random() < phase_conflict_probability(preferred)
        if conflict:
            promised = preferred
            if is_teacher_available(avail_map, teacher_id, promised):
                promised += pd.Timedelta(hours=int(choice([3, 4, 5])))
        else:
            promised = next_teacher_available(avail_map, teacher_id, preferred)

        if is_teacher_available(avail_map, teacher_id, promised):
            academic_confirmed = promised
            confirmation_status = "已确认"
        else:
            academic_confirmed = next_teacher_available(avail_map, teacher_id, promised)
            confirmation_status = "冲突"

        actual_trial_dt = min(academic_confirmed, END_DATE)
        enrolled = RNG.random() < phase_conversion_probability(actual_trial_dt)
        trial_type = weighted_choice(["试听", "等级测试"], [0.74, 0.26])
        level_result = weighted_choice(LEVELS, [0.34, 0.30, 0.22, 0.14])

        student_id = None
        if enrolled:
            student_id = f"STU{student_counter:04d}"
            customer_to_student[cid] = student_id
            country = choice(COUNTRIES)
            student_rows.append({
                "student_id": student_id,
                "student_name": learner_names[cid],
                "country": country,
                "timezone": COUNTRY_TIMEZONES[country],
                "age": int(RNG.integers(8, 43)),
                "sales_id": c["sales_id"],
                "academic_id": choice(ACADEMIC_IDS),
                "status": "在读",
            })
            enrollment_seed.append({
                "student_id": student_id,
                "customer_id": cid,
                "trial_id": f"TR{trial_counter:04d}",
                "trial_date": actual_trial_dt,
                "level": level_result,
                "sales_id": c["sales_id"],
                "academic_id": student_rows[-1]["academic_id"],
            })
            student_counter += 1

        trial_rows.append({
            "trial_id": f"TR{trial_counter:04d}",
            "customer_id": cid,
            "student_id": student_id,
            "trial_type": trial_type,
            "teacher_id": teacher_id,
            "trial_date": as_iso_dt(actual_trial_dt),
            "level_result": level_result,
            "teacher_feedback": weighted_choice(
                ["基础较好，建议继续", "需要加强口语", "建议巩固语法", "零基础，建议从A1开始", None],
                [0.22, 0.22, 0.22, 0.20, 0.14],
            ),
            "enrolled": "是" if enrolled else "否",
            "customer_preferred_time": as_iso_dt(preferred),
            "sales_promised_time": as_iso_dt(promised),
            "academic_confirmed_time": as_iso_dt(academic_confirmed),
            "confirmation_status": confirmation_status,
        })
        trial_counter += 1

    return pd.DataFrame(trial_rows), pd.DataFrame(student_rows), pd.DataFrame(enrollment_seed), customer_to_student


def build_classes(teachers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    # Long-running classes are primarily assigned to the established pool.
    teacher_ids = teachers["teacher_id"].tolist()[:N_TEACHERS_BASE]
    class_ids = id_series("CLS", N_CLASSES, 3)
    for i, cid in enumerate(class_ids):
        level = LEVELS[i % len(LEVELS)]
        mode = DELIVERY_MODES[(i // len(LEVELS)) % 2]
        weekday1 = choice(["周一", "周二", "周三", "周四", "周五", "周六"])
        weekday2 = choice(["周二", "周三", "周四", "周五", "周六", "周日"])
        hour = random_clock_hour()
        rows.append({
            "class_id": cid,
            "class_name": f"{level}-{mode}-{i+1:02d}",
            "teacher_id": choice(teacher_ids),
            "schedule": f"{weekday1}/{weekday2} {hour:02d}:00",
            "student_count": 0,
            "level": level,
            "delivery_mode": mode,
            "status": weighted_choice(["进行中", "结束"], [0.76, 0.24]),
        })
    return pd.DataFrame(rows)


def build_private_courses(teachers: pd.DataFrame) -> pd.DataFrame:
    rows = []
    all_teacher_ids = teachers["teacher_id"].tolist()
    established_ids = all_teacher_ids[:N_TEACHERS_BASE]
    for i, pcid in enumerate(id_series("PC", N_PRIVATE_COURSES, 3)):
        ctype = weighted_choice(["1V1", "1V2", "1V3", "1V4"], [0.55, 0.26, 0.12, 0.07])
        start = random_date(START_DATE, pd.Timestamp("2026-08-10"))
        eligible = all_teacher_ids if start >= HIRING_SPIKE_DATE else established_ids
        weekday = choice(["周一", "周二", "周三", "周四", "周五", "周六", "周日"])
        hour = random_clock_hour()
        rows.append({
            "private_course_id": pcid,
            "course_type": ctype,
            "teacher_id": choice(eligible),
            "schedule": f"{weekday} {hour:02d}:00",
            "current_status": weighted_choice(["进行中", "暂停", "停课", "完成"], [0.70, 0.08, 0.13, 0.09]),
            "start_date": as_iso_date(start),
        })
    return pd.DataFrame(rows)

def assign_enrollments_and_members(
    student_seed: pd.DataFrame,
    students: pd.DataFrame,
    classes: pd.DataFrame,
    private_courses: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create enrollment, private-course membership, class membership; update class counts."""
    enrollment_rows = []
    private_member_rows = []
    class_member_rows = []

    student_ids = students["student_id"].tolist()
    RNG.shuffle(student_ids)

    private_slots = []
    for _, pc in private_courses.iterrows():
        capacity = int(pc["course_type"][-1])
        private_slots.extend([pc["private_course_id"]] * capacity)

    private_target = min(len(private_slots), int(len(student_ids) * 0.48))
    private_students = student_ids[:private_target]
    class_students = student_ids[private_target:]

    # Fill private course memberships.
    pc_iter = iter(private_slots)
    pcs_for_student = {}
    for sid in private_students:
        try:
            pcid = next(pc_iter)
        except StopIteration:
            break
        pcs_for_student[sid] = pcid
        seed = student_seed.loc[student_seed["student_id"] == sid].iloc[0]
        join_dt = pd.Timestamp(seed["trial_date"]) + pd.Timedelta(days=int(RNG.integers(1, 7)))
        pc = private_courses.loc[private_courses["private_course_id"] == pcid].iloc[0]
        start_dt = max(join_dt.normalize(), pd.Timestamp(pc["start_date"]))
        private_member_rows.append({
            "private_course_student_id": f"PCS{len(private_member_rows)+1:04d}",
            "private_course_id": pcid,
            "student_id": sid,
            "join_date": as_iso_date(start_dt),
            "leave_date": None,
            "status": "在读",
        })
        enrollment_rows.append({
            "enrollment_id": f"ENR{len(enrollment_rows)+1:04d}",
            "student_id": sid,
            "enrollment_date": as_iso_date(join_dt),
            "course_mode": "私教",
            "private_course_id": pcid,
            "class_id": None,
            "purchased_hours": int(choice([20, 30, 40, 60])),
            "sales_id": seed["sales_id"],
            "academic_id": seed["academic_id"],
            "status": "在读",
        })

    # Assign remaining students to classes, roughly balanced by their trial level.
    class_counts = {cid: 0 for cid in classes["class_id"]}
    for sid in class_students:
        seed = student_seed.loc[student_seed["student_id"] == sid].iloc[0]
        level = seed["level"]
        candidates = classes[classes["level"] == level]
        if candidates.empty:
            candidates = classes
        min_count = min(class_counts[c] for c in candidates["class_id"])
        candidate_ids = [c for c in candidates["class_id"] if class_counts[c] == min_count]
        cid = choice(candidate_ids)
        class_counts[cid] += 1
        join_dt = pd.Timestamp(seed["trial_date"]) + pd.Timedelta(days=int(RNG.integers(2, 10)))
        class_member_rows.append({
            "class_student_id": f"CST{len(class_member_rows)+1:04d}",
            "class_id": cid,
            "student_id": sid,
            "join_date": as_iso_date(join_dt),
            "leave_date": None,
            "status": "在读",
        })
        enrollment_rows.append({
            "enrollment_id": f"ENR{len(enrollment_rows)+1:04d}",
            "student_id": sid,
            "enrollment_date": as_iso_date(join_dt),
            "course_mode": "班课",
            "private_course_id": None,
            "class_id": cid,
            "purchased_hours": int(choice([30, 40, 60])),
            "sales_id": seed["sales_id"],
            "academic_id": seed["academic_id"],
            "status": "在读",
        })

    classes = classes.copy()
    classes["student_count"] = classes["class_id"].map(class_counts).fillna(0).astype(int)
    return (
        pd.DataFrame(enrollment_rows),
        pd.DataFrame(private_member_rows),
        pd.DataFrame(class_member_rows),
        classes,
        private_courses,
    )


def parse_schedule_hour(schedule_text: str) -> int:
    m = re.search(r"(\d{1,2}):00", str(schedule_text))
    return int(m.group(1)) if m else 18



def build_schedule_records(
    private_courses: pd.DataFrame,
    classes: pd.DataFrame,
    enrollments: pd.DataFrame,
    students: pd.DataFrame,
    avail_map: Dict[str, List[dict]],
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    schedule_rows = []
    change_rows = []

    objects = []
    for _, pc in private_courses.iterrows():
        objects.append(("私教", pc["private_course_id"], None, pc["teacher_id"], pd.Timestamp(pc["start_date"]), pc["schedule"]))
    for _, cl in classes.iterrows():
        ens = enrollments[enrollments["class_id"] == cl["class_id"]]
        start = pd.Timestamp(ens["enrollment_date"].min()) if not ens.empty else pd.Timestamp("2025-05-01")
        objects.append(("班课", None, cl["class_id"], cl["teacher_id"], start, cl["schedule"]))

    for idx, (mode, pcid, cid, tid, start, schedule_text) in enumerate(objects, 1):
        start = max(pd.Timestamp(start), START_DATE)
        hour = parse_schedule_hour(schedule_text)
        preferred = start.normalize() + pd.Timedelta(hours=hour)

        if preferred < POLICY_CHANGE_DATE:
            conflict_prob = 0.06
        elif preferred < pd.Timestamp("2026-07-01"):
            conflict_prob = 0.28 if mode == "私教" else 0.14
        else:
            conflict_prob = 0.44 if mode == "私教" else 0.22

        promised = preferred
        if RNG.random() >= conflict_prob:
            promised = next_teacher_available(avail_map, tid, preferred)
        elif is_teacher_available(avail_map, tid, promised):
            promised += pd.Timedelta(hours=int(choice([3, 4, 5])))

        if is_teacher_available(avail_map, tid, promised):
            confirmed = promised
            status = "已确认"
        else:
            confirmed = next_teacher_available(avail_map, tid, promised)
            status = "冲突"

        academic_id = choice(ACADEMIC_IDS)
        schedule_id = f"SCH{idx:04d}"
        schedule_rows.append({
            "schedule_id": schedule_id,
            "course_mode": mode,
            "private_course_id": pcid,
            "class_id": cid,
            "teacher_id": tid,
            "customer_preferred_time": as_iso_dt(preferred) if mode == "私教" else None,
            "sales_promised_time": as_iso_dt(promised) if mode == "私教" else None,
            "confirmed_start": as_iso_dt(confirmed),
            "confirmation_status": status,
            "confirmed_by": academic_id,
            "confirmed_at": as_iso_dt(max(start, confirmed - pd.Timedelta(days=int(RNG.integers(1, 4))))),
        })

        base_n = int(RNG.poisson(0.9 if mode == "班课" else 1.4))
        if confirmed >= POLICY_CHANGE_DATE:
            base_n += int(RNG.poisson(1.4 if mode == "私教" else 0.7))
        base_n = min(base_n, 7)
        old_start = confirmed
        for _ in range(base_n):
            change_time = min(END_DATE, old_start + pd.Timedelta(days=int(RNG.integers(5, 55))))
            reason = weighted_choice(
                ["学生改时间", "教师不可用", "销售承诺冲突", "教师临时请假", "班级整体调整", "其他"],
                [0.26, 0.25, 0.20 if mode == "私教" else 0.07, 0.14, 0.09, 0.06],
            )
            delta = pd.Timedelta(hours=int(choice([-3, -2, -1, 1, 2, 3])))
            new_start = old_start + delta
            initiator = {
                "学生改时间": "学生",
                "教师不可用": "教师",
                "销售承诺冲突": "销售",
                "教师临时请假": "教师",
                "班级整体调整": "教务",
                "其他": "其他",
            }[reason]
            change_rows.append({
                "schedule_change_id": f"CHG{len(change_rows)+1:05d}",
                "schedule_id": schedule_id,
                "change_time": as_iso_dt(change_time),
                "old_start": as_iso_dt(old_start),
                "new_start": as_iso_dt(new_start),
                "change_reason": reason,
                "initiator_type": initiator,
                "changed_by": choice(ACADEMIC_IDS),
            })
            old_start = new_start

    schedules = pd.DataFrame(schedule_rows)

    # Operational error injection: several confirmed schedules overlap for the same teacher.
    # These are "real operational errors", not dirty-data duplicates.
    eligible_idx = schedules.index[
        pd.to_datetime(schedules["confirmed_start"]) >= pd.Timestamp("2026-05-01")
    ].tolist()
    pair_count = min(10, max(4, len(eligible_idx) // 6))
    if len(eligible_idx) >= pair_count * 2:
        selected = RNG.choice(eligible_idx, size=pair_count * 2, replace=False)
        for i in range(pair_count):
            src_i = int(selected[2 * i])
            tgt_i = int(selected[2 * i + 1])
            source = schedules.loc[src_i]
            src_start = pd.Timestamp(source["confirmed_start"])
            tgt_start = pd.Timestamp(schedules.loc[tgt_i, "confirmed_start"])
            # Align target to the same weekday/time on or after its own start date.
            days_ahead = (src_start.weekday() - tgt_start.weekday()) % 7
            aligned = tgt_start.normalize() + pd.Timedelta(days=days_ahead, hours=src_start.hour)
            schedules.loc[tgt_i, "teacher_id"] = source["teacher_id"]
            schedules.loc[tgt_i, "confirmed_start"] = as_iso_dt(aligned)
            schedules.loc[tgt_i, "confirmation_status"] = "已确认"  # human error slipped through
            schedules.loc[tgt_i, "confirmed_at"] = as_iso_dt(aligned - pd.Timedelta(days=1))

    return schedules, pd.DataFrame(change_rows)


def build_lessons_attendance(
    schedules: pd.DataFrame,
    private_members: pd.DataFrame,
    class_members: pd.DataFrame,
    private_courses: pd.DataFrame,
    classes: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    lesson_rows = []
    attendance_rows = []

    private_students = private_members.groupby("private_course_id")["student_id"].apply(list).to_dict() if not private_members.empty else {}
    class_students = class_members.groupby("class_id")["student_id"].apply(list).to_dict() if not class_members.empty else {}

    for _, sch in schedules.iterrows():
        confirmed = pd.Timestamp(sch["confirmed_start"])
        # Longer and denser timeline: weekly recurring courses across the whole 18-month window.
        n_weeks = max(1, min(80, int((END_DATE - confirmed).days / 7) + 1))
        for w in range(n_weeks):
            lesson_dt = confirmed + pd.Timedelta(days=7 * w)
            if lesson_dt > END_DATE:
                break
            lesson_id = f"L{len(lesson_rows)+1:06d}"
            student_list = private_students.get(sch["private_course_id"], []) if sch["course_mode"] == "私教" else class_students.get(sch["class_id"], [])
            student_id = student_list[0] if sch["course_mode"] == "私教" and len(student_list) == 1 else None
            duration = weighted_choice([1.0, 1.5, 1.67, 2.0], [0.50, 0.15, 0.25, 0.10])
            lesson_rows.append({
                "lesson_id": lesson_id,
                "schedule_id": sch["schedule_id"],
                "student_id": student_id,
                "teacher_id": sch["teacher_id"],
                "lesson_date": as_iso_date(lesson_dt),
                "duration": duration,
                "feedback": weighted_choice(
                    ["完成本节内容", "需要加强口语练习", "语法掌握一般", "课堂参与积极", None],
                    [0.32, 0.20, 0.18, 0.20, 0.10],
                ),
            })
            for sid in student_list:
                status = weighted_choice(["出席", "请假", "缺席", "其他"], [0.84, 0.09, 0.06, 0.01])
                attendance_rows.append({
                    "attendance_id": f"ATT{len(attendance_rows)+1:07d}",
                    "lesson_id": lesson_id,
                    "student_id": sid,
                    "attendance_status": status,
                    "remark": "临时请假" if status == "请假" and RNG.random() < 0.5 else None,
                })

    return pd.DataFrame(lesson_rows), pd.DataFrame(attendance_rows)


def build_student_status_and_renewals(
    students: pd.DataFrame,
    enrollments: pd.DataFrame,
    lessons: pd.DataFrame,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    status_rows = []
    renewal_rows = []
    students = students.copy()
    enrollments = enrollments.copy()

    for _, stu in students.iterrows():
        sid = stu["student_id"]
        enr = enrollments[enrollments["student_id"] == sid].sort_values("enrollment_date").iloc[0]
        start = pd.Timestamp(enr["enrollment_date"])
        status_rows.append({
            "student_status_id": f"STS{len(status_rows)+1:05d}",
            "student_id": sid,
            "status": "在读",
            "effective_from": as_iso_date(start),
            "effective_to": None,
            "reason": None,
            "recorded_by": enr["academic_id"],
        })

        # Longer timeline: lifecycle changes can happen throughout, with extra pressure after policy change.
        tenure_days = max(0, (END_DATE - start).days)
        if tenure_days >= 60:
            late_pressure = 0.10 if start < POLICY_CHANGE_DATE else 0.20
            change_prob = min(0.48, 0.16 + tenure_days / 1200 + late_pressure)
            if RNG.random() < change_prob:
                earliest = start + pd.Timedelta(days=int(RNG.integers(45, 100)))
                if earliest <= END_DATE:
                    change_date = random_date(earliest, END_DATE)
                    new_status = weighted_choice(["暂停", "已停课", "已完成"], [0.22, 0.48, 0.30])
                    status_rows[-1]["effective_to"] = as_iso_date(change_date - pd.Timedelta(days=1))
                    status_rows.append({
                        "student_status_id": f"STS{len(status_rows)+1:05d}",
                        "student_id": sid,
                        "status": new_status,
                        "effective_from": as_iso_date(change_date),
                        "effective_to": None,
                        "reason": weighted_choice(
                            ["时间不合适", "完成课程", "暂时停学", "课程体验", "排课困难", None],
                            [0.22, 0.22, 0.17, 0.14, 0.15, 0.10],
                        ),
                        "recorded_by": enr["academic_id"],
                    })
                    students.loc[students["student_id"] == sid, "status"] = new_status
                    enrollments.loc[enrollments["student_id"] == sid, "status"] = new_status

        # Multiple renewals are possible on the longer timeline.
        if tenure_days >= 60:
            renewal_prob = 0.50 if start < POLICY_CHANGE_DATE else 0.34
            if RNG.random() < renewal_prob:
                max_n = 2 if tenure_days >= 240 else 1
                n_renewals = 1 + int(RNG.random() < 0.32 and max_n == 2)
                for r_i in range(n_renewals):
                    low = 55 + r_i * 90
                    high = min(tenure_days, 150 + r_i * 120)
                    if high <= low:
                        continue
                    rd = start + pd.Timedelta(days=int(RNG.integers(low, high + 1)))
                    renewal_rows.append({
                        "renewal_id": f"REN{len(renewal_rows)+1:05d}",
                        "student_id": sid,
                        "enrollment_id": enr["enrollment_id"],
                        "renewal_date": as_iso_date(min(END_DATE, rd)),
                        "renewal_hours": int(choice([20, 30, 40, 60])),
                        "sales_id": enr["sales_id"],
                        "remark": None if RNG.random() < 0.7 else "续费后继续原课程",
                    })

    return students, pd.DataFrame(status_rows), pd.DataFrame(renewal_rows)

def build_teacher_capacity_snapshot(
    teachers: pd.DataFrame,
    teacher_status_history: pd.DataFrame,
    availability: pd.DataFrame,
    lessons: pd.DataFrame,
) -> pd.DataFrame:
    """
    Three monthly snapshots showing:
    - shrinking weekly availability among established teachers,
    - a Jul-2026 new-hire spike,
    - scheduled load and remaining monthly capacity.
    """
    teacher_names = teachers.set_index("teacher_id")["teacher_name"].to_dict()
    start_dates = (
        teacher_status_history[teacher_status_history["status"] == "授课中"]
        .sort_values("effective_date")
        .drop_duplicates("teacher_id")
        .set_index("teacher_id")["effective_date"]
        .map(pd.Timestamp)
        .to_dict()
    )
    exit_dates = (
        teacher_status_history[teacher_status_history["status"].isin(["停止授课", "离职"])]
        .sort_values("effective_date")
        .drop_duplicates("teacher_id", keep="last")
        .set_index("teacher_id")["effective_date"]
        .map(pd.Timestamp)
        .to_dict()
    )

    av = availability.copy()
    av["effective_from"] = pd.to_datetime(av["effective_from"])
    av["effective_to"] = pd.to_datetime(av["effective_to"])
    lessons2 = lessons.copy()
    lessons2["lesson_date"] = pd.to_datetime(lessons2["lesson_date"])

    rows = []
    for month in AVAILABILITY_SNAPSHOT_MONTHS:
        mend = month + pd.offsets.MonthEnd(1)
        for tid in teachers["teacher_id"]:
            start = start_dates.get(tid, START_DATE)
            exit_d = exit_dates.get(tid)
            if start > mend:
                continue

            status = "授课中"
            if exit_d is not None and exit_d <= mend:
                status = "停止授课/离职"

            active_slots = av[
                (av["teacher_id"] == tid)
                & (av["effective_from"] <= mend)
                & (av["effective_to"] >= month)
            ].copy()
            weekly_hours = 0.0
            for _, slot in active_slots.iterrows():
                sh, sm = map(int, str(slot["start_time"]).split(":"))
                eh, em = map(int, str(slot["end_time"]).split(":"))
                weekly_hours += max(0, (eh * 60 + em - sh * 60 - sm) / 60)

            month_lessons = lessons2[
                (lessons2["teacher_id"] == tid)
                & (lessons2["lesson_date"] >= month)
                & (lessons2["lesson_date"] <= mend)
            ]
            scheduled_hours = float(month_lessons["duration"].sum()) if not month_lessons.empty else 0.0
            monthly_capacity = weekly_hours * 4.33
            remaining = max(0.0, monthly_capacity - scheduled_hours)

            rows.append({
                "snapshot_id": f"CAP-{month.strftime('%Y%m')}-{tid}",
                "snapshot_month": month.strftime("%Y-%m"),
                "teacher_id": tid,
                "teacher_name": teacher_names[tid],
                "teacher_status": status,
                "teacher_start_date": as_iso_date(start),
                "new_teacher_flag": "是" if start >= HIRING_SPIKE_DATE else "否",
                "availability_slot_count": int(len(active_slots)),
                "weekly_available_hours": round(weekly_hours, 2),
                "scheduled_hours_in_month": round(scheduled_hours, 2),
                "estimated_monthly_capacity": round(monthly_capacity, 2),
                "remaining_available_hours": round(remaining, 2),
            })

    return pd.DataFrame(rows)

def build_stopped_completed_source_truth(
    students: pd.DataFrame,
    student_status_history: pd.DataFrame,
    enrollments: pd.DataFrame,
    private_courses: pd.DataFrame,
    classes: pd.DataFrame,
    renewals: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    terminal = student_status_history[student_status_history["status"].isin(["已停课", "已完成"])]
    for _, st in terminal.iterrows():
        sid = st["student_id"]
        stu = students.loc[students["student_id"] == sid].iloc[0]
        enr = enrollments.loc[enrollments["student_id"] == sid].iloc[0]
        if enr["course_mode"] == "私教":
            course_type = private_courses.loc[private_courses["private_course_id"] == enr["private_course_id"], "course_type"].iloc[0]
            teacher_id = private_courses.loc[private_courses["private_course_id"] == enr["private_course_id"], "teacher_id"].iloc[0]
        else:
            course_type = "班课"
            teacher_id = classes.loc[classes["class_id"] == enr["class_id"], "teacher_id"].iloc[0]
        rows.append({
            "student_status_id": st["student_status_id"],
            "student_id": sid,
            "student_name": stu["student_name"],
            "course_type": course_type,
            "teacher_id": teacher_id,
            "academic_id": enr["academic_id"],
            "sales_id": enr["sales_id"],
            "country": stu["country"],
            "timezone": stu["timezone"],
            "age": stu["age"],
            "student_status": st["status"],
            "end_date": st["effective_from"],
            "remaining_hours": int(choice([0, 0, 0, 2, 5, 8])),
            "reason": st["reason"],
            "course_record_link": f"https://example.invalid/course/{sid}",
            "renewal_status": "是" if sid in set(renewals["student_id"]) else "否",
            "remark": None,
        })
    return pd.DataFrame(rows)



def build_issues(
    schedule_changes: pd.DataFrame,
    schedules: pd.DataFrame,
    private_members: pd.DataFrame,
    class_members: pd.DataFrame,
) -> pd.DataFrame:
    rows = []
    schedule_to_student = {}
    for _, sch in schedules.iterrows():
        if sch["course_mode"] == "私教" and pd.notna(sch["private_course_id"]):
            ss = private_members[private_members["private_course_id"] == sch["private_course_id"]]["student_id"].tolist()
        elif sch["course_mode"] == "班课" and pd.notna(sch["class_id"]):
            ss = class_members[class_members["class_id"] == sch["class_id"]]["student_id"].tolist()
        else:
            ss = []
        schedule_to_student[sch["schedule_id"]] = ss

    # Issues derived from schedule changes.
    if not schedule_changes.empty:
        for _, ch in schedule_changes.sample(frac=min(1.0, 0.78), random_state=SEED).iterrows():
            related_students = schedule_to_student.get(ch["schedule_id"], [])
            related_student = choice(related_students) if related_students else None
            reason = ch["change_reason"]
            category = "排课问题" if reason in ["学生改时间", "教师不可用", "教师临时请假", "班级整体调整"] else "销售承诺冲突"
            rows.append({
                "issue_id": f"ISS{len(rows)+1:05d}",
                "issue_date": ch["change_time"],
                "category": category,
                "related_student": related_student,
                "owner": ch["changed_by"],
                "status": weighted_choice(["已完成", "处理中", "待处理"], [0.72, 0.20, 0.08]),
                "resolution": weighted_choice(["重新确认时间", "更换教师", "与客户沟通", "调整班级安排", None], [0.28, 0.20, 0.24, 0.18, 0.10]),
                "related_schedule_id": ch["schedule_id"],
            })

    # Detect recurring teacher overlaps from confirmed schedules.
    s = schedules.copy()
    s["confirmed_start"] = pd.to_datetime(s["confirmed_start"])
    for teacher_id, grp in s.groupby("teacher_id"):
        grp = grp.sort_values("confirmed_start")
        records = grp.to_dict("records")
        for i in range(len(records)):
            for j in range(i + 1, len(records)):
                a, b = records[i], records[j]
                da, db = pd.Timestamp(a["confirmed_start"]), pd.Timestamp(b["confirmed_start"])
                if da.weekday() == db.weekday() and da.hour == db.hour:
                    if RNG.random() < 0.70:  # some errors are discovered, some remain latent
                        ss = schedule_to_student.get(b["schedule_id"], [])
                        rows.append({
                            "issue_id": f"ISS{len(rows)+1:05d}",
                            "issue_date": as_iso_dt(max(da, db)),
                            "category": "教师时间重叠",
                            "related_student": choice(ss) if ss else None,
                            "owner": choice(ACADEMIC_IDS),
                            "status": weighted_choice(["已完成", "处理中"], [0.75, 0.25]),
                            "resolution": choice(["调整其中一节课程", "更换教师", "重新确认时间"]),
                            "related_schedule_id": b["schedule_id"],
                        })

    # Information-transfer errors increase after policy change.
    for _ in range(55):
        d = random_ts(POLICY_CHANGE_DATE, END_DATE)
        sch = schedules.sample(n=1, random_state=int(RNG.integers(0, 1_000_000))).iloc[0]
        ss = schedule_to_student.get(sch["schedule_id"], [])
        rows.append({
            "issue_id": f"ISS{len(rows)+1:05d}",
            "issue_date": as_iso_dt(d),
            "category": weighted_choice(["信息传递错误", "销售承诺冲突", "排课问题"], [0.30, 0.45, 0.25]),
            "related_student": choice(ss) if ss else None,
            "owner": choice(ACADEMIC_IDS),
            "status": weighted_choice(["已完成", "处理中"], [0.82, 0.18]),
            "resolution": choice(["重新确认时间", "更换教师", "重新通知学生"]),
            "related_schedule_id": sch["schedule_id"],
        })

    return pd.DataFrame(rows).sort_values("issue_date").reset_index(drop=True)

def build_monthly_stats(
    trials: pd.DataFrame,
    students: pd.DataFrame,
    enrollments: pd.DataFrame,
    private_courses: pd.DataFrame,
    classes: pd.DataFrame,
    teacher_status: pd.DataFrame,
    schedule_changes: pd.DataFrame,
) -> pd.DataFrame:
    months = pd.date_range(START_DATE, END_DATE, freq="MS")
    rows = []
    exits = teacher_status[teacher_status["status"].isin(["停止授课", "离职"])].copy()
    exits["effective_date"] = pd.to_datetime(exits["effective_date"])

    trials2 = trials.copy()
    trials2["trial_date"] = pd.to_datetime(trials2["trial_date"])
    enroll2 = enrollments.copy()
    enroll2["enrollment_date"] = pd.to_datetime(enroll2["enrollment_date"])
    changes2 = schedule_changes.copy()
    if not changes2.empty:
        changes2["change_time"] = pd.to_datetime(changes2["change_time"])

    for m in months:
        mend = m + pd.offsets.MonthEnd(1)
        tm = trials2[(trials2["trial_date"] >= m) & (trials2["trial_date"] <= mend)]
        trial_count = len(tm)
        conv = (tm["enrolled"] == "是").mean() if trial_count else 0.0
        student_count = int((enroll2["enrollment_date"] <= mend).sum())
        private_growth = int(((enroll2["enrollment_date"] >= m) & (enroll2["enrollment_date"] <= mend) & (enroll2["course_mode"] == "私教")).sum())
        # class_growth = number of classes receiving first member this month
        class_first = enroll2[enroll2["course_mode"] == "班课"].groupby("class_id")["enrollment_date"].min()
        class_growth = int(((class_first >= m) & (class_first <= mend)).sum()) if len(class_first) else 0
        teacher_exit_count = int(((exits["effective_date"] >= m) & (exits["effective_date"] <= mend)).sum())
        schedule_change_count = int(((changes2["change_time"] >= m) & (changes2["change_time"] <= mend)).sum()) if not changes2.empty else 0
        # class open rate is a derived operational metric; keep plausible values.
        class_open_rate = float(np.clip(RNG.normal(0.82, 0.06), 0.60, 0.96))
        rows.append({
            "month": m.strftime("%Y-%m"),
            "trial_count": trial_count,
            "conversion_rate": round(conv, 4),
            "student_count": student_count,
            "private_growth": private_growth,
            "class_growth": class_growth,
            "class_open_rate": round(class_open_rate, 4),
            "teacher_exit_count": teacher_exit_count,
            "schedule_change_count": schedule_change_count,
        })
    return pd.DataFrame(rows)


def update_customer_and_post_outcomes(customers: pd.DataFrame, inquiries: pd.DataFrame, trials: pd.DataFrame, posts: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    customers = customers.copy()
    enrolled_customers = set(trials.loc[trials["enrolled"] == "是", "customer_id"])
    trial_customers = set(trials["customer_id"])
    customers["status"] = customers["customer_id"].map(
        lambda x: "已报名" if x in enrolled_customers else ("试听后未转化" if x in trial_customers else "跟进中")
    )

    posts = posts.copy()
    first_post = inquiries.dropna(subset=["post_id"]).sort_values("inquiry_time").drop_duplicates("customer_id")[["customer_id", "post_id"]]
    success = first_post[first_post["customer_id"].isin(enrolled_customers)].groupby("post_id")["customer_id"].nunique()
    posts["success_customer_count"] = posts["post_id"].map(success).fillna(0).astype(int)
    return customers, posts



def build_truth_tables() -> TruthTables:
    employees = build_employees()
    teachers, teacher_status = build_teachers()
    availability = build_teacher_availability(teachers, teacher_status)
    avail_map = availability_lookup(availability)
    accounts, posts = build_accounts_and_posts()
    customers, inquiries, learner_names = build_customers_and_inquiries(posts)
    trials, students, student_seed, customer_to_student = build_trials_students_enrollments(
        customers, learner_names, teachers, avail_map
    )
    classes = build_classes(teachers)
    private_courses = build_private_courses(teachers)
    enrollments, private_members, class_members, classes, private_courses = assign_enrollments_and_members(
        student_seed, students, classes, private_courses
    )
    schedules, schedule_changes = build_schedule_records(
        private_courses, classes, enrollments, students, avail_map
    )
    lessons, attendance = build_lessons_attendance(
        schedules, private_members, class_members, private_courses, classes
    )
    teacher_capacity_snapshot = build_teacher_capacity_snapshot(
        teachers, teacher_status, availability, lessons
    )
    students, student_status, renewals = build_student_status_and_renewals(students, enrollments, lessons)
    stopped_completed = build_stopped_completed_source_truth(
        students, student_status, enrollments, private_courses, classes, renewals
    )
    issues = build_issues(schedule_changes, schedules, private_members, class_members)
    monthly = build_monthly_stats(
        trials, students, enrollments, private_courses, classes, teacher_status, schedule_changes
    )
    customers, posts = update_customer_and_post_outcomes(customers, inquiries, trials, posts)

    tables = {
        "运营账号表": accounts,
        "广告帖子表": posts,
        "客户信息表": customers,
        "客户咨询事件表": inquiries,
        "试听测试表": trials,
        "学生信息表": students,
        "教师信息表": teachers,
        "员工信息表": employees,
        "报名记录表": enrollments,
        "私教课程表": private_courses,
        "私教学生关系表": private_members,
        "班课信息表": classes,
        "学生班级关系表": class_members,
        "教师可用时间表": availability,
        "教师月度可用时间快照表": teacher_capacity_snapshot,
        "排课记录表": schedules,
        "排课变更历史表": schedule_changes,
        "课程记录表": lessons,
        "课程出勤表": attendance,
        "学生状态历史表": student_status,
        "教师状态历史表": teacher_status,
        "续费记录表": renewals,
        "异常反馈表": issues,
        "月度统计表": monthly,
        "已停课已完成学生表": stopped_completed,
    }
    return TruthTables(tables=tables, learner_name_by_customer=learner_names)

def raw_customer_inquiries(truth: TruthTables) -> pd.DataFrame:
    inquiries = truth.tables["客户咨询事件表"].copy()
    customers = truth.tables["客户信息表"].set_index("customer_id")
    posts = truth.tables["广告帖子表"].set_index("post_id")
    employees = truth.tables["员工信息表"].set_index("employee_id")

    rows = []
    for i, r in inquiries.iterrows():
        customer_id = r["customer_id"]
        # 18% missing customer_id demonstrates weak linkage.
        customer_no = customer_id if RNG.random() > 0.18 else None
        account = mutate_account_name(r["customer_account"])
        sales_name = employees.loc[r["sales_id"], "employee_name"]
        post_id = r["post_id"]
        source_account = r["account_id"]
        row = {
            "编号": i + 1,
            "日期": dirty_date_string(pd.Timestamp(r["inquiry_date"])),
            "客户编号": customer_no,
            "客户账号": account,
            "咨询类型": r["inquiry_type"],
            "广告帖子编号": post_id if RNG.random() > 0.05 else None,
            "引流账号 / 私信账号": source_account,
            "负责人": mutate_person_name(sales_name),
            "销售名片": weighted_choice(["已发送", "未发送", "发送"], [0.50, 0.30, 0.20]),
            "微信添加状态": r["wechat_status"],
            "咨询时间": dirty_datetime_string(pd.Timestamp(r["inquiry_time"])),
            "回复时间": dirty_datetime_string(pd.Timestamp(r["response_time"])) if RNG.random() > 0.04 else None,
            "响应时间": r["response_duration"] if RNG.random() > 0.07 else int(r["response_duration"] + RNG.integers(10, 60)),
            "关键词": r["keyword"],
            "网络地址地区": r["region"],
            "点击次数": int(RNG.integers(1, 5)),
        }
        rows.append(row)

    df = pd.DataFrame(rows)
    # Inject exact/near duplicates.
    dup_count = max(5, int(len(df) * 0.045))
    dups = df.sample(n=dup_count, random_state=SEED).copy()
    for idx in dups.index[: len(dups) // 2]:
        dups.loc[idx, "客户账号"] = mutate_account_name(str(dups.loc[idx, "客户账号"]))
    return pd.concat([df, dups], ignore_index=True).sample(frac=1, random_state=SEED).reset_index(drop=True)


def raw_posts(truth: TruthTables) -> pd.DataFrame:
    posts = truth.tables["广告帖子表"].copy()
    accounts = truth.tables["运营账号表"].set_index("account_id")
    employees = truth.tables["员工信息表"].set_index("employee_id")

    account_totals = posts.groupby("account_id")["impression"].sum().to_dict()
    rows = []
    for _, r in posts.iterrows():
        acc = accounts.loc[r["account_id"]]
        rows.append({
            "帖子编号": r["post_id"],
            "作品名称": r["post_name"],
            "发布时间": dirty_date_string(pd.Timestamp(r["publish_date"])),
            "运营人员名称": mutate_person_name(employees.loc[r["operator_id"], "employee_name"]),
            "运营账号": mutate_account_name(acc["account_name"]),
            "曝光量": r["impression"],
            # Intentional mixed grain: account total repeated on every post row.
            "账号总曝光量": account_totals[r["account_id"]],
            "账号总粉丝量": int(RNG.integers(1000, 25000)),
        })
    return pd.DataFrame(rows)


def trial_raw_common(truth: TruthTables, trial_type: str) -> pd.DataFrame:
    trials = truth.tables["试听测试表"]
    sub = trials[trials["trial_type"] == trial_type].copy()
    employees = truth.tables["员工信息表"].set_index("employee_id")
    teachers = truth.tables["教师信息表"].set_index("teacher_id")
    students = truth.tables["学生信息表"].set_index("student_id")

    rows = []
    for _, r in sub.iterrows():
        sid = r["student_id"]
        student_name = students.loc[sid, "student_name"] if sid in students.index else truth.learner_name_by_customer[r["customer_id"]]
        preferred = pd.Timestamp(r["customer_preferred_time"])
        promised = pd.Timestamp(r["sales_promised_time"])
        confirmed = pd.Timestamp(r["academic_confirmed_time"])

        # The raw table does not reliably separate preference / promise / confirmation.
        if RNG.random() < 0.58:
            time_text = f"客户希望{preferred.strftime('%m/%d %H:%M')}，销售回复{promised.strftime('%m/%d %H:%M')}，教务{confirmed.strftime('%m/%d %H:%M')}"
        elif RNG.random() < 0.75:
            time_text = promised.strftime("%m/%d %H:%M")
        else:
            time_text = None

        base = {
            "学生姓名": department_name_variant(student_name, "销售"),
            "商业课程顾问": department_name_variant(employees.loc[truth.tables["客户信息表"].set_index("customer_id").loc[r["customer_id"], "sales_id"], "employee_name"], "销售"),
            "学生背景": weighted_choice(["零基础", "学过一点", "学校二外", "准备考试", None], [0.28, 0.28, 0.20, 0.14, 0.10]),
            "学习目标": weighted_choice(["日常交流", "DELE", "学校课程", "工作使用", "兴趣"], [0.27, 0.18, 0.20, 0.15, 0.20]),
            "备注": None if RNG.random() < 0.65 else "家长希望尽快安排",
            "时间安排": time_text,
            "教师安排": department_name_variant(teachers.loc[r["teacher_id"], "teacher_name"], "销售"),
            "教学组确认": confirmation_dirty(r["confirmation_status"]),
        }
        if trial_type == "试听":
            base.update({
                "试听班级": r["level_result"],
                "试听形式": weighted_choice(["线上", "线下"], [0.75, 0.25]),
            })
        else:
            base.update({
                "测试形式": weighted_choice(["线上", "线下"], [0.75, 0.25]),
                "当前水平": r["level_result"],
                "课程建议": f"建议进入 {r['level_result']} 课程",
            })
        rows.append(base)
    return pd.DataFrame(rows)


def raw_student_summary(truth: TruthTables) -> pd.DataFrame:
    students = truth.tables["学生信息表"]
    enrollments = truth.tables["报名记录表"].set_index("student_id")
    private_courses = truth.tables["私教课程表"].set_index("private_course_id")
    classes = truth.tables["班课信息表"].set_index("class_id")
    teachers = truth.tables["教师信息表"].set_index("teacher_id")
    employees = truth.tables["员工信息表"].set_index("employee_id")
    renewals = set(truth.tables["续费记录表"]["student_id"])

    rows = []
    active = students[students["status"].isin(["在读", "暂停"])]
    for _, s in active.iterrows():
        enr = enrollments.loc[s["student_id"]]
        if isinstance(enr, pd.DataFrame):
            enr = enr.iloc[0]
        if enr["course_mode"] == "私教":
            pc = private_courses.loc[enr["private_course_id"]]
            course_type = course_type_dirty(pc["course_type"])
            teacher_id = pc["teacher_id"]
        else:
            cl = classes.loc[enr["class_id"]]
            course_type = course_type_dirty("班课")
            teacher_id = cl["teacher_id"]

        rows.append({
            "学生姓名": department_name_variant(s["student_name"], "教务"),
            "国家": s["country"],
            "年龄": s["age"],
            "上课形式": course_type,
            "销售负责人": department_name_variant(employees.loc[s["sales_id"], "employee_name"], "教务"),
            "教师": department_name_variant(teachers.loc[teacher_id, "teacher_name"], "教务"),
            "教务负责人": department_name_variant(employees.loc[s["academic_id"], "employee_name"], "教务"),
            "学生及家长性格特点": weighted_choice(["沟通积极", "时间变化较多", "重视考试", "要求较严格", None], [0.22, 0.18, 0.18, 0.16, 0.26]),
            "课程记录链接": f"https://example.invalid/records/{s['student_id']}",
            "下月课程更新状态": weighted_choice(["已更新", "待更新", "无需更新", "done"], [0.55, 0.20, 0.20, 0.05]),
            "是否需要续费": "否" if s["student_id"] in renewals else weighted_choice(["是", "否", "待确认"], [0.30, 0.50, 0.20]),
        })
    df = pd.DataFrame(rows)
    # Duplicate a few students with slightly different names / course-type spelling.
    if len(df) >= 8:
        dup = df.sample(n=5, random_state=SEED).copy()
        dup["学生姓名"] = dup["学生姓名"].map(lambda x: mutate_person_name(str(x)))
        dup["上课形式"] = dup["上课形式"].map(lambda x: "私教" if x in ["一对一", "单人私教", "1V1"] else x)
        df = pd.concat([df, dup], ignore_index=True)
    return df


def raw_stopped_completed(truth: TruthTables) -> pd.DataFrame:
    df = truth.tables["已停课已完成学生表"].copy()
    teachers = truth.tables["教师信息表"].set_index("teacher_id")
    employees = truth.tables["员工信息表"].set_index("employee_id")

    rows = []
    for _, r in df.iterrows():
        rows.append({
            "学生姓名": mutate_person_name(r["student_name"]),
            "课程形式": course_type_dirty(r["course_type"] if r["course_type"] != "班课" else "班课"),
            "教师": department_name_variant(teachers.loc[r["teacher_id"], "teacher_name"], "销售"),
            "教务负责人": mutate_person_name(employees.loc[r["academic_id"], "employee_name"]),
            "销售负责人": mutate_person_name(employees.loc[r["sales_id"], "employee_name"]),
            "国家": r["country"],
            "学生时差": r["timezone"],
            "年龄": r["age"],
            "学生状态": weighted_choice([r["student_status"], "停课" if r["student_status"] == "已停课" else r["student_status"]], [0.7, 0.3]),
            "结束日期": dirty_date_string(pd.Timestamp(r["end_date"])),
            "剩余课时": r["remaining_hours"],
            "结束原因": r["reason"] if RNG.random() > 0.25 else None,
            "课程记录链接": r["course_record_link"],
            "是否续费": r["renewal_status"],
            "备注": r["remark"],
        })
    raw = pd.DataFrame(rows)
    # Intentional overlap with active table can happen due to file movement delay.
    return raw



def raw_course_records(truth: TruthTables) -> pd.DataFrame:
    lessons = truth.tables["课程记录表"]
    attendance = truth.tables["课程出勤表"]
    students = truth.tables["学生信息表"].set_index("student_id")
    teachers = truth.tables["教师信息表"].set_index("teacher_id")
    schedules = truth.tables["排课记录表"].set_index("schedule_id")

    rows = []
    for _, lesson in lessons.iterrows():
        attendees = attendance[attendance["lesson_id"] == lesson["lesson_id"]]
        student_ids = attendees["student_id"].tolist() or ([lesson["student_id"]] if lesson["student_id"] else [])
        sch = schedules.loc[lesson["schedule_id"]]
        schedule_start = pd.Timestamp(sch["confirmed_start"])
        madrid_hour = schedule_start.hour

        for sid in student_ids:
            if sid not in students.index:
                continue
            s = students.loc[sid]
            d = pd.Timestamp(lesson["lesson_date"])
            correct_local, correct_diff = timezone_local_time(d, madrid_hour, s["timezone"])

            local_hour = correct_local.hour
            recorded_diff = correct_diff

            # Human timezone-calculation errors:
            # - stale DST: +/- 1 hour
            # - wrong sign / copied old offset: +/- 2-3 hours
            error_roll = RNG.random()
            if error_roll < 0.10:
                delta = int(choice([-1, 1]))
                local_hour = (local_hour + delta) % 24
                recorded_diff += delta
            elif error_roll < 0.135:
                delta = int(choice([-3, -2, 2, 3]))
                local_hour = (local_hour + delta) % 24
                recorded_diff += delta

            rows.append({
                "学生姓名": department_name_variant(s["student_name"], "教务"),
                "课程类型": department_course_label(
                    "1V1" if lesson["student_id"] else "班课", "教务"
                ),
                "教师": department_name_variant(teachers.loc[lesson["teacher_id"], "teacher_name"], "教务"),
                "课程序号": lesson["lesson_id"],
                "上课日期": dirty_date_string(d),
                "中文星期": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][d.weekday()],
                "西班牙语星期": ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"][d.weekday()],
                "英语星期": d.day_name(),
                "西班牙时间": f"{madrid_hour:02d}:00",
                "学生当地时间": f"{local_hour:02d}:00",
                "时差": f"{recorded_diff:+d}h",
                "课时计算": lesson["duration"],
                "当日学习内容": weighted_choice(["语法", "口语", "阅读", "听力", "复习"], [0.25, 0.25, 0.18, 0.16, 0.16]),
                "页数": int(RNG.integers(1, 15)),
                "教师反馈": lesson["feedback"],
            })

    df = pd.DataFrame(rows)

    # Exact duplicates + near duplicates from manual copy/paste.
    if len(df) > 30:
        exact_n = max(10, int(len(df) * 0.018))
        near_n = max(8, int(len(df) * 0.012))
        exact = df.sample(n=exact_n, random_state=SEED).copy()
        near = df.sample(n=near_n, random_state=SEED + 1).copy()
        near["学生姓名"] = near["学生姓名"].map(lambda x: str(x).strip().upper())
        near["课程类型"] = near["课程类型"].map(lambda x: "私教" if "1V1" in str(x) or "一对一" in str(x) else x)
        df = pd.concat([df, exact, near], ignore_index=True)

    return df

def raw_class_files(truth: TruthTables) -> None:
    classes = truth.tables["班课信息表"]
    members = truth.tables["学生班级关系表"]
    students = truth.tables["学生信息表"].set_index("student_id")
    teachers = truth.tables["教师信息表"].set_index("teacher_id")

    for idx, cl in classes.iterrows():
        ms = members[members["class_id"] == cl["class_id"]]
        rows = []
        for _, m in ms.iterrows():
            rows.append({
                "学生姓名": mutate_person_name(students.loc[m["student_id"], "student_name"]),
                "教师": mutate_person_name(teachers.loc[cl["teacher_id"], "teacher_name"]),
                "课程时间": cl["schedule"],
                "状态": weighted_choice([m["status"], "在读中", "active"], [0.70, 0.20, 0.10]),
                "加入日期": dirty_date_string(pd.Timestamp(m["join_date"])),
                "离开日期": dirty_date_string(pd.Timestamp(m["leave_date"])) if pd.notna(m["leave_date"]) else None,
            })
        df = pd.DataFrame(rows)
        # Header drift across files.
        if idx % 4 == 1:
            df = df.rename(columns={"学生姓名": "姓名", "教师": "老师"})
        elif idx % 4 == 2:
            df = df.rename(columns={"课程时间": "上课时间", "状态": "学生状态"})
        elif idx % 4 == 3:
            df = df.rename(columns={"加入日期": "入班日期"})
        fname = f"{cl['delivery_mode']}_{cl['level']}_{cl['class_id']}.csv"
        write_csv(df, CLASS_RAW_DIR / fname)


def raw_private_files(truth: TruthTables) -> None:
    pcs = truth.tables["私教课程表"]
    members = truth.tables["私教学生关系表"]
    students = truth.tables["学生信息表"].set_index("student_id")
    teachers = truth.tables["教师信息表"].set_index("teacher_id")

    for idx, pc in pcs.iterrows():
        ms = members[members["private_course_id"] == pc["private_course_id"]]
        rows = []
        for _, m in ms.iterrows():
            rows.append({
                "学生姓名": mutate_person_name(students.loc[m["student_id"], "student_name"]),
                "课程形式": course_type_dirty(pc["course_type"]),
                "教师": mutate_person_name(teachers.loc[pc["teacher_id"], "teacher_name"]),
                "当前上课时间": pc["schedule"],
                "课程状态": weighted_choice([pc["current_status"], "上课中", "进行"], [0.70, 0.15, 0.15]),
                "开始日期": dirty_date_string(pd.Timestamp(pc["start_date"])),
                # No structured change history in raw file: intentional P3 gap.
                "调课备注": None if RNG.random() < 0.55 else choice(["改过时间", "学生临时调整", "老师时间变化", "见群聊"]),
            })
        df = pd.DataFrame(rows)
        if idx % 3 == 1:
            df = df.rename(columns={"当前上课时间": "课程时间", "教师": "老师"})
        write_csv(df, PRIVATE_RAW_DIR / f"{pc['private_course_id']}_{pc['course_type']}.csv")


def raw_schedule_files(truth: TruthTables) -> None:
    schedules = truth.tables["排课记录表"]
    classes = truth.tables["班课信息表"].set_index("class_id")
    private_courses = truth.tables["私教课程表"].set_index("private_course_id")
    teachers = truth.tables["教师信息表"].set_index("teacher_id")

    rows = []
    for _, sch in schedules.iterrows():
        if sch["course_mode"] == "班课":
            cl = classes.loc[sch["class_id"]]
            level = cl["level"]
            delivery = cl["delivery_mode"]
            obj = sch["class_id"]
        else:
            # Private courses are assigned to a synthetic level for source-file fragmentation only.
            level = choice(LEVELS)
            delivery = weighted_choice(DELIVERY_MODES, [0.82, 0.18])
            obj = sch["private_course_id"]

        rows.append({
            "level": level,
            "delivery_mode": delivery,
            "课程对象": obj,
            "课程模式": sch["course_mode"],
            "教师": mutate_person_name(teachers.loc[sch["teacher_id"], "teacher_name"]),
            # Raw source often keeps only current/final arrangement.
            "当前课程时间": dirty_datetime_string(pd.Timestamp(sch["confirmed_start"])),
            "确认状态": confirmation_dirty(sch["confirmation_status"]),
            "教务确认人": EMPLOYEE_NAME[sch["confirmed_by"]],
            "备注": "曾调整" if sch["schedule_id"] in set(truth.tables["排课变更历史表"]["schedule_id"]) else None,
        })

    df = pd.DataFrame(rows)
    for (level, delivery), part in df.groupby(["level", "delivery_mode"]):
        out = part.drop(columns=["level", "delivery_mode"]).copy()
        # Minor schema drift.
        if level in ["A2", "B2"]:
            out = out.rename(columns={"当前课程时间": "上课时间"})
        write_csv(out, SCHEDULE_RAW_DIR / f"{delivery}_{level}_课程安排.csv")


def raw_teacher_capacity_snapshot(truth: TruthTables) -> pd.DataFrame:
    snap = truth.tables["教师月度可用时间快照表"].copy()
    rows = []
    for _, r in snap.iterrows():
        # This table is intentionally a management snapshot and therefore repeats teacher info.
        rows.append({
            "月份": r["snapshot_month"],
            "教师": department_name_variant(r["teacher_name"], "运营"),
            "教师状态": weighted_choice(
                [r["teacher_status"], "active" if r["teacher_status"] == "授课中" else "inactive"],
                [0.78, 0.22],
            ),
            "是否新教师": weighted_choice([r["new_teacher_flag"], "new" if r["new_teacher_flag"] == "是" else "old"], [0.80, 0.20]),
            "每周可用小时": r["weekly_available_hours"],
            "当月已排课时": r["scheduled_hours_in_month"],
            "剩余可用小时": r["remaining_available_hours"],
            "备注": "新教师集中加入" if r["new_teacher_flag"] == "是" and r["snapshot_month"] == "2026-07" else None,
        })

    df = pd.DataFrame(rows)
    # A few duplicated monthly snapshot rows due to repeated reporting.
    if len(df) > 15:
        dup = df.sample(n=max(3, int(len(df) * 0.04)), random_state=SEED + 3).copy()
        dup["教师"] = dup["教师"].map(lambda x: str(x).upper())
        df = pd.concat([df, dup], ignore_index=True)
    return df

def raw_issues(truth: TruthTables) -> pd.DataFrame:
    issues = truth.tables["异常反馈表"].copy()
    students = truth.tables["学生信息表"].set_index("student_id")
    employees = truth.tables["员工信息表"].set_index("employee_id")
    category_variants = {
        "排课问题": ["排课问题", "排课", "时间冲突", "schedule issue"],
        "销售承诺冲突": ["销售承诺冲突", "销售时间问题", "承诺错误", "sales issue"],
        "信息传递错误": ["信息传递错误", "沟通问题", "信息错误", "communication"],
    }
    rows = []
    for _, r in issues.iterrows():
        dt = pd.Timestamp(r["issue_date"])
        rows.append({
            "日期": dirty_date_string(dt),
            "星期": dt.day_name(),
            "工作类别": choice(category_variants.get(r["category"], [r["category"]])),
            "具体事项": weighted_choice(["课程时间需重新确认", "教师不可用", "客户信息不一致", "临时改课"], [0.32, 0.24, 0.22, 0.22]),
            "学生": mutate_person_name(students.loc[r["related_student"], "student_name"]) if r["related_student"] in students.index else None,
            "班级": None,
            "教师": None,
            "记录人": mutate_person_name(employees.loc[r["owner"], "employee_name"]),
            "负责人": mutate_person_name(employees.loc[r["owner"], "employee_name"]),
            "优先级": weighted_choice(["高", "中", "低", "紧急"], [0.22, 0.46, 0.22, 0.10]),
            "状态": weighted_choice([r["status"], "完成" if r["status"] == "已完成" else r["status"]], [0.75, 0.25]),
            "截止时间": dirty_date_string(dt + pd.Timedelta(days=int(RNG.integers(1, 5)))),
            "完成时间": dirty_date_string(dt + pd.Timedelta(days=int(RNG.integers(0, 6)))) if r["status"] == "已完成" else None,
            "是否异常": "是",
            "异常等级": weighted_choice(["1", "2", "3", "高", "中"], [0.18, 0.28, 0.18, 0.18, 0.18]),
            "处理结果": r["resolution"],
            "后续跟进": None if r["status"] == "已完成" else "继续跟进",
            "备注": None,
        })
    return pd.DataFrame(rows)


def raw_bonus_scores(truth: TruthTables) -> pd.DataFrame:
    months = pd.date_range(START_DATE, END_DATE, freq="MS")
    issues = truth.tables["异常反馈表"].copy()
    issues["issue_date"] = pd.to_datetime(issues["issue_date"])
    rows = []
    for m in months:
        mend = m + pd.offsets.MonthEnd(1)
        issue_count = ((issues["issue_date"] >= m) & (issues["issue_date"] <= mend)).sum()
        penalty = min(2.0, issue_count / 35)
        for aid in ACADEMIC_IDS:
            base = 8.8 - penalty + RNG.normal(0, 0.35)
            rows.append({
                "月份": m.strftime("%Y-%m"),
                "教务": EMPLOYEE_NAME[aid],
                "教学运营稳定性": round(float(np.clip(base, 5, 10)), 1),
                "班级健康度": round(float(np.clip(base + RNG.normal(0, 0.3), 5, 10)), 1),
                "学员满意度": round(float(np.clip(base + RNG.normal(0.2, 0.35), 5, 10)), 1),
                "教学材料完成情况": round(float(np.clip(base + RNG.normal(0.1, 0.25), 5, 10)), 1),
                "教师协作情况": round(float(np.clip(base - penalty * 0.35 + RNG.normal(0, 0.4), 5, 10)), 1),
            })
    return pd.DataFrame(rows)


def raw_monthly_summary(truth: TruthTables) -> pd.DataFrame:
    monthly = truth.tables["月度统计表"].copy()
    rows = []
    for _, r in monthly.iterrows():
        conv = float(r["conversion_rate"])
        # Intentional KPI drift in some months: saved summary differs from detail recomputation.
        if r["month"] in ["2026-03", "2026-06", "2026-08"]:
            conv = float(np.clip(conv + RNG.choice([-0.04, -0.03, 0.03, 0.04]), 0, 1))
        rows.append({
            "月份": r["month"],
            "试听数量": r["trial_count"],
            "试听转化率": f"{conv:.1%}",
            "学生总数": r["student_count"],
            "私教新增": r["private_growth"],
            "班课新增": r["class_growth"],
            "开班率": f"{r['class_open_rate']:.0%}",
            "教师停止授课/离职数量": r["teacher_exit_count"],
            "排课变更数量": r["schedule_change_count"],
        })
    return pd.DataFrame(rows)


def build_raw_sources(truth: TruthTables) -> Dict[str, pd.DataFrame]:
    raw_tables = {
        "小红书客户咨询表": raw_customer_inquiries(truth),
        "小红书运营帖子表": raw_posts(truth),
        "试听课对接表": trial_raw_common(truth, "试听"),
        "等级测试表": trial_raw_common(truth, "等级测试"),
        "学生汇总表_已报名学生": raw_student_summary(truth),
        "已停课_已完成学生表": raw_stopped_completed(truth),
        "学生课程记录表": raw_course_records(truth),
        "异常事件记录表": raw_issues(truth),
        "教务团队奖金评分数据": raw_bonus_scores(truth),
        "教师可用时间月度快照": raw_teacher_capacity_snapshot(truth),
        "月度汇总统计": raw_monthly_summary(truth),
    }
    raw_class_files(truth)
    raw_private_files(truth)
    raw_schedule_files(truth)
    return raw_tables


# -----------------------------------------------------------------------------
# 5. Metadata from 04 data dictionary
# -----------------------------------------------------------------------------

def metadata_tables() -> Dict[str, pd.DataFrame]:
    entity_index = pd.DataFrame([
        ["运营账号表", "核心实体", "小红书运营帖子表", "一个运营账号", "连接账号与帖子", "P1/P2"],
        ["广告帖子表", "核心实体", "小红书运营帖子表", "一个帖子", "内容表现分析", "P2"],
        ["客户信息表", "核心实体", "小红书客户咨询表", "一个唯一客户", "客户主体去重", "P1/P2"],
        ["客户咨询事件表", "业务事件", "小红书客户咨询表", "一次咨询/互动", "市场→销售事件链", "P2"],
        ["试听测试表", "业务事件", "试听课对接表/等级测试表", "一次试听或测试", "试听与测试跟踪", "P2/P4"],
        ["学生信息表", "核心实体", "已报名学生表", "一个学生", "学生稳定主体", "P2"],
        ["教师信息表", "核心实体", "学生/课程/排课相关表", "一个教师", "教师稳定主体", "P2/P4"],
        ["员工信息表", "核心实体", "销售/教务/运营字段", "一个内部员工", "统一员工身份", "P2/P4"],
        ["报名记录表", "业务关系", "报名/学生汇总", "一次报名/购买", "学生与课程关系", "P2"],
        ["私教课程表", "课程组实体", "私教文件", "一个私教课程组", "私教长期关系", "P2/P3"],
        ["私教学生关系表", "关系表", "私教文件", "一个学生加入一个私教组", "支持1V2/1V3/1V4", "P2"],
        ["班课信息表", "课程组实体", "班课文件", "一个班级", "班级主体", "P1/P2"],
        ["学生班级关系表", "关系表", "班课文件", "一个学生加入一个班级", "班级成员历史", "P2/P3"],
        ["教师可用时间表", "业务状态", "课程安排/待确认", "教师的一段可用时间", "真实资源约束", "P4"],
        ["排课记录表", "业务事件/状态", "课程安排表", "一次排课安排", "区分偏好/承诺/确认", "P3/P4/P5"],
        ["排课变更历史表", "历史事件", "课程安排/异常", "一次排课变更", "保留改课历史", "P3/P5"],
        ["课程记录表", "业务事件", "学生课程记录表", "一次实际课程", "课程执行事实", "P2/P3"],
        ["课程出勤表", "关系/事件", "课程记录/班课记录", "一个学生在一节课的出勤", "多人出勤", "P2/P3"],
        ["学生状态历史表", "历史事件", "在读/停课/完成表", "一次学生状态变化", "生命周期历史", "P3"],
        ["教师状态历史表", "历史事件", "教师相关记录", "一次教师状态变化", "教师流失分析", "P4"],
        ["续费记录表", "业务事件", "续费管理字段", "一次续费", "续费分析", "P3/P5"],
        ["异常反馈表", "业务事件", "异常事件记录表", "一次运营异常", "运营风险分析", "P4/P5"],
        ["月度统计表", "派生汇总", "月度报表", "一个月份", "历史汇总对照", "P5"],
        ["已停课已完成学生表", "历史源表/过渡", "已停课/已完成学生表", "一条结束/状态记录", "源数据映射与校验", "P3"],
    ], columns=["实体/表", "类型", "主要来源", "一行代表什么", "主要作用", "对应痛点"])

    source_mapping = pd.DataFrame([
        ["小红书客户咨询表", "市场→销售", "一次咨询/互动", "客户信息表 + 客户咨询事件表", "一条记录不等于唯一客户", "P1/P2"],
        ["小红书运营帖子表", "市场", "帖子/账号/月度混合", "运营账号表 + 广告帖子表", "账号汇总与帖子粒度混合", "P2"],
        ["试听课对接表", "销售→教务", "一次试听安排", "试听测试表 + 排课确认字段", "销售/教师/教务信息混合", "P2/P4"],
        ["等级测试表", "销售→教务", "一次等级测试", "试听测试表", "试听与测试需区分", "P2"],
        ["学生汇总表", "报名→教务", "学生 + 当前状态", "学生信息表 + 报名记录表 + 状态历史", "稳定属性与状态混合", "P2/P3"],
        ["已停课/已完成学生表", "生命周期", "结束/停课记录", "学生状态历史表 + 续费记录表", "状态依赖文件位置", "P3"],
        ["学生课程记录表", "课程交付", "学生-单节课程", "课程记录表 + 出勤表", "计划与实际关系不足", "P2/P3"],
        ["私教课程文件", "教务排课", "课程组/学生/教师混合", "私教课程表 + 私教学生关系表", "多人关系", "P2/P3"],
        ["班课文件", "教务排课", "一个班级文件", "班课信息表 + 学生班级关系表", "新增文件扩展业务", "P1/P2"],
        ["课程安排表", "排课", "当前排课状态", "教师可用时间表 + 排课记录 + 变更历史", "历史和确认状态不足", "P3/P4"],
        ["异常事件记录表", "运营", "一次异常/任务", "异常反馈表", "异常类型需标准化", "P4/P5"],
        ["教务奖金评分数据", "运营管理", "月度汇总评价", "月度统计/评价数据", "不能替代事件明细", "P5"],
    ], columns=["当前源数据", "业务流程", "当前粒度", "主要标准化目标", "主要已知问题", "对应痛点"])

    rules = pd.DataFrame([
        ["R-001", "同一个客户可以产生多次咨询事件；Customer 与 Interaction 必须区分。", "P2"],
        ["R-002", "学生主体与试听、报名、课程记录分离。", "P2"],
        ["R-003", "私教课程组与学生采用关系表。", "P2"],
        ["R-004", "班课主体与班级成员采用关系表。", "P2/P3"],
        ["R-005", "学生状态变化不能只覆盖当前值，应保留状态历史。", "P3"],
        ["R-006", "排课调整不能只保留当前时间，应保留变更历史。", "P3/P5"],
        ["R-007", "客户偏好、销售承诺、教师可用时间、教务确认时间必须区分。", "P4"],
        ["R-008", "不假设历史 sales_promised_time / teacher availability 完整存在。", "数据可信度"],
        ["R-009", "月度汇总指标优先由明细重新计算并固定口径。", "P5"],
        ["R-010", "无法恢复的历史信息标记缺失，不人为补造。", "数据可信度"],
    ], columns=["规则编号", "业务规则", "对应问题"])

    relationships = pd.DataFrame([
        ["运营账号表", "account_id", "广告帖子表", "1:N"],
        ["广告帖子表", "post_id", "客户咨询事件表", "1:N"],
        ["客户信息表", "customer_id", "客户咨询事件表", "1:N"],
        ["客户信息表", "customer_id", "试听测试表", "1:N"],
        ["学生信息表", "student_id", "试听测试表", "1:N 可选"],
        ["学生信息表", "student_id", "报名记录表", "1:N"],
        ["私教课程表", "private_course_id", "私教学生关系表", "1:N"],
        ["班课信息表", "class_id", "学生班级关系表", "1:N"],
        ["教师信息表", "teacher_id", "教师可用时间表", "1:N"],
        ["排课记录表", "schedule_id", "排课变更历史表", "1:N"],
        ["排课记录表", "schedule_id", "课程记录表", "1:N"],
        ["课程记录表", "lesson_id", "课程出勤表", "1:N"],
        ["学生信息表", "student_id", "学生状态历史表", "1:N"],
        ["教师信息表", "teacher_id", "教师状态历史表", "1:N"],
        ["学生信息表", "student_id", "续费记录表", "1:N"],
        ["异常反馈表", "related_schedule_id", "排课记录表", "N:1"],
    ], columns=["主表", "关联字段", "关联表", "关系"])

    return {
        "01_实体索引": entity_index,
        "02_源表映射": source_mapping,
        "业务规则": rules,
        "数据关系说明": relationships,
    }


# -----------------------------------------------------------------------------
# 6. Validation and injected-issue manifest
# -----------------------------------------------------------------------------

def validate_truth(tables: Dict[str, pd.DataFrame]) -> List[str]:
    checks = []
    pk_map = {
        "运营账号表": "account_id",
        "广告帖子表": "post_id",
        "客户信息表": "customer_id",
        "客户咨询事件表": "inquiry_id",
        "试听测试表": "trial_id",
        "学生信息表": "student_id",
        "教师信息表": "teacher_id",
        "员工信息表": "employee_id",
        "报名记录表": "enrollment_id",
        "私教课程表": "private_course_id",
        "私教学生关系表": "private_course_student_id",
        "班课信息表": "class_id",
        "学生班级关系表": "class_student_id",
        "教师可用时间表": "availability_id",
        "教师月度可用时间快照表": "snapshot_id",
        "排课记录表": "schedule_id",
        "排课变更历史表": "schedule_change_id",
        "课程记录表": "lesson_id",
        "课程出勤表": "attendance_id",
        "学生状态历史表": "student_status_id",
        "教师状态历史表": "teacher_status_id",
        "续费记录表": "renewal_id",
        "异常反馈表": "issue_id",
        "月度统计表": "month",
        "已停课已完成学生表": "student_status_id",
    }
    for name, pk in pk_map.items():
        df = tables[name]
        checks.append(f"{name}.{pk} unique = {pk_unique(df, pk)}")

    # Key FKs.
    def fk_subset(child, col, parent, pcol):
        vals = set(tables[child][col].dropna())
        pvals = set(tables[parent][pcol].dropna())
        return vals.issubset(pvals)

    fk_checks = [
        ("客户咨询事件表", "customer_id", "客户信息表", "customer_id"),
        ("试听测试表", "customer_id", "客户信息表", "customer_id"),
        ("报名记录表", "student_id", "学生信息表", "student_id"),
        ("私教学生关系表", "student_id", "学生信息表", "student_id"),
        ("学生班级关系表", "student_id", "学生信息表", "student_id"),
        ("排课变更历史表", "schedule_id", "排课记录表", "schedule_id"),
        ("课程记录表", "schedule_id", "排课记录表", "schedule_id"),
        ("课程出勤表", "lesson_id", "课程记录表", "lesson_id"),
    ]
    for args in fk_checks:
        checks.append(f"FK {args[0]}.{args[1]} -> {args[2]}.{args[3]} = {fk_subset(*args)}")
    return checks



def injected_issue_manifest(raw_tables: Dict[str, pd.DataFrame], truth: TruthTables) -> pd.DataFrame:
    inquiries_raw = raw_tables["小红书客户咨询表"]
    trials = truth.tables["试听测试表"].copy()
    trials["trial_date"] = pd.to_datetime(trials["trial_date"])
    snap = truth.tables["教师月度可用时间快照表"]

    pre = trials[trials["trial_date"] < POLICY_CHANGE_DATE]
    boost = trials[(trials["trial_date"] >= POLICY_CHANGE_DATE) & (trials["trial_date"] < pd.Timestamp("2026-07-01"))]
    late = trials[trials["trial_date"] >= pd.Timestamp("2026-07-01")]

    snap_summary = snap.groupby("snapshot_month").agg(
        teacher_count=("teacher_id", "nunique"),
        avg_weekly_available=("weekly_available_hours", "mean"),
        avg_remaining=("remaining_available_hours", "mean"),
        new_teacher_count=("new_teacher_flag", lambda s: int((s == "是").sum())),
    ).reset_index()

    overlap_issues = int((truth.tables["异常反馈表"]["category"] == "教师时间重叠").sum())
    issues = [
        ["SIM-001", "P1", "班课/课程安排/私教被拆成多个独立文件", "raw/班课文件, raw/私教课程文件, raw/课程安排表", "文件数量与模式本身体现碎片化"],
        ["SIM-002", "P2", "同一客户可有多次咨询；不同部门对姓名/账号写法不同", "客户咨询/试听/学生汇总", f"raw inquiry rows={len(inquiries_raw)}"],
        ["SIM-003", "P2", "课程形式在销售/教务/运营中使用不同标签", "试听表/学生汇总/班课私教文件", "VIP一对一/1对1私教/1V1/私教等"],
        ["SIM-004", "P3", "raw 学生/排课主要保存当前状态；truth 才保留历史", "学生汇总/已停课表/课程安排表", "用于展示状态覆盖与历史缺口"],
        ["SIM-005", "P4", "Jun-Jul-Aug 教师可用时间逐步压缩，Jul 新教师集中加入", "教师可用时间月度快照", snap_summary.to_json(orient="records", force_ascii=False)],
        ["SIM-006", "P4", "2026-05 后销售承诺与教师可用时间冲突概率提高", "试听测试表/排课记录表", f"pre={(pre['confirmation_status']=='冲突').mean():.1%}; May-Jun={(boost['confirmation_status']=='冲突').mean():.1%}; Jul-Aug={(late['confirmation_status']=='冲突').mean():.1%}"],
        ["SIM-007", "P4", "短期转化提升、约两个月后回落", "试听测试表/月度统计", f"pre={(pre['enrolled']=='是').mean():.1%}; May-Jun={(boost['enrolled']=='是').mean():.1%}; Jul-Aug={(late['enrolled']=='是').mean():.1%}"],
        ["SIM-008", "P4/P5", "人工排课造成同一教师时间重叠", "排课记录表/异常事件", f"detected overlap issues={overlap_issues}"],
        ["SIM-009", "P5", "学生课程记录存在真实时区换算错误（DST/错符号/旧时差）", "学生课程记录表", "约10%-14%记录被注入时差错误"],
        ["SIM-010", "P2/P5", "跨部门重复记录且标记方式不同", "试听/学生/异常/班课私教", "同一人、同一课程、同一状态出现不同名称与标签"],
        ["SIM-011", "P5", "部分月度汇总转化率与明细重算不一致", "月度汇总统计 vs 试听测试表", "人为加入口径漂移"],
        ["SIM-012", "P2/P5", "学生课程记录存在 exact + near duplicates", "学生课程记录表", "用于 DISTINCT/去重/双重计课风险分析"],
    ]
    return pd.DataFrame(issues, columns=["issue_id", "对应痛点", "注入问题", "涉及数据", "预期信号"])

def export_all(truth: TruthTables, raw_tables: Dict[str, pd.DataFrame]) -> None:
    ensure_dirs()

    # Standardized truth - every business data table from 04.
    for name, df in truth.tables.items():
        write_csv(df, STD_DIR / f"{name}.csv")

    # Raw source tables - data assets from 03.
    for name, df in raw_tables.items():
        write_csv(df, RAW_DIR / f"{name}.csv")

    # Metadata corresponding to 04 workbook non-data tabs.
    for name, df in metadata_tables().items():
        write_csv(df, META_DIR / f"{name}.csv")

    manifest = injected_issue_manifest(raw_tables, truth)
    write_csv(manifest, META_DIR / "注入问题清单_仅开发校验.csv")

    checks = validate_truth(truth.tables)
    (META_DIR / "truth_validation.txt").write_text("\n".join(checks), encoding="utf-8")

    readme = f"""# 模拟数据说明

本目录由 `generate_mock_data.py` 自动生成，随机种子为 `{SEED}`。

## 目录

- `raw/`：模拟当前 Excel / Google Sheets 式原始数据，**故意保留脏数据和结构问题**。
- `standardized_truth/`：内部一致的模拟真值，用于验证后续 ETL 是否合理；正式 Portfolio 分析时建议把它视为开发校验数据，而不是清洗输入。
- `metadata/`：实体索引、源表映射、业务规则、关系说明和注入问题清单。

## 模拟规模

- 客户：{len(truth.tables['客户信息表'])}
- 咨询事件：{len(truth.tables['客户咨询事件表'])}
- 试听/测试：{len(truth.tables['试听测试表'])}
- 学生：{len(truth.tables['学生信息表'])}
- 教师：{len(truth.tables['教师信息表'])}
- 班级：{len(truth.tables['班课信息表'])}
- 私教课程组：{len(truth.tables['私教课程表'])}
- 实际课程记录：{len(truth.tables['课程记录表'])}
- 排课变更：{len(truth.tables['排课变更历史表'])}
- 异常记录：{len(truth.tables['异常反馈表'])}

## 重点模拟问题

1. P1：班课、私教、课程安排被拆分成多个独立文件。
2. P2：Customer 与 Interaction 混合；姓名、课程类型、字段名存在不一致。
3. P3：raw 层主要保存当前状态，历史状态/排课变更难以从源文件直接恢复。
4. P4：从 `{POLICY_CHANGE_DATE.date()}` 起，提高“销售承诺时间与教师实际可用时间不一致”的概率。
5. P4：Jun / Jul / Aug 三个月教师月度容量快照中，既有教师每周可用时间逐步压缩；Jul 集中新加入一批教师。
6. P5：课程记录中注入时差换算错误，包括 DST 误差、旧时差和正负方向错误。
7. P5：部分正式排课存在同一教师同一时间重叠，模拟人工协调失误。
8. P2/P5：不同部门对同一学生、教师、课程形式和状态使用不同名称或标签，并存在 exact / near duplicates。
9. P5：异常类型不标准、课程记录重复、月度汇总 KPI 口径漂移。

## 推荐使用方式

1. 后续 Python ETL **只读取 `raw/`**。
2. 将清洗结果写入新的 `processed/` 或数据库 staging 层。
3. 不要直接使用 `standardized_truth/` 做最终分析；它主要用于开发时检查你的 ETL 是否大致恢复了正确关系。
4. SQL 分析优先从明细重新计算 KPI，再与 `raw/月度汇总统计.csv` 对比。
5. `metadata/注入问题清单_仅开发校验.csv` 不应作为业务分析证据，仅用于确认你的代码有没有检测到预设问题。

所有数据均为模拟数据，不对应真实学生、教师、客户或员工。
"""
    (BASE_DIR / "README_模拟数据说明.md").write_text(readme, encoding="utf-8")


def print_summary(truth: TruthTables, raw_tables: Dict[str, pd.DataFrame]) -> None:
    print("\n=== Standardized truth tables ===")
    for name, df in truth.tables.items():
        print(f"{name:<16} {len(df):>5} rows")
    print("\n=== Raw top-level source tables ===")
    for name, df in raw_tables.items():
        print(f"{name:<22} {len(df):>5} rows")
    print(f"\nClass files: {len(list(CLASS_RAW_DIR.glob('*.csv')))}")
    print(f"Private-course files: {len(list(PRIVATE_RAW_DIR.glob('*.csv')))}")
    print(f"Schedule files: {len(list(SCHEDULE_RAW_DIR.glob('*.csv')))}")
    print(f"\nOutput: {BASE_DIR}")


# -----------------------------------------------------------------------------
# 8. Main
# -----------------------------------------------------------------------------

def main() -> None:
    ensure_dirs()
    truth = build_truth_tables()
    raw_tables = build_raw_sources(truth)
    export_all(truth, raw_tables)
    print_summary(truth, raw_tables)


if __name__ == "__main__":
    main()
