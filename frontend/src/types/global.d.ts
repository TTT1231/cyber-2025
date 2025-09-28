declare type Nullable<T> = T | null;

// Error-log information
declare interface ErrorLogInfo {
   // Type of error
   type: ErrorTypeEnum;
   // Error file
   file: string;
   // Error name
   name?: string;
   // Error message
   message: string;
   // Error stack
   stack?: string;
   // Error detail
   detail: string;
   // Error url
   url: string;
   // Error time
   time?: string;
}

declare interface UserPayloadDTO {
   username: string;
   account: string;
   avatar_url: string;
   password: string;
}
