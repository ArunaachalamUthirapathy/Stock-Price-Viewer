import streamlit as st
import yfinance as yf
import plotly.graph_objs as go
from datetime import date

# App title
st.title("📈 Advanced Stock Price Viewer")

# Sidebar inputs
st.sidebar.header("Enter Stock Details")

ticker = st.sidebar.text_input("Stock Symbol (e.g. AAPL, TSLA, INFY.NS)", value='AAPL')
start_date = st.sidebar.date_input("Start Date", value=date(2023, 1, 1))
end_date = st.sidebar.date_input("End Date", value=date.today())

# Moving averages
show_ma = st.sidebar.checkbox("Show Moving Averages")
ma1 = st.sidebar.number_input("MA Window 1", min_value=1, value=20)
ma2 = st.sidebar.number_input("MA Window 2", min_value=1, value=50)

# Bollinger Bands
show_bollinger = st.sidebar.checkbox("Show Bollinger Bands")

# Volume chart
show_volume = st.sidebar.checkbox("Show Volume Chart")

# Theme toggle
theme = st.sidebar.radio("Chart Theme", options=["Light", "Dark"])

# Button to fetch data
if st.sidebar.button("Show Stock Data"):
    if ticker:
        try:
            # Fetch data
            data = yf.download(ticker, start=start_date, end=end_date)

            if not data.empty:
                st.success(f"Showing stock price for **{ticker.upper()}** from {start_date} to {end_date}")

                # Add MAs
                if show_ma:
                    data[f"MA{ma1}"] = data['Close'].rolling(window=ma1).mean()
                    data[f"MA{ma2}"] = data['Close'].rolling(window=ma2).mean()

                # Add Bollinger Bands
                if show_bollinger:
                    sma = data['Close'].rolling(window=20).mean()
                    std = data['Close'].rolling(window=20).std()
                    data['Upper Band'] = sma + (std * 2)
                    data['Lower Band'] = sma - (std * 2)

                # Raw data
                st.subheader("📄 Raw Data")
                st.dataframe(data)

                # Main Chart
                st.subheader("📈 Price Chart")
                layout_bg = "#FFFFFF" if theme == "Light" else "#111111"
                font_color = "#000000" if theme == "Light" else "#FFFFFF"

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=data.index, y=data['Close'], name='Close', line=dict(color='blue')))
                if show_ma:
                    fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{ma1}"], name=f"MA{ma1}", line=dict(color='orange')))
                    fig.add_trace(go.Scatter(x=data.index, y=data[f"MA{ma2}"], name=f"MA{ma2}", line=dict(color='green')))
                if show_bollinger:
                    fig.add_trace(go.Scatter(x=data.index, y=data['Upper Band'], name='Upper Band', line=dict(color='purple', dash='dot')))
                    fig.add_trace(go.Scatter(x=data.index, y=data['Lower Band'], name='Lower Band', line=dict(color='purple', dash='dot')))

                fig.update_layout(title=f"{ticker.upper()} Price Chart",
                                  xaxis_title='Date', yaxis_title='Price (USD)',
                                  plot_bgcolor=layout_bg, paper_bgcolor=layout_bg,
                                  font=dict(color=font_color),
                                  xaxis_rangeslider_visible=True)
                st.plotly_chart(fig)

                # Volume Chart
                if show_volume:
                    st.subheader("📉 Volume Chart")
                    vol_fig = go.Figure()
                    vol_fig.add_trace(go.Bar(x=data.index, y=data['Volume'], name='Volume', marker_color='gray'))
                    vol_fig.update_layout(title=f"{ticker.upper()} Volume",
                                          xaxis_title='Date', yaxis_title='Volume',
                                          plot_bgcolor=layout_bg, paper_bgcolor=layout_bg,
                                          font=dict(color=font_color))
                    st.plotly_chart(vol_fig)

                # Download CSV
                st.subheader("⬇️ Download Data")
                csv = data.to_csv().encode('utf-8')
                st.download_button("Download CSV", csv, file_name=f"{ticker}_data.csv", mime='text/csv')

            else:
                st.warning("No data found for the given inputs.")
        except Exception as e:
            st.error(f"Error fetching data: {e}")
    else:
        st.warning("Please enter a stock symbol.")
