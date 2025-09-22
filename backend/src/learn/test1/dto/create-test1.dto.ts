import { IsNotEmpty, ValidatorOptions, IsString, IsDefined } from 'class-validator';
export class CreateTest1Dto {
   constructor() {
      console.log('create dto instance initialized');
   }
   @IsDefined()
   name: number;
}

export class MyExtendDTO extends CreateTest1Dto {
   @IsNotEmpty()
   age: number;
}
