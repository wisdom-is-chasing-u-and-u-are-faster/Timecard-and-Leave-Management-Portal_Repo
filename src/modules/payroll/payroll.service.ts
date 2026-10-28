import { Injectable, NotFoundException } from '@nestjs/common';

export interface PayrollRecord {
  id: string;
  employeeId: string;
  month: string;
  baseSalary: number;
  allowances: number;
  deductions: number;
  netPay: number;
  status: 'PAID' | 'PROCESSED' | 'PENDING';
  breakdown: {
    housingAllowance: number;
    transportAllowance: number;
    taxDeduction: number;
    pensionDeduction: number;
    healthInsurance: number;
  };
}

@Injectable()
export class PayrollService {
  private records: PayrollRecord[] = [
    {
      id: 'pay-001',
      employeeId: 'emp-002',
      month: '2026-09',
      baseSalary: 11500,
      allowances: 800,
      deductions: 2650,
      netPay: 9650,
      status: 'PAID',
      breakdown: {
        housingAllowance: 500,
        transportAllowance: 300,
        taxDeduction: 2000,
        pensionDeduction: 450,
        healthInsurance: 200,
      },
    },
    {
      id: 'pay-002',
      employeeId: 'emp-002',
      month: '2026-10',
      baseSalary: 11500,
      allowances: 800,
      deductions: 2650,
      netPay: 9650,
      status: 'PAID',
      breakdown: {
        housingAllowance: 500,
        transportAllowance: 300,
        taxDeduction: 2000,
        pensionDeduction: 450,
        healthInsurance: 200,
      },
    },
  ];

  async getLedger(employeeId: string = 'emp-002', year?: string) {
    let list = this.records.filter((r) => r.employeeId === employeeId);
    if (year) {
      list = list.filter((r) => r.month.startsWith(year));
    }
    return {
      records: list,
      total: list.length,
      ytdSummary: {
        totalGross: list.reduce((sum, r) => sum + r.baseSalary + r.allowances, 0),
        totalDeductions: list.reduce((sum, r) => sum + r.deductions, 0),
        totalNet: list.reduce((sum, r) => sum + r.netPay, 0),
      },
    };
  }

  async getPayslip(id: string) {
    const record = this.records.find((r) => r.id === id);
    if (!record) {
      throw new NotFoundException(`Payroll record '${id}' not found`);
    }

    return {
      ...record,
      payslipPdfUrl: `/api/v1/payroll/payslips/${id}/download`,
      generatedAt: new Date().toISOString(),
    };
  }

  async calculateCompensation(baseSalary: number, allowances: number = 0, deductions: number = 0) {
    const netPay = baseSalary + allowances - deductions;
    return {
      baseSalary,
      allowances,
      deductions,
      netPay,
    };
  }
}
