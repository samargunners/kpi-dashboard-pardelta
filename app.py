import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from supabase import create_client, Client
import psycopg2
from typing import Dict, List, Tuple, Optional

# Page config
st.set_page_config(page_title="Pardelta Dashboard", layout="wide")

#  store data
STORES = [
    {
        "pc_number": "301290",
        "store_name": "Paxton",
        "address": "2820 Paxton Street",
        "company": "RK Inc",
        "bank_account_last4": "9427",
    },
    {
        "pc_number": "343939",
        "store_name": "Mt Joy",
        "address": "807 E Maint St",
        "company": "RK Inc",
        "bank_account_last4": "1672",
    },
    {
        "pc_number": "357993",
        "store_name": "Enola",
        "address": "423 N. Enola Rd",
        "company": "RK Inc",
        "bank_account_last4": "1867",
    },
    {
        "pc_number": "358529",
        "store_name": "Columbia",
        "address": "3929 Columbia Ave",
        "company": "Par-Delta",
        "bank_account_last4": "2415",
    },
    {
        "pc_number": "359042",
        "store_name": "Lititz",
        "address": "737 S. Broad Street",
        "company": "Par-Delta",
        "bank_account_last4": "3421",
    },
    {
        "pc_number": "362913",
        "store_name": "Eisenhower",
        "address": "900 Eisenhower Blvd",
        "company": "KPA",
        "bank_account_last4": "1347",
    },
    {
        "pc_number": "363271",
        "store_name": "Marietta",
        "address": "1154 River Rd",
        "company": "RK Inc",
        "bank_account_last4": "4837",
    },
    {
        "pc_number": "364322",
        "store_name": "ETown",
        "address": "820 S. Market Street",
        "company": "Par-Delta",
        "bank_account_last4": "6345",
    },
]


def get_supabase_config():
    """Extract Supabase configuration from Streamlit secrets."""
    supabase = st.secrets.get("supabase", {})
    return {
        "url": st.secrets.get("supabase_url", ""),
        "key": st.secrets.get("supabase_anon_key", ""),
        "host": supabase.get("host", ""),
        "database": supabase.get("database", "") or supabase.get("dbname", ""),
        "user": supabase.get("user", ""),
        "password": supabase.get("password", ""),
        "port": supabase.get("port", 5432),
    }


def get_date_range(period: str) -> Tuple[datetime, datetime]:
    """
    Calculate start and end dates based on period selection.
    
    Special handling for Week to Date:
    - On Sunday (day 0): Show LAST complete week (previous Sun-Sat)
      Reason: Saturday's data arrives by 9 AM Sunday, but Sunday's data isn't complete yet
    - On Monday-Saturday (days 1-6): Show CURRENT week to date (Sun-today)
      Reason: Previous Sunday's data is now available
    
    Args:
        period: One of "Week to Date", "Month to Date", "Year to Date"
    
    Returns:
        Tuple of (start_date, end_date)
    """
    today = datetime.now().date()
    
    if period == "Week to Date":
        # Week is Sunday to Saturday
        current_day_of_week = (today.weekday() + 1) % 7  # 0=Sunday, 1=Monday, ..., 6=Saturday
        
        if current_day_of_week == 0:  # Sunday
            # Show LAST complete week (previous Sunday to Saturday)
            # Go back 7 days to last Sunday, then that's the start
            last_sunday = today - timedelta(days=7)
            last_saturday = today - timedelta(days=1)
            start_date = last_sunday
            end_date = last_saturday
        else:  # Monday through Saturday
            # Show CURRENT week to date (this Sunday to today)
            days_since_sunday = current_day_of_week
            start_date = today - timedelta(days=days_since_sunday)
            end_date = today
            
    elif period == "Month to Date":
        start_date = today.replace(day=1)
        end_date = today
    else:  # Year to Date
        start_date = today.replace(month=1, day=1)
        end_date = today
    
    return datetime.combine(start_date, datetime.min.time()), datetime.combine(end_date, datetime.max.time())


@st.cache_resource
def get_supabase_client() -> Optional[Client]:
    """Create and cache Supabase client."""
    config = get_supabase_config()
    if config["url"] and config["key"]:
        try:
            return create_client(config["url"], config["key"])
        except Exception as e:
            st.error(f"Failed to create Supabase client: {e}")
            return None
    return None


