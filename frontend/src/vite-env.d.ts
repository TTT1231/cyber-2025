/// <reference types="vite/client" />

interface ImportMetaEnv {
   readonly VITE_APP_Test1: string;
   readonly VITE_APP_Test2: string;
   readonly VITE_APP_Test3: string;
   readonly VITE_API_BASE_URL: string;
}

//如果您需要声明import.meta上存在给定的属性，则可以通过接口合并来增强此类型。
interface ImportMeta {
   readonly env: ImportMetaEnv;
}
