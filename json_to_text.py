import json
import re


f = open('data.json')
data = json.load(f)
count = 1


def write_to_file(fp, key, value, tag=1):
    if tag != 0:
        fp.write("<" + key + ">")
        # print(value)
        fp.write(value)
        fp.write("</" + key + ">")
        fp.write("\n")
    else:
        fp.write(value)


for place in data['places_url']:
    place_name = place['place']
    place_url = place['link']
    for review in place['reviews']:
        if 'name' in review:
            reviewer = review['name']
            reviewer_comment_encoded = reviewer.encode("ascii", "ignore")
            reviewer = reviewer_comment_encoded.decode()
        if 'title' in review:
            review_title = review['title']
            review_title_comment_encoded = review_title.encode("ascii", "ignore")
            review_title = review_title_comment_encoded.decode()
        if 'date' in review:
            review_date = review['date']
            # review_date = re.sub('[^A-Za-z0-9 ]+', '', review_date)
            review_date_comment_encoded = review_date.encode("ascii", "ignore")
            review_date = review_date_comment_encoded.decode()
            # print(review_date)
        if 'comment' in review:
            review_comment = review['comment']
            # review_comment = re.sub('[^A-Za-z0-9 ,.-!"\'&+]+', '', review_comment)
            review_comment_encoded = review_comment.encode("ascii", "ignore")
            review_comment = review_comment_encoded.decode()
        # write the details to the text file
        # open a file for each review
        # dir = '/data/'
        file1 = open('/Users/vinutha/Documents/IR/TravelMadeEasy/webScraping/data/doc'+str(count)+'.txt', 'w')
        write_to_file(file1, 'id', 'doc-'+str(count))
        write_to_file(file1, 'place_name', place_name)
        write_to_file(file1, 'place_url', place_url)
        write_to_file(file1, 'reviewer', reviewer)
        write_to_file(file1, 'review_title', review_title)
        write_to_file(file1, 'review_date', review_date)
        write_to_file(file1, 'review_comment', review_comment, 0)


        file1.close()
        count += 1







