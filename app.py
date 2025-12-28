import io
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="SOD Dashboard", layout="wide")

# --- Curated artifact paths (bundled with this repo) ---
PR018_NPY = "data/pr018/compensated_trajectory.npy"

@st.cache_data
def load_pr018_xy(npy_path: str) -> pd.DataFrame:
    arr = np.load(npy_path, allow_pickle=False)  # numeric array only
    if arr.ndim != 2 or arr.shape[1] != 2:
        raise ValueError(f"Expected shape (N,2) for x,y; got {arr.shape}")
    df = pd.DataFrame(arr, columns=["x", "y"])
    df.insert(0, "t", np.arange(len(df)))  # frame index as time for display
    return df

# --- Sidebar Navigation ---
page = st.sidebar.radio("Navigate", ["SOD Dashboard", "Curated Case Studies"])

# --- Persistent Guardrails Panel (always visible) ---
with st.container(border=True):
    st.subheader("What This Dashboard Does — and Does Not Do")

    st.markdown("""
**Purpose**  
This dashboard presents descriptive motion structure derived using the Structured Orb Dynamics (SOD) framework.
It visualizes kinematic states, segmentation, and geometric time series for illustrative and exploratory purposes.

**Scope**  
The dashboard does not perform object identification, intent inference, or origin attribution. No probabilistic or evidentiary claims are made.

**Methodological Guardrails**  
Curated case studies (e.g., PR-018) are shown with locked policies and fixed inputs. Parameters are not user-adjustable in these cases to prevent outcome forcing and to preserve methodological integrity.

**Source of Truth**  
The authoritative definitions, decision rules, and assumptions of SOD are documented in the accompanying manuscript and versioned code repository. This interface is a presentation layer only.
""")

st.divider()

# =============================================================================
# Page: SOD Dashboard
# =============================================================================
if page == "SOD Dashboard":
    # --- Layout: Inputs (left) / Visuals (right) ---
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.header("Inputs")
        mode = st.selectbox(
            "Analysis Mode",
            ["Sandbox (Exploratory)", "Curated Case Study (Read-Only)"]
        )
        is_curated = (mode == "Curated Case Study (Read-Only)")

        uploaded = st.file_uploader(
            "Upload trajectory data (CSV)",
            type=["csv"],
            disabled=is_curated
        )
        st.caption("Expected columns: t, x, y (header row required).")

        analyze_clicked = st.button(
            "Analyze",
            type="primary",
            use_container_width=True,
            disabled=is_curated
        )

        if is_curated:
            st.warning(
                "Curated mode is read-only: uploads and analysis are disabled to prevent outcome forcing.",
                icon="🔒"
            )
        else:
            st.info("UI-only skeleton: Analyze does not run the engine yet.", icon="ℹ️")

    with right:
        st.header("Visualizations")

        # Placeholder data
        t = np.linspace(0, 10, 200)
        x = np.cos(t) + 0.05*np.random.randn(len(t))
        y = np.sin(t) + 0.05*np.random.randn(len(t))
        speed = np.abs(np.gradient(x, t)) + np.abs(np.gradient(y, t))
        curvature = np.abs(np.gradient(np.gradient(y, t), t))  # placeholder, not SOD curvature

        traj_df = pd.DataFrame({"t": t, "x": x, "y": y})
        speed_df = pd.DataFrame({"t": t, "speed": speed})
        curv_df = pd.DataFrame({"t": t, "curvature": curvature})

        st.subheader("Trajectory View (placeholder)")
        st.plotly_chart(px.line(traj_df, x="x", y="y"), use_container_width=True)

        c1, c2 = st.columns(2, gap="large")
        with c1:
            st.subheader("Speed vs Time (placeholder)")
            st.plotly_chart(px.line(speed_df, x="t", y="speed"), use_container_width=True)
        with c2:
            st.subheader("Curvature vs Time (placeholder)")
            st.plotly_chart(px.line(curv_df, x="t", y="curvature"), use_container_width=True)

        st.subheader("State Timeline / Segmentation (placeholder)")
        st.caption("Reserved for SOD state labels & segments once the engine API is connected.")

    st.divider()

    # --- Exports (placeholders) ---
    st.header("Exports")
    engine_label = st.text_input("Engine Version / Policy ID", value="(placeholder)")

    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button("Download Results (CSV)", data="t,x,y\n", file_name="results_placeholder.csv")
    with col_b:
        st.download_button("Download Run Summary (JSON)", data='{"note":"placeholder"}', file_name="summary_placeholder.json")

    st.caption("Exports are placeholders until the engine connection is implemented.")

# =============================================================================
# Page: Curated Case Studies
# =============================================================================
else:
    st.title("Curated Case Studies (Read-Only)")
    st.caption("These examples are shown under locked policies and fixed inputs. No parameter tuning is available.")

    with st.container(border=True):
        st.subheader("PR-018 — Curated, Read-Only Example")
        st.markdown("""
**Status:** Curated case study (read-only)  
**Policy:** Locked (not user-adjustable)  
**Inputs:** Fixed trajectory (pre-extracted; no raw video)  
**Purpose:** Demonstrate segmentation + descriptive motion structure under partial observation.
""")

    st.divider()

      # --- PR-018 artifact (locked) ---
    st.subheader("Trajectory View (PR-018 — artifact)")

    try:
        traj_df = load_pr018_xy(PR018_NPY)
    except Exception as e:
        st.error(f"PR-018 artifact missing or unreadable: {PR018_NPY}\n\n{e}")
        st.stop()

    st.plotly_chart(px.line(traj_df, x="x", y="y"), use_container_width=True)

    st.divider()
    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.subheader("Speed vs Time (display proxy)")
        dx = np.gradient(traj_df["x"].to_numpy())
        dy = np.gradient(traj_df["y"].to_numpy())
        speed_proxy = np.sqrt(dx*dx + dy*dy)
        speed_df = pd.DataFrame({"t": traj_df["t"], "speed": speed_proxy})
        st.plotly_chart(px.line(speed_df, x="t", y="speed"), use_container_width=True)
        st.caption("Proxy only (derived from plotted x,y). Not an engine output.")

    with c2:
        st.subheader("Curvature vs Time (display proxy)")
        ddx = np.gradient(np.gradient(traj_df["x"].to_numpy()))
        ddy = np.gradient(np.gradient(traj_df["y"].to_numpy()))
        curvature_proxy = np.sqrt(ddx*ddx + ddy*ddy)
        curv_df = pd.DataFrame({"t": traj_df["t"], "curvature": curvature_proxy})
        st.plotly_chart(px.line(curv_df, x="t", y="curvature"), use_container_width=True)
        st.caption("Proxy only. True SOD curvature will come from engine exports (locked).")

    st.subheader("State Timeline / Segmentation (placeholder)")
    st.caption("Reserved for SOD state labels once engine exports are wired in. Curated mode remains locked.")
    
