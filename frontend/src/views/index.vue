<script setup lang="ts">
import LoginForm from '@/components/common/LoginForm.vue';

const s = 1;
</script>

<template>
   <div class="grid grid-cols-1 md:grid-cols-[1.5fr_1fr] gap-1 h-screen">
      <!-- 左侧背景 -->
      <div class="hidden md:flex md:flex-col md:justify-center md:items-center login-bg">
         <img
            src="@/assets/images/worker.svg"
            alt="worker"
            class="animate-float h-64 w-2/5 animate-up-down"
         />
         <span class="mt-20 text-1xl text-foreground font-sans lg:text-2xl text-gray-500">
            你好啊，欢迎您！！
         </span>
      </div>

      <!-- 右侧内容 -->
      <div class="flex justify-center items-center w-full">
         <LoginForm />
      </div>
   </div>
</template>

<style scoped>
.login-bg {
   background-image: linear-gradient(
      150deg,
      #07070915 30%,
      hsl(220 90% 56% / 30%) 48%,
      #07070915 64%
   );
}

@keyframes up-down {
   0%,
   100% {
      transform: translateY(0);
   }
   50% {
      transform: translateY(-20px);
   }
}
.animate-up-down {
   animation: up-down 2s ease-in-out infinite;
}
</style>
