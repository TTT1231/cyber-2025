<script setup lang="ts">
import AiChat from '@/components/chat/AiChat.vue';
import { ref } from 'vue';

const startChating = ref(false);

//标记聊天的开始
const handleChatStarting = (value: boolean) => {
   startChating.value = value;
};
</script>
<template>
   <div class="flex items-center flex-col h-screen">
      <div
         v-if="!startChating"
         class="py-8"
      >
         <h2>
            Hi~ 我是哈姆雷特 ，可以为你答疑解惑、缓解心情、陪伴你，让你的生活多姿多彩，多点生活
         </h2>
      </div>

      <div class="w-[calc(100%-12px)] md:w-1/2">
         <AiChat @emit:chat-starting="handleChatStarting" />
      </div>
   </div>
</template>
