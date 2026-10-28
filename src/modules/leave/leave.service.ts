import { Injectable, BadRequestException, NotFoundException } from '@nestjs/common';
import { CreateLeaveRequestDto } from './dto/create-leave-request.dto';

export interface LeaveBalance {
  type: string;
  allocated: number;
  used: number;
  remaining: number;
}

export interface LeaveRequest {
  id: string;
  employeeId: string;
  leaveType: string;
  startDate: string;
  endDate: string;
  days: number;
  reason: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  approverComment?: string;
  createdAt: string;
}

@Injectable()
export class LeaveService {
  private balances: Map<string, LeaveBalance[]> = new Map([
    [
      'emp-002',
      [
        { type: 'Paid Time Off (PTO)', allocated: 20, used: 5, remaining: 15 },
        { type: 'Sick Leave', allocated: 10, used: 2, remaining: 8 },
        { type: 'Casual Leave', allocated: 5, used: 0, remaining: 5 },
      ],
    ],
  ]);

  private requests: LeaveRequest[] = [
    {
      id: 'lr-001',
      employeeId: 'emp-002',
      leaveType: 'Paid Time Off (PTO)',
      startDate: '2026-11-10',
      endDate: '2026-11-12',
      days: 3,
      reason: 'Family vacation trip',
      status: 'APPROVED',
      approverComment: 'Approved, enjoy your time off!',
      createdAt: '2026-10-20T10:00:00Z',
    },
    {
      id: 'lr-002',
      employeeId: 'emp-002',
      leaveType: 'Sick Leave',
      startDate: '2026-11-20',
      endDate: '2026-11-20',
      days: 1,
      reason: 'Dental checkup',
      status: 'PENDING',
      createdAt: '2026-10-25T14:30:00Z',
    },
  ];

  async getBalances(employeeId: string = 'emp-002') {
    const balanceList = this.balances.get(employeeId) || [
      { type: 'Paid Time Off (PTO)', allocated: 20, used: 0, remaining: 20 },
      { type: 'Sick Leave', allocated: 10, used: 0, remaining: 10 },
      { type: 'Casual Leave', allocated: 5, used: 0, remaining: 5 },
    ];
    return {
      employeeId,
      balances: balanceList,
    };
  }

  async getRequests(employeeId?: string) {
    let list = this.requests;
    if (employeeId) {
      list = list.filter((r) => r.employeeId === employeeId);
    }
    return {
      items: list,
      total: list.length,
    };
  }

  async createRequest(dto: CreateLeaveRequestDto, empId: string = 'emp-002') {
    const employeeId = dto.employeeId || empId;
    const start = new Date(dto.startDate);
    const end = new Date(dto.endDate);

    if (end < start) {
      throw new BadRequestException('End date cannot precede start date');
    }

    // Overlapping check
    const hasOverlap = this.requests.some(
      (r) =>
        r.employeeId === employeeId &&
        r.status !== 'REJECTED' &&
        new Date(r.startDate) <= end &&
        new Date(r.endDate) >= start,
    );

    if (hasOverlap) {
      throw new BadRequestException('A leave request already exists overlapping these selected dates');
    }

    const diffTime = Math.abs(end.getTime() - start.getTime());
    const days = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;

    // Check balance
    const empBalances = this.balances.get(employeeId) || [];
    const balance = empBalances.find((b) => b.type.toLowerCase() === dto.leaveType.toLowerCase());
    if (balance && balance.remaining < days) {
      throw new BadRequestException(`Insufficient leave balance: requested ${days} days, remaining ${balance.remaining}`);
    }

    const newRequest: LeaveRequest = {
      id: 'lr-' + (this.requests.length + 1).toString().padStart(3, '0'),
      employeeId,
      leaveType: dto.leaveType,
      startDate: dto.startDate,
      endDate: dto.endDate,
      days,
      reason: dto.reason,
      status: 'PENDING',
      createdAt: new Date().toISOString(),
    };

    this.requests.push(newRequest);
    return newRequest;
  }

  async updateStatus(id: string, status: 'APPROVED' | 'REJECTED', comment?: string) {
    const req = this.requests.find((r) => r.id === id);
    if (!req) {
      throw new NotFoundException(`Leave request '${id}' not found`);
    }

    req.status = status;
    if (comment) req.approverComment = comment;

    // If approved, deduct balance
    if (status === 'APPROVED') {
      const empBalances = this.balances.get(req.employeeId);
      if (empBalances) {
        const bal = empBalances.find((b) => b.type.toLowerCase() === req.leaveType.toLowerCase());
        if (bal) {
          bal.used += req.days;
          bal.remaining = Math.max(0, bal.allocated - bal.used);
        }
      }
    }

    return req;
  }
}
