import { defineConfig, loadEnv } from 'vite';
import vue from '@vitejs/plugin-vue';
import vueDevTools from 'vite-plugin-vue-devtools';
import Components from 'unplugin-vue-components/vite';
import { AntDesignVueResolver } from 'unplugin-vue-components/resolvers';

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
   const env = loadEnv(mode, process.cwd(), '');

   // 获取代理目标地址
   const proxyTarget = env.VITE_PROXY_TARGET;

   console.log('🚀 Vite 配置:');
   console.log('   模式:', mode);
   console.log('   代理目标:', proxyTarget);
   console.log('   API Base:', env.VITE_API_BASE_URL || '(空字符串)');

   return {
      plugins: [
         vue(),
         vueDevTools(),
         Components({
            resolvers: [AntDesignVueResolver({ importStyle: false })],
         }),
      ],
      resolve: {
         alias: {
            '@': '/src',
         },
      },
      server: {
         proxy: {
            '/api': {
               target: proxyTarget, // 动态设置代理目标
               changeOrigin: true,
               rewrite: path => path.replace(/^\/api/, ''),
               // 添加更多配置选项
               configure: proxy => {
                  proxy.on('error', err => {
                     console.log('❌ 代理错误:', err.message);
                  });
                  proxy.on('proxyReq', (proxyReq, req) => {
                     console.log(
                        '📤 代理请求:',
                        req.method,
                        req.url,
                        '→',
                        proxyTarget
                     );
                  });
                  proxy.on('proxyRes', (proxyRes, req) => {
                     console.log('📥 代理响应:', proxyRes.statusCode, req.url);
                  });
               },
            },
         },
         open: true,
      },
   };
});
