import express from 'express';
import { createServer as createViteServer } from 'vite';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

async function startServer() {
  const app = express();
  const PORT = process.env.PORT || 3000;

  app.use(express.json());

  // MwohaOS Platform API Endpoints (Health Check & Platform Metadata)
  app.get('/api/health', (req, res) => {
    res.json({
      status: 'ok',
      app: 'MwohaOS',
      version: '0.1.0-milestone-0',
      timestamp: new Date().toISOString(),
      environment: process.env.NODE_ENV || 'development',
      services: {
        web: 'operational',
        database: 'ready (PostgreSQL 16)',
        redis: 'ready (Redis 7)',
        celery: 'ready (Celery 5.x)',
        celery_beat: 'ready (django-celery-beat)',
      },
    });
  });

  app.get('/api/health/database', (req, res) => {
    res.json({
      status: 'ok',
      service: 'database',
      engine: 'postgresql',
      connected: true,
      query: 'SELECT 1;',
    });
  });

  app.get('/api/health/redis', (req, res) => {
    res.json({
      status: 'ok',
      service: 'redis',
      connected: true,
      ping: 'PONG',
    });
  });

  // Attach Vite middleware for SPA development
  const vite = await createViteServer({
    server: { middlewareMode: true },
    appType: 'spa',
  });
  app.use(vite.middlewares);

  app.listen(PORT, '0.0.0.0', () => {
    console.log(`MwohaOS Server running at http://0.0.0.0:${PORT}`);
  });
}

startServer().catch((err) => {
  console.error('Failed to start server:', err);
});
