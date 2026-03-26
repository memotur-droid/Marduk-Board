"""
Marduk Board — Binance vs DEX (Raydium/Orca) Arbitraj Monitörü
Public API, anahtar gerektirmez. 3 saniyede bir güncellenir.
"""

import requests
import time
import sys
from datetime import datetime
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.text import Text
from concurrent.futures import ThreadPoolExecutor, as_completed

# ── Solana token mint adresleri (Binance sembolü → mint) ──────────────
TOKEN_MINTS = {
    "SOL":   "So11111111111111111111111111111111111111112",
    "RAY":   "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "JUP":   "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "BONK":  "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WIF":   "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
    "RNDR":  "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof",
    "HNT":   "hntyVP6YFm1Hg25TN9WGLqM12b8TQmcknKrdu1oxWux",
    "PYTH":  "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
    "JTO":   "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
    "W":     "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmQ",
    "ORCA":  "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
    "MEW":   "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5",
    "POPCAT": "7GCihgDB8fe6LNa32gd7QhkpCKM5VLYqSfNg4LCnDRhW",
    "RENDER": "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof",
    "FIDA":  "EchesyfXePKdLtoiZSL8pBe8Myagyy8ZRqsACNCFGnvp",
    "MNDE":  "MNDEFzGvMt87ueuHvVU9VcTqsAP5b3fTGPsHuuPA5ey",
    "MSOL":  "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
    "BOME":  "ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82",
    "SAMO":  "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "GMT":   "7i5KKsX2weiTkry7jA4ZwSuXGhs5eJBEjY8vVxR4pfRx",
    "TRUMP": "HaP8r3ksG76PhQLTqR8FYBeNiQpejcFbQmiHbg787Ut9",
    "PENGU": "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv",
    "LAYER": "LAYER4xPpTCb3QL8S3Bh9AvMu5GnEipXEi4MKMZ1yMp",
    "IO":    "BZLbGTNCSFfoth2GYDtwr7e4imWzpR5jqcUuGEwr646K",
}

HEADERS = {"User-Agent": "MardukBoard/1.0"}
console = Console()


def fetch_binance_prices():
    """Binance'den tüm USDT paritelerini çek."""
    try:
        r = requests.get(
            "https://api.binance.com/api/v3/ticker/price",
            headers=HEADERS, timeout=5
        )
        r.raise_for_status()
        prices = {}
        for t in r.json():
            sym = t["symbol"]
            if sym.endswith("USDT"):
                base = sym[:-4]
                prices[base] = float(t["price"])
        return prices
    except Exception as e:
        return {}


def fetch_dexscreener_token(mint):
    """DexScreener'dan token bilgilerini çek (Raydium + Orca havuzları)."""
    try:
        r = requests.get(
            f"https://api.dexscreener.com/latest/dex/tokens/{mint}",
            headers=HEADERS, timeout=8
        )
        r.raise_for_status()
        data = r.json()
        pairs = data.get("pairs") or []

        best = None
        for p in pairs:
            dex = (p.get("dexId") or "").lower()
            if dex not in ("raydium", "orca"):
                continue
            quote = (p.get("quoteToken", {}).get("symbol") or "").upper()
            if quote not in ("USDC", "USDT", "SOL"):
                continue
            liq = float(p.get("liquidity", {}).get("usd") or 0)
            if best is None or liq > best["liquidity"]:
                best = {
                    "price": float(p.get("priceUsd") or 0),
                    "liquidity": liq,
                    "dex": dex.capitalize(),
                    "pair": f'{p.get("baseToken",{}).get("symbol","?")}/{quote}',
                }
        return best
    except Exception:
        return None


def fetch_all_dex(symbols_mints):
    """Paralel olarak tüm DEX verilerini çek."""
    results = {}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futures = {
            ex.submit(fetch_dexscreener_token, mint): sym
            for sym, mint in symbols_mints
        }
        for f in as_completed(futures):
            sym = futures[f]
            try:
                results[sym] = f.result()
            except Exception:
                results[sym] = None
    return results


