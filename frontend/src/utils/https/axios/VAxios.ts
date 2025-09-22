import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { formatToDateTime, dateUtil } from '@/utils/dateUtils';

//模块声明
declare module 'axios' {
   interface AxiosRequestConfig {
      metaData?: {
         retryCount: number;
         startTime: string; // 改为字符串类型，存储 Day.js 格式化后的时间
      };
   }
}

export interface RequestResult<T = unknown> {
   data: T;
   status: number;
   statusText: string;
   headers: Record<string, unknown>;
   config: AxiosRequestConfig;
}

interface RequestRetryMeta {
   /**请求失败重试次数，默认1次 */
   retryCount?: number;
   /**请求失败重试间隔，默认100ms */
   retryDelay?: number;
   /**是否开启请求重试，默认开启 */
   retryEnabled?: boolean;
}
interface VAxiosConfig extends AxiosRequestConfig {
   meta?: RequestRetryMeta;
}

export class VAxios {
   private axiosInstance: AxiosInstance;
   private readonly config: VAxiosConfig;

   constructor(config: VAxiosConfig) {
      this.config = {
         meta: {
            retryCount: 1,
            retryDelay: 100,
            retryEnabled: true,
            ...config.meta,
         },
         ...config,
      };
      this.axiosInstance = axios.create(config);
      this.setupInterceptors();
   }

   //设置拦截器
   private setupInterceptors(): void {
      // 请求拦截器
      this.axiosInstance.interceptors.request.use(
         config => {
            // 可以在这里添加 token、请求头等

            // 只在首次请求时初始化 metaData，避免覆盖重试请求的数据
            if (!config.metaData) {
               config.metaData = {
                  retryCount: 0,
                  startTime: formatToDateTime(),
               };
            }
            return config;
         },
         error => {
            return Promise.reject(error);
         }
      );

      // 响应拦截器
      this.axiosInstance.interceptors.response.use(
         (response: AxiosResponse) => {
            return response;
         },
         async error => {
            // 统一错误处理和重试
            return this.handleErrorWithRetry(error);
         }
      );
   }
   /**
    * @description 合并默认配置和请求配置
    * @param requestConfig - 请求配置
    * @returns 合并后的配置
    */
   private mergeConfig(requestConfig?: AxiosRequestConfig): AxiosRequestConfig {
      if (!requestConfig) {
         const { meta, ...defaultConfig } = this.config;
         return defaultConfig;
      }

      const { meta, ...baseConfig } = this.config;

      // 使用 Object.entries 和 reduce 过滤 undefined 值
      const validRequestConfig = Object.entries(requestConfig).reduce(
         (acc, [key, value]) => {
            if (value !== undefined) {
               acc[key] = value;
            }
            return acc;
         },
         {} as Record<string, unknown>
      );

      return {
         ...baseConfig,
         ...validRequestConfig,
      };
   }

   /**
    * @description 处理错误并实现重试逻辑
    * @param error - 请求错误
    * @returns Promise
    */
   private async handleErrorWithRetry(
      error: Error & { config?: AxiosRequestConfig; response?: AxiosResponse }
   ): Promise<unknown> {
      const { config } = error;

      // 确保 config 存在
      if (!config) {
         return this.handleError(error);
      }

      // 检查是否应该重试
      if (!this.shouldRetry(error, config)) {
         return this.handleError(error);
      }

      // 增加重试计数
      config.metaData = config.metaData || {
         retryCount: 0,
         startTime: formatToDateTime(),
      };
      config.metaData.retryCount += 1;

      const currentTime = formatToDateTime();
      const elapsedTime = dateUtil().diff(
         dateUtil(config.metaData.startTime),
         'millisecond'
      );

      console.warn(
         `[${currentTime}] 请求重试 ${config.metaData.retryCount}/${this.config.meta?.retryCount}: ${config.method?.toUpperCase()} ${config.url} (已耗时: ${elapsedTime}ms)`
      );

      // 等待重试延迟
      await this.delay(this.getRetryDelay(config.metaData.retryCount));

      // 重新发送请求
      try {
         return await this.axiosInstance.request(config);
      } catch (retryError) {
         // 递归处理重试错误，需要类型断言
         const typedRetryError = retryError as Error & {
            config?: AxiosRequestConfig;
            response?: AxiosResponse;
         };
         return this.handleErrorWithRetry(typedRetryError);
      }
   }

   /**
    * @description 判断是否应该重试
    * @param error - 错误对象
    * @param config - 请求配置
    * @returns 是否应该重试
    */
   private shouldRetry(
      error: Error & { config?: AxiosRequestConfig; response?: AxiosResponse },
      config: AxiosRequestConfig
   ): boolean {
      // 检查重试是否启用
      if (!this.config.meta?.retryEnabled) {
         return false;
      }

      // 检查是否还有重试次数
      const currentRetryCount = config?.metaData?.retryCount || 0;
      if (currentRetryCount >= (this.config.meta?.retryCount || 1)) {
         return false;
      }

      // 检查错误类型是否可重试
      if (!this.isRetryableError(error)) {
         return false;
      }

      return true;
   }

   /**
    * @description 判断错误是否可重试
    * @param error - 错误对象
    * @returns 是否可重试
    */
   private isRetryableError(
      error: Error & {
         config?: AxiosRequestConfig;
         response?: AxiosResponse;
         code?: string;
      }
   ): boolean {
      // 网络错误或请求超时
      if (
         error.code === 'ENOTFOUND' ||
         error.code === 'ETIMEDOUT' ||
         error.code === 'ECONNRESET'
      ) {
         return true;
      }

      // 没有响应（网络问题）
      if (!error.response) {
         return true;
      }

      // 5xx 服务器错误
      const status = error.response.status;
      if (status >= 500 && status < 600) {
         return true;
      }

      // 特定的 4xx 错误可以重试
      const retryableStatusCodes = [408, 429]; // 请求超时、请求过多
      if (retryableStatusCodes.includes(status)) {
         return true;
      }

      return false;
   }

