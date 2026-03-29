"""
Marduk Board — Veri çekici (GitHub Actions ile çalışır)
Binance + DexScreener API → data.json
"""
import requests
import json
import time
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

TOKEN_MINTS = {
    "SOL":    "So11111111111111111111111111111111111111112",
    "RAY":    "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
    "JUP":    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
    "BONK":   "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
    "WIF":    "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
    "HNT":    "hntyVP6YFm1Hg25TN9WGLqM12b8TQmcknKrdu1oxWux",
    "PYTH":   "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
    "JTO":    "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
    "W":      "85VBFQZC9TZkfaptBWjvUw7YbZjy52A6mjtPGjstQAmQ",
    "ORCA":   "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
    "MEW":    "MEW1gQWJ3nEXg2qgERiKu7FAFj79PHvQVREQUzScPP5",
    "POPCAT": "7GCihgDB8fe6LNa32gd7QhkpCKM5VLYqSfNg4LCnDRhW",
    "FIDA":   "EchesyfXePKdLtoiZSL8pBe8Myagyy8ZRqsACNCFGnvp",
    "MSOL":   "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
    "BOME":   "ukHH6c7mMyiWCf1b9pnWe25TSpkDDt3H5pQZgZ74J82",
    "GMT":    "7i5KKsX2weiTkry7jA4ZwSuXGhs5eJBEjY8vVxR4pfRx",
    "TRUMP":  "HaP8r3ksG76PhQLTqR8FYBeNiQpejcFbQmiHbg787Ut9",
    "PENGU":  "2zMMhcVQEXDtdE6vsFS7S7D5oUodfJHE8vd1gnBouauv",
    "LAYER":  "LAYER4xPpTCb3QL8S3Bh9AvMu5GnEipXEi4MKMZ1yMp",
    "IO":     "BZLbGTNCSFfoth2GYDtwr7e4imWzpR5jqcUuGEwr646K",
    "RENDER": "rndrizKT3MK1iimdxRdWabcF7Zg7AR5T4nud4EkHBof",
    "SAMO":   "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "MNDE":   "MNDEFzGvMt87ueuHvVU9VcTqsAP5b3fTGPsHuuPA5ey",
    "MOBILE": "mb1eu7TzEc71KxDpsmsKoucSSuuoGLv1drys1oP2jh6",
    "KMNO":   "KMNo3nJsBXfcpJTVhZcXLW7RmTwTt4GVFE7suUBo9sS",
    "PRCL":   "4LLbsb5ReP3yEtYzmXewyGjcRJMx2MvBfENfsgW9EVcQ",
    "NOS":    "nosXBVoaCTtYdLvKY6Csb4AC8JCdQKKAaWYtx2ZMoo7",
    "DRIFT":  "DriFtupJYLTosbwoN8koMbEYSx54aFAVLddWsbksjwg7",
    "TNSR":   "TNSRxcUxoT9xBG3de7PiJyTDYu7kskLqcpddxnEJAS6",
    "HONEY":  "4vMsoUT2BWatFweudnQM1xedRLfJgJ7hsWhs4xE5STR8",
    "ZEUS":   "ZEUS1aR7aX8DFFJf5QjWj2ftDDdNTroMNGo8YoQm3Gp",
    "WEN":    "WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk",
    "SLERF":  "7BgBvyjrZX1YKz4oh9mjb8ZScatkkwb8DzFx7LoiVkM3",
    "MPLX":   "METAewgxyPbgwsseH8T16a39CQ5VyVxLpEn5pnCfBZS",
    "NYAN":   "NYANpAp9Cr7YarBNrby7Xx4xU6No6JKTBuohNA3yscP",
    "BOBA":   "bobaM3u8QmqZhY1HwAtnGze3bWWRPcBQaQEqwmAf8jP",
    "SC":     "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm",
    "GRASS":  "Grass7B4RdKfBCjTKgSqnXkqjwiGvQyFbuSCUJr3XXjs",
    "ME":     "MEFNBXixkEbait3xn9x0tMEMBXuKsNETEJsVPEZwJRT",
    "ACT":    "GJAFwWjJ3vnTsrQVabjBVK2TYB1YtRCQXRDfDgUnpump",
    "PNUT":   "2qEHjDLDLbuBgRYvsxhc5D6uDWAivNFZGan56P1tpump",
    "THE":    "4bCrajAPmJbCpWGsHM4eLguVNbpDJbCaHTm8oa8Hpump",
    "AIXBT":  "BFicBFmLHsGfGRQ48mCMGeZfR4SFQHGfMFEEMmnM3vaj",
}

HEADERS = {"User-Agent": "MardukBoard/1.0"}


def fetch_binance():
    r = requests.get("https://api.binance.us/api/v3/ticker/price", headers=HEADERS, timeout=10)
    r.raise_for_status()
    prices = {}
    for t in r.json():
        if t["symbol"].endswith("USDT"):
            prices[t["symbol"][:-4]] = float(t["price"])
    return prices


def fetch_dex(mint):
    try:
        r = requests.get(f"https://api.dexscreener.com/latest/dex/tokens/{mint}", headers=HEADERS, timeout=10)
        r.raise_for_status()
        pairs = r.json().get("pairs") or []
        best = None
        for p in pairs:
            dex = (p.get("dexId") or "").lower()
            if dex not in ("raydium", "orca"):
                continue
            quote = (p.get("quoteToken", {}).get("symbol") or "").upper()
            if quote not in ("USDC", "USDT"):
                continue
            liq = float(p.get("liquidity", {}).get("usd") or 0)
            if liq < 5000:
                continue
            price = float(p.get("priceUsd") or 0)
            if price <= 0:
                continue
            if not best or liq > best["liquidity"]:
                best = {"price": price, "liquidity": liq, "dex": dex.capitalize()}
        return best
    except Exception:
        return None


def main():
    print("Binance verileri çekiliyor...")
    binance = fetch_binance()

    print("DexScreener verileri çekiliyor...")
    dex_data = {}
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = {ex.submit(fetch_dex, mint): sym for sym, mint in TOKEN_MINTS.items()}
        for f in as_completed(futures):
            sym = futures[f]
            dex_data[sym] = f.result()

    rows = []
    for sym, mint in TOKEN_MINTS.items():
        bp = binance.get(sym)
        dd = dex_data.get(sym)
        if not bp or not dd or not dd["price"]:
            continue
        diff = dd["price"] - bp
        pct = (diff / bp) * 100
        if abs(pct) > 10:
            continue
        rows.append({
            "sym": sym,
            "dex": dd["dex"],
            "bp": bp,
            "dp": dd["price"],
            "diff": round(diff, 8),
            "pct": round(pct, 4),
            "liq": round(dd["liquidity"], 0),
        })

    rows.sort(key=lambda r: abs(r["pct"]), reverse=True)

    output = {
        "updated": datetime.now(timezone.utc).isoformat(),
        "count": len(rows),
        "rows": rows,
    }

    with open("data.json", "w") as f:
        json.dump(output, f, indent=2)

    print(f"data.json yazıldı — {len(rows)} coin")


if __name__ == "__main__":
    main()
