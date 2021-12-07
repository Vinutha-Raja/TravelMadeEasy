import json
import requests

category_dict = dict()
doc_limit = 10
index_name = 'reviews_dirichlet'
# category to place mapping
category_dict['outdoors'] = ["Little Cottonwood Canyon",
                             "Big Cottonwood Canyon",
                             "Wendover Will",
                             "West Wendover Welcome Center"]
category_dict['national_parks'] = ["Zion National Park",
                                   "Bryce Canyon National Park",
                                   "Arches National Park",
                                   "Canyonlands National Park",
                                   "Capitol Reef National Park"]
category_dict['art_and_culture'] = ["Natural History Museum of Utah",
                                    "Brigham Young University Museum of Art (MOA)",
                                    "Utah Museum of Fine Arts",
                                    "Church History Museum",
                                    "Salt Lake Temple"]
category_dict['History'] = ["Hill Aerospace Museum",
                            "Natural Bridges National Monument"]

# Place to category mapping
reverse_category_dict = dict()
reverse_category_dict['Little Cottonwood Canyon'] = "outdoors"
reverse_category_dict['Big Cottonwood Canyon'] = "outdoors"
reverse_category_dict['Wendover Will'] = "outdoors"
reverse_category_dict['West Wendover Welcome Center'] = "outdoors"

reverse_category_dict['Zion National Park'] = "national_parks"
reverse_category_dict['Bryce Canyon National Park'] = "national_parks"
reverse_category_dict['Arches National Park'] = "national_parks"
reverse_category_dict['Canyonlands National Park'] = "national_parks"
reverse_category_dict['Capitol Reef National Park'] = "national_parks"

reverse_category_dict['Natural History Museum of Utah'] = "art_and_culture"
reverse_category_dict['Brigham Young University Museum of Art (MOA)'] = "art_and_culture"
reverse_category_dict['Utah Museum of Fine Arts'] = "art_and_culture"
reverse_category_dict['Church History Museum'] = "art_and_culture"
reverse_category_dict['Salt Lake Temple'] = "art_and_culture"

reverse_category_dict['Hill Aerospace Museum'] = "history"
reverse_category_dict['Natural Bridges National Monument'] = "history"
reverse_category_dict['Hovenweep National Monument'] = "history"
reverse_category_dict['Cathedral of the Madeleine'] = "history"
reverse_category_dict['Museum of Ancient Life at Thanksgiving Point'] = "history"



# category to keyword mapping

keywords_dict = dict()
keywords_dict['outdoors'] = ['Scenic', 'Wasatch', 'Rock', 'Hiking', 'Ski', 'Climb', 'Hike', 'Camp', 'Drive', 'Snow',
                             'River', 'Nature', 'Mountain', 'Lake', 'Fish', 'Park', 'Casino', 'money', 'gambling',
                             'road', 'route', 'kid', 'toddler']
keywords_dict['national_parks'] = ['Camp', 'Trial', 'scenery', 'wildlife', 'scenery', 'Waterfalls', 'Beauty', 'Drive',
                                   'Animals', 'kid', 'toddler']
keywords_dict['history'] = ['Plane', 'Aircraft', 'Jet', 'War', 'Military', 'Murals', 'Mass', 'Priest', 'Historic',
                            'Religious', 'Fossil', 'Archeology', 'Geology', 'Christ', 'Glass''kid', 'toddler']
keywords_dict['art_and_culture'] = ['Exhibit', 'Display', 'Building', 'Dinosaur', 'Paleontology', 'Gallery','Paintings',
                                    'Portrait', 'creation', 'Jesus', 'Christ', 'Interior', 'Saint', 'History', 'Family'
                                    'kid', 'toddler']

# Keyword list based on the FAQ
keywords_dict['time'] = ['january', 'february', 'march', 'april', 'may', 'june', 'july', 'august', 'september',
                         'october', 'november', 'december', 'morning', 'evening', 'night', 'fall', 'spring', 'summer',
                         'winter', 'weather']
