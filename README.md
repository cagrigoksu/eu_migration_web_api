# EU Migration Web API

A comprehensive REST API for European migration data analysis, providing endpoints for immigration, emigration, and net migration statistics across European countries.

## Features

- Secure API key authentication
- Comprehensive migration data from Eurostat
- Advanced analytics endpoints (trends, comparisons, correlations)
- Rate limiting and caching
- Interactive API documentation (Swagger)
- Health check endpoints
- Flexible filtering and pagination
- CORS enabled for web applications

## Quick Start

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/cagrigoksu/eu_migration_web_api.git
cd eu_migration_web_api
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # on Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Setup environment variables:**
```bash
cp .env.example .env
# Edit .env with your values
```

5. **Initialize database:**
```bash
python -c "from db.database import init_db; init_db()"
```

6. **Run the application:**
```bash
python app.py
```

The API will be available at `http://localhost:8080`

## Configuration

Edit `.env` file with your configuration:

```env
# Application
SECRET_KEY=secret-key
DEBUG=True
PORT=8080

# Database
DB_ENCRYPTION_KEY=encryption-key

# Admin credentials 
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password
```

### Main Endpoints

#### Migration Data

- `GET /api/migration/data` - Get migration data with filters
- `GET /api/migration/countries` - List available countries
- `GET /api/migration/years` - List available years
- `GET /api/migration/country/{code}` - Get country summary
- `GET /api/migration/year/{year}` - Get year summary
- `GET /api/migration/statistics` - Get overall statistics

#### Analytics

- `GET /api/analytics/trends` - Migration trends over time
- `GET /api/analytics/comparison` - Compare multiple countries
- `GET /api/analytics/top` - Top countries by metric
- `GET /api/analytics/balance` - Migration balance analysis
- `GET /api/analytics/growth` - Year-over-year growth rates
- `GET /api/analytics/correlation` - Correlation analysis
- `GET /api/analytics/distribution` - Distribution statistics

## API Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8080/apidocs/`

## Data Sources

This project uses migration data from Eurostat:

- **Immigration Dataset**: [tps00176](https://ec.europa.eu/eurostat/databrowser/product/page/tps00176)
- **Emigration Dataset**: [tps00177](https://ec.europa.eu/eurostat/databrowser/product/page/tps00177)

## Rate Limiting

Default limits:
- 100 requests per hour per API key
- 1000 requests per day per API key

## Security Features

- Encrypted database (SQLCipher)
- API key authentication
- Rate limiting
- CORS protection
- Input validation
- Error handling
- Request logging

## Support

For issues and questions:
- GitHub Issues: [Create an issue](https://github.com/cagrigoksu/eu_migration_web_api/issues)
- Documentation: See `/apidocs/` endpoint

## Version

Current version: See `version.txt`

## Acknowledgments

- Data provided by Eurostat
- Built with Flask and Pandas
