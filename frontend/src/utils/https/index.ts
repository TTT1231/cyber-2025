import { VAxios } from './axios/VAxios';

/**
 * 方案1：统一使用相对路径 + 环境变量
 *
 * 核心思路：
 * - 开发环境：baseURL = '', API调用使用完整路径 '/api/xxx'，让Vite代理处理
 * - 生产环境：baseURL = '/api', API调用使用相对路径 'xxx'，让axios拼接
 */

const isDevelopment = import.meta.env.MODE === 'development';

const baseURL = isDevelopment
   ? '' // 开发环境：空字符串，让Vite代理处理跨域
   : import.meta.env.VITE_API_BASE_URL || '/api'; // 生产环境：API基础路径

// 调试信息
console.log('🚀 API配置:', {
   mode: import.meta.env.MODE,
   baseURL: baseURL || '(空字符串)',
   isDevelopment,
});

export const defHttp = new VAxios({
   baseURL: baseURL,
   timeout: 60 * 1000,
   meta: {
      retryCount: 3,
      retryDelay: 1000,
      retryEnabled: true,
   },
});
