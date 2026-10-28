import { Test, TestingModule } from '@nestjs/testing';
import { PayrollController } from '../src/modules/payroll/payroll.controller';
import { PayrollService } from '../src/modules/payroll/payroll.service';
import { AuthModule } from '../src/modules/auth/auth.module';

describe('PayrollController', () => {
  let controller: PayrollController;
  let service: PayrollService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [AuthModule],
      controllers: [PayrollController],
      providers: [PayrollService],
    }).compile();

    controller = module.get<PayrollController>(PayrollController);
    service = module.get<PayrollService>(PayrollService);
  });

  it('should retrieve monthly payroll ledger and YTD summary', async () => {
    const res = await controller.getLedger('emp-002');
    expect(res).toBeDefined();
    expect(res.records.length).toBeGreaterThanOrEqual(2);
    expect(res.ytdSummary.totalNet).toBeGreaterThan(0);
  });

  it('should retrieve specific payslip statement with breakdown', async () => {
    const payslip = await controller.getPayslip('pay-001');
    expect(payslip).toBeDefined();
    expect(payslip.month).toBe('2026-09');
    expect(payslip.netPay).toBe(9650);
    expect(payslip.breakdown).toBeDefined();
  });
});
