import aiohttp
import asyncio
from bs4 import BeautifulSoup
import tempfile
import rich

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
		rich.print(cart.find('a'))
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
	url = 'http://example.com'
	html = await get_link_on_catalog_pages('https://baby-shop54opt.ru/products/category/3000271')
	print(html)

asyncio.run(main())