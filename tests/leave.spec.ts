import { Test, TestingModule } from '@nestjs/testing';
import { LeaveController } from '../src/modules/leave/leave.controller';
import { LeaveService } from '../src/modules/leave/leave.service';
import { AuthModule } from '../src/modules/auth/auth.module';
import { BadRequestException } from '@nestjs/common';

describe('LeaveController', () => {
  let controller: LeaveController;
  let service: LeaveService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [AuthModule],
      controllers: [LeaveController],
      providers: [LeaveService],
    }).compile();

    controller = module.get<LeaveController>(LeaveController);
    service = module.get<LeaveService>(LeaveService);
  });

  it('should retrieve employee leave balances across types', async () => {
    const res = await controller.getBalances('emp-002');
    expect(res).toBeDefined();
    expect(res.balances.length).toBe(3);
    const pto = res.balances.find((b) => b.type.includes('PTO'));
    expect(pto).toBeDefined();
    expect(pto?.remaining).toBe(15);
  });

  it('should list existing leave requests', async () => {
    const res = await controller.getRequests('emp-002');
    expect(res.items.length).toBeGreaterThanOrEqual(1);
  });

  it('should submit a valid new leave request', async () => {
    const req = await controller.createRequest({
      leaveType: 'Paid Time Off (PTO)',
      startDate: '2026-12-01',
      endDate: '2026-12-03',
      reason: 'Year-end rest',
      employeeId: 'emp-002',
    });
    expect(req).toBeDefined();
    expect(req.status).toBe('PENDING');
    expect(req.days).toBe(3);
  });

  it('should reject overlapping leave requests', async () => {
    await expect(
      controller.createRequest({
        leaveType: 'Paid Time Off (PTO)',
        startDate: '2026-11-10',
        endDate: '2026-11-12',
        reason: 'Duplicate dates',
        employeeId: 'emp-002',
      }),
    ).rejects.toThrow(BadRequestException);
  });

  it('should allow manager to approve a leave request', async () => {
    const updated = await controller.updateStatus('lr-002', {
      status: 'APPROVED',
      comment: 'Approved by manager',
    });
    expect(updated.status).toBe('APPROVED');
    expect(updated.approverComment).toBe('Approved by manager');
  });
});
