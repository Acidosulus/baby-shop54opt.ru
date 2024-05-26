cls
rem pip install pika
rem pip install rich
rem pip install bs4
rem pip install requests
rem pip install html5lib
rem pip install configparser
rem pip install click
python main.py get_links_from_catalog "https://baby-shop54opt.ru/products/category/3000271" "G:\baby-shop54opt.ru\csvs\nalichie.csv"
python main.py get_links_from_catalog "https://baby-shop54opt.ru/products/category/2910853" "G:\baby-shop54opt.ru\csvs\sumki.csv"
python main.py get_links_from_catalog "https://baby-shop54opt.ru/products/category/3084216" "G:\baby-shop54opt.ru\csvs\kepki.csv"
python main.py get_links_from_catalog "https://baby-shop54opt.ru/products/category/5059924" "G:\baby-shop54opt.ru\csvs\sale.csv"




start unload_prices.cmd
start unload_goods.cmd

