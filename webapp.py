from flask import Flask
from flask import request, jsonify
from es import queries
from query_expansion import get_category, get_keywords_for_category, get_data

app = Flask(__name__)


@app.route('/reviews')
def index():
    args = request.args
    print(args)
    place_name = args.get('place_name')
    print(place_name)
    start_time = args.get('start_time')
    end_time = args.get('end_time')
    print(start_time)
    print(end_time)
    result = process_review_request(place_name, start_time, end_time)
    resp = jsonify(result)
    # return 'Hello world'
    return resp


def process_review_request(place, start_time, end_time):
    category = get_category(place)
    print("category", category)
    keyword_list = get_keywords_for_category(category)
    print("keyword_list", keyword_list)
    result = get_data(place, keyword_list)
    return result


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