@st.cache_resource
def get_postgres_connection():
    """Create and cache PostgreSQL connection."""
    config = get_supabase_config()
    if config["host"] and config["database"] and config["user"] and config["password"]:
        try:
            conn = psycopg2.connect(
                host=config["host"],
                database=config["database"],
                user=config["user"],
                password=config["password"],
                port=config["port"],
            )
            return conn
        except Exception as e:
            st.error(f"Failed to connect to PostgreSQL: {e}")
            return None
    return None


@st.cache_data(ttl=300)  # Cache for 5 minutes
def fetch_hme_data(start_date: datetime, end_date: datetime, use_postgres: bool = True) -> pd.DataFrame:
    """
    Fetch HME report data from Supabase.
    
    Returns DataFrame with columns: date, store, time_measure, lane_total
    """
    try:
        if use_postgres:
            conn = get_postgres_connection()
            if conn:
                query = """
                    SELECT date, store, time_measure, lane_total
                    FROM hme_report
                    WHERE date >= %s AND date <= %s
                    ORDER BY date, store, time_measure
                """
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
                return df
        else:
            client = get_supabase_client()
            if client:
                response = (
                    client.table("hme_report")
                    .select("date,store,time_measure,lane_total")
                    .gte("date", start_date.strftime("%Y-%m-%d"))
                    .lte("date", end_date.strftime("%Y-%m-%d"))
                    .execute()
                )
                return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching HME data: {e}")
    
    return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_labor_data(start_date: datetime, end_date: datetime, use_postgres: bool = True) -> pd.DataFrame:
    """
    Fetch labor metrics data from Supabase.
    
    Returns DataFrame with columns: date, pc_number, labor_position, percent_labor
    """
    try:
        if use_postgres:
            conn = get_postgres_connection()
            if conn:
                query = """
                    SELECT date, pc_number, labor_position, percent_labor
                    FROM labor_metrics
                    WHERE date >= %s AND date <= %s
                    ORDER BY date, pc_number, labor_position
                """
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
                return df
        else:
            client = get_supabase_client()
            if client:
                response = (
                    client.table("labor_metrics")
                    .select("date,pc_number,labor_position,percent_labor")
                    .gte("date", start_date.strftime("%Y-%m-%d"))
                    .lte("date", end_date.strftime("%Y-%m-%d"))
                    .execute()
                )
                return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching labor data: {e}")
    
    return pd.DataFrame()


@st.cache_data(ttl=300)
def fetch_medallia_data(start_date: datetime, end_date: datetime, use_postgres: bool = True) -> pd.DataFrame:
    """
    Fetch Medallia (OSAT) data from Supabase.
    
    Returns DataFrame with columns: report_date, pc_number, osat
    """
    try:
        if use_postgres:
            conn = get_postgres_connection()
            if conn:
                query = """
                    SELECT report_date, pc_number, osat
                    FROM medallia_report
                    WHERE report_date >= %s AND report_date <= %s
                    AND osat IS NOT NULL
                    ORDER BY report_date, pc_number
                """
                df = pd.read_sql_query(query, conn, params=(start_date, end_date))
                return df
        else:
            client = get_supabase_client()
            if client:
                response = (
                    client.table("medallia_report")
                    .select("report_date,pc_number,osat")
                    .gte("report_date", start_date.strftime("%Y-%m-%d"))
                    .lte("report_date", end_date.strftime("%Y-%m-%d"))
                    .not_.is_("osat", "null")
                    .execute()
                )
                return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error fetching Medallia data: {e}")
    
    return pd.DataFrame()


