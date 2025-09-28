import { apiPath } from '../utils/apiPath';
import { defHttp } from '../utils/https';
interface RolesDto {
   id: number;
   user_id: number;
   name: string;
   avatar: string;
   preset_prompt: string;
   create_at: string;
}

//获取角色列表
export async function getRoles() {
   return defHttp.get<RolesDto[]>({
      url: apiPath('/api/roles/'),
      metaData: {
         retryCount: 1, // 失败时允许重试一次（可选）
         startTime: new Date().toISOString(),
      },
   });
}
