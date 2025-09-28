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

//register
export async function register(userPayload: UserPayloadDTO) {
   return defHttp.post({
      url: apiPath('/api/users/register'),
      data: userPayload,
      metaData: {
         retryCount: 0, // 注册请求不重试
         startTime: '',
      },
   });
}

//update user
export async function updateUser(userPayload: UserPayloadDTO) {
   return defHttp.put({
      url: apiPath('/api/users/profile'),
      data: userPayload,
      metaData: {
         retryCount: 0, // 更新请求不重试
         startTime: '',
      },
   });
}

// src/api/message.ts
export async function sendMessage(data: {
   session_id: number;
   role: number;
   content: string;
   message_type?: string;
   metadata?: Record<string, any>;
}) {
   return defHttp.post({
      url: apiPath('/api/messages/'),
      data,
      metaData: {
         retryCount: 1, // 失败时允许重试一次（可选）
         startTime: new Date().toISOString(),
      },
   });
}

export async function createSession(role_id: number) {
   return defHttp.post({
      url: apiPath('/api/sessions/'),
      data: { role_id },
      metaData: {
         retryCount: 0, // 不重试
         startTime: new Date().toISOString(),
      },
   });
}