def calculate_hme_metrics(df: pd.DataFrame) -> Tuple[Dict[str, Dict[str, int]], Dict[str, float]]:
    """
    Calculate HME rankings and averages by week.

    Args:
        df: HME report DataFrame

    Returns:
        Tuple of (color_counts, averages) where:
        - color_counts: {pc_number: {Green: count, Yellow: count, Red: count}} - counts of weeks
        - averages: {pc_number: average_lane_total}
    """
    if df.empty:
        return {}, {}

    # Convert store (bigint) to pc_number (string)
    store_to_pc = {int(s["pc_number"]): s["pc_number"] for s in STORES}

    # Calculate daily average across all 5 dayparts
    df["date"] = pd.to_datetime(df["date"])
    daily_avg = df.groupby(["date", "store"])["lane_total"].mean().reset_index()
    daily_avg["pc_number"] = daily_avg["store"].map(store_to_pc)

    # Assign week (Sunday to Saturday) - week starts on Sunday
    daily_avg["week"] = daily_avg["date"].dt.to_period("W-SAT")

    # Calculate weekly average
    weekly_avg = daily_avg.groupby(["week", "pc_number"])["lane_total"].mean().reset_index()

    # Color coding based on average lane_total
    color_counts = {}
    averages = {}

    for pc in [s["pc_number"] for s in STORES]:
        store_data = weekly_avg[weekly_avg["pc_number"] == pc]

        if len(store_data) == 0:
            color_counts[pc] = {"Green": 0, "Yellow": 0, "Red": 0}
            averages[pc] = 0
            continue

        green = (store_data["lane_total"] <= 150).sum()
        yellow = ((store_data["lane_total"] > 150) & (store_data["lane_total"] <= 160)).sum()
        red = (store_data["lane_total"] > 160).sum()

        color_counts[pc] = {"Green": int(green), "Yellow": int(yellow), "Red": int(red)}
        averages[pc] = float(store_data["lane_total"].mean())

    return color_counts, averages


def calculate_hme_dp2_metrics(df: pd.DataFrame) -> Tuple[Dict[str, Dict[str, int]], Dict[str, float]]:
    """
    Calculate HME Daypart 2 rankings and averages by week.

    Args:
        df: HME report DataFrame

    Returns:
        Tuple of (color_counts, averages) where counts are weeks in each color
    """
    if df.empty:
        return {}, {}

    # Filter for Daypart 2 only
    df_dp2 = df[df["time_measure"] == "Daypart 2"].copy()

    if df_dp2.empty:
        return {}, {}

    store_to_pc = {int(s["pc_number"]): s["pc_number"] for s in STORES}
    df_dp2["date"] = pd.to_datetime(df_dp2["date"])
    df_dp2["pc_number"] = df_dp2["store"].map(store_to_pc)

    # Assign week (Sunday to Saturday)
    df_dp2["week"] = df_dp2["date"].dt.to_period("W-SAT")

    # Calculate weekly average
    weekly_avg = df_dp2.groupby(["week", "pc_number"])["lane_total"].mean().reset_index()

    color_counts = {}
    averages = {}

    for pc in [s["pc_number"] for s in STORES]:
        store_data = weekly_avg[weekly_avg["pc_number"] == pc]

        if len(store_data) == 0:
            color_counts[pc] = {"Green": 0, "Yellow": 0, "Red": 0}
            averages[pc] = 0
            continue

        green = (store_data["lane_total"] <= 140).sum()
        yellow = ((store_data["lane_total"] > 140) & (store_data["lane_total"] <= 150)).sum()
        red = (store_data["lane_total"] > 150).sum()

        color_counts[pc] = {"Green": int(green), "Yellow": int(yellow), "Red": int(red)}
        averages[pc] = float(store_data["lane_total"].mean())

    return color_counts, averages


def calculate_labor_metrics(df: pd.DataFrame) -> Tuple[Dict[str, Dict[str, int]], Dict[str, float]]:
    """
    Calculate Labor rankings and averages by week.

    Excludes: "DD Manager" and "DD Manager - Salary"

    Args:
        df: Labor metrics DataFrame

    Returns:
        Tuple of (color_counts, averages) where counts are weeks in each color
    """
    if df.empty:
        return {}, {}

    # Exclude manager positions
    excluded_positions = ["DD Manager", "DD Manager - Salary"]
    df_filtered = df[~df["labor_position"].isin(excluded_positions)].copy()

    if df_filtered.empty:
        return {}, {}

    df_filtered["date"] = pd.to_datetime(df_filtered["date"])

    # Sum percent_labor by date and pc_number
    daily_labor = df_filtered.groupby(["date", "pc_number"])["percent_labor"].sum().reset_index()
    daily_labor["percent_labor"] = daily_labor["percent_labor"] * 100  # Convert to percentage

    # Assign week (Sunday to Saturday)
    daily_labor["week"] = daily_labor["date"].dt.to_period("W-SAT")

    # Calculate weekly average
    weekly_labor = daily_labor.groupby(["week", "pc_number"])["percent_labor"].mean().reset_index()

    color_counts = {}
    averages = {}

    for pc in [s["pc_number"] for s in STORES]:
        store_data = weekly_labor[weekly_labor["pc_number"] == pc]

        if len(store_data) == 0:
            color_counts[pc] = {"Green": 0, "Yellow": 0, "Red": 0}
            averages[pc] = 0
            continue

        green = (store_data["percent_labor"] < 20).sum()
        yellow = ((store_data["percent_labor"] >= 20) & (store_data["percent_labor"] <= 23)).sum()
        red = (store_data["percent_labor"] > 23).sum()

        color_counts[pc] = {"Green": int(green), "Yellow": int(yellow), "Red": int(red)}
        averages[pc] = float(store_data["percent_labor"].mean())

    return color_counts, averages


