import { Test, TestingModule } from '@nestjs/testing';
import { EmployeesController } from '../src/modules/employees/employees.controller';
import { EmployeesService } from '../src/modules/employees/employees.service';
import { AuthModule } from '../src/modules/auth/auth.module';

describe('EmployeesController', () => {
  let controller: EmployeesController;
  let service: EmployeesService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [AuthModule],
      controllers: [EmployeesController],
      providers: [EmployeesService],
    }).compile();

    controller = module.get<EmployeesController>(EmployeesController);
    service = module.get<EmployeesService>(EmployeesService);
  });

  it('should list all active employees in directory', async () => {
    const res = await controller.findAll({});
    expect(res).toBeDefined();
    expect(res.items.length).toBeGreaterThanOrEqual(3);
    expect(res.total).toBeGreaterThanOrEqual(3);
  });

  it('should search employees by department', async () => {
    const res = await controller.findAll({ department: 'Engineering' });
    expect(res.items.every((e) => e.department === 'Engineering')).toBe(true);
  });

  it('should retrieve a single employee profile with reporting manager', async () => {
    const emp = await controller.findOne('emp-002');
    expect(emp).toBeDefined();
    expect(emp.employeeId).toBe('EMP-1002');
    expect(emp.manager).toBeDefined();
    expect(emp.manager?.id).toBe('emp-001');
  });

  it('should create a new employee profile record', async () => {
    const created = await controller.create({
      employeeId: 'EMP-9999',
      firstName: 'Taylor',
      lastName: 'Swift',
      email: 'taylor.swift@enterprise-hrms.internal',
      title: 'Staff Architect',
      department: 'Engineering',
    });
    expect(created).toBeDefined();
    expect(created.employeeId).toBe('EMP-9999');
  });
});
