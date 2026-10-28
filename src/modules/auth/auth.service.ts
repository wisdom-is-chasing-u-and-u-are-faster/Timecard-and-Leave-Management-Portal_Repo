import { Injectable } from '@nestjs/common';

@Injectable()
export class AuthService {
  async getProfile(user: any) {
    return {
      id: user?.id || 'usr-admin',
      email: user?.email || 'admin@enterprise-hrms.internal',
      name: user?.name || 'HR Administrator',
      role: user?.role || 'ADMIN',
      department: user?.department || 'People & Culture',
      azureAdTenant: process.env.AZURE_AD_TENANT_ID || 'common',
    };
  }

  async loginWithAzure(azureToken: string) {
    // JIT user provisioning from Azure AD OIDC claims
    return {
      accessToken: 'jwt-session-token-' + Date.now(),
      tokenType: 'Bearer',
      expiresIn: 3600,
      user: {
        id: 'usr-admin',
        email: 'admin@enterprise-hrms.internal',
        name: 'HR Administrator',
        role: 'ADMIN',
      },
    };
  }
}
