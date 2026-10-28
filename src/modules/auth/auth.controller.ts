import { Controller, Get, Post, Body, UseGuards, Request } from '@nestjs/common';
import { AuthService } from './auth.service';
import { JwtAuthGuard } from './jwt.guard';

@Controller('api/v1/auth')
export class AuthController {
  constructor(private readonly authService: AuthService) {}

  @UseGuards(JwtAuthGuard)
  @Get('me')
  async getMe(@Request() req: any) {
    return this.authService.getProfile(req.user);
  }

  @Post('login')
  async login(@Body() body: { token?: string }) {
    return this.authService.loginWithAzure(body.token || 'mock-azure-token');
  }
}
