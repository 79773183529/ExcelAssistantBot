import datetime
import random
import string

import pandas as pd
from openpyxl import load_workbook


def get_list_ru():
    with open('Data/Main_files/list_ru.txt') as f:
        list_ru = f.read().split('\n')
    return list_ru


def change_language(message, list_ru):
    if str(message.from_user.id) not in list_ru:
        with open('Data/Main_files/list_ru.txt', 'a', encoding='utf-8') as f:
            print(message.from_user.id, file=f)
    else:
        with open('Data/Main_files/list_ru.txt', 'w+', encoding='utf-8') as f:
            cont = f.read().split('\n')
            cont_new = [x for x in cont if x and x != str(message.from_user.id)]
            print(*cont_new, sep='\n', file=f)


#  регистрация новах пользователей в файл
def start_registration(message):
    make_start_time = datetime.datetime.now()
    make_start_time += datetime.timedelta(hours=3)  # Перевод в Московское время
    make_start_time = make_start_time.strftime('%d.%m.%Y-%H:%M')
    with open('Data/Main_files/list_registration.txt', 'a', encoding='utf-8') as f:
        print(message.from_user.id, make_start_time, sep=';', file=f)


def get_list_topic(the_id=None, src='Data/Main_files/table_topics.txt'):
    with open(src, encoding='utf-8') as f:
        cont = f.read().split('\n')
        print('cont=  ', cont)
        cont = list(filter(lambda x: len(x.split(';')) == 4, cont))
        print('cont_f=  ', cont)
        if the_id:
            cont = list(filter(lambda x: str(x.split(';')[1]).strip() == str(the_id) and x.split(';')[3] == 'True',
                               cont))
            print('cont_if= ', cont)
        list_topic = [x.split(';')[0] for x in cont]
        print('list_topic=', list_topic)
    return list_topic


def name_to_src(lst, src='Data/Main_files/table_topics.txt'):
    with open(src, encoding='utf-8') as f:
        cont = f.read().split('\n')
        cont = list(filter(lambda x: len(x.split(';')) == 4, cont))
    return [x.split(';')[2].strip() for x in cont if x.split(';')[0] in lst]


# Удаляет файл
def delete_file(file_name):
    for src in ['Data/Main_files/table_topics.txt', 'Data/Main_files/table_patterns.txt']:  # добавил Патерн !!!!
        result = False
        with open(src, encoding='utf-8') as f:
            cont_new = []
            cont = f.read().split('\n')
            cont = list(filter(lambda x: len(x.split(';')) == 4, cont))
            for row in cont:
                lst = row.split(';')
                if file_name in lst[0]:
                    lst[3] = 'False'
                    result = True
                cont_new.append(';'.join(lst))
        if result:
            with open(src, 'w', encoding='utf-8') as f:
                print(*cont_new, sep='\n', file=f)
            break


def search_object_in_src(the_object, src):
    pass


#  Получае список файлов - возвращает список DataFrames
def get_list_df(list_src_topics):
    list_df = []
    for file in list_src_topics:
        print('file = ', file)
        for s in [';', ',', '|']:
            df = pd.read_csv(file, encoding='utf-8-sig', sep=s)
            if df.shape[1] > 1:
                list_df.append(df)
                break
        else:
            print('Количество строк не превышает 1')
    return list_df


def is_text_in_df(df, text, accuracy):
    list_row = []
    for i in range(df.shape[0]):
        for j in df.columns.values:
            value = df.at[i, j]
            value = str(value).strip()
            text = text.strip()
            if not accuracy and value.lower() == text.lower() or accuracy == 1 and text.lower() in value.lower():
                list_row.append(i)
    return list_row


def save_changes_pattern(list_src_patterns, the_list):
    src_pattern = list_src_patterns[0]
    wb = load_workbook(src_pattern)
    sheet = wb.active

    position = search_inside_file(sheet, '/date')[0]
    if position:
        data = get_date()
        super_writer_excel(sheet, data, position)

    lst = search_inside_file(sheet, '/number')
    position = lst[0]
    if position:
        cell_value = lst[1]
        data = get_number(src_pattern, cell_value)
        super_writer_excel(sheet, data, position)

    position = search_inside_file(sheet, '/text')[0]
    if position:
        super_writer_excel(sheet, the_list, position)

    src_pattern_spliting = src_pattern.split('.')
    src_new = '.'.join(src_pattern_spliting[:-1]) + '_' + str(random.randrange(1000000)) + '.' + src_pattern_spliting[-1]
    wb.save(src_new)

    return src_new


# Ищит внутри заведома открытого файла
def search_inside_file(sheet, the_object):
    the_position = False
    cell_value = False
    for row in range(1, 500):
        for column in string.ascii_lowercase.upper():
            position = column + str(row)
            if the_object in str(sheet[position].value):
                cell_value = str(sheet[position].value)
                the_position = position
                break
        if the_position:
            break
    return [the_position, cell_value]


def super_writer_excel(sheet, data, position):
    if not isinstance(data, list):
        sheet[position].value = data
    else:
        row, column = int(position[1:]), position[0]
        alphas = string.ascii_lowercase.upper()
        alphas = alphas[alphas.index(column):]
        i = 0
        for stroka in data:
            for kolonka in stroka:
                the_position = column + str(row)
                sheet[the_position].value = kolonka
                i += 1
                column = alphas[i]
            row += 1
            i = 0
            column = alphas[i]


def get_date():
    td_ = datetime.date.today()
    td = td_.strftime('%d.%m.%Y')  # Разворачивает представление даты на европейский лад
    return td


def get_number(src_pattern, cell_value):
    src = 'Data/Main_files/list_numbers.txt'
    with open(src, encoding='utf-8') as f:
        cont = f.read().split('\n')
        cont = list(filter(lambda x: len(x.split(';')) == 2, cont))
        cont = list(filter(lambda x: x.split(';')[0].strip() == src_pattern, cont))
        if cont:
            last_number = cont[-1]
            the_index = -len(last_number)
            last_number = last_number.split(';')[1].strip()
            for i in range(-1, -len(last_number), -1):
                if not last_number[i].isdigit():
                    the_index = i + 1
                    break
            else:
                number = str(int(last_number) + 1)

            if the_index == 0:
                number = last_number + '01'
            elif the_index:
                number = last_number[:the_index] + str(int(last_number[the_index:]) + 1)

        else:
            if '=' in cell_value and cell_value[-1] != '=':
                number = cell_value.split('=')[-1].strip()
            else:
                number = random.randrange(11, 1000)
    with open(src, 'a', encoding='utf-8') as f:
        print(src_pattern, number, sep=';', file=f)
    return number

