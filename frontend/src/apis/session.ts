//获取sessionId
import { apiPath } from '../utils/apiPath';
import { defHttp } from '../utils/https';
export interface SessionDTO {
   role_id: number;
   id: number;
   last_message_at: string;
   created_at: string;
}
//获取角色列表
export async function getSession(role_id: number) {
   return defHttp.get<SessionDTO>({
      url: apiPath(`/api/sessions/role/${role_id}`),
      metaData: {
         retryCount: 1, // 失败时允许重试一次（可选）
         startTime: new Date().toISOString(),
      },
   });
}
