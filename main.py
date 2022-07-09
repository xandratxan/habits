from datetime import datetime

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

index_order_list = ['Sueño', 'Comida', 'Higiene', 'Deporte', 'Hogar', 'Tareas', 'Hobbies', 'Vicios']
color_list_1 = ['tab:red', 'orangered', 'orange', 'gold', 'green', 'lightskyblue', 'tab:blue', 'darkblue']
color_list_2 = ['tab:red'] * 3 + ['orangered'] * 3 + ['orange'] * 5 + ['gold'] * 3 + ['green'] * 3 + \
               ['lightskyblue'] * 4 + ['tab:blue'] * 4 + ['darkblue'] * 8
group_weights = [2, 2, 1.5, 1.5, 1.3, 1.3, 1, -2]


def read_register_spreadsheet(sheet_url):
    # Read register spreadsheet from Google sheet (Permitir acceso a cualquiera con enlace)
    sheet_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
    register = pd.read_csv(sheet_url)
    return register


def replace_dataframe_group(register):
    # Group register by groups, get group dataframe and invert values of day columns
    group = register.groupby('Grupo').get_group('Vicios').replace({'Sí': 'No', 'No': 'Sí'})
    # Drop original group from register
    register = raw_data.drop(register.groupby('Grupo').get_group('Vicios').index)
    # Concatenate register and modified group
    register = pd.concat([register, group], axis=0)
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


def plot_daily_task_register(register):
    # Plot daily task register
    t_register = register.set_index('Tarea', drop=True)
    t_register = t_register.transpose()
    t_register = t_register.drop(labels=['Grupo', 'Pregunta'])
    a = np.array([[np.array(i, dtype=np.uint8) for i in j] for j in t_register.transpose().values], dtype=np.uint8)
    tasks = register['Tarea']
    days = register.select_dtypes(include=np.number).columns

    fig = plt.figure()
    plt.ylabel(f'Registro diario hábitos')
    plt.imshow(a, cmap='gray_r')
    plt.xticks(ticks=range(0, len(days)), labels=list(days))
    plt.yticks(ticks=range(0, len(tasks)), labels=list(tasks))
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.xlim(-0.5, len(days) - 0.5)
    plt.ylim(len(tasks) - 0.5, -0.5)
    plt.hlines(y=np.arange(0, len(tasks) - 1) + 0.5, xmin=-0.5, xmax=len(days), color="gray", linewidth=1)
    plt.vlines(x=np.arange(0, len(days) - 1) + 0.5, ymin=-0.5, ymax=len(tasks), color="gray", linewidth=1)

    plt.show()
    return fig


def plot_frequency_histogram_tasks(frequency, days):
    # Frequency histogram for tasks
    plot = frequency.plot(kind='bar', zorder=3, yticks=range(0, 101, 10), color=color_list_2)
    plt.ylabel('Hábitos diarios (% días realizados)')
    plt.title(f'Días: {days}')
    plt.grid(axis='y', zorder=0)
    plt.tight_layout()

    plt.show()
    fig = plot.get_figure()
    return fig


def plot_frequency_histogram_groups(register, frequency, days):
    # Frequency histogram for task groups
    group_frequency = register[['Grupo', 'Tarea']]
    group_frequency['Frecuencia'] = frequency.values
    group_frequency = group_frequency.groupby('Grupo')
    group_frequency = group_frequency.mean()
    group_frequency = group_frequency.reindex(index_order_list)

    plot = group_frequency.plot(kind='bar', legend=False, zorder=3, yticks=range(0, 101, 10))
    plt.ylabel('Hábitos diarios (% días realizados)')
    plt.title(f'Días: {days}')
    plt.grid(axis='y', zorder=0)
    plt.tight_layout()

    plt.show()
    fig = plot.get_figure()
    return fig


def plot_completed_task_percentage(register, groups_norm, groups):
    # Percentage of group task completed in terms of time
    t_groups_norm = groups_norm.transpose()
    t_groups_per = t_groups_norm * 100
    a = np.array([[np.array(i, dtype=np.uint8) for i in j] for j in t_groups_per.transpose().values], dtype=np.uint8)
    days = register.select_dtypes(include=np.number).columns

    fig = plt.figure()
    plt.imshow(a, cmap='RdYlGn')
    plt.title(f'Porcentage de habitos realizados en cada grupo')
    plt.colorbar()
    plt.xticks(ticks=range(0, len(days)), labels=list(days))
    plt.yticks(ticks=range(0, len(index_order_list)), labels=list(index_order_list))
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.xlim(-0.5, len(days) - 0.5)
    plt.ylim(len(groups) - 0.5, -0.5)
    plt.hlines(y=np.arange(0, len(index_order_list) - 1) + 0.5, xmin=-0.5, xmax=len(days), color="gray", linewidth=1)
    plt.vlines(x=np.arange(0, len(days) - 1) + 0.5, ymin=-0.5, ymax=len(index_order_list), color="gray", linewidth=1)

    plt.show()
    return fig


def plot_daily_points(groups_norm):
    # Daily points by groups
    weights = pd.Series(data=group_weights, index=index_order_list, name='Pesos')
    weights = weights * 100 / (weights.sum() + 2)
    groups_weighted = groups_norm.multiply(weights, axis=0)
    t_groups_weighted = groups_weighted.transpose()
    print(t_groups_weighted['Vicios'].min())

    plot = t_groups_weighted.plot(kind='bar', stacked=True, color=color_list_1, zorder=3, yticks=range(-20, 101, 10))
    plt.ylabel('Puntos diarios obtenidos')
    plt.legend(loc=(0, 1.05), ncol=4)
    plt.grid(axis='y', zorder=0)
    plt.ylim(-20, 101)
    plt.tight_layout()

    plt.show()
    fig = plot.get_figure()
    return fig


def pdf_report(file_path, fig1, fig2, fig3, fig4, fig5):
    # Save figures to pdf
    pdffile = PdfPages(file_path)
    pdffile.savefig(fig1)
    pdffile.savefig(fig2)
    pdffile.savefig(fig3)
    pdffile.savefig(fig4)
    pdffile.savefig(fig5)
    pdffile.close()


if __name__ == '__main__':
    # Sample data
    # url = 'https://docs.google.com/spreadsheets/d/1oQNtGS4UCbiHvHIOjpUrm3MTqUJzlHmwIcK0wqP1IrQ/edit#gid=0'
    # day = datetime(2022, 7, 15)  # Sample register
    # path = '/home/txan/Descargas/habitos_modelo.pdf'

    # Actual data
    url = 'https://docs.google.com/spreadsheets/d/1X5BtfmzyTD_zXmcdnXxK85hmbVBn0spicDqbwev3WYI/edit#gid=0'
    day = datetime.today()
    path = '/home/txan/Descargas/habitos.pdf'

    raw_data = read_register_spreadsheet(url)
    data = clean_register(raw_data, day)
    frequency_tasks, time_days = task_frequency(data)
    groups_points, register_groups = normalized_points(data)

    plot1 = plot_daily_task_register(data)
    plot2 = plot_frequency_histogram_tasks(frequency_tasks, time_days)
    plot3 = plot_frequency_histogram_groups(data, frequency_tasks, time_days)
    plot4 = plot_completed_task_percentage(data, groups_points, register_groups)
    plot5 = plot_daily_points(groups_points)

    pdf_report(path, plot1, plot2, plot3, plot4, plot5)
