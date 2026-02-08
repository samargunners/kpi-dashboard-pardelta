import pandas as pd
import streamlit as st


st.set_page_config(page_title="Pardelta Dashboard", layout="wide")

st.title("Pardelta Dashboard")
st.caption("Skeleton UI with mock data. Replace mock data with Supabase queries.")


def get_supabase_config():
    supabase = st.secrets.get("supabase", {})
    return {
        "url": st.secrets.get("supabase_url", ""),
        "key": st.secrets.get("supabase_anon_key", ""),
        "host": supabase.get("host", ""),
        "database": supabase.get("database", ""),
        "dbname": supabase.get("dbname", ""),
        "user": supabase.get("user", ""),
        "password": supabase.get("password", ""),
        "port": supabase.get("port", ""),
    }


def mask_value(value, keep=2):
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    return f"{value[:keep]}{'*' * (len(value) - keep)}"


def color_for_metric(metric, value):
    green = "#c6efce"
    yellow = "#ffeb9c"
    red = "#ffc7ce"

    if metric in ("HME", "HME DP_2"):
        if metric == "HME":
            if value <= 150:
                return f"background-color: {green}"
            if value <= 160:
                return f"background-color: {yellow}"
            return f"background-color: {red}"
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


def build_ranking_table(stores, counts):
    rows = []
    for store in stores:
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
    df = df.sort_values(["Red", "pc_number"], ascending=[False, True])
    return df[["Store", "Green", "Yellow", "Red"]]


stores = [
    {"pc_number": 101, "store_name": "Pardelta North"},
    {"pc_number": 102, "store_name": "Pardelta East"},
    {"pc_number": 103, "store_name": "Pardelta South"},
    {"pc_number": 104, "store_name": "Pardelta West"},
    {"pc_number": 105, "store_name": "Pardelta Central"},
    {"pc_number": 106, "store_name": "Pardelta River"},
    {"pc_number": 107, "store_name": "Pardelta Lake"},
    {"pc_number": 108, "store_name": "Pardelta Hill"},
]

config = get_supabase_config()
with st.sidebar:
    st.header("Filters")
    period = st.selectbox(
        "Time Period",
        ["Week to Date", "Month to Date", "Year to Date"],
        index=0,
    )
    has_url = bool(config["url"] and config["key"])
    has_pg = bool(
        config["host"] and config["database"] and config["user"] and config["password"]
    )
    if has_url or has_pg:
        st.success("Supabase configured")
    else:
        st.warning("Supabase not configured")

    with st.expander("Supabase secret status", expanded=False):
        st.write("URL key configured:", "Yes" if has_url else "No")
        st.write("Postgres configured:", "Yes" if has_pg else "No")
        if has_pg:
            st.write("Host:", config["host"])
            st.write("Database:", config["database"] or config["dbname"])
            st.write("User:", mask_value(config["user"]))
            st.write("Port:", config["port"])
            st.write("Password:", "set")

st.subheader("Ranking Tables")

hme_counts = {
    101: {"Green": 4, "Yellow": 2, "Red": 1},
    102: {"Green": 3, "Yellow": 2, "Red": 2},
    103: {"Green": 2, "Yellow": 2, "Red": 3},
    104: {"Green": 5, "Yellow": 1, "Red": 1},
    105: {"Green": 3, "Yellow": 3, "Red": 1},
    106: {"Green": 2, "Yellow": 3, "Red": 2},
    107: {"Green": 4, "Yellow": 1, "Red": 2},
    108: {"Green": 1, "Yellow": 3, "Red": 3},
}

hme_dp2_counts = {
    101: {"Green": 3, "Yellow": 3, "Red": 1},
    102: {"Green": 2, "Yellow": 3, "Red": 2},
    103: {"Green": 3, "Yellow": 2, "Red": 2},
    104: {"Green": 4, "Yellow": 2, "Red": 1},
    105: {"Green": 2, "Yellow": 4, "Red": 1},
    106: {"Green": 1, "Yellow": 3, "Red": 3},
    107: {"Green": 5, "Yellow": 1, "Red": 1},
    108: {"Green": 2, "Yellow": 2, "Red": 3},
}

labour_counts = {
    101: {"Green": 5, "Yellow": 1, "Red": 1},
    102: {"Green": 3, "Yellow": 2, "Red": 2},
    103: {"Green": 2, "Yellow": 3, "Red": 2},
    104: {"Green": 4, "Yellow": 2, "Red": 1},
    105: {"Green": 1, "Yellow": 3, "Red": 3},
    106: {"Green": 3, "Yellow": 3, "Red": 1},
    107: {"Green": 4, "Yellow": 1, "Red": 2},
    108: {"Green": 2, "Yellow": 2, "Red": 3},
}

osat_counts = {
    101: {"Green": 4, "Yellow": 2, "Red": 1},
    102: {"Green": 3, "Yellow": 3, "Red": 1},
    103: {"Green": 2, "Yellow": 2, "Red": 3},
    104: {"Green": 5, "Yellow": 1, "Red": 1},
    105: {"Green": 3, "Yellow": 2, "Red": 2},
    106: {"Green": 2, "Yellow": 3, "Red": 2},
    107: {"Green": 4, "Yellow": 1, "Red": 2},
    108: {"Green": 1, "Yellow": 3, "Red": 3},
}

ranking_cols = st.columns(4)
with ranking_cols[0]:
    st.markdown("**HME**")
    st.dataframe(build_ranking_table(stores, hme_counts), use_container_width=True)
with ranking_cols[1]:
    st.markdown("**HME DP_2**")
    st.dataframe(build_ranking_table(stores, hme_dp2_counts), use_container_width=True)
with ranking_cols[2]:
    st.markdown("**Labour**")
    st.dataframe(build_ranking_table(stores, labour_counts), use_container_width=True)
with ranking_cols[3]:
    st.markdown("**OSAT**")
    st.dataframe(build_ranking_table(stores, osat_counts), use_container_width=True)

st.subheader("Performance Table")

perf_rows = []
for store in stores:
    perf_rows.append(
        {
            "pc_number": store["pc_number"],
            "Store": store["store_name"],
            "HME": 148 + (store["pc_number"] % 7) * 3,
            "HME DP_2": 138 + (store["pc_number"] % 6) * 3,
            "Labour": 18 + (store["pc_number"] % 6),
            "OSAT": 84 + (store["pc_number"] % 10),
        }
    )

perf_df = pd.DataFrame(perf_rows).sort_values("pc_number")
perf_df = perf_df[["Store", "HME", "HME DP_2", "Labour", "OSAT"]]

styled = perf_df.style
for metric in ["HME", "HME DP_2", "Labour", "OSAT"]:
    styled = styled.applymap(lambda v, m=metric: color_for_metric(m, v), subset=[metric])

styled = styled.format(
    {
        "HME": "{:.0f}",
        "HME DP_2": "{:.0f}",
        "Labour": "{:.1f}%",
        "OSAT": "{:.0f}%",
    }
)

st.dataframe(styled, use_container_width=True)

st.caption(f"Selected period: {period}")
