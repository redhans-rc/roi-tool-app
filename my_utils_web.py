import matplotlib.pyplot as plt


def parse_float(value, default=0.0):
    if value is None:
        return float(default)

    text = str(value).strip().replace(",", "")
    if not text:
        return float(default)

    try:
        return float(text)
    except (TypeError, ValueError):
        return float(default)


def format_int(value):
    return f"{int(round(value)):,}"


def format_currency(value):
    return f"${float(value):,.2f}"


def build_roi_figure(quarters, cumulative_roi, cumulative_benefit):
    fig, ax = plt.subplots(figsize=(6.2, 3.0), facecolor="#12212B")
    ax.set_facecolor("#12212B")

    bars = ax.bar(quarters, cumulative_roi, color="#0EA5E9")
    ax.set_xlabel("Quarter", color="white")
    ax.set_ylabel("Cumulative ROI (%)", color="white")
    ax.set_title("Cumulative Quarterly ROI", color="white")
    ax.axhline(y=100, linestyle="--", linewidth=1.4, color="#FDBA74")

    ax.tick_params(colors="white")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["bottom"].set_color("white")
    ax.spines["left"].set_color("white")

    for bar, benefit in zip(bars, cumulative_benefit):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1,
            f"${benefit:,.0f}",
            ha="center",
            va="bottom",
            color="white",
            fontsize=8,
        )

    fig.tight_layout()
    return fig


def build_revenue_rows(
    cr_entry,
    cr_total,
    m_vol,
    sms_price,
    sa_price,
    s_totalsucc,
    sa_totalsucc,
    s_totalcost,
    sa_totalcost,
    ux_rev_client,
):
    return [
        {
            "SCENARIO": "SMS",
            "CONVERSION LIFT": f"{int(cr_entry)}%",
            "AUTHENTICATION VOLUME": format_int(s_totalsucc * 12),
            "YEARLY COST": format_currency((m_vol * 12) * sms_price),
            "TCO": format_currency(0),
            "VOLUME LIFT": format_int(0),
        },
        {
            "SCENARIO": "SMS + SA (standard)",
            "CONVERSION LIFT": f"{int(cr_total)}%",
            "AUTHENTICATION VOLUME": format_int(sa_totalsucc * 12),
            "YEARLY COST": format_currency(sa_totalcost * 12),
            "TCO": format_currency((sa_totalcost * 12) - (s_totalcost * 12)),
            "VOLUME LIFT": format_int(
                (sa_totalsucc * 12 - s_totalsucc * 12) 
            ),
            "VOLUME - $ VALUE ": format_int(
                (sa_totalsucc * 12 - s_totalsucc * 12) * ux_rev_client
            ),
        },
        {
            "SCENARIO": "SMS + SA (Best)",
            "CONVERSION LIFT": "100%",
            "AUTHENTICATION VOLUME": format_int(m_vol * 12),
            "YEARLY COST": format_currency(m_vol * 12 * sa_price),
            "TCO": format_currency((m_vol * 12 * sa_price) - (s_totalcost * 12)),
            "VOLUME LIFT": format_int(
                (m_vol * 12 - s_totalsucc * 12) 
            ),
            "VOLUME - $ VALUE ": format_int(
                (m_vol * 12 - s_totalsucc * 12) * ux_rev_client
            ),
        },
    ]
    
def build_table_rows(
    cr_entry,
    cr_total,
    m_vol,
    sms_price,
    sa_price,
    s_totalsucc,
    sa_totalsucc,
    s_totalcost,
    sa_totalcost,
    ux_rev_client,
    ux_signup,
    drp_off,
    ux_cc_interaction,
    ux_cc_cost
):
    # total_uplift = max(0, (sa_totalsucc * 12) - (s_totalsucc * 12))
    total_uplift = max(0, (m_vol * 12))
    signup_ratio = ux_signup / 100
    drp_off_ratio = drp_off / 100
    ux_cc_interaction_ration = ux_cc_interaction / 100

    def capped(value):
        return min(total_uplift, max(0, value))

    rows = [
        {
            "SCENARIO": f"Signup {int(ux_signup)} %",
            "Current State - Settings Values": format_currency(capped(total_uplift * signup_ratio *ux_rev_client)),
            "Conservative (20 %)": format_currency(capped(total_uplift * (signup_ratio+0.1)*ux_rev_client )),
            "Likely (30 %)": format_currency(capped(total_uplift * (signup_ratio+0.2)*ux_rev_client)),
            "Aggressive (40 %)": format_currency(capped(total_uplift * (signup_ratio+0.3)*ux_rev_client)),
            # "Aggressive": format_currency(total_uplift),
        },
                {
            "SCENARIO": f"{int(drp_off)} % Drop off during Signups ",
            "Current State - Settings Values": f"{format_currency(total_uplift * signup_ratio *(drp_off_ratio)*ux_rev_client)}",
            "Conservative (20 %)": f"{format_currency(total_uplift *  signup_ratio*(0.1+drp_off_ratio)*ux_rev_client)}",
            "Likely (30 %)": f"{format_currency(total_uplift * signup_ratio*(drp_off_ratio+0.2)*ux_rev_client)}",
            "Aggressive (40 %)": f"{format_currency(total_uplift * signup_ratio*(drp_off_ratio+0.3)*ux_rev_client)}",
        },
                        {
            "SCENARIO": f"{int(ux_cc_interaction)} % Call Center Interactions ",
            "Current State - Settings Values": f"{format_currency(total_uplift * signup_ratio *ux_cc_interaction_ration*ux_cc_cost)}",
            "Conservative (20 %)": f"{format_currency(total_uplift * (signup_ratio)*(ux_cc_interaction_ration+0.01)*ux_cc_cost)}",
            "Likely (30 %)": f"{format_currency(total_uplift * (signup_ratio)*(ux_cc_interaction_ration+0.02)*ux_cc_cost)}",
            "Aggressive (40 %)": f"{format_currency(total_uplift * (signup_ratio)*(ux_cc_interaction_ration+0.03)*ux_cc_cost)}",
        },
        
    ]

    sum_columns = [
        "Current State - Settings Values",
        "Conservative (20 %)",
        "Likely (30 %)",
        "Aggressive (40 %)",
    ]

    def to_number(currency_text):
        return float(str(currency_text).replace("$", "").replace(",", ""))

    excluded_from_sum = {"Drop off during Signups"}
    rows_for_sum = [
        row
        for row in rows
        if not any(excluded_label in str(row.get("SCENARIO", "")) for excluded_label in excluded_from_sum)
    ]

    total_row = {"SCENARIO": "TOTAL"}
    for col in sum_columns:
        total_row[col] = format_currency(sum(to_number(row[col]) for row in rows_for_sum))

    rows.append(total_row)
    return rows
