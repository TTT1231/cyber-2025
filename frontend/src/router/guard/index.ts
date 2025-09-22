import type { Router } from 'vue-router';

export const setupRouterGuard = (router: Router) => {
   router.beforeEach((to, from, next) => {
      next();
   });

   router.afterEach((to, from, failure) => {
      if (failure) {
         console.error('Failed to navigate:', failure);
      }
   });
};
