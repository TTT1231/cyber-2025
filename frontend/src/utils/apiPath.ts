/**
 * @description API 路径构建工具,自动适配开发环境和生产环境
 * @param endpoint API端点，如 'testjava', 'user/profile'
 * @returns 适合当前环境的API路径
 */
export function apiPath(endpoint: string): string {
   // 去掉开头的斜杠，保证格式统一
   const cleanEndpoint = endpoint.replace(/^\/+/, '');

   // 开发环境：返回完整路径给Vite代理
   // 生产环境：返回相对路径给axios baseURL
   return import.meta.env.MODE === 'development' ? `/api/${cleanEndpoint}` : cleanEndpoint;
}