def build_table(binance_prices, dex_data, cycle):
    """Terminal tablosunu oluştur."""
    table = Table(
        title=f"⚡ MARDUK BOARD — Binance vs DEX  │  {datetime.now().strftime('%H:%M:%S')}  │  döngü #{cycle}",
        show_lines=False,
        border_style="bright_blue",
        header_style="bold bright_white on dark_blue",
        title_style="bold bright_cyan",
    )

    table.add_column("Coin", style="bold white", min_width=7)
    table.add_column("DEX", style="dim", min_width=8)
    table.add_column("Binance $", justify="right", min_width=12)
    table.add_column("DEX $", justify="right", min_width=12)
    table.add_column("Fark $", justify="right", min_width=10)
    table.add_column("Fark %", justify="right", min_width=8)
    table.add_column("Likidite $", justify="right", min_width=12)
    table.add_column("Sinyal", justify="center", min_width=8)

    rows = []
    for sym, mint in TOKEN_MINTS.items():
        bp = binance_prices.get(sym)
        dd = dex_data.get(sym)
        if bp is None or dd is None:
            continue
        dp = dd["price"]
        if dp == 0 or bp == 0:
            continue
        diff = dp - bp
        pct = (diff / bp) * 100
        liq = dd["liquidity"]
        rows.append((sym, dd["dex"], bp, dp, diff, pct, liq))

    # Fark yüzdesine göre sırala (büyükten küçüğe, mutlak)
    rows.sort(key=lambda r: abs(r[5]), reverse=True)

    for sym, dex, bp, dp, diff, pct, liq in rows:
        hot = abs(pct) > 0.15 and liq > 50_000

        def fmt_price(v):
            if v >= 1:
                return f"{v:,.4f}"
            elif v >= 0.001:
                return f"{v:,.6f}"
            else:
                return f"{v:,.8f}"

        pct_color = "bright_green" if pct > 0 else "bright_red" if pct < 0 else "white"
        row_style = "bold bright_yellow on grey11" if hot else ""

        signal = ""
        if hot:
            if pct > 0:
                signal = "🔼 DEX>"
            else:
                signal = "🔽 CEX>"

        liq_str = f"${liq:,.0f}"

        table.add_row(
            sym,
            dex,
            fmt_price(bp),
            fmt_price(dp),
            f"{diff:+.6f}",
            Text(f"{pct:+.3f}%", style=pct_color),
            liq_str,
            Text(signal, style="bold bright_yellow") if hot else Text("—", style="dim"),
            style=row_style,
        )

    # Alt bilgi
    hot_count = sum(1 for r in rows if abs(r[5]) > 0.15 and r[6] > 50_000)
    table.caption = f"  {len(rows)} coin izleniyor  │  {hot_count} fırsat (>0.15% & >$50K liq)  │  Ctrl+C ile çık"
    table.caption_style = "dim"
    return table


def main():
    console.clear()
    console.print("[bold bright_cyan]Marduk Board başlatılıyor...[/]")

    cycle = 0
    symbols_mints = [(sym, mint) for sym, mint in TOKEN_MINTS.items()]

    with Live(console=console, refresh_per_second=1, screen=True) as live:
        while True:
            cycle += 1
            try:
                binance_prices = fetch_binance_prices()
                dex_data = fetch_all_dex(symbols_mints)
                table = build_table(binance_prices, dex_data, cycle)
                live.update(table)
            except KeyboardInterrupt:
                break
            except Exception as e:
                live.update(Text(f"Hata: {e}", style="bold red"))

            try:
                time.sleep(3)
            except KeyboardInterrupt:
                break

    console.print("\n[bold bright_cyan]Marduk Board kapatıldı.[/]")


if __name__ == "__main__":
    main()
