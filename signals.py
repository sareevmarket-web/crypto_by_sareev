import requests
import pandas as pd
import pandas_ta as ta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import feedparser

# Анализатор настроения новостей
analyzer = SentimentIntensityAnalyzer()

# Какие монеты анализируем
SYMBOLS = ["bitcoin", "ethereum"]

# Получаем текущую цену
def get_current_price(coin_id):
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd"
    try:
        return requests.get(url, timeout=10).json()[coin_id]["usd"]
    except:
        return None

# Получаем исторические данные за последние 14 дней (почасовые)
def get_history(coin_id):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": "14", "interval": "hourly"}
    try:
        data = requests.get(url, params=params, timeout=15).json()
        df = pd.DataFrame(data["prices"], columns=["timestamp", "price"])
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
        df.set_index("timestamp", inplace=True)
        return df
    except:
        return pd.DataFrame()

# Получаем средний сентимент новостей
def get_news_sentiment():
    try:
        feed = feedparser.parse("https://www.coindesk.com/arc/outboundfeeds/rss/")
        texts = []
        for entry in feed.entries[:20]:
            texts.append(entry.title + " " + getattr(entry, "summary", ""))
        scores = [analyzer.polarity_scores(t)["compound"] for t in texts]
        return sum(scores) / len(scores) if scores else 0.0
    except:
        return 0.0

# Основная функция — ищет сигналы
def find_signals():
    sentiment = get_news_sentiment()
    new_signals = []

    for coin in SYMBOLS:
        price = get_current_price(coin)
        if not price:
            continue

        df = get_history(coin)
        if df.empty or len(df) < 50:
            continue

        # Считаем индикаторы
        df["rsi"] = ta.rsi(df["price"], length=14)
        macd = ta.macd(df["price"])
        df = pd.concat([df, macd], axis=1)

        rsi = df["rsi"].iloc[-1]
        macd_line = df["MACD_12_26_9"].iloc[-1]
        signal_line = df["MACDs_12_26_9"].iloc[-1]
        macd_line_prev = df["MACD_12_26_9"].iloc[-2]
        signal_line_prev = df["MACDs_12_26_9"].iloc[-2]

        # Условия для LONG
        long_condition = (
            rsi < 38 and
            macd_line > signal_line and macd_line_prev <= signal_line_prev and
            sentiment > 0.12
        )

        # Условия для SHORT
        short_condition = (
            rsi > 62 and
            macd_line < signal_line and macd_line_prev >= signal_line_prev and
            sentiment < -0.12
        )

        if long_condition or short_condition:
            direction = "LONG" if long_condition else "SHORT"
            leverage = 10 if abs(sentiment) > 0.35 else 5

            # SL и TP простые, но рабочие
            if direction == "LONG":
                sl = price * 0.97   # −3%
                tp = price * 1.09   # +9%
            else:
                sl = price * 1.03   # +3%
                tp = price * 0.91   # −9%

            new_signals.append({
                "symbol": coin.upper(),
                "direction": direction,
                "price": round(price, 2),
                "sl": round(sl, 2),
                "tp": round(tp, 2),
                "leverage": leverage,
                "sentiment": round(sentiment, 3)
            })

    return new_signals