keywords_dict['budget'] = ['budget', 'ticket', 'Ticket']
keywords_dict['transportation'] = ['airport', 'bus', 'trax', 'train', 'shuttle']
keywords_dict['covid_safety'] = ['covid', 'sanitize', 'mask']
keywords_dict['food'] = ['restaurant', 'food', 'hotel', 'cafe', 'breakfast', 'lunch', 'dinner']
keywords_dict['accessibility'] = ['wheelchair']


def get_category(place):
    # print("place: ----", place)
    # place = 'Little Cottonwood Canyon'
    # print("get_category, place", place)
    # print(type(place))
    # r = reverse_category_dict[place]
    # print(r)
    return reverse_category_dict.get(place)


def get_keywords_for_category(category):
    return keywords_dict.get(category)


def get_data(place, keyword_list):
    filters = []
    should_filters = []
    sort_by = []
    must = []
    keywords = ''
    # place = 'Little Cottonwood Canyon'
    for key in keyword_list:
        keywords += key + ' '
    filters.append({"term": {"place_name": place}})
    # filters.append({"match": {"comment": keywords}})
    # sort_by.append({"contributions": "desc"})
    # must.append({"terms": {"comment": keyword_list}})

    # match phrase query
    for key in keyword_list:
        should_filters.append({"match_phrase": {"comment": key}})

    term_query = get_query_based_on_should_match_phrase(doc_limit, filters, should_filters)
    # term_query = get_query_based_on_filter(doc_limit, filters)
    # term_query = get_query_based_on_filter_and_must(10, filters, must)

    headers = {"content-type": "application/json"}
    es_url = "http://127.0.0.1:9200/"+index_name+"/_search"
    response = requests.get(es_url, data=term_query, headers=headers)
    print("query: ", term_query)
    # print("response: ", response.text)

    result = json.loads(response.text)
    # print(result)
    result_hits = result['hits']['hits']
    respose_dict = dict()
    doc_list = []
    for doc in result_hits:
        comment = doc['_source']['comment']
        for key in keyword_list:
            if key in comment:
                # print("replacing")
                newKey = '<b>' + key + '</b>'
                # print(newKey)
                comment = comment.replace(key, newKey)
                # print("comment 1", comment)
        # print("comment ", comment)
        doc['_source']['comment'] = comment
        doc_list.append(doc)
    result_hits = doc_list
    respose_dict['general_info'] = result_hits
    respose_dict['accessibility'] = get_data_for_accessibility(place)
    respose_dict['food'] = get_data_for_best_food_options(place)
    respose_dict['accessibility'] = get_data_for_accessibility(place)
    respose_dict['time_to_travel'] = get_data_for_best_time_to_travel(place)
    respose_dict['transportation'] = get_data_for_transportation_facility(place)
    respose_dict['budget'] = get_data_for_budget(place)

    return respose_dict


def get_data_for_best_time_to_travel(place):
    filters = []
    should_filters = []
    keyword_list = keywords_dict['time']
    keywords = ''
    for key in keyword_list:
        keywords += key + ' '
    filters.append({"term": {"place_name": place}})
    # filters.append({"match": {"comment": keywords}})
    # match phrase query
    for key in keyword_list:
        should_filters.append({"match_phrase": {"comment": key}})

    term_query = get_query_based_on_should_match_phrase(doc_limit, filters, should_filters)
    # term_query = get_query_based_on_filter(doc_limit, filters)
    headers = {"content-type": "application/json"}
    es_url = "http://127.0.0.1:9200/"+index_name+"/_search"
    response = requests.get(es_url, data=term_query, headers=headers)
    print("best_time_to_travel  query: ", term_query)
    # print("best_time_to_travel response: ", response.text)

    result = json.loads(response.text)
    # print("best_time_to_travel", result)
    result_hits = result['hits']['hits']
    doc_list = []
    for doc in result_hits:
        comment = doc['_source']['comment']
        for key in keyword_list:
            if key in comment:
                # print("replacing")
                newKey = '<b>' + key + '</b>'
                # print(newKey)
                comment = comment.replace(key, newKey)
                # print("comment 1", comment)
        # print("comment ", comment)
        doc['_source']['comment'] = comment
        doc_list.append(doc)
    result_hits = doc_list
    return result_hits


