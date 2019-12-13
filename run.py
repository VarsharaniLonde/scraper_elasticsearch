from scraper.scraper import scraper
from scraper.query_ES import search_by_city, search_by_zipcode, search_by_speciality, search_exp_range

url = "https://health.usnews.com/"
city = "new-jersey"
scraper(url, city)
c = search_by_city(city='ABSECON')
print(c)
z = search_by_zipcode(zipcode="08234")
print(z)
s = search_by_speciality(speciality="GENERAL INTERNAL MEDICINE")
print(s)
e = search_exp_range(upper=22, lower=18)
print(e)