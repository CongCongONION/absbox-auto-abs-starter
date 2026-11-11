"""
Figures from the actual engine outputs (../outputs/*.csv).

    python src/make_figures.py

Writes both SVG (for GitHub) and PNG (for reports/slides) to ../figures/:
  fig1_pool_balance.svg/png         pool balance by scenario
  fig2_tranche_amortization.svg/png A/B/E outstanding balance, base scenario
  fig3_stress_comparison.svg/png    pool cumulative net loss vs equity loss
"""

import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
FIG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "figures")
os.makedirs(FIG, exist_ok=True)
SCEN = ["base", "optimistic", "stress"]


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, name + ".svg"))
    fig.savefig(os.path.join(FIG, name + ".png"), dpi=150)
    plt.close(fig)
    print("wrote", name)


def main():
    # Fig 1: pool balance by scenario
    fig, ax = plt.subplots(figsize=(7, 4))
    for s in SCEN:
        pool = pd.read_csv(os.path.join(BASE, f"pool_flow_{s}.csv"), parse_dates=["Date"])
        pool = pool.drop_duplicates(subset="Date").sort_values("Date")
        ax.plot(pool["Date"], pool["Balance"] / 1e6, label=s)
    ax.set_ylabel("Pool balance ($mm)")
    ax.set_title("Fig 1. Loan pool amortization by scenario")
    ax.legend()
    save(fig, "fig1_pool_balance")

    # Fig 2: tranche balances, base scenario
    fig, ax = plt.subplots(figsize=(7, 4))
    for tr in ["A", "B", "E"]:
        flow = pd.read_csv(os.path.join(BASE, f"bond_{tr}_flow_base.csv"), parse_dates=["date"])
        ax.plot(flow["date"], flow["balance"] / 1e6, label=f"Class {tr}")
    ax.set_ylabel("Outstanding balance ($mm)")
    ax.set_title("Fig 2. Tranche amortization — sequential pay (base scenario)")
    ax.legend()
    save(fig, "fig2_tranche_amortization")

    # Fig 3: pool cumulative net loss vs equity principal loss, by scenario
    summary = pd.read_csv(os.path.join(BASE, "scenario_summary.csv"))
    pool_loss = {}
    for s in SCEN:
        pool = pd.read_csv(os.path.join(BASE, f"pool_flow_{s}.csv"))
        pool_loss[s] = float(pool["CumLoss"].iloc[-1]) / 1e6
    e_loss = (summary[(summary.tranche == "E")].set_index("scenario")
              ["principal_loss"] / 1e6)
    x = range(len(SCEN))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar([i - 0.2 for i in x], [pool_loss[s] for s in SCEN], width=0.4,
           label="Pool cumulative net loss")
    ax.bar([i + 0.2 for i in x], [e_loss[s] for s in SCEN], width=0.4,
           label="Equity (E) principal loss")
    ax.set_xticks(list(x))
    ax.set_xticklabels(SCEN)
    ax.set_ylabel("$mm")
    ax.set_title("Fig 3. Stress comparison — losses stop at the equity tranche")
    ax.legend()
    save(fig, "fig3_stress_comparison")


if __name__ == "__main__":
    main()
