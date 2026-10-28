import {
  ExceptionFilter,
  Catch,
  ArgumentsHost,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { Request, Response } from 'express';

@Catch()
export class HttpExceptionFilter implements ExceptionFilter {
  catch(exception: unknown, host: ArgumentsHost) {
    const ctx = host.switchToHttp();
    const response = ctx.getResponse<Response>();
    const request = ctx.getRequest<Request>();

    const status =
      exception instanceof HttpException
        ? exception.getStatus()
        : HttpStatus.INTERNAL_SERVER_ERROR;

    const exceptionResponse =
      exception instanceof HttpException ? exception.getResponse() : null;

    let detail = 'An unexpected error occurred';
    let title = 'Internal Server Error';

    if (typeof exceptionResponse === 'string') {
      detail = exceptionResponse;
    } else if (typeof exceptionResponse === 'object' && exceptionResponse !== null) {
      const resObj = exceptionResponse as any;
      detail = resObj.message || resObj.detail || detail;
      title = resObj.error || title;
    } else if (exception instanceof Error) {
      detail = exception.message;
    }

    // RFC 7807 Problem Details envelope
    response.status(status).json({
      type: 'about:blank',
      title,
      status,
      detail: Array.isArray(detail) ? detail.join(', ') : detail,
      instance: request.url,
      timestamp: new Date().toISOString(),
    });
  }
}