def calculate_osat_metrics(df: pd.DataFrame) -> Tuple[Dict[str, Dict[str, int]], Dict[str, float]]:
    """
    Calculate OSAT rankings and averages by week.

    Args:
        df: Medallia report DataFrame

    Returns:
        Tuple of (color_counts, averages) where averages are in percentage (0-100) and counts are weeks
    """
    if df.empty:
        return {}, {}

    df["report_date"] = pd.to_datetime(df["report_date"])

    # Calculate daily average OSAT and convert to percentage
    daily_osat = df.groupby(["report_date", "pc_number"])["osat"].mean().reset_index()
    daily_osat["osat_percent"] = (daily_osat["osat"] / 5) * 100

    # Assign week (Sunday to Saturday)
    daily_osat["week"] = daily_osat["report_date"].dt.to_period("W-SAT")

    # Calculate weekly average
    weekly_osat = daily_osat.groupby(["week", "pc_number"])["osat_percent"].mean().reset_index()

    color_counts = {}
    averages = {}

    for pc in [s["pc_number"] for s in STORES]:
        store_data = weekly_osat[weekly_osat["pc_number"] == pc]

        if len(store_data) == 0:
            color_counts[pc] = {"Green": 0, "Yellow": 0, "Red": 0}
            averages[pc] = 0
            continue

        green = (store_data["osat_percent"] > 90).sum()
        yellow = ((store_data["osat_percent"] >= 85) & (store_data["osat_percent"] <= 90)).sum()
        red = (store_data["osat_percent"] < 85).sum()

        color_counts[pc] = {"Green": int(green), "Yellow": int(yellow), "Red": int(red)}
        averages[pc] = float(store_data["osat_percent"].mean())

    return color_counts, averages


def get_metric_ranges(metric: str) -> Dict[str, str]:
    """
    Get the range descriptions for each metric's color coding.
    
    Args:
        metric: One of "HME", "HME DP_2", "Labour", "OSAT"
    
    Returns:
        Dict with keys: "green", "yellow", "red" containing the range descriptions
    """
    if metric == "HME":
        return {"green": "≤150", "yellow": "150-160", "red": ">160"}
    elif metric == "HME DP_2":
        return {"green": "≤140", "yellow": "140-150", "red": ">150"}
    elif metric == "Labour":
        return {"green": "<20", "yellow": "20-23", "red": ">23"}
    elif metric == "OSAT":
        return {"green": ">90", "yellow": "85-90", "red": "<85"}
    return {"green": "", "yellow": "", "red": ""}


def color_for_metric(metric: str, value: float) -> str:
    """
    Return CSS background color for a metric value.
    
    Args:
        metric: One of "HME", "HME DP_2", "Labour", "OSAT"
        value: Metric value
    
    Returns:
        CSS style string
    """
    green = "#c6efce"
    yellow = "#ffeb9c"
    red = "#ffc7ce"

    if metric == "HME":
        if value <= 150:
            return f"background-color: {green}"
        if value <= 160:
            return f"background-color: {yellow}"
        return f"background-color: {red}"
    
    if metric == "HME DP_2":
        if value <= 140:
            return f"background-color: {green}"
        if value <= 150:
            return f"background-color: {yellow}"
        return f"background-color: {red}"

    if metric == "Labour":
        if value < 20:
            return f"background-color: {green}"
        if value <= 23:
            return f"background-color: {yellow}"
        return f"background-color: {red}"

    if metric == "OSAT":
        if value > 90:
            return f"background-color: {green}"
        if value >= 85:
            return f"background-color: {yellow}"
        return f"background-color: {red}"

    return ""


