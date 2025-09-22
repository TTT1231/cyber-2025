import { IsNotEmpty } from 'class-validator';

export class MyExtendDTO {
   constructor() {}
   @IsNotEmpty()
   age: number;
}
