import { Controller, Get, Post, Body, Query, UseGuards } from '@nestjs/common';
import { AttendanceService } from './attendance.service';
import { JwtAuthGuard } from '../auth/jwt.guard';

@Controller('api/v1/attendance')
@UseGuards(JwtAuthGuard)
export class AttendanceController {
  constructor(private readonly attendanceService: AttendanceService) {}

  @Get()
  async getRecords(@Query('employeeId') employeeId?: string) {
    return this.attendanceService.getRecords(employeeId);
  }

  @Post('check-in')
  async checkIn(@Body() body: { employeeId?: string; timestamp?: string }) {
    return this.attendanceService.checkIn(body.employeeId, body.timestamp);
  }

  @Post('check-out')
  async checkOut(@Body() body: { employeeId?: string; timestamp?: string }) {
    return this.attendanceService.checkOut(body.employeeId, body.timestamp);
  }

  @Post('reconcile')
  async reconcile() {
    return this.attendanceService.reconcileMidnightUnclosed();
  }
}
