import { Injectable, NotFoundException } from '@nestjs/common';

export interface DocumentRecord {
  id: string;
  employeeId: string;
  fileName: string;
  gcsUri: string;
  category: string;
  mimeType: string;
  fileSize: number;
  isEncrypted: boolean;
  uploadedAt: string;
}

@Injectable()
export class DocumentsService {
  private documents: DocumentRecord[] = [
    {
      id: 'doc-001',
      employeeId: 'emp-002',
      fileName: 'employment_agreement_signed.pdf',
      gcsUri: 'gs://persistent-genai-tf-state/hrms-vault/emp-002/agreement.pdf',
      category: 'Contracts',
      mimeType: 'application/pdf',
      fileSize: 1048576,
      isEncrypted: true,
      uploadedAt: '2026-03-01T10:00:00Z',
    },
    {
      id: 'doc-002',
      employeeId: 'emp-002',
      fileName: 'w4_tax_form_2026.pdf',
      gcsUri: 'gs://persistent-genai-tf-state/hrms-vault/emp-002/w4.pdf',
      category: 'Tax',
      mimeType: 'application/pdf',
      fileSize: 524288,
      isEncrypted: true,
      uploadedAt: '2026-03-05T12:00:00Z',
    },
  ];

  async findAll(employeeId: string = 'emp-002', category?: string) {
    let list = this.documents.filter((d) => d.employeeId === employeeId);
    if (category) {
      list = list.filter((d) => d.category.toLowerCase() === category.toLowerCase());
    }
    return {
      items: list,
      total: list.length,
    };
  }

  async getUploadUrl(dto: { fileName: string; mimeType: string; category: string }, employeeId: string = 'emp-002') {
    const fileKey = `hrms-vault/${employeeId}/${Date.now()}_${dto.fileName}`;
    const bucket = process.env.GCS_BUCKET_NAME || 'persistent-genai-tf-state';
    
    // 15-minute pre-signed upload URL simulation or GCS V4 Signed URL
    const uploadUrl = `https://storage.googleapis.com/${bucket}/${fileKey}?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Expires=900`;

    // Record document placeholder in metadata catalog
    const newDoc: DocumentRecord = {
      id: 'doc-' + (this.documents.length + 1).toString().padStart(3, '0'),
      employeeId,
      fileName: dto.fileName,
      gcsUri: `gs://${bucket}/${fileKey}`,
      category: dto.category || 'General',
      mimeType: dto.mimeType,
      fileSize: 0,
      isEncrypted: true,
      uploadedAt: new Date().toISOString(),
    };
    this.documents.push(newDoc);

    return {
      uploadUrl,
      fileKey,
      documentId: newDoc.id,
      expiresInSeconds: 900,
    };
  }

  async getDownloadUrl(id: string) {
    const doc = this.documents.find((d) => d.id === id);
    if (!doc) {
      throw new NotFoundException(`Document with ID '${id}' not found`);
    }

    const bucket = process.env.GCS_BUCKET_NAME || 'persistent-genai-tf-state';
    const downloadUrl = `https://storage.googleapis.com/${bucket}/${doc.gcsUri.replace('gs://' + bucket + '/', '')}?X-Goog-Algorithm=GOOG4-RSA-SHA256&X-Goog-Expires=900`;

    return {
      downloadUrl,
      fileName: doc.fileName,
      expiresInSeconds: 900,
    };
  }
}
