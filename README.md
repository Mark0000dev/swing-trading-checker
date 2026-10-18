# swing-trading-checker
This Python-based cryptocurrency market scanner that analyzes candlestick data to identify swing points, detect market structure, and monitor potential trend changes across multiple trading pairs.  The bot uses price action and swing structure analysis to identify bullish and bearish market conditions

It works only with BingX and gets data from this platform. Supports multiple cryptocurrency trading pairs, including BTC, ETH, and altcoins.

Logic:
📍 Identifies significant swing highs and swing lows using a ZigZag-based algorithm.
📍 Uses price movements and a configurable threshold to filter market fluctuations.
📍 Records swing points with their timestamps, prices, and types.

Logic market:
📌 Analyzes swing points to identify bullish and bearish market structures.
📌 Bullish structure: Higher Highs (HH) and Higher Lows (HL).
📌 Bearish structure: Lower Highs (LH) and Lower Lows (LL).
📌 Detects Break of Structure (BOS) when a candle closes beyond a significant structural level.
📌 Generates charts displaying price movements, swing points, and market structure.

The goal is to automate the analysis of cryptocurrency market structure, reduce manual chart inspection, and provide a consistent way to monitor swing formations and structural breakouts across multiple trading pairs.
This project is under active development. It focuses on technical analysis and market monitoring rather than automatic trade execution.
