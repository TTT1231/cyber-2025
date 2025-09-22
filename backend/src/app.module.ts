import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { Test1Controller } from './learn/test1/test1.controller';
import { Test1Service } from './learn/test1/test1.service';

@Module({
   imports: [],
   controllers: [AppController, Test1Controller],
   providers: [AppService, Test1Service],
})
export class AppModule {}
