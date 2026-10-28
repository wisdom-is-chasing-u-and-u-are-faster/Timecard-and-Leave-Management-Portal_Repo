import { Injectable } from '@nestjs/common';

@Injectable()
export class HealthService {
  check() {
    return {
      status: 'ok',
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      database: 'connected',
      cloudRun: {
        region: process.env.GCP_REGION || 'us-central1',
        ready: true,
      },
    };
  }
}
