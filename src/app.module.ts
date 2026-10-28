import { Module } from '@nestjs/common';
import { HealthModule } from './modules/health/health.module';
import { AuthModule } from './modules/auth/auth.module';
import { EmployeesModule } from './modules/employees/employees.module';
import { LeaveModule } from './modules/leave/leave.module';
import { AttendanceModule } from './modules/attendance/attendance.module';
import { DocumentsModule } from './modules/documents/documents.module';
import { PayrollModule } from './modules/payroll/payroll.module';
import { DashboardModule } from './modules/dashboard/dashboard.module';

@Module({
  imports: [
    HealthModule,
    AuthModule,
    EmployeesModule,
    LeaveModule,
    AttendanceModule,
    DocumentsModule,
    PayrollModule,
    DashboardModule,
  ],
})
export class AppModule {}
