import { Injectable, NotFoundException } from '@nestjs/common';
import { CreateEmployeeDto } from './dto/create-employee.dto';

export interface Employee {
  id: string;
  employeeId: string;
  firstName: string;
  lastName: string;
  email: string;
  title: string;
  department: string;
  managerId: string | null;
  status: string;
  hireDate: string;
  directReports?: Employee[];
}

@Injectable()
export class EmployeesService {
  private employees: Employee[] = [
    {
      id: 'emp-001',
      employeeId: 'EMP-1001',
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@enterprise-hrms.internal',
      title: 'Engineering Director',
      department: 'Engineering',
      managerId: null,
      status: 'ACTIVE',
      hireDate: '2022-01-15',
    },
    {
      id: 'emp-002',
      employeeId: 'EMP-1002',
      firstName: 'Jane',
      lastName: 'Smith',
      email: 'jane.smith@enterprise-hrms.internal',
      title: 'Senior Software Engineer',
      department: 'Engineering',
      managerId: 'emp-001',
      status: 'ACTIVE',
      hireDate: '2023-03-01',
    },
    {
      id: 'emp-003',
      employeeId: 'EMP-1003',
      firstName: 'Robert',
      lastName: 'Chen',
      email: 'robert.chen@enterprise-hrms.internal',
      title: 'HR Operations Lead',
      department: 'People & Culture',
      managerId: null,
      status: 'ACTIVE',
      hireDate: '2021-08-20',
    },
  ];

  async findAll(query?: { search?: string; department?: string; status?: string }) {
    let result = [...this.employees];

    if (query?.search) {
      const q = query.search.toLowerCase();
      result = result.filter(
        (e) =>
          e.firstName.toLowerCase().includes(q) ||
          e.lastName.toLowerCase().includes(q) ||
          e.email.toLowerCase().includes(q) ||
          e.employeeId.toLowerCase().includes(q) ||
          e.title.toLowerCase().includes(q),
      );
    }

    if (query?.department) {
      result = result.filter((e) => e.department.toLowerCase() === query.department.toLowerCase());
    }

    if (query?.status) {
      result = result.filter((e) => e.status.toLowerCase() === query.status.toLowerCase());
    }

    return {
      items: result,
      total: result.length,
    };
  }

  async findOne(id: string) {
    const employee = this.employees.find((e) => e.id === id || e.employeeId === id);
    if (!employee) {
      throw new NotFoundException(`Employee with ID '${id}' not found`);
    }

    const manager = employee.managerId
      ? this.employees.find((e) => e.id === employee.managerId) || null
      : null;

    const directReports = this.employees.filter((e) => e.managerId === employee.id);

    return {
      ...employee,
      manager,
      directReports,
    };
  }

  async create(dto: CreateEmployeeDto) {
    const newEmp: Employee = {
      id: 'emp-' + (this.employees.length + 1).toString().padStart(3, '0'),
      employeeId: dto.employeeId,
      firstName: dto.firstName,
      lastName: dto.lastName,
      email: dto.email,
      title: dto.title,
      department: dto.department,
      managerId: dto.managerId || null,
      status: 'ACTIVE',
      hireDate: new Date().toISOString().split('T')[0],
    };

    this.employees.push(newEmp);
    return newEmp;
  }
}
