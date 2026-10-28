import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';
import { ValidationPipe } from '@nestjs/common';
import { HttpExceptionFilter } from './common/filters/http-exception.filter';
import { NestExpressApplication } from '@nestjs/platform-express';
import { join } from 'path';

async function bootstrap() {
  const app = await NestFactory.create<NestExpressApplication>(AppModule);

  // Serve modern interactive frontend from public/
  app.useStaticAssets(join(__dirname, '..', 'public'));

  // Enable CORS for cloud & local development
  app.enableCors({
    origin: '*',
    methods: 'GET,HEAD,PUT,PATCH,POST,DELETE,OPTIONS',
    credentials: true,
  });

  // Global RFC 7807 problem details filter
  app.useGlobalFilters(new HttpExceptionFilter());

  // Input validation with automatic DTO stripping
  app.useGlobalPipes(
    new ValidationPipe({
      whitelist: true,
      forbidNonWhitelisted: false,
      transform: true,
    }),
  );

  const port = process.env.PORT || 8080;
  await app.listen(port);
  console.log(`🚀 Enterprise HRMS Platform Core listening on port ${port}`);
}

bootstrap();
