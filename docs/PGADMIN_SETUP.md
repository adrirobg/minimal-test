# pgAdmin Setup for Kairos BCP Development

## Automatic Configuration

The pgAdmin container is pre-configured to automatically connect to the PostgreSQL database when you start the development environment.

## Access Information

- **URL**: http://localhost:8080
- **Email**: admin@kairos.dev
- **Password**: admin

## Pre-configured Database Connection

The following database server is automatically configured:

- **Server Name**: Kairos BCP Development
- **Host**: postgres (Docker container name)
- **Port**: 5432
- **Database**: kairos_bcp_dev
- **Username**: kairos_user
- **Password**: kairos_password (stored in pgpass file)

## Usage

1. Start the development environment: `docker-compose up -d`
2. Wait for all services to be ready (about 30-60 seconds)
3. Open http://localhost:8080 in your browser
4. Log in with the credentials above
5. The database server should already be available in the left panel under "Development > Kairos BCP Development"

## Troubleshooting

If the connection doesn't work automatically:

1. Make sure all containers are running: `docker-compose ps`
2. Check if PostgreSQL is ready: `docker-compose logs postgres`
3. Manually add the server in pgAdmin:
   - Right-click "Servers" > "Create" > "Server"
   - General tab: Name = "Kairos BCP Development"
   - Connection tab: Host = "postgres", Port = 5432, Database = "kairos_bcp_dev", Username = "kairos_user", Password = "kairos_password"

## Features

- Direct access to all tables and data
- Query editor for SQL commands
- Database schema browser
- Performance monitoring
- Backup and restore capabilities