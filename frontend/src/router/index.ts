import { createWebHistory, createRouter } from 'vue-router';
const routes = [
   // 配置默认路由
   {
      path: '/',
      name: 'home',
      component: () => import('@/views/index.vue'),
   },
   {
      path: '/ai-role-home',
      name: 'ai-role-display',
      component: () => import('@/views/role-display/index.vue'),
   },
];

export const router = createRouter({
   history: createWebHistory(),
   routes,
});
