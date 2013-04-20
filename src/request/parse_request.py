import json


if __name__ == "__main__":
    test = json.loads('["foo", {"bar":["baz", null, 1.0, 2]}]')
    print test[1]