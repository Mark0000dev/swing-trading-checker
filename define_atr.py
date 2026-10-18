
import pandas as pd
import matplotlib.pyplot as plt
from last_structure import status_of_structure
import os
from datetime import datetime


def building_graph(candles_df, ranges, symbol,
                   significant_highs, significant_lows, df_swings):
    candles_df = candles_df.copy()
    df_swings = df_swings.copy()

    candles_df['TimeStamp'] = pd.to_datetime(candles_df['TimeStamp'])
    df_swings['time'] = pd.to_datetime(df_swings['time'])

    candles_df['Close'] = pd.to_numeric(candles_df['Close'])
    df_swings['price'] = pd.to_numeric(df_swings['price'])

    fig, ax = plt.subplots(figsize=(15, 7))

    ax.plot(
        candles_df['TimeStamp'],
        candles_df['Close'],
        color='black',
        linewidth=1,
        label='Close'
    )

    for start, end, trend in ranges:
        ax.axvspan(
            pd.to_datetime(start),
            pd.to_datetime(end),
            color='green' if trend == 'LONG' else 'red',
            alpha=0.12
        )

    highs = df_swings[df_swings['type'] == 'HIGH']
    ax.scatter(
        highs['time'], highs['price'],
        color='green', marker='^', s=65,
        label='Swing High', zorder=3
    )
    lows = df_swings[df_swings['type'] == 'LOW']
    ax.scatter(
        lows['time'], lows['price'],
        color='red', marker='v', s=65,
        label='Swing Low', zorder=3
    )
    if not df_swings.empty:
        last_swing = df_swings.iloc[-1]

        ax.scatter(
            last_swing['time'],
            last_swing['price'],
            color='orange',
            marker='*',
            s=200,
            label='Last swing',
            zorder=5
        )

    right_edge = candles_df['TimeStamp'].iloc[-1]

    for time, price, _ in significant_highs:
        ax.hlines(
            y=price,
            xmin=pd.to_datetime(time),
            xmax=right_edge,
            color='green',
            linestyle='--',
            linewidth=1.2,
            alpha=0.8
        )
    for time, price, _ in significant_lows:
        ax.hlines(
            y=price,
            xmin=pd.to_datetime(time),
            xmax=right_edge,
            color='red',
            linestyle='--',
            linewidth=1.2,
            alpha=0.8
        )

    ax.set_title(f'Swing-structure {symbol}')
    ax.set_xlabel('Time')
    ax.set_ylabel('Price Close')
    ax.grid(alpha=0.3)
    ax.legend()

    fig.autofmt_xdate()
    fig.tight_layout()

    now = datetime.now()

    folder = os.path.join(
        'graphs',
        now.strftime('%Y-%m-%d'),
        now.strftime('%H-00')
    )
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f'graph {symbol}.png')
    if os.path.exists(filename):
        filename = os.path.join(
            folder,
            f'graph {symbol} {now.strftime("%M-%S-%f")}.png'
        )
    fig.savefig(filename, dpi=300, bbox_inches='tight')

    status_of_structure(df_swings, symbol)

    plt.close(fig)


def define_percentage_change(df, symbol):
    df['% change'] = round(
        (df['Close'] - df['Close'].shift()) /
        df['Close'].shift() * 100, 3
    )
    df['Change'] = df['Close'] - df['Close'].shift()

    define_atr(df, symbol)


