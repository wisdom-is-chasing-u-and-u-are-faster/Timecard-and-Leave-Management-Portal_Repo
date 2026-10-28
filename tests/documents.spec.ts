import { Test, TestingModule } from '@nestjs/testing';
import { DocumentsController } from '../src/modules/documents/documents.controller';
import { DocumentsService } from '../src/modules/documents/documents.service';
import { AuthModule } from '../src/modules/auth/auth.module';

describe('DocumentsController', () => {
  let controller: DocumentsController;
  let service: DocumentsService;

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      imports: [AuthModule],
      controllers: [DocumentsController],
      providers: [DocumentsService],
    }).compile();

    controller = module.get<DocumentsController>(DocumentsController);
    service = module.get<DocumentsService>(DocumentsService);
  });

  it('should list employee documents in secure vault', async () => {
    const res = await controller.findAll('emp-002');
    expect(res).toBeDefined();
    expect(res.items.length).toBeGreaterThanOrEqual(2);
  });

  it('should generate a 15-minute signed upload URL for GCS', async () => {
    const res = await controller.getUploadUrl({
      fileName: 'passport_scan.pdf',
      category: 'Identification',
      mimeType: 'application/pdf',
      employeeId: 'emp-002',
    });
    expect(res).toBeDefined();
    expect(res.uploadUrl).toContain('storage.googleapis.com');
    expect(res.expiresInSeconds).toBe(900);
  });

  it('should generate a 15-minute signed download URL for an existing file', async () => {
    const res = await controller.getDownloadUrl('doc-001');
    expect(res).toBeDefined();
    expect(res.downloadUrl).toContain('storage.googleapis.com');
    expect(res.expiresInSeconds).toBe(900);
  });
});