def build_ranking_table(counts: Dict[str, Dict[str, int]], metric: str = "") -> pd.DataFrame:
    """
    Build ranking table from color counts with ranges displayed in column headers.

    Args:
        counts: {pc_number: {Green: count, Yellow: count, Red: count}}
        metric: Name of metric (e.g., "HME", "Labour") for displaying ranges

    Returns:
        DataFrame sorted by Red (desc), Yellow (desc), Green (desc)
    """
    rows = []
    for store in STORES:
        pc = store["pc_number"]
        row = counts.get(pc, {"Green": 0, "Yellow": 0, "Red": 0})
        rows.append(
            {
                "pc_number": pc,
                "Store": store["store_name"],
                "Green": row["Green"],
                "Yellow": row["Yellow"],
                "Red": row["Red"],
            }
        )

    df = pd.DataFrame(rows)
    df = df.sort_values(["Red", "Yellow", "Green"], ascending=[False, False, False])
    df = df[["Store", "Green", "Yellow", "Red"]]
    
    # Add ranges to column names if metric provided
    if metric:
        ranges = get_metric_ranges(metric)
        df = df.rename(columns={
            "Green": f"Green ({ranges['green']})",
            "Yellow": f"Yellow ({ranges['yellow']})",
            "Red": f"Red ({ranges['red']})"
        })
    
    return df


def build_performance_table(
    hme_avg: Dict[str, float],
    hme_dp2_avg: Dict[str, float],
    labor_avg: Dict[str, float],
    osat_avg: Dict[str, float],
) -> pd.DataFrame:
    """
    Build performance table with all metrics and ranges displayed in column headers.
    
    Args:
        hme_avg: {pc_number: average_hme}
        hme_dp2_avg: {pc_number: average_hme_dp2}
        labor_avg: {pc_number: average_labor_percent}
        osat_avg: {pc_number: average_osat_percent}
    
    Returns:
        Styled DataFrame
    """
    rows = []
    for store in sorted(STORES, key=lambda x: x["pc_number"]):
        pc = store["pc_number"]
        rows.append(
            {
                "pc_number": pc,
                "Store": store["store_name"],
                "HME": hme_avg.get(pc, 0),
                "HME DP_2": hme_dp2_avg.get(pc, 0),
                "Labour": labor_avg.get(pc, 0),
                "OSAT": osat_avg.get(pc, 0),
            }
        )

    perf_df = pd.DataFrame(rows)
    perf_df = perf_df[["Store", "HME", "HME DP_2", "Labour", "OSAT"]]

    # Create column name mappings with ranges
    metric_to_col = {
        "HME": "HME",
        "HME DP_2": "HME DP_2",
        "Labour": "Labour",
        "OSAT": "OSAT",
    }
    
    column_name_map = {}
    for metric, orig_col in metric_to_col.items():
        ranges = get_metric_ranges(metric)
        new_col = f"{metric}\n(G: {ranges['green']} | Y: {ranges['yellow']} | R: {ranges['red']})"
        column_name_map[orig_col] = new_col
    
    # Rename dataframe columns to include ranges
    perf_df = perf_df.rename(columns=column_name_map)

    # Apply styling with new column names
    styled = perf_df.style
    for metric, orig_col in metric_to_col.items():
        new_col = column_name_map[orig_col]
        styled = styled.applymap(lambda v, m=metric: color_for_metric(m, v), subset=[new_col])

    # Format columns with new names
    format_dict = {}
    for metric, orig_col in metric_to_col.items():
        new_col = column_name_map[orig_col]
        if metric in ["HME", "HME DP_2"]:
            format_dict[new_col] = "{:.0f}"
        elif metric == "Labour":
            format_dict[new_col] = "{:.1f}%"
        elif metric == "OSAT":
            format_dict[new_col] = "{:.0f}%"
    
    styled = styled.format(format_dict)

    return styled


def mask_value(value: str, keep: int = 2) -> str:
    """Mask a value for display."""
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    return f"{value[:keep]}{'*' * (len(value) - keep)}"


# Main App
st.title("Pardelta Dashboard")
st.caption("Real-time performance metrics across all stores")

