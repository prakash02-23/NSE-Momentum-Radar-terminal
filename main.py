import streamlit as st

        metrics = calculate_metrics(df)

        metrics["stock"] = stock
        metrics["sector"] = SECTOR_MAP.get(stock, "Other")

        momentum_data.append(metrics)

        if chart_stock_data is None:
            chart_stock_data = df
            chart_symbol = stock

# =====================================================
# MOMENTUM TABLE
# =====================================================

if len(momentum_data) > 0:

    momentum_df = pd.DataFrame(momentum_data)

    momentum_df = momentum_df.sort_values(
        by="score",
        ascending=False
    ).reset_index(drop=True)

    momentum_df.index = momentum_df.index + 1

    momentum_df.rename_axis("Rank", inplace=True)

    def score_color(val):
        if val >= 80:
            return 'background-color: #00aa66; color: white'
        elif val >= 60:
            return 'background-color: #2ecc71; color: white'
        elif val >= 40:
            return 'background-color: #f1c40f; color: black'
        else:
            return 'background-color: #e74c3c; color: white'

    st.subheader("⚡ Live Momentum Ladder")

    styled_df = momentum_df.style.map(
        score_color,
        subset=["score"]
    )

    st.dataframe(
        styled_df,
        use_container_width=True,
        height=420
    )

    # =================================================
    # SECTOR HEATMAP
    # =================================================

    sector_strength = momentum_df.groupby(
        "sector"
    )["score"].mean().reset_index
