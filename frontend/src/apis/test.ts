import { defHttp } from '@/utils/https';
import { apiPath } from '@/utils/apiPath';

export async function testApi() {
   return defHttp.get({
      url: apiPath('testjava'), // 使用工具函数自动适配环境
   });
}
