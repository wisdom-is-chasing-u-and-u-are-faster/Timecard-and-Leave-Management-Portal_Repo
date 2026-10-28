import { Controller, Get, Post, Body, Param, Query, UseGuards } from '@nestjs/common';
import { EmployeesService } from './employees.service';
import { CreateEmployeeDto } from './dto/create-employee.dto';
import { JwtAuthGuard } from '../auth/jwt.guard';

@Controller('api/v1/employees')
@UseGuards(JwtAuthGuard)
export class EmployeesController {
  constructor(private readonly employeesService: EmployeesService) {}

  @Get()
  async findAll(@Query() query: any) {
    return this.employeesService.findAll(query);
  }

  @Get(':id')
  async findOne(@Param('id') id: string) {
    return this.employeesService.findOne(id);
  }

  @Post()
  async create(@Body() dto: CreateEmployeeDto) {
    return this.employeesService.create(dto);
  }
}
