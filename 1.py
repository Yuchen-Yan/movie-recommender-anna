import sys
import json
import requests


def argv():
    args = {}
    if len(sys.argv)>-1:
        args['ipAddress'] = 'localhost'#sys.argv[1]
        args['portNum'] = 5001#sys.argv[2]
        args['type'] = 'comment'#sys.argv[3]

        if(args['type'] == "search"):
            args['query'] = 'leonardo'#sys.argv[4]
            args['attribute'] = 'actor'#sys.argv[5]
            args['sortby'] = 'year'#sys.argv[6]
            args['order'] = 'descending'#sys.argv[7]

        if(args['type'] == "movie"):
            args['movie_id'] = 5#sys.argv[4]

        if(args['type'] == "comment"):
            args['userName'] = 'albert'#sys.argv[4]
            args['movie_id'] = 85#sys.argv[5]

    else:
        print("Error!")
    return args


def excute(args):
    result = "Defult"
    if args['type'] == "search":
        param = {'query': args['query'], 'attribute': args['attribute'], 'sortby': args['sortby'],
                 'order': args['order']}
        req = 'http://{}:{}/search'.format(args['ipAddress'], args['portNum'])
        r = requests.get(req, params=param)
        result = json.dumps(r.json(), indent=4, sort_keys=True)
        print("Request: /search?query={}&attribute={}&sortby={}&order={}".format(args['query'], args['attribute'],args['sortby'], args['order']))
        print("\r")
        print("Response: ")
    if args['type'] == "movie":
        request = 'http://{}:{}/{}/{}'.format(args['ipAddress'], args['portNum'], args['type'], args['movie_id'])
        response = requests.get(request)
        result = json.dumps(response.json(), indent=4, sort_keys=True)
        print("Request: /movie/{}".format(args['movie_id']))
        print("\r")
        print("Response:")



if __name__ == "__main__":
    args = argv()
    #print(args)
    excute(args)
