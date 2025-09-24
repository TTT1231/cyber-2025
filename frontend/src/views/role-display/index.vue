<script setup lang="ts">
import AiCard from '@/components/common/ai-card/AiCard.vue';
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const names: Array<'哈姆雷特' | '苏格拉底' | '哈利波特'> = ['哈姆雷特', '苏格拉底', '哈利波特'];
const currentIndex = ref(-1);
const router = useRouter();

function handleGoChat() {
   if (currentIndex.value === -1) {
      alert('请选择一个角色');
      return;
   }
   // 跳转到聊天页面，并传递选中的角色
   const selectedRole = names[currentIndex.value];
   router.push({ path: '/chat', query: { role: selectedRole } });
}
</script>

<template>
   <div class="flex flex-col items-center h-screen gap-8 bg-opacity-80 backdrop-blur-sm">
      <!--TODO title -->
      <span
         class="text-5xl font-black text-gray-800 w-full h-20 flex justify-center items-center tracking-wide border-b border-gray-300"
         style="
            font-family: 'PingFang SC', 'Microsoft YaHei', 'Helvetica Neue', Arial, sans-serif;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
         "
      >
         AI角色扮演
      </span>

      <!--TODO 卡片式机器框子 -->
      <div class="grid grid-cols-1 md:grid-cols-3">
         <div
            v-for="(name, index) in names"
            :key="index"
            class="p-4"
         >
            <AiCard
               :name="name"
               v-model:active-index="currentIndex"
               @click="currentIndex = index"
            />
         </div>
      </div>

      <!--TODO 进入对话按钮  -->
      <span>
         <button
            type="button"
            class="px-24 py-8 font-bold text-xl bg-[conic-gradient(from_var(--shimmer-angle),theme(colors.slate.950)_0%,theme(colors.slate.100)_10%,theme(colors.slate.950)_20%)] animate-[shimmer_2s_linear_infinite] relative rounded-[24px] after:flex after:absolute after:bg-white after:inset-1 after:rounded-[21px] after:content-[attr(aria-label)] after:items-center after:justify-center after:text-gray-700 after:text-xl after:font-bold after:shadow-md cursor-pointer select-none active:scale-95"
            aria-label="进入对话"
            @click="handleGoChat()"
         >
            进入对话
         </button>
      </span>
   </div>
</template>

<style scoped>
@keyframes shimmer {
   0% {
      --shimmer-angle: 0deg;
   }
   100% {
      --shimmer-angle: 360deg;
   }
}
</style>
