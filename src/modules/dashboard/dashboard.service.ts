import { Injectable } from '@nestjs/common';

@Injectable()
export class DashboardService {
  async getMetrics() {
    return {
      totalEmployees: 142,
      pendingLeaveApprovals: 3,
      todayAttendanceRate: 96.4,
      departmentsCount: 8,
      announcements: [
        {
          id: 'ann-1',
          title: 'Annual Benefits Open Enrollment Period',
          date: '2026-11-01',
          category: 'HR Updates',
        },
        {
          id: 'ann-2',
          title: 'GCP Cloud Run Modernization Complete',
          date: '2026-10-28',
          category: 'Engineering',
        },
      ],
      upcomingHolidays: [
        { name: 'Thanksgiving Day', date: '2026-11-26' },
        { name: 'Christmas Day', date: '2026-12-25' },
      ],
    };
  }
}
