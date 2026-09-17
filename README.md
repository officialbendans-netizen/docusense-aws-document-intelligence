# 📄 DocuSense — Serverless Document Intelligence Engine

A fully serverless AI-powered document intelligence application built entirely on AWS. Upload any document or image and the system automatically extracts text, detects key phrases, identifies named entities and analyzes sentiment — all in seconds with zero server management.

![AWS](https://img.shields.io/badge/AWS-Serverless-orange?style=flat-square&logo=amazon-aws)
![Textract](https://img.shields.io/badge/Amazon-Textract-blue?style=flat-square)
![Comprehend](https://img.shields.io/badge/Amazon-Comprehend-purple?style=flat-square)
![Lambda](https://img.shields.io/badge/AWS-Lambda-orange?style=flat-square)
![DynamoDB](https://img.shields.io/badge/Amazon-DynamoDB-blue?style=flat-square)

---

## 🌟 Live Demo

Hosted on Amazon S3 Static Website Hosting — accessible from any browser worldwide.

---

## 🎯 What It Does

DocuSense uses Amazon Textract and Amazon Comprehend to turn any document into structured, analyzable data:

1. **Upload** any JPG, PNG or PDF document
2. **Textract** extracts all text from the document automatically
3. **Comprehend** analyzes the extracted text for:
   - 🔑 Key phrases — most important topics
   - 🏷️ Named entities — People, Organizations, Dates, Locations, Quantities
   - 😊 Sentiment — Positive, Negative, Neutral or Mixed
4. Results saved to **DynamoDB** for permanent storage
5. Everything displayed beautifully in the browser

**Supports multiple files** — upload many documents at once and process them all automatically.

---

## 🏢 Real World Business Use Cases

| Industry | Use Case | Value |
|---|---|---|
| **Finance** | Process invoices and receipts automatically | Eliminate manual data entry |
| **Legal** | Extract key clauses and parties from contracts | Save hours of reading |
| **HR** | Screen CVs and extract candidate information | Process hundreds in minutes |
| **Healthcare** | Digitize patient forms and medical records | Reduce paperwork backlogs |
| **Banking** | Process loan application documents | Speed up approvals |
| **Retail** | Analyze customer feedback letters | Understand sentiment at scale |
| **Education** | Process admission forms and certificates | Automate document verification |

---

## 🏗️ Architecture

```
Browser (S3 Static Frontend)
        ↓
User selects multiple documents
        ↓
Phase 1 — Browser compresses all files automatically
        ↓
Phase 2 — Files sent one by one to API Gateway
        ↓
AWS Lambda (Python 3.12)
        ↓
┌─────────────────┬──────────────────────┐
│   Image Files   │     PDF Files        │
│  (JPG, PNG)     │                      │
│                 │  Saved to S3 first   │
│ Textract Bytes  │  Textract S3Object   │
│    method       │      method          │
└────────┬────────┴──────────┬───────────┘
         │                   │
         └────────┬──────────┘
                  ↓
         Extracted Text
                  ↓
    Amazon Comprehend Analysis
    Key Phrases + Entities + Sentiment
                  ↓
         Amazon DynamoDB
         (Permanent Storage)
                  ↓
    Results returned to browser
```

---

## ☁️ AWS Services Used

| Service | Purpose | Why This Service |
|---|---|---|
| **Amazon S3** | Document storage + frontend hosting | Durable, scalable, serverless |
| **AWS Lambda** | Serverless document processing | No servers — pay per execution |
| **Amazon Textract** | AI text extraction from documents | Handles images, PDFs, forms, tables |
| **Amazon Comprehend** | NLP text analysis | Detects entities, phrases, sentiment |
| **Amazon API Gateway** | REST API endpoint | Managed, scalable, CORS-enabled |
| **Amazon DynamoDB** | Results storage | Fast NoSQL — no server management |
| **AWS IAM** | Secure service permissions | Least privilege access |
| **Amazon CloudWatch** | Logging and monitoring | Real-time debugging and metrics |

---

## ✨ Features

- 📁 **Multiple file upload** — select and process many documents at once
- ⚡ **Auto compression** — images compressed automatically before upload
- 📄 **PDF support** — single-page text PDFs processed via S3
- 🖼️ **Image support** — JPG and PNG documents and photos
- 📝 **Text extraction** — full text extracted from any document
- 😊 **Sentiment analysis** — Positive, Negative, Neutral or Mixed
- 🔑 **Key phrases** — most important topics identified automatically
- 🏷️ **Named entities** — People, Organizations, Dates, Locations detected
- 📊 **Per-document results** — each file gets its own result card
- 💾 **DynamoDB storage** — all results saved permanently
- 🆓 **AWS Free Tier** — runs within free tier limits
- 🔒 **Fully serverless** — zero server management

---

## 📁 Project Structure

```
docusense-aws-document-intelligence/
│
├── frontend/
│   └── index.html                  # Complete frontend — HTML + CSS + JS
│                                   # Multi-file upload with auto-compression
│
├── lambda/
│   └── lambda_function.py          # AWS Lambda backend
│                                   # Handles images and PDFs
│                                   # Textract + Comprehend integration
│
├── architecture/
│   └── architecture.md             # Detailed architecture documentation
│
└── README.md
```

---

## 🚀 How to Deploy

### Prerequisites
- AWS Account (Free Tier works)
- AWS Console access

---

### Step 1 — Create S3 Bucket for uploads
```
Name: document-intelligence-uploads-{yourname}
Block all public access: ON
Versioning: Enable
Encryption: SSE-S3
```

### Step 2 — Create DynamoDB Table
```
Table name: document-intelligence-results
Partition key: documentId (String)
Capacity: On-demand
```

### Step 3 — Create Lambda Function
```
Name: document-intelligence-processor
Runtime: Python 3.12
Timeout: 60 seconds
```

**Attach these IAM policies:**
```
AmazonTextractFullAccess
ComprehendFullAccess
AmazonS3FullAccess
AmazonDynamoDBFullAccess
CloudWatchLogsFullAccess
```

Paste code from `lambda/lambda_function.py` and click Deploy.

### Step 4 — Create API Gateway
```
Type: REST API
Name: document-intelligence-api
Resource: /analyze
Method: POST
Integration: Lambda function
Lambda proxy integration: ON
CORS: Enable
Request body passthrough: When there are no templates defined
Stage: prod
```

### Step 5 — Update Frontend
Open `frontend/index.html` and replace the API_URL:
```javascript
const API_URL = 'https://YOUR_ID.execute-api.us-east-1.amazonaws.com/prod/analyze';
```

### Step 6 — Host Frontend on S3
```
Name: docusense-frontend-{yourname}
Uncheck: Block all public access
Enable: Static website hosting
Index document: index.html
Add public read bucket policy
Upload: index.html
```

---

## 🔧 Technical Details

### File Processing Flow

**Images (JPG, PNG):**
1. Browser compresses image to max 1024x1024 at 80% quality
2. Converted to base64 and sent to API Gateway
3. Lambda decodes and sends bytes directly to Textract
4. Text extracted and sent to Comprehend for analysis

**PDFs:**
1. Browser reads PDF as base64
2. Sent to API Gateway
3. Lambda saves to S3 first
4. Textract reads from S3 using S3Object method
5. Text extracted and sent to Comprehend

### Supported Document Types
- ✅ JPG and PNG images with text
- ✅ Single-page text-based PDFs
- ❌ Multi-page PDFs (use single pages)
- ❌ Scanned image PDFs (convert to JPG first)
- ❌ Password protected PDFs

### Comprehend Analysis
- **Key phrases** — min confidence 70% — top 10 returned
- **Entities** — min confidence 70% — top 10 returned
- **Sentiment** — POSITIVE, NEGATIVE, NEUTRAL or MIXED
- **Text limit** — first 5000 characters analyzed

---

## 🐛 Common Issues and Fixes

| Issue | Cause | Fix |
|---|---|---|
| No file provided | API Gateway body passthrough wrong | Set to When there are no templates defined |
| UnsupportedDocumentException | Multi-page or scanned PDF | Convert to JPG or use single-page PDF |
| Body empty at Lambda | Lambda proxy integration off | Enable Lambda proxy integration |
| CORS error | CORS not properly configured | Enable CORS and redeploy API |
| No text found | Image too blurry or low resolution | Use clearer image with visible text |
| File too large | PDF exceeds API Gateway 10MB limit | Compress or use smaller file |

---

## 🧠 What I Learned Building This

- **Amazon Textract** — two methods: Bytes for images, S3Object for PDFs
- **Amazon Comprehend** — entity detection, key phrase extraction, sentiment analysis
- **API Gateway body passthrough** — critical configuration for receiving request body
- **Lambda proxy integration** — required for headers and body to pass through correctly
- **Multi-file processing** — compress all first then analyze sequentially
- **Error handling** — graceful errors for unsupported formats
- **Real debugging** — CloudWatch logs analysis to find root causes

---

## 📈 Cost Estimate (Free Tier)

| Service | Free Tier | Typical Usage |
|---|---|---|
| Lambda | 1M requests/month | ~$0 |
| API Gateway | 1M calls/month | ~$0 |
| Amazon Textract | 1,000 pages/month free (3 months) | ~$0 |
| Amazon Comprehend | 50,000 units/month | ~$0 |
| S3 | 5GB storage | ~$0 |
| DynamoDB | 25GB storage | ~$0 |
| **Total** | **Within free tier** | **~$0/month** |

---

## 🔮 Future Improvements

- [ ] Multi-page PDF support using async Textract jobs
- [ ] Table extraction from invoices using Textract AnalyzeDocument
- [ ] Export results to CSV or Excel
- [ ] Search through all analyzed documents
- [ ] Amazon Cognito user authentication
- [ ] CloudFront CDN for faster global delivery
- [ ] Email notification when analysis is complete via SNS

---

## 👨‍💻 Author

**Benjamin Asare Danquah**
- 🏆 AWS Certified Cloud Practitioner
- 🌍 Based in Takoradi, Ghana, West Africa
- 💼 GitHub: [@officialbendans-netizen](https://github.com/officialbendans-netizen)
- ☁️ Preparing for AWS Solutions Architect Associate

---

## 📄 License

MIT License — feel free to use, modify and share.

---

*This is Project 3 of my AWS Cloud Portfolio — building real serverless AI applications while preparing for the AWS Solutions Architect Associate certification.*
