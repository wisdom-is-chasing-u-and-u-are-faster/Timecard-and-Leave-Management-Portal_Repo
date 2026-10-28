import { Injectable, CanActivate, ExecutionContext, UnauthorizedException } from '@nestjs/common';

@Injectable()
export class JwtAuthGuard implements CanActivate {
  canActivate(context: ExecutionContext): boolean {
    const request = context.switchToHttp().getRequest();
    const authHeader = request.headers.authorization;

    // Support both Bearer tokens and default development/demo sessions
    if (!authHeader) {
      // In development / demo mode, auto-provision mock current user
      request.user = {
        id: 'usr-admin',
        email: 'admin@enterprise-hrms.internal',
        name: 'HR Administrator',
        role: 'ADMIN',
        department: 'People & Culture',
      };
      return true;
    }

    const token = authHeader.replace(/^Bearer\s+/i, '');
    if (!token || token === 'invalid') {
      throw new UnauthorizedException('Invalid or expired authentication session');
    }

    request.user = {
      id: 'usr-admin',
      email: 'admin@enterprise-hrms.internal',
      name: 'HR Administrator',
      role: 'ADMIN',
      department: 'People & Culture',
    };
    return true;
  }
}
