from Common.config import *


start = f'''
Hi, this is bot to <a href="{site_url}">magazine.</a> 
You can view goods here and then buy it on our site.
Good shopping!!!
'''

about = '''
Our magazine provide you opportunity to shopping online!
This is a bot that give you ability to look at our products
from telegram. Good shopping!
'''

contacts = f'''
Phone: <a href="tel:{phone}">{phone}</a>
Mail: <a href="mailto:{mail}">{mail}</a>
Site: <a href="{site_url}">{site_url}</a>
'''

site = f'<a href="{site_url}">{site_url}</a>'
notFound = 'Unsupported message'
resetSuccess = 'Your query was reset'
resetFailure = 'You don\'t have make query now'

productStart = 'Ok, would you like to filter products at first?'

filterCategory = 'Select one of categories or send dot to skip this filter'
filterCategoryInvalid = 'This category don\'t exist! Select from list'

filterSize = 'Select one of sizes or send dot to skip this filter'
filterSizeInvalid = 'Select size from a list or send dot to skip filter'

filterColor = 'Select one of colors or send dot to skip this filter'
filterColorInvalid = 'We have not goods with this color'

filterPrice = '''
Enter range of price that you had like to see  or send dot to skip this filter
PS Range format: %from%-%to%
'''
filterPriceInvalid = 'Invalid format or data'

showProducts = 'Results of your search'
invalidValue = 'Invalid value!'
