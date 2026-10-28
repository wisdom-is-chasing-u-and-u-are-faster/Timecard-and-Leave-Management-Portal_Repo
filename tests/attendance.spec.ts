import { Test, TestingModule } from '@nestjs/testing';
import { AttendanceController } from '../src/modules/attendance/attendance.controller';
import { AttendanceService } from '../src/modules/attendance/attendance.service';
import { AuthModule } from '../src/modules/auth/auth.module';
import { BadRequestException } from '@nestjs/common';

describe('AttendanceController', () => {
  let controller: AttendanceController;
  let service: AttendanceService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [AuthModule],
      controllers: [AttendanceController],
      providers: [AttendanceService],
    }).compile();

    controller = module.get<AttendanceController>(AttendanceController);
    service = module.get<AttendanceService>(AttendanceService);
  });

  it('should list daily attendance logs', async () => {
    const res = await controller.getRecords('emp-002');
    expect(res).toBeDefined();
    expect(res.records.length).toBeGreaterThanOrEqual(1);
  });

  it('should clock in successfully for a new day', async () => {
    const record = await controller.checkIn({
      employeeId: 'emp-003',
      timestamp: '2026-10-29T09:00:00Z',
    });
    expect(record).toBeDefined();
    expect(record.status).toBe('IN_PROGRESS');
    expect(record.checkIn).toBeDefined();
  });

  it('should clock out and compute working hours', async () => {
    const record = await controller.checkOut({
      employeeId: 'emp-002',
      timestamp: '2026-10-28T17:30:00Z',
    });
    expect(record).toBeDefined();
    expect(record.status).toBe('COMPLETED');
    expect(record.totalHours).toBeGreaterThan(0);
  });

  it('should execute midnight automated reconciliation of unclosed shifts', async () => {
    const res = await controller.reconcile();
    expect(res).toBeDefined();
    expect(res.reconciled).toBeGreaterThanOrEqual(0);
  });
});
