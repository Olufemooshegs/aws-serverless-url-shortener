# URL Shortener — Serverless on AWS

A production-pattern URL shortener built with Terraform and Python.
Supports custom codes, click tracking, TTL-based expiry, and 301 redirects.

## Architecture
# URL Shortener — Serverless on AWS

![Architecture](docs/architecture.png)
text

## Tech Stack

| Layer | Technology |
|---|---|
| Infrastructure as Code | Terraform (≥ 1.5) |
| Cloud provider | AWS (us-east-1) |
| Compute | AWS Lambda (Python 3.12) |
| API | API Gateway (HTTP API v2) |
| Storage | DynamoDB (on-demand, TTL enabled) |
| Static hosting | Amazon S3 |
| State backend | S3 + DynamoDB lock (shared with visitor-counter) |

## Features

- ✅ **Create short URLs** with random or custom codes
- ✅ **301 redirects** with proper `Location` header
- ✅ **Click tracking** via atomic DynamoDB `ADD`
- ✅ **Custom codes** with collision detection (409 response)
- ✅ **TTL support** — links auto-delete when `DEFAULT_TTL_DAYS > 0`
- ✅ **Delete endpoint** with conditional check
- ✅ **Stats endpoint** — clicks, created_at, original URL
- ✅ **Least-privilege IAM** — 4 DynamoDB actions on one table
- ✅ **Remote state** with S3 versioning + DynamoDB locking
- ✅ **Modular Terraform** — 4 reusable modules
- ✅ **Frontend** — polished UI with recent-links persistence

## Endpoints

| Method | Path | Purpose |
|---|---|---|
| POST | `/shorten` | Create a short URL |
| GET | `/{code}` | Redirect to original URL (301) |
| GET | `/stats/{code}` | Get stats: clicks, created_at, URL |
| DELETE | `/{code}` | Delete a short URL |

### Example Requests

```bash
API="https://your-api-id.execute-api.us-east-1.amazonaws.com"

# Create
curl -X POST "$API/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/your-username"}'

# Custom code
curl -X POST "$API/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com", "code": "mylink"}'

# Redirect (301)
curl -s -D - -o /dev/null "$API/abc1234"

# Stats
curl "$API/stats/abc1234"

# Delete
curl -X DELETE "$API/abc1234"
Project Structure
text
.
├── terraform/
│   ├── modules/
│   │   ├── dynamodb/       # Table with TTL on expires_at
│   │   ├── lambda/         # Function + IAM role + log group
│   │   ├── api_gateway/    # HTTP API with 4 routes
│   │   └── s3_website/     # Static site + templating
│   └── environments/
│       └── dev/            # Dev environment consuming the modules
├── lambda/src/
│   ├── config.py           # Env vars
│   ├── shortener.py        # Code generation + DynamoDB ops
│   ├── handlers.py         # One function per endpoint
│   └── index.py            # Router
└── frontend/index.html     # Static site with fetch() API calls
'''
## Deployment
1. Bootstrap Terraform backend (run once)
bash
cd terraform/bootstrap  # from the visitor-counter project
terraform init
terraform apply
2. Configure the dev environment
Edit terraform/environments/dev/backend.tf and set the bucket/table names
from the bootstrap outputs.

3. Deploy
bash
cd terraform/environments/dev
terraform init
terraform plan
terraform apply
4. Test
bash
API=$(terraform output -raw api_endpoint)

curl -X POST "$API/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
Cleanup
bash
cd terraform/environments/dev
terraform destroy
Design Decisions'''

Base62 random codes — 62^7 ≈ 3.5 trillion codes; collisions practically impossible

Atomic conditional writes — attribute_not_exists(code) prevents duplicate codes under concurrency

Retry loop on collision — up to 5 attempts, then fail loudly

BASE_URL derived from the request — breaks a Lambda↔API Gateway dependency cycle, works across stages and custom domains

Best-effort click tracking — analytics failures never block the redirect

Catch-all route / {code} declared last — API Gateway uses longest-prefix match

HTTPS + S3 website endpoint — HTTP only for now; CloudFront would add HTTPS

Shared state backend — one S3 bucket, different key per project

What I Learned
Bootstrapping Terraform state backends and reusing them across projects

Multi-route API Gateway configuration with path parameters

Conditional DynamoDB writes for atomic uniqueness

DynamoDB TTL for automatic data expiry

Circular dependency resolution between Lambda and API Gateway

Templating Terraform + JavaScript syntax collisions

HTTP 301 redirects from a serverless function

License
MIT
