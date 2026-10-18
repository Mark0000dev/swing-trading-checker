import pandas as pd
from datetime import datetime
import os

FILE_STRUCTURES = 'history_of_structures.csv'

if os.path.exists(FILE_STRUCTURES):
    history_of_structures_overall = pd.read_csv(FILE_STRUCTURES)
else:
    history_of_structures_overall = pd.DataFrame(
        columns=['Дата', 'Symbol', 'Структура', 'Свинг']
    )

list_of_structures = []


def status_of_structure(swings_df, symbol):
    structures_df = pd.read_csv(FILE_STRUCTURES) if os.path.exists(FILE_STRUCTURES) else history_of_structures_overall

    if len(swings_df) < 4:
        return None

    last_swing0 = swings_df.iloc[-1]['price']
    last_swing1 = swings_df.iloc[-2]['price']
    last_swing2 = swings_df.iloc[-3]['price']
    last_swing3 = swings_df.iloc[-4]['price']

    last_structures = structures_df.loc[
        structures_df['Symbol'] == symbol, 'Структура'
    ]

    if len(last_structures) == 0:
        last_structure = None
    else:
        last_structure = last_structures.iloc[-1]

    if last_swing0 > last_swing1 and last_swing2 > last_swing3:
        status = (
            'LONG'
            if last_structure in ['LONG', 'Начало LONG']
            else 'Начало LONG'
        )
    elif last_swing0 < last_swing1 and last_swing2 < last_swing3:
        status = (
            'SHORT'
            if last_structure in ['SHORT', 'Начало SHORT']
            else 'Начало SHORT'
        )
    else:
        status = 'Нет четкой структуры'

    list_of_structures.append([
        datetime.now(), symbol, status, last_swing0
    ])

    df_of_structures = pd.DataFrame(
        list_of_structures,
        columns=['Дата', 'Symbol', 'Структура', 'Свинг']
    )

    df_of_structures.to_csv(
        FILE_STRUCTURES,
        mode='a',
        header=not os.path.exists(FILE_STRUCTURES),
        index=False
    )