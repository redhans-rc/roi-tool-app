import os
from dataclasses import dataclass

import streamlit as st
# ***** health codde ***
from streamlit.web.server.server import Server
import tornado.web

def setup_custom_health_check():
    class CustomHealthHandler(tornado.web.RequestHandler):
        def get(self):
            self.write("OK")
            self.set_status(200)
            self.write("OK")

    try:
        server = Server.get_current()
        if server:
            server._app.add_handlers(r".*", [
                (r"/_/health", CustomHealthHandler)
            ])
    except Exception:
        pass
# Initialize the endpoint
setup_custom_health_check()

from my_utils_web import (
    build_revenue_rows,
    build_roi_figure,
    format_currency,
    parse_float,
    build_table_rows
)


@dataclass
class Defaults:
    cr_var: float = 82
    cr_in: float = 8
    sa_sr: float = 75
    sa_cov: float = 75
    drp_off_reduc: float = 91
    ux_cc_interaction: float = 1
    ux_signup: float = 10
    baseline: float = 1_000_000
    ux_cc_cost: float = 1
    ux_rev_client: float = 1
    drp_off: float = 22
    sms_price: float = 0.02985
    sa_price: float = 0.0326
    m_vol: float = 300_000
    y_tco: float = 200_000
    


DEFAULTS = Defaults()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ******************************LOGIN *********************
def show_login():
    st.title("Login")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Sign in")

    if submit:
        # Replace with st.secrets in production
        if username == st.secrets["APP_USER"] and password == st.secrets["APP_PASS"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid credentials")
# ******************************LOGIN *********************            
def calculate(values):
    cr_entry = parse_float(values.get("cr_entry"), DEFAULTS.cr_var)
    m_vol = parse_float(values.get("m_vol"), DEFAULTS.m_vol)
    y_tco = parse_float(values.get("y_tco"), DEFAULTS.y_tco)
    ux_signup = parse_float(values.get("ux_signup"), DEFAULTS.ux_signup)
    ux_cc_interaction = parse_float(values.get("ux_cc_interaction"), DEFAULTS.ux_cc_interaction)
    ux_cc_cost = parse_float(values.get("ux_cc_cost"), DEFAULTS.ux_cc_cost)
    drp_off = parse_float(values.get("drp_off"), DEFAULTS.drp_off)
    ux_rev_client = parse_float(values.get("ux_rev_client"), DEFAULTS.ux_rev_client)
    sms_price = parse_float(values.get("sms_price"), DEFAULTS.sms_price)
    sa_price = parse_float(values.get("sa_price"), DEFAULTS.sa_price)
    ux_signup_baseline = parse_float(values.get("ux_signup_baseline"), DEFAULTS.baseline)

    sa_cr = DEFAULTS.cr_var + DEFAULTS.cr_in
    cr_total = cr_entry + DEFAULTS.cr_in
    s_totalsucc = round(m_vol * (cr_entry / 100))
    s_totalcost = round(m_vol * sms_price)
    s_aut_price = round(s_totalcost / s_totalsucc, 5) if s_totalsucc else 0

    sa_totalsucc = round(m_vol * cr_total / 100)
    sa_totalcost = round(
        (m_vol * sa_price * DEFAULTS.sa_sr / 100 * DEFAULTS.sa_cov / 100)
        + ((m_vol - m_vol * DEFAULTS.sa_sr / 100 * DEFAULTS.sa_cov / 100) * sms_price)
    )
    sa_aut_price = round(sa_totalcost / sa_totalsucc, 5) if sa_totalsucc else 0

    y_volume = s_totalsucc * 12
    s_ytransaccions = round(y_volume / (DEFAULTS.cr_var / 100)) if DEFAULTS.cr_var else 0
    sa_ytransaccions = round(y_volume / (sa_cr / 100)) if sa_cr else 0

    s_ycost = round(s_ytransaccions * sms_price)
    sa_ycost = round(
        (sa_ytransaccions * sa_price * DEFAULTS.sa_sr / 100 * DEFAULTS.sa_cov / 100)
        + ((sa_ytransaccions - sa_ytransaccions * DEFAULTS.sa_sr / 100 * DEFAULTS.sa_cov / 100) * sms_price)
    )
    calculated_tco = sa_ycost - s_ycost

    ux_opex_cost = round(
        (s_ytransaccions - sa_ytransaccions)
        * (ux_cc_interaction / 100)
        * DEFAULTS.ux_cc_cost
    )
    # ux_cli_lost = (
    #     round(drp_off / 100, 2)
    #     * round(DEFAULTS.drp_off_reduc / 100, 2)  ----> Tthis was removed in the calculation of ux_cli_lost for testing
    #     * round(ux_signup / 100, 2)
    #     * y_volume
    # )
    ux_cli_lost = (
        round(drp_off / 100, 2)
        * round(ux_signup / 100, 2)
        * y_volume
        )
    ux_rev_lost = ux_cli_lost * ux_rev_client
    ux_total = round(ux_opex_cost + ux_rev_lost)

    base_investment = round(y_tco + abs(calculated_tco))

    
    revenue_rows = build_revenue_rows(
        cr_entry=cr_entry,
        cr_total=cr_total,
        m_vol=m_vol,
        sms_price=sms_price,
        sa_price=sa_price,
        s_totalsucc=s_totalsucc,
        sa_totalsucc=sa_totalsucc,
        s_totalcost=s_totalcost,
        sa_totalcost=sa_totalcost,
        ux_rev_client=ux_rev_client,
    )
    
    table_rows = build_table_rows(
        cr_entry=cr_entry,
        cr_total=cr_total,
        m_vol=m_vol,
        sms_price=sms_price,
        sa_price=sa_price,
        s_totalsucc=s_totalsucc,
        sa_totalsucc=sa_totalsucc,
        s_totalcost=s_totalcost,
        sa_totalcost=sa_totalcost,
        ux_rev_client=ux_rev_client,
        ux_signup = ux_signup,
        drp_off= drp_off,
        ux_cc_interaction = ux_cc_interaction,
        ux_cc_cost = ux_cc_cost,
        
    )

    sum_row = next((row for row in table_rows if row.get("SCENARIO") == "SUM"), None)
    if sum_row:
        annual_benefit = parse_float(
            str(sum_row.get("Current State - Settings", "0")).replace("$", "").replace(",", ""),
            0.0,
        )
    else:
        annual_benefit = float(ux_total)

    profit_quarter = annual_benefit / 4
    quarters = ["Q1-1", "Q2-1", "Q3-1", "Q4-1", "Q1-2", "Q2-2", "Q3-2", "Q4-2"]
    cumulative_benefit = [profit_quarter * i for i in range(1, 9)]
    cumulative_roi = [((b / base_investment) * 100 if base_investment else 0) for b in cumulative_benefit]
    figure = build_roi_figure(quarters, cumulative_roi, cumulative_benefit)
   
    return {
        "inputs": {
            "cr_entry": cr_entry,
            "m_vol": m_vol,
            "y_tco": y_tco,
            "ux_signup": ux_signup,
            "ux_rev_client": ux_rev_client,
            "sms_price": sms_price,
            "sa_price": sa_price,
            "ux_signup_baseline": ux_signup_baseline,
        },
        "metrics": {
            "cr_total": cr_total,
            "s_totalsucc": s_totalsucc,
            "s_totalcost": s_totalcost,
            "s_aut_price": s_aut_price,
            "sa_totalsucc": sa_totalsucc,
            "sa_totalcost": sa_totalcost,
            "sa_aut_price": sa_aut_price,
            "s_ycost": s_ycost,
            "sa_ycost": sa_ycost,
            "calculated_tco": abs(calculated_tco),
            "ux_opex_cost": ux_opex_cost,
            "ux_cli_lost": ux_cli_lost,
            "ux_rev_lost": ux_rev_lost,
            "vol_year": m_vol*12,
        },
        "figure": figure,
        "revenue_rows": revenue_rows,
        "table_rows" : table_rows
    }


def input_sidebar():
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False

    st.sidebar.title("Inputs")

    cr_entry = st.sidebar.text_input("Conversion Rate %", f"{DEFAULTS.cr_var}")
    m_vol = st.sidebar.text_input("Monthly Volumes", f"{DEFAULTS.m_vol:,.0f}")
    y_tco = st.sidebar.text_input("Investment", f"{DEFAULTS.y_tco:,.0f}")

    ux_signup = DEFAULTS.ux_signup
    ux_cc_interaction = DEFAULTS.ux_cc_interaction
    ux_cc_cost = DEFAULTS.ux_cc_cost
    drp_off = DEFAULTS.drp_off
    ux_rev_client = DEFAULTS.ux_rev_client
    sms_price = DEFAULTS.sms_price
    sa_price = DEFAULTS.sa_price
    ux_signup_baseline = DEFAULTS.baseline

    if st.sidebar.button("Settings"):
        st.session_state.show_settings = not st.session_state.show_settings

    execute = st.sidebar.button("Execute")
    # execute = st.form_submit_button("Execute")


    if st.session_state.show_settings:
        st.sidebar.caption("Advanced settings")
        ux_signup = parse_float(st.sidebar.text_input("% Signups", f"{DEFAULTS.ux_signup}"), DEFAULTS.ux_signup)
        ux_cc_interaction = parse_float(
            st.sidebar.text_input("CC Interaction %", f"{DEFAULTS.ux_cc_interaction}"),
            DEFAULTS.ux_cc_interaction,
        )
        ux_cc_cost = parse_float(
            st.sidebar.text_input("CC Interaction Cost", f"{DEFAULTS.ux_cc_cost}"),
            DEFAULTS.ux_cc_cost,
        )
        drp_off = parse_float(st.sidebar.text_input("Drop off %", f"{DEFAULTS.drp_off}"), DEFAULTS.drp_off)
        ux_rev_client = parse_float(
            st.sidebar.text_input("Average Revenue Per Client", f"{DEFAULTS.ux_rev_client}"),
            DEFAULTS.ux_rev_client,
        )
        sms_price = parse_float(st.sidebar.text_input("SMS Default Price", f"{DEFAULTS.sms_price}"), DEFAULTS.sms_price)
        sa_price = parse_float(st.sidebar.text_input("SA Default Price", f"{DEFAULTS.sa_price}"), DEFAULTS.sa_price)
        ux_signup_baseline = parse_float(
            st.sidebar.text_input("Baseline Signups (IF AVAILABLE)", f"{DEFAULTS.baseline:,.0f}"),
            DEFAULTS.baseline,
        )
        

    values = {
        "cr_entry": cr_entry,
        "m_vol": m_vol,
        "y_tco": y_tco,
        "ux_signup": ux_signup,
        "ux_cc_interaction": ux_cc_interaction,
        "ux_cc_cost": ux_cc_cost,
        "drp_off": drp_off,
        "ux_rev_client": ux_rev_client,
        "sms_price": sms_price,
        "sa_price": sa_price,
        "ux_signup_baseline": ux_signup_baseline,
    }
    return values, execute


def main():
    
    
    st.set_page_config(page_title="ROI Tool Kit", layout="wide")
    st.title("ROI Analysis")
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        show_login()
        st.stop()

    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()
    
    values, execute = input_sidebar()

    if "last_values" not in st.session_state:
        st.session_state.last_values = values

    if execute:
        st.session_state.last_values = values

    result = calculate(st.session_state.last_values)
    i = result["inputs"]
    m = result["metrics"]
   
    st.markdown(
    """
    <style>
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] > div,
    div[data-testid="stMetricLabel"] p {
        font-size: 18px !important;
        line-height: 1.2 !important;
    }
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] > div,
    div[data-testid="stMetricValue"] p {
        font-size: 42px !important;
        line-height: 1.1 !important;
    }
    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] > div,
    div[data-testid="stMetricDelta"] p {
        font-size: 16px !important;
    }
    div[data-testid="stDataFrame"] div[role="gridcell"] {
        font-size: 18px !important;
    }
    div[data-testid="stDataFrame"] div[role="columnheader"] {
        font-size: 19px !important;
        font-weight: 700 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
    k1, k2, k3 = st.columns(3)
    k1.metric("SMS SUCCESS/M", 
        f"{m['s_totalsucc']:,}",
        f"Covertion Rate: {i['cr_entry']}%",
        delta_color='off')
    k2.metric("SA SUCCESS/M",      
        f"{m['sa_totalsucc']:,}",
        f"Conversion Rate: {m['cr_total']}%")
    k3.metric("VOLUME PER YEAR", f"{m['vol_year']:,.2f}".rstrip("0").rstrip("."),
        f"FULL CONVERTION RATE: 100 %")

    image_col, chart_col = st.columns([1, 2])
    image_path = os.path.join(BASE_DIR, "assets", "slide.png")
    if os.path.exists(image_path):
        with image_col:
            st.image(image_path, use_container_width=True)
    st.markdown(
        "<p style='text-align: left; font-size: 22px; font-weight: bold;'>ROI reference</p>",
        unsafe_allow_html=True
    )
    with chart_col:
        st.pyplot(result["figure"], width=810)
    st.write("")
    st.write("")
    st.write("")
    st.markdown(
        "<h3 style='text-align: center;font-weight: bold'>Revenue Lift Per Year</h3>",
        unsafe_allow_html=True
    )
    st.dataframe(result["revenue_rows"], hide_index=True, use_container_width=True)
    st.dataframe(result["table_rows"], hide_index=True, use_container_width=True)
# *********************************SUMMARY FOR TESTING ***********
    
    
    
    
    
    # st.markdown(
    #     "<h3 style='text-align: center;'>Summary - IGNORE FOR NOW</h3>",
    # unsafe_allow_html=True
    # )
    
    # st.write(
    #     f"SMS ONLY {i['cr_entry']}% CR | Total Success: {m['s_totalsucc']:,} | "
    #     f"Cost: {format_currency(m['s_totalcost'])} | Price/Auth: {m['s_aut_price']}"
    # )
    # st.write(
    #     f"Silent Auth + SMS {m['cr_total']}% CR | Total Success: {m['sa_totalsucc']:,} | "
    #     f"Cost: {format_currency(m['sa_totalcost'])} | Price/Auth: {m['sa_aut_price']}"
    # )
    # st.write(
    #     f"Yearly SMS Cost: {format_currency(m['s_ycost'])} | "
    #     f"Yearly SMS + SA Cost: {format_currency(m['sa_ycost'])}"
    # )
    # st.write(f"Calculated TCO: {format_currency(m['calculated_tco'])}")
    # st.write(
    #     f"UX Impact -> Op Cost: {format_currency(m['ux_opex_cost'])} | "
    #     f"Clients Lost: {int(m['ux_cli_lost']):,} | Revenue Lost: {format_currency(m['ux_rev_lost'])}"
    # )

if __name__ == "__main__":
    main()
