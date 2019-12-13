import logging
import re
import requests
from bs4 import BeautifulSoup


from .query_ES import load_data

def scraper(base_url, area):

	logging.basicConfig(level=logging.DEBUG)
	headers = {
	    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
	    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
		"accept-encoding": "gzip, deflate, br",
		"accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
		"Host": "health.usnews.com",
		"path": "/doctors/city-index/"+area.lower()
	    }

	link = base_url+headers['path']
	try:
	
		response = requests.request("GET", link, headers=headers, timeout=5, allow_redirects=False)
		
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			# for each city
			for city in soup.findAll('a', {'href': re.compile("^/doctors/specialists-index/")}):
				city_link = base_url + city['href']
				city_name = city.text
				city_page = requests.request("GET", city_link, headers=headers, timeout=5, allow_redirects=False)			
				if city_page.status_code == 200:
					city_soup = BeautifulSoup(city_page.text, 'html.parser')
					
					divs = city_soup.findAll('div', {'class':'mb5'}) 
					for div in divs:
						# for each specialization
						for s in div.findAll('a', {'href': re.compile("^/doctors/")}):
							count = 0
							speciality_link = base_url+ s['href']
							doctors_page = requests.request("GET", speciality_link, headers=headers, timeout=5, allow_redirects=False)
							if doctors_page.status_code == 200:
								doc_soup = BeautifulSoup(doctors_page.text, 'html.parser')
								doc_divs = doc_soup.findAll("div", {"data-test-id": "DetailCardDoctor"})
								for div1 in doc_divs:
									scrape_individual_doc_page(headers, base_url, div1, city_name, count)
									count +=1
									
	except requests.ConnectionError as e:
	    logging.debug("OOPS!! Connection Error. Make sure you are connected to Internet. Technical Details given below.\n")
	    logging.debug(str(e))
	except requests.Timeout as e:
	    logging.debug("OOPS!! Timeout Error")
	    logging.debug(str(e))
	except requests.RequestException as e:
	    logging.debug("OOPS!! General Error")
	    logging.debug(str(e))
	except Exception as e:
		logging.debug(str(e))




def scrape_individual_doc_page(headers, base_url, div, city_name, count):
	
	location, affiliation = '', ''
	training, certification = '', ''
	sub_a = div.find('a')
	a_link = base_url+sub_a['href']
	
	doc_page = requests.request("GET", a_link, headers=headers, timeout=5)
	sub_soup = BeautifulSoup(doc_page.text, 'html.parser')
	# overview
	overview = sub_soup.find("section", {"id": "overview"})
	name = overview.find('h2').text.replace('About ',"").strip()
	about = overview.find("div",{"data-test-id":"AboutDoctor"}).find('div').text
	years_exp = overview.find("div",{"title":"Years of Practice"}).findAll('div')[-1].text
	languages = overview.find("div",{"title":"Languages"}).findAll('div')[-1].text
	speciality = overview.find("div",{"title":"Specialty"}).findAll('div')[-1].text
	
	sub_speciality = sub_soup.find("section", {"id": "specialties"}).findAll('p')[-1].text
	
	# location
	location_section = sub_soup.find("section", {"id": "location"})
	doc_location = location_section.findAll('p')
	for item in doc_location:
		location += item.text
	contact = location_section.find('a', attrs={'href': re.compile("^tel://")}).text
	
	# affiliations
	affiliation_links = sub_soup.find("section", {"id": "hospitals"}).findAll('a', href=True)
	for item in affiliation_links:
		p = item.find('p')
		if p:
			affiliation += item.find('p').text
	
	# training and certifications
	
	education_exp = sub_soup.find("section", {"id": "experience"}).findAll('div', {"class": "mb5"})
	if len(education_exp) >= 2:
		medical_training = education_exp[0].findAll('p')
		for i in range(0, len(medical_training), 2):
			training += medical_training[i].text+ "-" + medical_training[i+1].text.replace(',',' ')+", "
		certifications = education_exp[1].findAll('p')
		for i in range(0, len(certifications), 2):
			certification += certifications[i].text+ "-" + certifications[i+1].text.replace(',',' ')+", "
	
	build_load_json(count, name, about, years_exp, city_name, languages, speciality, sub_speciality, location, contact, affiliation, training, certification)
	count += 1	



def build_load_json(i, name, about, years_exp, city_name, languages, speciality, sub_speciality, location, contact, affiliation, training, certification):
	doctor_json = {
	"overview": clean_data(about),
	"full_name": clean_data(name),
	"years_in_practice": parse_years(years_exp), 
	"language": clean_data(languages),
	"office_location": clean_data(city_name)+','+clean_data(location),
	"hospital_affiliations": clean_data(affiliation),
	"specialties_and_sub_specialities": clean_data(speciality+','+sub_speciality),
	"education_and_medicalTraining": clean_data(training),
	"certifications_and_licensure": clean_data(certification),
	}
	
	load_data("test_index", "test", i, doctor_json)


def clean_data(data):
	if data is not None:
		data = data.encode('ascii', 'ignore')
		data = data.strip()
		if data == "Unknown":
			return None
		return data.lower()
	else:
		return None

def parse_years(years):
	years = clean_data(years)
	if years is not None:
		if '-' in years:
			years = years.split('-')[-1]
		elif '+' in years:
			years = years.replace('+', '')
		
		return int(years)



if __name__ == '__main__':
	url = "https://health.usnews.com"
	scraper(url, "new-jersey")

	