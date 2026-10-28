import { Controller, Get, Param, Query, UseGuards } from '@nestjs/common';
import { PayrollService } from './payroll.service';
import { JwtAuthGuard } from '../auth/jwt.guard';

@Controller('api/v1/payroll')
@UseGuards(JwtAuthGuard)
export class PayrollController {
  constructor(private readonly payrollService: PayrollService) {}

  @Get('ledger')
  async getLedger(@Query('employeeId') employeeId?: string, @Query('year') year?: string) {
    return this.payrollService.getLedger(employeeId, year);
  }

  @Get('payslips/:id')
  async getPayslip(@Param('id') id: string) {
    return this.payrollService.getPayslip(id);
  }
}
