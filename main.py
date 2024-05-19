import aiohttp
import asyncio
from bs4 import BeautifulSoup
import tempfile
import rich
from my_library import append_if_not_exists

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
	result['title'] = soup.find('h1').text
	
	cost = soup.find('span',{'class':'sale-price'})
	if cost:
		cost = cost.find('span',{'class':'product-price-data'}).get('data-cost')
	else:
		cost = soup.find('span',{'class':'product-price-data'}).get('data-cost')
	result['cost'] = cost

	images_container = soup.find('div', {'class':'avatar-wrap image'})
	rich.print(images_container)
	links = images_container.find_all('a')
	rich.print(links)
	result['pictures']=[]
	for ilink in links:
		append_if_not_exists(ilink.get('href').replace('//','https://'), result['pictures'])

	description = soup.find('div',{'class':'ui tab segment active'}).text
	rich.print(description)
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

async def main():
	async with aiohttp.ClientSession() as session:
		result = await load_data_by_good_from_link('https://baby-shop54opt.ru/products/32783487', session)
		rich.print(result)

	return
	url = 'http://example.com'
	html = await get_link_on_catalog_pages('https://baby-shop54opt.ru/products/category/3000271')
	print(html)

asyncio.run(main())