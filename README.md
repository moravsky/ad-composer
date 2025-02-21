# Ad Composer

Ad Composer is a full-stack application for personalizing landing pages using AI. It consists of a Node.js API with OpenAI integration and a Django web interface.

## System Architecture

- **API**: Node.js backend with OpenAI integration
- **Web Interface**: Django application
- **Database**: PostgreSQL
- **Development/Production**: Docker containerization

## Project Structure

```
ad-composer/
├── api/              # Node.js API
│   ├── src/         # API source code
│   └── package.json # Node.js dependencies
├── web/             # Django web application
│   ├── landing/     # Landing page management
│   ├── templates/   # HTML templates
│   └── manage.py   
├── db/              # Database initialization scripts
└── docker/          # Docker configuration files
```

## API Endpoints

### Get Account Names
- `GET /api/account-names`
  - Returns a list of available account names from the database
  - Response: Array of account names

### Personalize Text
- `POST /api/personalize`
  - Personalizes text content for a specific client using AI
  - Request Body:
    ```json
    {
      "client": "client_name",
      "texts": ["text1", "text2", ...]
    }
    ```
  - Response:
    ```json
    {
      "client": "client_name",
      "originalTexts": ["text1", "text2", ...],
      "personalizedContent": ["personalized1", "personalized2", ...]
    }
    ```

## Prerequisites

- Docker and Docker Compose
- Node.js 18+ (for local development)
- Python 3.9+ (for local development)
- PostgreSQL 16+ (for local development)

## Quick Start with Docker

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ad-composer.git
cd ad-composer
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration including OpenAI API key
```

3. Start the services:
```bash
docker-compose up --build
```

The services will be available at:
- API: http://localhost:8080
- Web Interface: http://localhost:8000

## Local Development Setup

### API Setup

1. Navigate to API directory:
```bash
cd api
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

### Web Setup

1. Navigate to web directory:
```bash
cd web
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run migrations:
```bash
python manage.py migrate
```

5. Start the development server:
```bash
python manage.py runserver
```

## Database Setup

The database is automatically initialized with Docker. For local development:

1. Create PostgreSQL database:
```bash
createdb tofudb
```

2. Run initialization scripts:
```bash
psql -d tofudb -f db/init.sql
```

## Environment Variables

### API Environment Variables
```
NODE_ENV=production
PORT=8080
DB_USER=tofu_user
DB_HOST=db
DB_DATABASE=tofudb
DB_PASSWORD=your_secure_password
DB_PORT=5432
OPENAI_API_KEY=your_openai_api_key
```

### Web Environment Variables
```
DATABASE_URL=postgresql://tofu_user:your_secure_password@db:5432/tofudb
DJANGO_SETTINGS_MODULE=config.settings
DJANGO_SECRET_KEY=your_secure_django_secret
ALLOWED_HOSTS=localhost,127.0.0.1
```

## Production Deployment

The application is configured for deployment using Docker:

```bash
docker-compose up --build
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.