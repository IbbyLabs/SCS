# Docker Deployment Guide

## Quick Start (Local Dev)

1. **Copy environment file:**
   ```bash
   cp .env.docker.example .env
   ```

2. **Edit `.env` file and set REQUIRED credentials:**
   - Secret key (SECRET_KEY - min 32 characters)

   For local dev you can disable email verification:
   - DISABLE_EMAIL_VERIFICATION=true

   **Optional configurations:**
   - Database URL (SQLite by default in docker-compose, can use MySQL/PostgreSQL)
   - Cloudinary (for cloud storage instead of local files)
   - TMDB API (for better metadata)
   - MAL Client ID (for anime metadata)
   - Better Stack (for centralized logging)

3. **Build and start:**
   ```bash
   docker-compose up -d
   ```

4. **Initialize database:**
   ```bash
   docker-compose exec app python run.py init-db
   docker-compose exec app python run.py create-roles
   ```

5. **Create admin user (optional):**
   ```bash
   docker-compose exec app python run.py create-admin admin@example.com admin yourpassword
   ```

6. **Access the application:****
   - Application: http://localhost:4949

## Storage

### Database (SQLite by default)
- Database file: `./data/stremio_subtitles.db`
- No additional setup needed
- For MySQL/PostgreSQL, set `DATABASE_URL` in `.env`

### Subtitles (Local by default)
- Stored in: `./subtitles/` directory
- For Cloudinary, set credentials in `.env`

### Logs
- Application logs: `./logs/`

## Minimal Configuration (Local Dev Only)

Only 1 thing is required in `.env`:
```bash
SECRET_KEY=your-random-64-char-hex-string
```

That's it! Email verification can be disabled for local development.

**To enable email verification (Brevo SMTP example):**
```bash
DISABLE_EMAIL_VERIFICATION=false
EMAIL_METHOD=smtp
MAIL_DEFAULT_SENDER="IbbyLabs <noreply@your-domain.com>"
MAIL_SERVER=smtp-relay.brevo.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-brevo-smtp-key
```

Everything else has sensible defaults!

## Production Checklist

Set these in `.env` before deploying:

- `FLASK_ENV=production`
- `SECRET_KEY` (32+ chars)
- `SERVER_NAME=your-domain.com`
- `PREFERRED_URL_SCHEME=https`
- `DATABASE_URL=sqlite:////app/data/stremio_subtitles.db` (local file) or `postgresql://user:password@host:5432/dbname`
- `DISABLE_EMAIL_VERIFICATION=false`
- `EMAIL_METHOD=smtp` (or `resend` / `local_api`)
- `MAIL_DEFAULT_SENDER="IbbyLabs <noreply@your-domain.com>"`
- `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` (for SMTP, Brevo uses smtp-relay.brevo.com)

## Brevo Setup Checklist

1. Verify your sender domain in Brevo (recommended for deliverability).
2. Add and verify the sender email address (must match `MAIL_DEFAULT_SENDER`).
3. Generate an SMTP key in Brevo and use it as `MAIL_PASSWORD`.
4. Use your Brevo SMTP login as `MAIL_USERNAME`.
5. Confirm SPF/DKIM records are published for your domain.

## Commands

**View logs:**
```bash
docker-compose logs -f app
```

**Stop containers:**
```bash
docker-compose down
```

**Restart application:**
```bash
docker-compose restart app
```

**Access application shell:**
```bash
docker-compose exec app bash
```

**Database backup:**
```bash
docker-compose exec db mysqldump -u stremio -p stremio_subtitles > backup.sql
```

## Production Deployment

For production, use a reverse proxy (nginx/Caddy) in front of the application:

```yaml
# Add to docker-compose.yml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./certs:/etc/nginx/certs
    depends_on:
      - app
```

## Environment Variables

See `.env.docker.example` for all available configuration options.

## Volumes

- `db_data` - MariaDB database files (persistent)
- `./logs` - Application logs (mounted from host)

## Troubleshooting

**Database connection issues:**
```bash
docker-compose logs db
docker-compose exec db mysql -u root -p
```

**Application errors:**
```bash
docker-compose logs app
```

**Reset everything:**
```bash
docker-compose down -v
docker-compose up -d
```
