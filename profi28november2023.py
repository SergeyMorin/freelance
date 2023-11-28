import requests
from bs4 import BeautifulSoup
import os
import pandas as pd


target_site = 'https://www.leomebel.ru'
link_list = list()
for i in range(1, 6):
    resp = requests.get(f'https://www.leomebel.ru/catalog/ARMADIOCOMBIKombinirovannye/?PAGEN_1={i}')
    soup = BeautifulSoup(resp.content, 'lxml')
    items = soup.find_all('div', class_='item_block js-notice-block grid-list__item grid-list-border-outer')
    [link_list.append(target_site + sh.find('a', class_='thumb').get('href')) for sh in items]

current_dir = os.getcwd()
result_list = list()
for el in range(len(link_list)):
    resp = requests.get(link_list[el])
    soup = BeautifulSoup(resp.content, 'lxml')

    article = soup.find('div', class_='article iblock').get_text().replace('Артикул:', '').strip()
    el_dict = {
        'name': soup.find('h1', id='pagetitle').get_text().strip(),
        'article': article,
        'color': soup.find('div', class_='name', string='Цвет').find_next_sibling().get_text().strip(),
        'weight': soup.find('div', class_='name', string='Вес, кг').find_next_sibling().get_text().strip(),
        'material': soup.find('div', class_='name', string='Материал').find_next_sibling().get_text().strip(),
        'size': soup.find('div', class_='name', string='Размеры (ВxШxГ)').find_next_sibling().get_text().strip(),
        'price': soup.find('span', class_='price_value').get_text().strip(),
        'description': soup.find('div', class_='detail_text').get_text().replace('Описание', '').strip()
    }
    result_list.append(el_dict)

    os.mkdir(os.path.join(os.getcwd(), article))
    images = soup.find('ul', class_='slides_block').find_all('li')
    for image in range(len(images)):
        format_img = images[image]['data-big_img'].split('.')[-1]
        img_src = requests.get(target_site + images[image]['data-big_img'])
        img_name = article + f'({image}).' + format_img
        img_path = os.path.join(article, img_name)
        with open(f'{img_path}', "wb") as f:
            f.write(img_src.content)

df = pd.DataFrame(result_list)
excel_file_path = os.path.join(current_dir, 'result.xlsx')
df.to_excel(excel_file_path, index=False)
