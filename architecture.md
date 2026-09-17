# DocuSense — Architecture Details

## Overview
Fully serverless document intelligence. Zero servers. Scales automatically.

## Flow
1. Browser compresses all files automatically
2. Files sent one by one to API Gateway
3. Lambda processes each file
4. Images — Textract Bytes method
5. PDFs — saved to S3 first then Textract S3Object method
6. Comprehend analyzes extracted text
7. Results saved to DynamoDB
8. Frontend displays per-document result cards

## Services
- S3 — document storage and frontend hosting
- Lambda — serverless processing
- Textract — AI text extraction
- Comprehend — NLP analysis
- API Gateway — REST API
- DynamoDB — results storage

## Key Lessons
- Textract Bytes for images — S3Object for PDFs
- API Gateway body passthrough — When there are no templates defined
- Lambda proxy integration must be ON
- Compress images before sending
