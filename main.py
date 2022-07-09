from datetime import datetime

import numpy as np
import pandas as pd

index_order_list = ['Sueño', 'Comida', 'Higiene', 'Deporte', 'Hogar', 'Tareas', 'Hobbies', 'Recompensas', 'Vicios']


def read_register_spreadsheet(sheet_url):
    # Read register spreadsheet from Google sheet (Permitir acceso a cualquiera con enlace)
    sheet_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    register = pd.read_csv(sheet_url)
    return register


def clean_register(register, date):
    # Select columns up to date
    today = date.strftime('%d/%m/%y').replace('0', '')
    register = register.loc[:, :today]
    # Fill nan with zero
    register = register.fillna(0)
    # Replace string values for numbers
    register = register.replace({'Sí': 1, 'No': 0, 'NaN': 0})
    return register


def task_frequency(register):
    frequency = register.set_index('Tarea', drop=True)
    frequency = frequency.sum(axis=1)
    days = len(register.select_dtypes(include=np.number).columns)
    frequency = frequency / days * 100
    return frequency, days


def normalized_points(register):
    groups = register.groupby('Grupo')
    groups_sum = groups.sum()
    groups_sum = groups_sum.reindex(index_order_list)
    groups_size = groups.size()
    groups_size = groups_size.reindex(index_order_list)
    groups_norm = groups_sum.divide(groups_size, axis=0)
    return groups_norm, groups


if __name__ == '__main__':
    # Sample data
    # url = 'https://docs.google.com/spreadsheets/d/1oQNtGS4UCbiHvHIOjpUrm3MTqUJzlHmwIcK0wqP1IrQ/edit#gid=0'
    # day = datetime(2022, 7, 11)  # Sample register
    # path = '/home/txan/Descargas/habitos_modelo.pdf'

    # Actual data
    url = 'https://docs.google.com/spreadsheets/d/1X5BtfmzyTD_zXmcdnXxK85hmbVBn0spicDqbwev3WYI/edit#gid=0'
    day = datetime.today()
    path = '/home/txan/Descargas/habitos.pdf'

    data = read_register_spreadsheet(url)
    data = clean_register(data, day)
    frequency_tasks, time_days = task_frequency(data)
    groups_points, register_groups = normalized_points(data)
