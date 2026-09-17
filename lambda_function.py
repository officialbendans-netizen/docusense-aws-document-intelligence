import boto3
import json
import uuid
import base64
from urllib.parse import unquote_plus
from datetime import datetime

textract = boto3.client('textract')
comprehend = boto3.client('comprehend')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('document-intelligence-results')
s3 = boto3.client('s3')

BUCKET = 'document-intelligence-uploads-benjamin'


def lambda_handler(event, context):
    print("Event keys: " + str(list(event.keys())))
    if 'Records' in event:
        return handle_s3_trigger(event)
    return handle_api_request(event)


def analyze_with_comprehend(text):
    try:
        kp = comprehend.detect_key_phrases(Text=text[:5000], LanguageCode='en')
        key_phrases = [p['Text'] for p in kp['KeyPhrases'] if p['Score'] > 0.7][:10]
        en = comprehend.detect_entities(Text=text[:5000], LanguageCode='en')
        entities = [{'text': e['Text'], 'type': e['Type']} for e in en['Entities'] if e['Score'] > 0.7][:10]
        se = comprehend.detect_sentiment(Text=text[:5000], LanguageCode='en')
        sentiment = se['Sentiment']
        return key_phrases, entities, sentiment
    except Exception as e:
        print("Comprehend error: " + str(e))
        return [], [], 'NEUTRAL'


def extract_text_from_image_bytes(file_bytes):
    resp = textract.detect_document_text(Document={'Bytes': file_bytes})
    lines = [b['Text'] for b in resp['Blocks'] if b['BlockType'] == 'LINE']
    return '\n'.join(lines)


def extract_text_from_s3(key):
    try:
        resp = textract.detect_document_text(
            Document={'S3Object': {'Bucket': BUCKET, 'Name': key}}
        )
        lines = [b['Text'] for b in resp['Blocks'] if b['BlockType'] == 'LINE']
        return '\n'.join(lines)
    except Exception as e:
        error_str = str(e)
        if 'UnsupportedDocument' in error_str or 'InvalidParameter' in error_str:
            raise Exception('UnsupportedDocumentException: ' + error_str)
        raise e


def save_to_dynamodb(doc_id, file_name, full_text, key_phrases, entities, sentiment):
    table.put_item(Item={
        'documentId': doc_id,
        'fileName': file_name,
        'extractedText': full_text[:2000],
        'keyPhrases': key_phrases,
        'entities': entities,
        'sentiment': sentiment,
        'analyzedAt': datetime.now().isoformat(),
        'status': 'analyzed'
    })


def handle_s3_trigger(event):
    try:
        bucket_name = event['Records'][0]['s3']['bucket']['name']
        object_key = unquote_plus(event['Records'][0]['s3']['object']['key'])
        print("S3 trigger: " + object_key)
        full_text = extract_text_from_s3(object_key)
        key_phrases, entities, sentiment = analyze_with_comprehend(full_text)
        doc_id = str(uuid.uuid4())
        save_to_dynamodb(doc_id, object_key, full_text, key_phrases, entities, sentiment)
        return {'statusCode': 200, 'body': json.dumps({'documentId': doc_id, 'extractedText': full_text[:500], 'keyPhrases': key_phrases, 'entities': entities, 'sentiment': sentiment})}
    except Exception as e:
        print("S3 error: " + str(e))
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def handle_api_request(event):
    headers = {'Access-Control-Allow-Origin': '*', 'Access-Control-Allow-Headers': 'Content-Type', 'Access-Control-Allow-Methods': 'POST, OPTIONS'}
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': headers, 'body': ''}
    try:
        raw_body = event.get('body', None)
        if raw_body is None:
            body = {}
        elif isinstance(raw_body, str):
            body = json.loads(raw_body)
        elif isinstance(raw_body, dict):
            body = raw_body
        else:
            body = {}

        file_data = body.get('file', '')
        file_name = body.get('fileName', 'document.jpg')
        file_type = body.get('fileType', 'image/jpeg')

        print("File name: " + str(file_name))
        print("File data length: " + str(len(str(file_data))))

        if not file_data or len(str(file_data)) < 10:
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'No file provided'})}

        if isinstance(file_data, str) and ',' in file_data:
            file_data = file_data.split(',')[1]

        file_bytes = base64.b64decode(file_data)
        print("File bytes: " + str(len(file_bytes)))

        unique_name = str(uuid.uuid4()) + '_' + file_name
        s3.put_object(Bucket=BUCKET, Key=unique_name, Body=file_bytes, ContentType=file_type)
        print("Saved to S3: " + unique_name)

        is_pdf = 'pdf' in file_type.lower() or file_name.lower().endswith('.pdf')

        if is_pdf:
            print("Processing as PDF via S3")
            try:
                full_text = extract_text_from_s3(unique_name)
            except Exception as tex:
                if 'UnsupportedDocument' in str(tex):
                    return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'This PDF could not be processed. Please convert pages to JPG and upload as images instead.'})}
                raise tex
        else:
            print("Processing as image via Bytes")
            full_text = extract_text_from_image_bytes(file_bytes)

        print("Extracted lines: " + str(len(full_text.split('\n'))))

        if not full_text.strip():
            return {'statusCode': 400, 'headers': headers, 'body': json.dumps({'error': 'No text found. Please upload a clearer image or text-based document.'})}

        key_phrases, entities, sentiment = analyze_with_comprehend(full_text)
        doc_id = str(uuid.uuid4())
        save_to_dynamodb(doc_id, unique_name, full_text, key_phrases, entities, sentiment)
        print("Success - documentId: " + doc_id)

        return {'statusCode': 200, 'headers': headers, 'body': json.dumps({'message': 'Success', 'documentId': doc_id, 'extractedText': full_text, 'keyPhrases': key_phrases, 'entities': entities, 'sentiment': sentiment, 'fileName': unique_name})}

    except Exception as e:
        print("API error: " + str(e))
        return {'statusCode': 500, 'headers': headers, 'body': json.dumps({'error': str(e)})}
