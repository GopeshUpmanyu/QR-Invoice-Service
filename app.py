import base64
import json
import requests
import boto3
from pdf2image import convert_from_bytes
from pyzbar.pyzbar import decode
import csv
import os
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from urllib.parse import urlparse
from pprint import pprint
from fastapi.middleware.cors import CORSMiddleware


s3_client = boto3.client('s3', aws_access_key_id='AKIAWVKQBF2LVYONJBRP',
                         aws_secret_access_key='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', region_name='ap-south-1')
def extract_qr_data_from_pdf(pdf_data):
    images = convert_from_bytes(pdf_data)
    qr_data_list = []
    for page_num, image in enumerate(images):
        decoded_qr_objects = decode(image)
        for qr_obj in decoded_qr_objects:
            qr_data = qr_obj.data.decode('utf-8')
            qr_data_list.append(qr_data)
    return qr_data_list
def decode_jwt(token):
    parts = token.split('.')
    if len(parts) != 3:
        raise ValueError('Token must have exactly 3 parts')
    payload = parts[1]
    padding_needed = 4 - len(payload) % 4
    payload += '=' * padding_needed
    decoded_bytes = base64.urlsafe_b64decode(payload)
    decoded_data = json.loads(decoded_bytes)
    return decoded_data
def process_qr_data(qr_data, s3_url):
    try:
        decoded_data = decode_jwt(qr_data)
        data_dict = json.loads(decoded_data['data'])
        result = {
            'SellerGstin': data_dict['SellerGstin'],
            'BuyerGstin': data_dict['BuyerGstin'],
            'DocNo': data_dict['DocNo'],
            'DocTyp': data_dict['DocTyp'],
            'DocDt': data_dict['DocDt'],
            'TotInvVal': data_dict['TotInvVal'],
            'ItemCnt': data_dict['ItemCnt'],
            'MainHsnCode': data_dict['MainHsnCode'],
            'Irn': data_dict['Irn'],
            'IrnDt': data_dict['IrnDt'],
            's3_link': s3_url
        }
        return result
    except ValueError as e:
        print(f"Error processing QR data: {str(e)}")
        return None
def process_pdf_from_s3(s3_bucket, s3_key,s3_url):
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    pdf_data = response['Body'].read()
    qr_data_list = extract_qr_data_from_pdf(pdf_data)
    results = []
    for qr_data in qr_data_list:
        result = process_qr_data(qr_data,s3_url)
        results.append(result)
    return results

from fastapi import FastAPI
from pydantic import BaseModel

from fastapi import FastAPI, Body
from pydantic import BaseModel

class S3Link(BaseModel):
    s3_url: str


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],  # Include "OPTIONS" in the allowed methods
    allow_headers=["*"],
)

@app.get("/process_qr_data")
async def process_pdf_from_s3():
        s3_url = 'https://qr-ocr-data.s3.ap-south-1.amazonaws.com/Abbott/Hard_Disk/20.10.2023/Akums/5100417682.PDF'
        try:
            s3_bucket = urlparse(s3_url).netloc.split('.')[0]
            s3_key = urlparse(s3_url).path.lstrip('/')
            response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
            pdf_data = response['Body'].read()
            qr_data_list = extract_qr_data_from_pdf(pdf_data)
            results = []
            for qr_data in qr_data_list:
                result = process_qr_data(qr_data, s3_url)
                results.append(result)
            print(result)
            return results
        except Exception as e:
            print(f"Error processing PDF from S3: {str(e)}")
            return {"error": "Internal Server Error"}
# process_pdf_from_s3('https://qr-ocr-data.s3.ap-south-1.amazonaws.com/Abbott/Hard_Disk/20.10.2023/Akums/5100417682.PDF')

# from fastapi import FastAPI

# app = FastAPI()

# from fastapi import FastAPI
# from fastapi.responses import JSONResponse

# app = FastAPI()

@app.get("/test")
async def process_qr_data_api():
    result = "hello"
    # response = JSONResponse(content=result)
    return result

