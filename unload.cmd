cls
pip install pika
pip install rich
pip install bs4
pip install requests
pip install html5lib
pip install configparser
pip install click
start unload_prices.cmd
start unload_goods.cmd
python main.py get_links_from_catalog "https://baby-shop54opt.ru/products/category/3000271" "G:\baby-shop54opt.ru\csvs\nalichie.csv"
python main.py get_links_from_catalog "https://baby-shop54opt.ru/products/category/2910853" "G:\baby-shop54opt.ru\csvs\sumki.csv"
python main.py get_links_from_catalog "https://baby-shop54opt.ru/products/category/3084216" "G:\baby-shop54opt.ru\csvs\kepki.csv"
python main.py get_links_from_catalog "https://baby-shop54opt.ru/products/category/5059924" "G:\baby-shop54opt.ru\csvs\sale.csv"





