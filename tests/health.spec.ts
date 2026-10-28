import { Test, TestingModule } from '@nestjs/testing';
import { HealthController } from '../src/modules/health/health.controller';
import { HealthService } from '../src/modules/health/health.service';

describe('HealthController', () => {
  let controller: HealthController;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      controllers: [HealthController],
      providers: [HealthService],
    }).compile();

    controller = module.get<HealthController>(HealthController);
  });

  it('should return ok health status for GCP Cloud Run container readiness', () => {
    const res = controller.getHealth();
    expect(res).toBeDefined();
    expect(res.status).toBe('ok');
    expect(res.version).toBe('1.0.0');
    expect(res.database).toBe('connected');
  });
});