def define_atr(df, symbol):
    candles_df = df.copy()

    temp_df = pd.concat([
        df['High'] - df['Low'],
        abs(df['High'] - df['Close'].shift()),
        abs(df['Low'] - df['Close'].shift())
    ], axis=1).max(axis=1)

    df['ATR'] = temp_df.rolling(14).mean()

    def zigzag_highlow(df, atr_multiplier=1.5):
        swings = []

        if df.empty:
            return swings

        direction = 0

        first = df.iloc[0]
        high = low = first['Close']
        high_time = low_time = first['TimeStamp']
        for row in df.itertuples():
            close = row.Close
            threshold = row.ATR * atr_multiplier
            if direction == 0:
                if close >= high:
                    high = close
                    high_time = row.TimeStamp

                if close <= low:
                    low = close
                    low_time = row.TimeStamp

                if pd.isna(threshold):
                    continue

                if high - close >= threshold:
                    swings.append([high_time, high, 'HIGH'])
                    direction = -1
                    low = close
                    low_time = row.TimeStamp

                elif close - low >= threshold:
                    swings.append([low_time, low, 'LOW'])
                    direction = 1
                    high = close
                    high_time = row.TimeStamp

            elif direction == 1:
                if close >= high:
                    high = close
                    high_time = row.TimeStamp

                if not pd.isna(threshold) and high - close >= threshold:
                    swings.append([high_time, high, 'HIGH'])
                    direction = -1
                    low = close
                    low_time = row.TimeStamp

            else:
                if close <= low:
                    low = close
                    low_time = row.TimeStamp

                if not pd.isna(threshold) and close - low >= threshold:
                    swings.append([low_time, low, 'LOW'])
                    direction = 1
                    high = close
                    high_time = row.TimeStamp

        if direction == 1:
            swings.append([high_time, high, 'HIGH'])
        elif direction == -1:
            swings.append([low_time, low, 'LOW'])
        else:
            if high_time > low_time:
                swings.append([high_time, high, 'HIGH'])
            elif low_time > high_time:
                swings.append([low_time, low, 'LOW'])
        return swings

    zigzag_result = zigzag_highlow(df, 0.04)
    zigzag_df = pd.DataFrame(
        zigzag_result,
        columns=['time', 'price', 'type']
    )
    zigzag_df.to_csv(
        f'Swings of {symbol} at '
        f'{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.csv',
        index=False
    )

    define_structure(candles_df, zigzag_df, symbol)


def define_structure(candles_df, swings_df, symbol):
    candles_df = candles_df.copy()
    swings_df = swings_df.copy()

    candles_df['TimeStamp'] = pd.to_datetime(candles_df['TimeStamp'])
    swings_df['time'] = pd.to_datetime(swings_df['time'])

    candles_df = candles_df.sort_values('TimeStamp').reset_index(drop=True)
    swings_df = swings_df.sort_values('time').reset_index(drop=True)

    if candles_df.empty or swings_df.empty:
        return

    last_price = candles_df['Close'].iloc[-1]

    significant_highs = []
    significant_lows = []

    for _, high in swings_df[swings_df['type'] == 'HIGH'].iterrows():
        future = candles_df[candles_df['TimeStamp'] > high['time']]
        if not (future['Close'] > high['price']).any() and last_price < high['price']:
            significant_highs.append([high['time'], high['price'], 'HIGH'])
    for _, low in swings_df[swings_df['type'] == 'LOW'].iterrows():
        future = candles_df[candles_df['TimeStamp'] > low['time']]

        if not (future['Close'] < low['price']).any() and last_price > low['price']:
            significant_lows.append([low['time'], low['price'], 'LOW'])

    ranges = []
    trend = None
    trend_start = None

    for i in range(1, len(swings_df)):
        current = swings_df.iloc[i]
        seen = swings_df.iloc[:i + 1]
        previous_highs = seen[seen['type'] == 'HIGH'].tail(2)
        previous_lows = seen[seen['type'] == 'LOW'].tail(2)

        if len(previous_highs) < 2 or len(previous_lows) < 2:
            continue

        h1, h2 = previous_highs['price'].iloc[-2:]
        l1, l2 = previous_lows['price'].iloc[-2:]

        if h2 > h1 and l2 > l1:
            new_trend = 'LONG'
            level = h2
        elif h2 < h1 and l2 < l1:
            new_trend = 'SHORT'
            level = l2
        else:
            continue
        if new_trend == trend:
            continue
        if new_trend == 'LONG':
            candles_after = candles_df[
                (candles_df['TimeStamp'] > current['time']) &
                (candles_df['Close'] > level)
            ]
        else:
            candles_after = candles_df[
                (candles_df['TimeStamp'] > current['time']) &
                (candles_df['Close'] < level)
            ]

        if candles_after.empty:
            continue

        bos_time = candles_after['TimeStamp'].iloc[0]

        if trend is not None and trend_start is not None:
            ranges.append([trend_start, bos_time, trend])

        trend = new_trend
        trend_start = bos_time

    if trend is not None and trend_start is not None:
        ranges.append([
            trend_start,
            candles_df['TimeStamp'].iloc[-1],
            trend
        ])

    building_graph(
        candles_df,
        ranges,
        symbol,
        significant_highs,
        significant_lows,
        swings_df
    )
