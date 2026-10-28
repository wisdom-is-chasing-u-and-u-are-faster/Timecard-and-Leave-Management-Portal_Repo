import { Controller, Get, Post, Body, Param, Query, UseGuards } from '@nestjs/common';
import { DocumentsService } from './documents.service';
import { JwtAuthGuard } from '../auth/jwt.guard';

@Controller('api/v1/documents')
@UseGuards(JwtAuthGuard)
export class DocumentsController {
  constructor(private readonly documentsService: DocumentsService) {}

  @Get()
  async findAll(@Query('employeeId') employeeId?: string, @Query('category') category?: string) {
    return this.documentsService.findAll(employeeId, category);
  }

  @Post('upload-url')
  async getUploadUrl(
    @Body() body: { fileName: string; mimeType: string; category: string; employeeId?: string },
  ) {
    return this.documentsService.getUploadUrl(body, body.employeeId);
  }

  @Get(':id/download-url')
  async getDownloadUrl(@Param('id') id: string) {
    return this.documentsService.getDownloadUrl(id);
  }
}
