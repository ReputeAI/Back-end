# Back-end

## Quickstart

1. Copy `.env.example` to `.env` and adjust as needed.
2. Start services:

   ```bash
   docker-compose up --build -d
   ```

3. Apply database migrations:

   ```bash
   docker-compose exec web alembic upgrade head
   ```

4. Seed demo data:

   ```bash
   docker-compose exec web python -m reputeai.app.seed
   ```

5. Create an additional superuser if desired.

The API will be available at `http://localhost:8000` with interactive docs at `/docs`.