def get_data_for_transportation_facility(place):
    filters = []
    should_filters = []
    keyword_list = keywords_dict['transportation']
    keywords = ''
    for key in keyword_list:
        keywords += key + ' '
    filters.append({"term": {"place_name": place}})
    # filters.append({"match": {"comment": keywords}})

    # match phrase query
    for key in keyword_list:
        should_filters.append({"match_phrase": {"comment": key}})

    term_query = get_query_based_on_should_match_phrase(doc_limit, filters, should_filters)
    # term_query = get_query_based_on_filter(doc_limit, filters)
    headers = {"content-type": "application/json"}
    es_url = "http://127.0.0.1:9200/"+index_name+"/_search"
    response = requests.get(es_url, data=term_query, headers=headers)
    print("transportation_facility  query: ", term_query)
    # print("transportation_facility response: ", response.text)

    result = json.loads(response.text)
    # print("transportation_facility", result)
    result_hits = result['hits']['hits']
    doc_list = []
    for doc in result_hits:
        comment = doc['_source']['comment']
        for key in keyword_list:
            if key in comment:
                # print("replacing")
                newKey = '<b>' + key + '</b>'
                # print(newKey)
                comment = comment.replace(key, newKey)
                # print("comment 1", comment)
        # print("comment ", comment)
        doc['_source']['comment'] = comment
        doc_list.append(doc)
    result_hits = doc_list
    return result_hits


def get_data_for_budget(place):
    filters = []
    should_filters = []
    keyword_list = keywords_dict['budget']
    keywords = ''
    for key in keyword_list:
        keywords += key + ' '
    filters.append({"term": {"place_name": place}})
    # filters.append({"match": {"comment": keywords}})

    # match phrase query
    for key in keyword_list:
        should_filters.append({"match_phrase": {"comment": key}})

    term_query = get_query_based_on_should_match_phrase(doc_limit, filters, should_filters)
    # term_query = get_query_based_on_filter(doc_limit, filters)
    headers = {"content-type": "application/json"}
    es_url = "http://127.0.0.1:9200/"+index_name+"/_search"
    response = requests.get(es_url, data=term_query, headers=headers)
    print("budget  query: ", term_query)
    # print("budget response: ", response.text)

    result = json.loads(response.text)
    # print("budget", result)
    result_hits = result['hits']['hits']
    doc_list = []
    for doc in result_hits:
        comment = doc['_source']['comment']
        for key in keyword_list:
            if key in comment:
                # print("replacing")
                newKey = '<b>' + key + '</b>'
                # print(newKey)
                comment = comment.replace(key, newKey)
                # print("comment 1", comment)
        # print("comment ", comment)
        doc['_source']['comment'] = comment
        doc_list.append(doc)
    result_hits = doc_list
    return result_hits


def get_data_for_covid_related_info(place):
    filters = []
    should_filters = []
    keyword_list = keywords_dict['covid_safety']
    keywords = ''
    for key in keyword_list:
        keywords += key + ' '
    filters.append({"term": {"place_name": place}})
    # filters.append({"match": {"comment": keywords}})

    # match phrase query
    for key in keyword_list:
        should_filters.append({"match_phrase": {"comment": key}})

    term_query = get_query_based_on_should_match_phrase(doc_limit, filters, should_filters)
    # term_query = get_query_based_on_filter(doc_limit, filters)
    headers = {"content-type": "application/json"}
    es_url = "http://127.0.0.1:9200/"+index_name+"/_search"
    response = requests.get(es_url, data=term_query, headers=headers)
    print("covid_related_info  query: ", term_query)
    # print("covid_related_info response: ", response.text)

    result = json.loads(response.text)
    # print("covid_related_info", result)
    result_hits = result['hits']['hits']
    # source = result_hits['_score']
    doc_list = []
    for doc in result_hits:
        comment = doc['_source']['comment']
        for key in keyword_list:
            if key in comment:
                # print("replacing")
                newKey = '<b>' + key + '</b>'
                # print(newKey)
                comment = comment.replace(key, newKey)
                # print("comment 1", comment)
        # print("comment ", comment)
        doc['_source']['comment'] = comment
        doc_list.append(doc)
    result_hits = doc_list
    return result_hits


