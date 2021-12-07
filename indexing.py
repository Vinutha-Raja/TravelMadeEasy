import json
import re
from datetime import datetime
from elasticsearch import Elasticsearch


month = {'january': 1, 'february': 2, 'march': 3, 'april': 4, 'may': 5, 'june': 6, 'july': 7, 'august': 8,
         'september': 9, 'october': 10, 'november': 11, 'december': 12}

def read_json_file(file):
    f = open(file)
    data = json.load(f)
    # count = 1
    document_list = []
    for place in data['review_url']:

        # doc['place_name'] = place['place']
        # doc['place_url'] = place['link']
        if 'reviews' in place.keys():
            for review in place['reviews']:
                doc = dict()
                doc['place_name'] = place['place']
                print(doc['place_name'])
                doc['place_url'] = place['link']
                if 'name' in review:
                    reviewer = review['name']
                    reviewer_encoded = reviewer.encode("ascii", "ignore")
                    doc['reviewer'] = reviewer_encoded.decode()
                if 'title' in review:
                    review_title = review['title']
                    review_title_encoded = review_title.encode("ascii", "ignore")
                    doc['review_title'] = review_title_encoded.decode()
                # if 'date' in review:
                #     review_date = review['date']
                #     # review_date = re.sub('[^A-Za-z0-9 ]+', '', review_date)
                #     review_date_encoded = review_date.encode("ascii", "ignore")
                #     doc['review_date'] = review_date_encoded.decode()
                # print(review_date)
                if 'comment' in review:
                    review_comment = review['comment']
                    # review_comment = re.sub('[^A-Za-z0-9 ,.-!"\'&+]+', '', review_comment)
                    review_comment_encoded = review_comment.encode("ascii", "ignore")
                    doc['comment'] = review_comment_encoded.decode()
                if 'date' in review:
                    visit_time = review['date']
                    # review_comment = re.sub('[^A-Za-z0-9 ,.-!"\'&+]+', '', review_comment)
                    visit_time_encoded = visit_time.encode("ascii", "ignore")
                    visit_time = visit_time_encoded.decode().split()
                    # print("visit_time", visit_time)
                    if len(visit_time) == 3:
                        companion = visit_time[2]
                        doc['companion'] = companion.lower()
                    mon = visit_time[0].lower()
                    # print("mon", mon)
                    for key, value in month.items():
                        # print("mon", mon)
                        if key.startswith(mon):
                            mon = value
                            break
                    year = int(visit_time[1])
                    date = 1
                    visit_time = datetime(year, mon, date, 0, 0).strftime('%s')
                    doc['visit_time'] = visit_time

                if 'review_time' in review:
                    review_time = review['review_time']
                    # review_comment = re.sub('[^A-Za-z0-9 ,.-!"\'&+]+', '', review_comment)
                    review_time_encoded = review_time.encode("ascii", "ignore")
                    review_time = review_time_encoded.decode().lower().replace(',', '').split()
                    review_mon = review_time[1]
                    for key, value in month.items():
                        print("review_mon", review_mon)
                        if key.startswith(review_mon):
                            review_mon = int(value)
                            break
                    review_date = int(review_time[2])
                    review_year = int(review_time[3])
                    review_time = datetime(review_year, review_mon, review_date, 0, 0).strftime('%s')
                    doc['review_time'] = review_time
                if 'likes' in review:
                    likes = review['likes']
                    # review_comment = re.sub('[^A-Za-z0-9 ,.-!"\'&+]+', '', review_comment)
                    likes_encoded = likes.encode("ascii", "ignore")
                    doc['likes'] = likes_encoded.decode()
                if 'contributions' in review:
                    contributions = review['contributions']
                    # review_comment = re.sub('[^A-Za-z0-9 ,.-!"\'&+]+', '', review_comment)
                    contributions_encoded = contributions.encode("ascii", "ignore")
                    contributions = contributions_encoded.decode().split()[0].replace(',', '')
                    print("contributions: ", contributions)
                    doc['contributions'] = int(contributions)
                document_list.append(doc)

    return document_list


def main():
    es = Elasticsearch("http://localhost:9200/")
    # doc = {
    #     'reviewer': 'kimchy',
    #     'comment': 'Elasticsearch: cool. bonsai cool.',
    #     'date': datetime.now()
    # }
    # res = es.index(index="test11", id=1, document=doc)
    # print(res['result'])
    index_name = "reviews_jm"
    doc_list = read_json_file('data.json')
    # print(doc_list)
    for doc in doc_list:
        if 'visit_time' in doc:
            doc_id = doc['place_name'].lower().replace(' ', '')+'_'+doc['reviewer'].lower().replace(' ', '')+'_'+doc['visit_time']
        else:
            doc_id = doc['place_name'].lower().replace(' ', '') + '_' + doc['reviewer'].lower().replace(' ', '')
        # print("id---", doc_id)
        res = es.index(index=index_name, document=doc, id=doc_id, timeout="60s")
        print(res['result'])


if __name__ == "__main__":
    main()


