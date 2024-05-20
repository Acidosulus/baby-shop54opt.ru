import aiohttp
import asyncio
from bs4 import BeautifulSoup
import tempfile
import rich
from my_library import append_if_not_exists, clear_spaces, Price, prepare_str, prepare_for_csv_non_list

async def fetch_html(url, session):
	async with session.get(url) as response:
		return await response.text()


def save_temp_file(data):
	with tempfile.NamedTemporaryFile(delete=False, mode='w', encoding='utf-8', suffix='.html') as temp_file:
		temp_file.write(data)


def get_list_of_goods_from_source(source):
	result = []
	table = BeautifulSoup(source, features='html5lib').find('article')
	carts = table.find_all('div',{'class':'product-item inline'})
	for cart in carts:
		append_if_not_exists(cart.find('a').get('href'), result)
	return result


async def load_data_by_good_from_link(link:str, session):
	html = await fetch_html(link, session)
	soup = BeautifulSoup(html, features='html5lib')
	result = {}

	result['link'] = link

	result['title'] = soup.find('h1').text
	
	cost = soup.find('span',{'class':'sale-price'})
	if cost:
		cost = cost.find('span',{'class':'product-price-data'}).get('data-cost')
	else:
		cost = soup.find('span',{'class':'product-price-data'}).get('data-cost')
	result['cost'] = cost

	images_container = soup.find('div', {'class':'avatar-wrap image'})
	links = images_container.find_all('a')
	result['pictures']=[]
	for ilink in links:
		append_if_not_exists(ilink.get('href').replace('//','https://'), result['pictures'])

	result['descriprion'] = clear_spaces(soup.find('div',{'class':'ui tab segment active'}).text.replace('\n', ' ')).strip()

	return result

async def get_link_on_catalog_pages(catalog_url:str):
	all_pages = []
	page_number =1
	html, html_last = '',''
	async with aiohttp.ClientSession() as session:
		while True:
			print(page_number)
			next_page_url = f"{catalog_url}?page={page_number}"
			html_last = html
			html = await fetch_html(next_page_url, session)
			if str(BeautifulSoup(html, features='html5lib').find('article')) != str(BeautifulSoup(html_last, features='html5lib').find('article')):
				all_pages.append(next_page_url)
				get_list_of_goods_from_source(html)
				page_number += 1
			else:
				break
	return all_pages


async def load_data_by_good_from_link(link:str, session, semaphore):
	async with semaphore:
		html = await fetch_html(link, session)
		soup = BeautifulSoup(html, features='html5lib')
		result = {}

		result['link'] = link

		result['title'] = soup.find('h1').text
		
		cost = soup.find('span',{'class':'sale-price'})
		if cost:
			cost = cost.find('span',{'class':'product-price-data'}).get('data-cost')
		else:
			cost = soup.find('span',{'class':'product-price-data'}).get('data-cost')
		result['cost'] = cost

		images_container = soup.find('div', {'class':'avatar-wrap image'})
		links = images_container.find_all('a')
		result['pictures']=[]
		for ilink in links:
			append_if_not_exists(ilink.get('href').replace('//','https://'), result['pictures'])

		result['description'] = clear_spaces(soup.find('div',{'class':'ui tab segment active'}).text.replace('\n', ' ')).strip()

		result['sizes']
		
		rich.print(result)
		return result

def save_price(goods:list, path:str):
	price = Price(path)
	for  result in goods:
		price.add_good('',
								prepare_str(result['title']),
								prepare_str(result['description']),
								prepare_str( str(round(float(result['cost']), 2))),
								'15',
								prepare_str(result['link']),
								prepare_for_csv_non_list(result['pictures']),
								prepare_str(result['sizes']))
		price.write_to_csv(price_path)



async def main():
	goods = []
	good_links = [
'https://baby-shop54opt.ru/products/58284052',
]


	semaphore = asyncio.Semaphore(20)
	async with aiohttp.ClientSession() as session:
		tasks = [load_data_by_good_from_link(link, session, semaphore) for link in good_links]
		results = await asyncio.gather(*tasks)
		save_price(results, 'G:\baby-shop54opt.ru\csvs\test.csv')
		# rich.print(results)
		# goods.append(result)
	


	# result = await load_data_by_good_from_link('https://baby-shop54opt.ru/products/32783487', session)
	# goods.append(result)
	# rich.print(result)

	return
	url = 'http://example.com'
	html = await get_link_on_catalog_pages('https://baby-shop54opt.ru/products/category/3000271')
	print(html)

asyncio.run(main())