   /**
    * @description 获取重试延迟时间（支持指数退避）
    * @param retryCount - 当前重试次数
    * @returns 延迟时间（毫秒）
    */
   private getRetryDelay(retryCount: number): number {
      const baseDelay = this.config.meta?.retryDelay || 100;
      // 指数退避：第一次重试 100ms，第二次 200ms，第三次 400ms...
      return baseDelay * Math.pow(2, retryCount - 1);
   }

   /**
    * @description 延迟函数
    * @param ms - 延迟毫秒数
    * @returns Promise
    */
   private delay(ms: number): Promise<void> {
      return new Promise(resolve => setTimeout(resolve, ms));
   }

   private handleError(
      error: Error & {
         config?: AxiosRequestConfig;
         response?: AxiosResponse;
         request?: unknown;
      }
   ): Promise<never> {
      const config = error.config;
      const retryInfo = config?.metaData
         ? ` (重试 ${config.metaData.retryCount}/${this.config.meta?.retryCount} 次后失败)`
         : '';

      // 计算请求总耗时
      const timeInfo = config?.metaData?.startTime
         ? ` [耗时: ${dateUtil().diff(dateUtil(config.metaData.startTime), 'millisecond')}ms]`
         : '';

      // 错误处理逻辑
      if (error.response) {
         // 服务器响应错误
         console.error(
            `Response error${retryInfo}${timeInfo}:`,
            error.response.status,
            error.response.data
         );
      } else if (error.request) {
         // 请求发送失败
         console.error(`Request error${retryInfo}${timeInfo}:`, error.request);
      } else {
         // 其他错误
         console.error(`Error${retryInfo}${timeInfo}:`, error.message);
      }
      return Promise.reject(error);
   }

   getAxiosInstance(): AxiosInstance {
      return this.axiosInstance;
   }

   getAxiosInstanceConfig(): VAxiosConfig {
      return {
         ...this.config,
      };
   }

   async request<T = unknown>(
      config?: AxiosRequestConfig
   ): Promise<RequestResult<T>> {
      const mergedConfig = this.mergeConfig(config);
      const response = await this.axiosInstance.request(mergedConfig);
      return this.transformResponse(response);
   }

   async get<T = unknown>(
      config?: AxiosRequestConfig
   ): Promise<RequestResult<T>> {
      const mergedConfig = this.mergeConfig(config);
      const response = await this.axiosInstance.request({
         ...mergedConfig,
         method: 'GET',
      });
      return this.transformResponse(response);
   }

   async post<T = unknown>(
      config?: AxiosRequestConfig
   ): Promise<RequestResult<T>> {
      const mergedConfig = this.mergeConfig(config);
      const response = await this.axiosInstance.request({
         ...mergedConfig,
         method: 'POST',
      });
      return this.transformResponse(response);
   }

   async put<T = unknown>(
      config?: AxiosRequestConfig
   ): Promise<RequestResult<T>> {
      const mergedConfig = this.mergeConfig(config);
      const response = await this.axiosInstance.request({
         ...mergedConfig,
         method: 'PUT',
      });
      return this.transformResponse(response);
   }

   async delete<T = unknown>(
      config?: AxiosRequestConfig
   ): Promise<RequestResult<T>> {
      const mergedConfig = this.mergeConfig(config);
      const response = await this.axiosInstance.request({
         ...mergedConfig,
         method: 'DELETE',
      });
      return this.transformResponse(response);
   }

   private transformResponse<T>(response: AxiosResponse<T>): RequestResult<T> {
      return {
         data: response.data,
         status: response.status,
         statusText: response.statusText,
         headers: response.headers,
         config: response.config,
      };
   }

   /**
    * @description 批量设置多个默认请求头，将其自动添加到后续http请求中
    */
   setDefaultHeaders(headers: Record<string, string>): void {
      Object.assign(this.axiosInstance.defaults.headers.common, headers);
   }

   /**
    * @description JWT中Bearer令牌设置
    * @param token - JWT令牌
    */
   setAuthToken(token: string): void {
      this.axiosInstance.defaults.headers.common['Authorization'] =
         `Bearer ${token}`;
   }

   /**
    * @description 清除认证令牌
    */
   clearAuthToken(): void {
      delete this.axiosInstance.defaults.headers.common['Authorization'];
   }

   /**
    * @description 移除特定头部
    * @param key - 头部键名
    */
   removeHeader(key: string): void {
      delete this.axiosInstance.defaults.headers.common[key];
   }

   /**
    * @description 获取当前头部配置
    * @returns 当前头部对象的副本
    */
   getCurrentHeaders(): Record<string, unknown> {
      return {
         ...this.axiosInstance.defaults.headers.common,
      };
   }

   /**
    * @description 更新重试配置
    * @param retryConfig - 重试配置
    */
   updateRetryConfig(retryConfig: Partial<RequestRetryMeta>): void {
      if (this.config.meta) {
         Object.assign(this.config.meta, retryConfig);
      }
   }

   /**
    * @description 获取当前重试配置
    * @returns 重试配置的副本
    */
   getRetryConfig(): RequestRetryMeta | undefined {
      return this.config.meta
         ? {
              ...this.config.meta,
           }
         : undefined;
   }
}
