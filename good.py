from my_library import *
from driver import *
import colorama
from colorama import Fore, Back, Style
from urllib.parse import quote
from bs4 import BeautifulSoup as BS
from click import echo, style

def poiskpers(url):
	geourl = '{0}'.format(quote(url))
	return geourl

class Good:
	def __init__(self, ol:WD, pc_good_link, pc_price:str):
		pc_good_link = pc_good_link.replace(r'amp;', '')
		self.pictures = []
		self.sizes = []
		self.prices = []
		self.color = ''
		self.article = ''
		self.name = ''
		self.description= ''
		self.price = ''
		self.brand = ''
		echo(style('Товар: ', fg='bright_yellow') + style(pc_good_link, fg='bright_white') + style('  Прайс:', fg='bright_cyan') + style(pc_price, fg='bright_green'))
		ol.Get_HTML(pc_good_link)
		soup = BS(ol.page_source, features='html5lib')
		
		## remove additinal goods miniatures into the page bottom
		while soup.find('div',{'class':'product-list'})!=None:
			soup.find('div',{'class':'product-list'}).replace_with('')

		self.name = soup.find('h1').text.strip()

		pictures = soup.find_all('a',{'class':'gallery-previews-l__link'})
		for picture in pictures:
			append_if_not_exists('https://doma-prosto.ru' + picture['href'], self.pictures)
		if len(self.pictures)==0:
			lc_picture_link = soup.find('img',{'class':'product-gallery-main__el-photo'})['src']
			append_if_not_exists('https://doma-prosto.ru' + lc_picture_link, self.pictures)


		try: self.description =  soup.find('div', {'itemprop':'description'}).text.replace(chr(10),' ').strip()
		except: pass


		try: # more than one color and price
			prices = soup.find_all('label')
			if len(prices)==0:
				raise Exception('Zero count of prices')
			for oprice in prices:
				if 'class="disabled"' in str(oprice):
					break # don't allowed for purchase
				name = oprice.find('span',{'itemprop':'name'}).text.strip()
				price = oprice.find('span',{'class':'price tiny nowrap'}).text.replace('₽','').strip()
				self.sizes.append(name)
				self.prices.append(price)
		except: # one price and no colors
			try:
				price = soup.find('div', {'class':'price'}).text.replace('₽','').strip()
			except:
				price = soup.find('span', {'class':'price'}).text.replace('₽','').strip()
			self.sizes.append('*')
			self.prices.append(price)

