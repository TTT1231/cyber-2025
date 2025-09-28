import { defHttp } from '@/utils/https';
import { apiPath } from '@/utils/apiPath';

export async function login(account: string, password: string) {
   return defHttp.post({
      url: apiPath('/api/users/login'),
      data: { account, password },
      metaData: {
         retryCount: 0, // 登录请求不重试
         startTime: '',
      },
   });
}
