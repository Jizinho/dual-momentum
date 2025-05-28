def get_1y_performance(ticker_symbol):
    today = datetime.today().date()
    one_year_ago = today - timedelta(days=365)

    try:
        data = yf.download(
            ticker_symbol,
            start=(one_year_ago - timedelta(days=30)).strftime('%Y-%m-%d'),
            end=(today + timedelta(days=1)).strftime('%Y-%m-%d'),
            progress=False
        )

        if data.empty or "Close" not in data:
            return None

        close_prices = data["Close"].dropna()
        close_prices.index = pd.to_datetime(close_prices.index).date

        # Prendre les dates les plus proches disponibles
        available_dates = sorted(close_prices.index)

        start_date = next((d for d in available_dates if d >= one_year_ago), None)
        end_date = next((d for d in reversed(available_dates) if d <= today), None)

        if not start_date or not end_date:
            return None

        start_price = close_prices.get(start_date)
        end_price = close_prices.get(end_date)

        if start_price is None or end_price is None:
            return None

        performance = ((end_price - start_price) / start_price) * 100
        return round(performance, 2)
    except Exception as e:
        st.error(f"Erreur pour {ticker_symbol} : {str(e)}")
        return None
