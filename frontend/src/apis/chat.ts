//聊天
import { apiPath } from '../utils/apiPath';
import { defHttp } from '../utils/https';
interface ChatDto {
   text: string;
   session_id: number;
   role_name: string;
}

export async function chatApi<T>(data: ChatDto) {
   return defHttp.post<T>({
      url: apiPath('/api/messages/voice'),
      data: data,
      metaData: {
         retryCount: 1, // 失败时允许重试一次（可选）
         startTime: new Date().toISOString(),
      },
   });
}
