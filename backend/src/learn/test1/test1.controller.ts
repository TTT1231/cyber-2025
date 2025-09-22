import {
   Controller,
   Get,
   Post,
   Body,
   Patch,
   Param,
   Delete,
   CanActivate,
   NestInterceptor,
   Injectable,
   type ExecutionContext,
   type CallHandler,
   UseInterceptors,
   ValidationPipe,
} from '@nestjs/common';
import { Test1Service } from './test1.service';
import { CreateTest1Dto, MyExtendDTO } from './dto/create-test1.dto';
import { UpdateTest1Dto } from './dto/update-test1.dto';
import { Observable } from 'rxjs';
import { tap } from 'rxjs/operators';

@Injectable()
export class LoggingInterceptor implements NestInterceptor {
   intercept(context: ExecutionContext, next: CallHandler): Observable<any> {
      console.log('Before 方法执行');

      const now = Date.now();

      // 👇 核心：调用 next.handle()，它返回一个 Observable
      return next.handle().pipe(
         tap(() => {
            console.log(`After 方法执行，耗时：${Date.now() - now}ms`);
         }),
      );
   }
}

@UseInterceptors(LoggingInterceptor)
@Controller('test1')
export class Test1Controller {
   constructor(private readonly test1Service: Test1Service) {}

   @Post()
   create(@Body(new ValidationPipe()) myDTO: MyExtendDTO) {
      // console.log('myDTO:', typeof myDTO.age);
      return this.test1Service.findAll();
   }

   @Get()
   findAll() {
      return this.test1Service.findAll();
   }

   @Get(':id')
   findOne(@Param('id') id: string) {
      return this.test1Service.findOne(+id);
   }

   @Patch(':id')
   update(@Param('id') id: string, @Body() updateTest1Dto: UpdateTest1Dto) {
      return this.test1Service.update(+id, updateTest1Dto);
   }

   @Delete(':id')
   remove(@Param('id') id: string) {
      return this.test1Service.remove(+id);
   }
}
