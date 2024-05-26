import requests
from bs4 import BeautifulSoup
import tempfile
import datetime
import rich
import sys
import json
from my_library import append_if_not_exists, clear_spaces, Price, prepare_str, prepare_for_csv_non_list, convert_file_to_ansi, reverse_csv_price
from driver import RabbitMQ_Driver




def download_page(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        print("Page Download error::", response.status_code)
        return None


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


# def load_data_by_good_from_link(link:str, session):
# 	html = download_page(link)
# 	soup = BeautifulSoup(html, features='html5lib')
# 	result = {}

# 	result['link'] = link

# 	result['title'] = soup.find('h1').text
	
# 	cost = soup.find('span',{'class':'sale-price'})
# 	if cost:
# 		cost = cost.find('span',{'class':'product-price-data'}).get('data-cost')
# 	else:
# 		cost = soup.find('span',{'class':'product-price-data'}).get('data-cost')
# 	result['cost'] = cost

# 	images_container = soup.find('div', {'class':'avatar-wrap image'})
# 	links = images_container.find_all('a')
# 	result['pictures']=[]
# 	for ilink in links:
# 		append_if_not_exists(ilink.get('href').replace('//','https://'), result['pictures'])

# 	result['descriprion'] = clear_spaces(soup.find('div',{'class':'user-inner'}).text.replace('\n', ' ')).strip()

# 	return result

def get_all_links_on_goods(catalog_url:str, queue:str, price_path:str, rqd:RabbitMQ_Driver):
	links_queue_name = queue+'_links_on_goods'
	rqd.create_queue(links_queue_name)
	rqd.create_queue(links_queue_name+'_good')
	all_pages = []
	links = []
	page_number =1
	html, html_last = '',''
	while True:
		rich.print(f'catalog page: {page_number}')
		next_page_url = f"{catalog_url}?page={page_number}"
		html_last = html
		html = download_page(next_page_url)
		if str(BeautifulSoup(html, features='html5lib').find('article')) != str(BeautifulSoup(html_last, features='html5lib').find('article')):
			all_pages.append(next_page_url)
			result = get_list_of_goods_from_source(html)
			links_from_page = get_list_of_goods_from_source(html)
			rich.print(links_from_page)
			links.extend(links_from_page)
			for lnk in links_from_page:
				rqd.put_message(links_queue_name, json.dumps({'price':price_path, 'catalog_url':catalog_url, 'link':lnk}))
			page_number += 1
		else:
			break
	return links


def load_data_by_good_from_link(link:str):
	html = download_page(link)
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
	
	try:
		result['description'] = clear_spaces(soup.find('div',{'class':'user-inner'}).text.replace('\n', ' ')).strip()
	except:
		result['description'] = ''

	result['sizes']= ''
	try:
		selector = soup.find('div', {'class':'variant-chooser-item variant-chooser__item -col-12 inline-block'})
		for size_block in selector.find_all('div', {'class':'variant-chooser-value'}):
			result['sizes'] = result['sizes'] + ('; ' if len(result['sizes'])>0 else '') + size_block.text.strip()
	except:
		pass
	if result['sizes'] is None:
		result['sizes'] = ''

	rich.print(result)
	return result

def save_price(result:list, path:str):
	price = Price(path)
	sizes = result['sizes']
	sizes = clear_spaces(sizes)
	sizes = sizes.strip()
	sizes = sizes.replace(" ","; ")
	price.add_good('',
							prepare_str(result['title']),
							prepare_str(result['description']),
							prepare_str( str(round(float(result['cost']), 2))),
							'15',
							prepare_str(result['link']),
							prepare_for_csv_non_list(result['pictures']),
							'"'+result['sizes']+'"')
	price.write_to_csv(path)




def consume_link_on_good(ch, method, properties, body:bytes):
	data = json.loads(body.decode(encoding='utf8',  errors='ignore'))
	rich.print(f"""Recieved link: {data['link']} from catalog: {data['catalog_url']} for price: {data['price']}""")
	method_frame, header_frame, body = ch.basic_get(queue=method.routing_key)
	good_data = load_data_by_good_from_link(data['link'])
	good_data['price'] = data['price']
	good_data['catalog_url'] = data['catalog_url']
	rqd.put_message(method.routing_key+'_good', json.dumps(good_data, ensure_ascii=False))
	

def consume_save_price(ch, method, properties, body:bytes):
	data = json.loads(body.decode(encoding='utf8',  errors='ignore'))
	rich.print(data)
	save_price(data, data['price'])


def main():
	if sys.argv[1]=='get_links_from_catalog':
		get_all_links_on_goods(	
								catalog_url=sys.argv[2],
					   			queue=queue_name,
								price_path=sys.argv[3],
								rqd=rqd
								)

	if sys.argv[1]=='get_goods_data':
		queues = rqd.get_broker_queues()
		queues = list(filter(lambda x: x.startswith('baby-shop54opt.ru') and x.endswith('_links_on_goods') and datetime.datetime.now().strftime("%Y-%m-%d") in x, queues))
		for queue in queues:
			rqd.add_queue_non_blocking(queue, consume_link_on_good)

	if sys.argv[1]=='unload_prices':
		queues = rqd.get_broker_queues()
		queues = list(filter(lambda x: x.startswith('baby-shop54opt.ru') and x.endswith('_links_on_goods_good') and datetime.datetime.now().strftime("%Y-%m-%d") in x, queues))
		for queue in queues:
			rqd.add_queue_non_blocking(queue, consume_save_price)

	if sys.argv[1]=='test':
		load_data_by_good_from_link("https://baby-shop54opt.ru/products/36324491")

	if sys.argv[1]=='ansirevert':
		convert_file_to_ansi(reverse_csv_price(sys.argv[2]))




if __name__ == '__main__':
	queue_name = "baby-shop54opt.ru" + datetime.datetime.now().strftime("%Y-%m-%d")
	rqd = RabbitMQ_Driver()
	main()