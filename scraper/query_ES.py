import logging
import json
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q


logging.basicConfig(level=logging.DEBUG)

def get_es_instance():
	try:
		es = Elasticsearch()
		return es
	except Exception as e:
		logging.debug(str(e))


def load_data(index, doctype, i, doctor_json):
	try:
		es = get_es_instance()
		es.index(index, doc_type=doctype, id=i, body=doctor_json)
	except Exception as e:
		logging.debug(str(e))


def search_by_city(city = "NJ"):
	count = 0
	try:
		es = get_es_instance()
		s = Search().using(es).query("match", office_location= "*"+city.lower()+"*")
		response = s.execute()
		count = response.hits.total.value
		result = json.dumps({"number_by_"+city : count})
		return result
	except Exception as e:
		logging.debug(str(e))


def search_by_zipcode(zipcode = "08902"):
	count = 0
	try:
		es = get_es_instance()
		s = Search().using(es).query("match", office_location="*"+zipcode+"*")
		response = s.execute()
		count = response.hits.total.value
		result = json.dumps({"number_by_"+zipcode : count})
		return result
	except Exception as e:
		logging.debug(str(e))


def search_by_speciality(speciality = "Oncology"):
	
	try:
		es = get_es_instance()
		s = Search().using(es).query("match", specialties_and_sub_specialities="*"+speciality.lower()+"*")
		response = s.execute()
		count = response.hits.total.value
		result = json.dumps({"number_by_"+speciality : count})
		return result

	except Exception as e:
		logging.debug(str(e))


def search_exp_range(upper=22, lower=20):
	count = 0
	try:
		es = get_es_instance()
		time_query = Q('range', years_in_practice={
	    'gte': lower,
	    'lt': upper})
		s = Search(using=es)
		s = s.query(time_query)
		response = s.execute()
		count = response.hits.total.value
		result = json.dumps({"number_in_range" : count})
		return result
	except Exception as e:
		logging.debug(str(e))

	

