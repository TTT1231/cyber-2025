import { createWebHistory, createRouter } from 'vue-router';
const routes = [
   // 配置默认路由
   {
      path: '/',
      name: 'home',
      component: () => import('@/views/index.vue'),
   },
];

export const router = createRouter({
   history: createWebHistory(),
   routes,
});
