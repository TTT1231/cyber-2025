import { defineStore } from 'pinia';
import { pinia } from '..';

//用户登录之后，信息存储
export const useGlobalStore = defineStore('gloal-store', {
   state: (): {
      test1: string | null;
   } => ({
      test1: null,
   }),
   getters: {
      getTest1: state => state.test1,
   },
   actions: {
      setTest1(value: string) {
         this.test1 = value;
      },
   },
});

//setup之外使用
export function useGlobalStoreWithOut() {
   return useGlobalStore(pinia);
}