# Sidebar
config = get_supabase_config()
with st.sidebar:
    st.header("Settings")

    # Connection status
    has_url = bool(config["url"] and config["key"])
    has_pg = bool(
        config["host"] and config["database"] and config["user"] and config["password"]
    )

    use_postgres = st.checkbox("Use PostgreSQL (faster)", value=has_pg)

    if has_url or has_pg:
        st.success("✓ Supabase configured")
    else:
        st.warning("⚠ Supabase not configured")

    with st.expander("Connection Details", expanded=False):
        st.write("**API Client:**", "Yes" if has_url else "No")
        st.write("**PostgreSQL:**", "Yes" if has_pg else "No")
        if has_pg:
            st.write("Host:", config["host"])
            st.write("Database:", config["database"])
            st.write("User:", mask_value(config["user"]))
            st.write("Port:", config["port"])

# Get date range for Performance Rankings (always Year to Date)
ranking_start_date, ranking_end_date = get_date_range("Year to Date")
st.sidebar.info(f"📅 Performance Rankings: {ranking_start_date.strftime('%Y-%m-%d')} to {ranking_end_date.strftime('%Y-%m-%d')}")

# Fetch data for Performance Rankings (Year to Date)
with st.spinner("Loading ranking data..."):
    ranking_hme_df = fetch_hme_data(ranking_start_date, ranking_end_date, use_postgres)
    ranking_labor_df = fetch_labor_data(ranking_start_date, ranking_end_date, use_postgres)
    ranking_medallia_df = fetch_medallia_data(ranking_start_date, ranking_end_date, use_postgres)

# Calculate ranking metrics
hme_counts, _ = calculate_hme_metrics(ranking_hme_df)
hme_dp2_counts, _ = calculate_hme_dp2_metrics(ranking_hme_df)
labor_counts, _ = calculate_labor_metrics(ranking_labor_df)
osat_counts, _ = calculate_osat_metrics(ranking_medallia_df)

# First Half - Ranking Tables
st.subheader("📊 Performance Rankings")
st.caption("Stores ranked by number of weeks in each performance category (Year to Date - Sunday to Saturday)")

ranking_cols = st.columns(4)
with ranking_cols[0]:
    st.markdown("**HME**")
    st.dataframe(build_ranking_table(hme_counts, "HME"), use_container_width=True, hide_index=True)
with ranking_cols[1]:
    st.markdown("**HME DP_2**")
    st.dataframe(build_ranking_table(hme_dp2_counts, "HME DP_2"), use_container_width=True, hide_index=True)
with ranking_cols[2]:
    st.markdown("**Labour**")
    st.dataframe(build_ranking_table(labor_counts, "Labour"), use_container_width=True, hide_index=True)
with ranking_cols[3]:
    st.markdown("**OSAT**")
    st.dataframe(build_ranking_table(osat_counts, "OSAT"), use_container_width=True, hide_index=True)

st.divider()

# Second Half - Performance Table with its own filter
st.subheader("📈 Store Performance Metrics")

# Filter for Store Performance Metrics
perf_period = st.selectbox(
    "Time Period for Performance Metrics",
    ["Week to Date", "Month to Date", "Year to Date"],
    index=0,
    key="perf_period"
)

perf_start_date, perf_end_date = get_date_range(perf_period)
st.caption(f"Average performance across all stores ({perf_start_date.strftime('%Y-%m-%d')} to {perf_end_date.strftime('%Y-%m-%d')})")

# Fetch data for Store Performance Metrics
with st.spinner("Loading performance data..."):
    perf_hme_df = fetch_hme_data(perf_start_date, perf_end_date, use_postgres)
    perf_labor_df = fetch_labor_data(perf_start_date, perf_end_date, use_postgres)
    perf_medallia_df = fetch_medallia_data(perf_start_date, perf_end_date, use_postgres)

# Calculate performance metrics
_, hme_avg = calculate_hme_metrics(perf_hme_df)
_, hme_dp2_avg = calculate_hme_dp2_metrics(perf_hme_df)
_, labor_avg = calculate_labor_metrics(perf_labor_df)
_, osat_avg = calculate_osat_metrics(perf_medallia_df)

styled_perf = build_performance_table(hme_avg, hme_dp2_avg, labor_avg, osat_avg)
st.dataframe(styled_perf, use_container_width=True, hide_index=True)

# Footer
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Performance Period", perf_period)
with col2:
    st.metric("HME Records (YTD)", len(ranking_hme_df))
with col3:
    st.metric("OSAT Responses (YTD)", len(ranking_medallia_df))
