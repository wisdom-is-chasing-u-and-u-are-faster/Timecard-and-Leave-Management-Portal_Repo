import { Injectable, BadRequestException } from '@nestjs/common';

export interface AttendanceRecord {
  id: string;
  employeeId: string;
  workDate: string;
  checkIn: string;
  checkOut: string | null;
  totalHours: number;
  status: 'IN_PROGRESS' | 'COMPLETED' | 'AUTO_RECONCILED';
}

@Injectable()
export class AttendanceService {
  private records: AttendanceRecord[] = [
    {
      id: 'att-001',
      employeeId: 'emp-002',
      workDate: '2026-10-27',
      checkIn: '2026-10-27T09:00:00Z',
      checkOut: '2026-10-27T17:30:00Z',
      totalHours: 8.5,
      status: 'COMPLETED',
    },
    {
      id: 'att-002',
      employeeId: 'emp-002',
      workDate: '2026-10-28',
      checkIn: '2026-10-28T08:55:00Z',
      checkOut: null,
      totalHours: 0,
      status: 'IN_PROGRESS',
    },
  ];

  async getRecords(employeeId: string = 'emp-002') {
    const list = this.records.filter((r) => r.employeeId === employeeId);
    return {
      records: list,
      total: list.length,
    };
  }

  async checkIn(employeeId: string = 'emp-002', timestamp?: string) {
    const now = timestamp ? new Date(timestamp) : new Date();
    const dateStr = now.toISOString().split('T')[0];

    const existing = this.records.find((r) => r.employeeId === employeeId && r.workDate === dateStr);
    if (existing && existing.status === 'IN_PROGRESS') {
      throw new BadRequestException('Already clocked in for today');
    }

    const record: AttendanceRecord = {
      id: 'att-' + (this.records.length + 1).toString().padStart(3, '0'),
      employeeId,
      workDate: dateStr,
      checkIn: now.toISOString(),
      checkOut: null,
      totalHours: 0,
      status: 'IN_PROGRESS',
    };

    this.records.push(record);
    return record;
  }

  async checkOut(employeeId: string = 'emp-002', timestamp?: string) {
    const now = timestamp ? new Date(timestamp) : new Date();
    const dateStr = now.toISOString().split('T')[0];

    const active = this.records.find(
      (r) => r.employeeId === employeeId && r.workDate === dateStr && r.status === 'IN_PROGRESS',
    );

    if (!active) {
      throw new BadRequestException('No active clock-in found for today');
    }

    active.checkOut = now.toISOString();
    const durationMs = now.getTime() - new Date(active.checkIn).getTime();
    active.totalHours = parseFloat((durationMs / (1000 * 60 * 60)).toFixed(2));
    active.status = 'COMPLETED';

    return active;
  }

  async reconcileMidnightUnclosed() {
    // Automated midnight reconciliation for shifts left unclosed
    const yesterday = new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    let reconciledCount = 0;

    for (const record of this.records) {
      if (record.status === 'IN_PROGRESS' && record.workDate <= yesterday) {
        // Auto-close with default 8 hours cap
        record.checkOut = record.workDate + 'T17:00:00Z';
        record.totalHours = 8.0;
        record.status = 'AUTO_RECONCILED';
        reconciledCount++;
      }
    }

    return { reconciled: reconciledCount };
  }
}
