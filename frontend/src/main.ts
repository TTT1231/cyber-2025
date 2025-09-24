import { createApp } from 'vue';
import '@/assets/css/tailwind.css';
import App from './App.vue';
import { setupStore } from './store';
import { router } from './router';
import { setupRouterGuard } from './router/guard';
import { setupErrorHandle } from './logics/errorhandler';
import ElementPlusX from 'vue-element-plus-x';

const app = createApp(App);

//配置路由
app.use(router);

//路由守卫
setupRouterGuard(router);

//配置store
setupStore(app);

//注册chat组件
app.use(ElementPlusX);

//配置全局错误处理
setupErrorHandle(app);

app.mount('#app');
