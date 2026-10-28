import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from '../src/app.module';

describe('Enterprise HRMS Platform E2E Smoke Tests', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('GET /health returns 200 OK for Cloud Run probe', () => {
    return request(app.getHttpServer())
      .get('/health')
      .expect(200)
      .expect((res) => {
        expect(res.body.status).toBe('ok');
        expect(res.body.version).toBe('1.0.0');
      });
  });

  it('GET /api/v1/auth/me returns current authenticated session', () => {
    return request(app.getHttpServer())
      .get('/api/v1/auth/me')
      .expect(200)
      .expect((res) => {
        expect(res.body.email).toBeDefined();
        expect(res.body.role).toBeDefined();
      });
  });

  it('GET /api/v1/employees returns employee directory items', () => {
    return request(app.getHttpServer())
      .get('/api/v1/employees')
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body.items)).toBe(true);
        expect(res.body.total).toBeGreaterThanOrEqual(1);
      });
  });

  it('GET /api/v1/leave/balances returns leave quotas', () => {
    return request(app.getHttpServer())
      .get('/api/v1/leave/balances?employeeId=emp-002')
      .expect(200)
      .expect((res) => {
        expect(res.body.balances.length).toBeGreaterThanOrEqual(1);
      });
  });

  it('GET /api/v1/attendance returns clock logs', () => {
    return request(app.getHttpServer())
      .get('/api/v1/attendance?employeeId=emp-002')
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body.records)).toBe(true);
      });
  });

  it('GET /api/v1/documents returns document vault files', () => {
    return request(app.getHttpServer())
      .get('/api/v1/documents?employeeId=emp-002')
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body.items)).toBe(true);
      });
  });

  it('GET /api/v1/payroll/ledger returns compensation summary', () => {
    return request(app.getHttpServer())
      .get('/api/v1/payroll/ledger?employeeId=emp-002')
      .expect(200)
      .expect((res) => {
        expect(Array.isArray(res.body.records)).toBe(true);
        expect(res.body.ytdSummary).toBeDefined();
      });
  });

  it('GET /api/v1/dashboard/metrics returns executive KPI summary', () => {
    return request(app.getHttpServer())
      .get('/api/v1/dashboard/metrics')
      .expect(200)
      .expect((res) => {
        expect(res.body.totalEmployees).toBeDefined();
        expect(res.body.todayAttendanceRate).toBeDefined();
      });
  });
});