def get_data_for_accessibility(place):
    filters = []
    should_filters = []
    keyword_list = keywords_dict['accessibility']
    keywords = ''
    for key in keyword_list:
        keywords += key + ' '
    filters.append({"term": {"place_name": place}})
    # filters.append({"match": {"comment": keywords}})

    # match phrase query
    for key in keyword_list:
        should_filters.append({"match_phrase": {"comment": key}})

    term_query = get_query_based_on_should_match_phrase(doc_limit, filters, should_filters)
    # term_query = get_query_based_on_filter(doc_limit, filters)
    headers = {"content-type": "application/json"}
    es_url = "http://127.0.0.1:9200/"+index_name+"/_search"
    response = requests.get(es_url, data=term_query, headers=headers)
    print("accessibility  query: ", term_query)
    # print("accessibility response: ", response.text)

    result = json.loads(response.text)
    # print("accessibility", result)
    result_hits = result['hits']['hits']
    doc_list = []
    for doc in result_hits:
        comment = doc['_source']['comment']
        for key in keyword_list:
            if key in comment:
                # print("replacing")
                newKey = '<b>' + key + '</b>'
                # print(newKey)
                comment = comment.replace(key, newKey)
                # print("comment 1", comment)
        # print("comment ", comment)
        doc['_source']['comment'] = comment
        doc_list.append(doc)
    result_hits = doc_list
    return result_hits


def get_data_for_best_food_options(place):
    filters = []
    should_filters = []
    keyword_list = keywords_dict['food']
    keywords = ''
    for key in keyword_list:
        keywords += key + ' '
    filters.append({"term": {"place_name": place}})
    # filters.append({"match": {"comment": keywords}})

    # match phrase query
    for key in keyword_list:
        should_filters.append({"match_phrase": {"comment": key}})

    term_query = get_query_based_on_should_match_phrase(doc_limit, filters, should_filters)

    # term_query = get_query_based_on_filter(doc_limit, filters)
    headers = {"content-type": "application/json"}
    es_url = "http://127.0.0.1:9200/"+index_name+"/_search"
    response = requests.get(es_url, data=term_query, headers=headers)
    print("best_food_options  query: ", term_query)
    # print("best_food_options response: ", response.text)

    result = json.loads(response.text)
    # print("best_food_options", result)
    result_hits = result['hits']['hits']
    doc_list = []
    for doc in result_hits:
        comment = doc['_source']['comment']
        for key in keyword_list:
            if key in comment:
                # print("replacing")
                newKey = '<b>' + key + '</b>'
                # print(newKey)
                comment = comment.replace(key, newKey)
                # print("comment 1", comment)
        # print("comment ", comment)
        doc['_source']['comment'] = comment
        doc_list.append(doc)
    result_hits = doc_list
    return result_hits


def get_query_based_on_filter(limit, filters=[]):
    query = json.dumps({
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "size": limit
    })
    return query


def get_query_based_on_filter1(limit, filters=[], sort_by=[]):
    query = json.dumps({
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "size": limit,
        "sort": sort_by
    })
    return query


def get_query_based_on_match_phrase(limit, filters=[], sort_by=[]):
    query = json.dumps({
        "query": {
            "bool": {
                "filter": filters
            }
        },
        "size": limit,
        "sort": sort_by
    })
    return query


def get_query_based_on_filter_and_must(limit, filters=[], must_list=[]):
    query = json.dumps({
        "query": {
            "bool": {
                "filter": filters,
                "must": must_list
            }
        },
        "size": limit,
        # "sort": sort_by
    })
    return query


def get_query_based_on_should_match_phrase(limit, filters=[], should_filters=[]):
    query = json.dumps({
        "query": {
            "bool": {
                "filter": filters,
                "should": should_filters,
                "minimum_should_match": 1
            }
        },
        "size": limit,
    })
    return query


