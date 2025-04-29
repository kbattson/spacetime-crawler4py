import requests
import cbor
import time
import pickle

from utils.response import Response

def download(url, config, logger=None):
    try:
        resp = requests.get(url)
    except requests.exceptions.RequestException as e:
        return Response({
            "url":   url,
            "status": None,
            "error": str(e)
        })
    return Response({
        "url":    url,
        "status": resp.status_code,
        "response": pickle.dumps(resp)
    })