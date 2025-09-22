import { defineStore } from 'pinia';
import { pinia } from '..';
import { formatToDateTime } from '@/utils/dateUtils';
import { ErrorTypeEnum } from '@/enums/errorLog';

export interface ErrorLogState {
   errorLogInfoList: Nullable<ErrorLogInfo[]>;
   errorLogCount: number;
}

export const useErrorLogStore = defineStore('app-error-log', {
   state: (): ErrorLogState => {
      return {
         errorLogInfoList: null,
         errorLogCount: 0,
      };
   },
   getters: {
      getErrorLogInfoList(state): ErrorLogInfo[] {
         return state.errorLogInfoList || [];
      },
      getErrorLogListCount(state): number {
         return state.errorLogCount;
      },
   },
   actions: {
      addErrorLogInfo(info: ErrorLogInfo) {
         const item = {
            ...info,
            time: formatToDateTime(new Date()),
         };
         this.errorLogInfoList = [item, ...(this.errorLogInfoList || [])];
         this.errorLogCount += 1;
      },

      setErrorLogListCount(count: number): void {
         this.errorLogCount = count;
      },

      /**
       * Triggered after ajax request error
       * @param error
       * @returns
       */
      addAjaxErrorInfo(error: any) {
         const errInfo: Partial<ErrorLogInfo> = {
            message: error.message,
            type: ErrorTypeEnum.AJAX,
         };
         if (error.response) {
            const {
               config: {
                  url = '',
                  data: params = '',
                  method = 'get',
                  headers = {},
               } = {},
               data = {},
            } = error.response;
            errInfo.url = url;
            errInfo.name = 'Ajax Error!';
            errInfo.file = '-';
            errInfo.stack = JSON.stringify(data);
            errInfo.detail = JSON.stringify({
               params,
               method,
               headers,
            });
         }
         this.addErrorLogInfo(errInfo as ErrorLogInfo);
      },
   },
});

export function useErrorLogStoreWithOut() {
   return useErrorLogStore(pinia);
}
