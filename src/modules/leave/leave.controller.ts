import { Controller, Get, Post, Put, Body, Param, Query, UseGuards } from '@nestjs/common';
import { LeaveService } from './leave.service';
import { CreateLeaveRequestDto } from './dto/create-leave-request.dto';
import { JwtAuthGuard } from '../auth/jwt.guard';

@Controller('api/v1/leave')
@UseGuards(JwtAuthGuard)
export class LeaveController {
  constructor(private readonly leaveService: LeaveService) {}

  @Get('balances')
  async getBalances(@Query('employeeId') employeeId?: string) {
    return this.leaveService.getBalances(employeeId);
  }

  @Get('requests')
  async getRequests(@Query('employeeId') employeeId?: string) {
    return this.leaveService.getRequests(employeeId);
  }

  @Post('requests')
  async createRequest(@Body() dto: CreateLeaveRequestDto) {
    return this.leaveService.createRequest(dto);
  }

  @Put('requests/:id/status')
  async updateStatus(
    @Param('id') id: string,
    @Body() body: { status: 'APPROVED' | 'REJECTED'; comment?: string },
  ) {
    return this.leaveService.updateStatus(id, body.status, body.comment);
  }
}
