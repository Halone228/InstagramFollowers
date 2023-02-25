import re

tempory_db_name = 'db'

with open('accounts.txt', 'r', encoding='utf-8') as f:
    accounts = [tuple(i.split(':')) for i in f.read().split('\n')]

with open('proxies.txt', 'r', encoding='utf-8') as f:
    proxies = [i for i in f.read().split('\n') if i and '://' in i]

# account to parse link or username
account_to_parse = "https://www.instagram.com/vasilyeva.stylist?igshid=YmMyMTA2M2Y%3D"  #


parsed_username = re.sub(r'https:\/\/www\.instagram\.com\/(.+)[\/\?$].+', lambda m: m.group(1), account_to_parse)

# keywords for description
keywords = {"Стилист", "баер", "байер", "buyer", "консьерж", "шоппер", "предприниматель", "стиль", "мода", "ЦУМ",
            "Меркури", "TSUM", "DLT",
            "Mercury", "менеджер", "ювелир", "fashion", "style", "люкс", "lux", "luxury", "styling", "детейлинг",
            "премиум", "premium", "оригинал",
            "часы", "комиссионка", "comission", "authentic", "подлинность", "shopper", "shopping"}
