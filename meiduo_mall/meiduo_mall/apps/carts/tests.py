from django.test import TestCase
import pickle
import base64
# Create your tests here.
if __name__ == '__main__':
    dict ={'name':'zhs',
           'age':10}

    datab = pickle.dumps(dict)
    print(datab)

    result = base64.b64encode(datab)
    print(result)