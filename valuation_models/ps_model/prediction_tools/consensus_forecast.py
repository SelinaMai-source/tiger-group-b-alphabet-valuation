import requests
from bs4 import BeautifulSoup

def forecast_revenue_consensus(ticker="GOOG") -> float:
    """
    获取分析师共识预测营收（2025E）
    如果无法抓取，则 fallback 使用默认模拟值
    """
    try:
        # Yahoo Finance 分析页面
        url = f"https://finance.yahoo.com/quote/{ticker}/analysis"
        headers = {
            "User-Agent": "Mozilla/5.0"
        }
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        # 找表格
        tables = soup.find_all("table")
        for table in tables:
            if "Revenue Estimate" in table.text:
                rows = table.find_all("tr")
                for row in rows:
                    if "Current Year" in row.text:
                        cells = row.find_all("td")
                        if len(cells) >= 2:
                            value = cells[1].text.replace(",", "").replace("B", "")
                            forecast = float(value) * 1e9
                            return forecast

        print("⚠️ 未能成功抓取，返回默认值")
        return 405_000_000_000  # fallback

    except Exception as e:
        print(f"❌ 共识营收抓取失败：{e}")
        return 0  # fallback 默认值：$405B