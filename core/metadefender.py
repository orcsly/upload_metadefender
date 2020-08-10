import requests, json
import argparse
import hashlib
import os, sys
from environs import Env

env = Env()
env.read_env()  # read .env file, if it exists

METADEFENDER_URL = env('METADEFENDER_URL')
METADEFENDER_API_KEY = env('METADEFENDER_API_KEY')
META_HASH = 'sha256'
META_METADATA = '0'
META_WORKFLOW = None


def _scan_file(api_key, file_stream, file_name=None, user_agent=None):
    url = "{}/file".format(METADEFENDER_URL)
    headers = {'apikey': api_key, 'user_agent': user_agent, 'Content-Type': "application/octet-stream"}
    try:
        print('url - {}'.format(url))
        response = requests.post(url=url, data=file_stream, headers=headers)
        output_data = response.json()
        print('results = {}'.format(output_data))
        return output_data['data_id'], 'Success'
    except requests.exceptions.RequestException as err:
        print("Request Error:", err)
        return '', 'Request Error'
    except:
        print("Unable to scan file.")
        return '', 'Scan error'


def _retrieve_scan(url, api_key, metadata='0'):
    headers = {'apikey': api_key, 'file-metadata': metadata}
    try:
        print('retrieval scan - {}'.format(url))
        response = requests.get(url=url, headers=headers)
        output_data = response.json()
        # print('retrieval scan result - {}'.format(output_data))
    except requests.exceptions.RequestException as err:
        print("Request Error:", err)
        return '', 'Request Error'
    except:
        print("Unable to retrieve file status.")
        sys.exit(0)

    return output_data


def _calculate_hash(hash_type, file_stream, chunk_size=65536):
    try:
        if hash_type == "md5":
            hash = hashlib.md5()
        elif hash_type == "sha1":
            hash = hashlib.sha1()
        elif hash_type == "sha256":
            hash = hashlib.sha256()
        for chunk in iter(lambda: file_stream.read(chunk_size), b""):
            hash.update(chunk)
    except:
        print("Unable to hash file.")
        return ''
    return hash.hexdigest()


def scan_file_sync(file_name, file_stream):
    # Calculate hash of file
    file_hash = _calculate_hash(META_HASH, file_stream).upper()
    if file_hash == '':
        return file_hash, 'Unable to has file'

    # Perform hash lookup for cached results
    url = "{}/hash/{}".format(METADEFENDER_URL, file_hash)
    scan_result = _retrieve_scan(url=url, api_key=METADEFENDER_API_KEY, metadata=META_METADATA)

    # Skip if cache found
    if scan_result == '' or ('error' not in scan_result):
        return scan_result, 'Success'

    # Initiate scan and get data id
    data_id, error_msg = _scan_file(api_key=METADEFENDER_API_KEY, file_stream=file_stream, file_name=file_name,
                                    user_agent=META_WORKFLOW)
    if data_id == '':
        return data_id, error_msg

    # Loop through and check for results because scan_file is async
    url = "{}/file/{}".format(METADEFENDER_URL, data_id)
    scan_result = _retrieve_scan(url=url, api_key=METADEFENDER_API_KEY, metadata=META_METADATA)
    while scan_result['scan_results']['progress_percentage'] != 100:
        scan_result = _retrieve_scan(url=url, api_key=METADEFENDER_API_KEY, metadata=META_METADATA)

    return scan_result, 'Success'
