# Marduk Board

Binance vs DEX (Raydium / Orca) gerçek zamanlı arbitraj monitörü.

## Özellikler

- Binance USDT paritelerini Solana DEX'leri (Raydium, Orca) ile karşılaştırır
- 3 saniyede bir güncellenen terminal tablosu
- Fark > %0.15 ve likidite > $50K olan fırsatları vurgular
- API anahtarı gerektirmez, tamamen public API kullanır

## Kurulum

```bash
pip install rich requests
```

## Kullanım

```bash
python marduk.py
```

Çıkmak için `Ctrl+C` basın.

## Veri Kaynakları

- **Binance**: Public ticker API
- **DEX**: DexScreener API (Raydium + Orca havuzları)
