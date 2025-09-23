<script setup lang="ts">
const props = defineProps<{
   name: '哈姆雷特' | '苏格拉底' | '哈利波特';
   activeIndex: number;
}>();

const map = {
   哈姆雷特: 'ai-cat.svg',
   苏格拉底: 'ai-dog.svg',
   哈利波特: 'ai-pig.svg',
};
const indexMap = {
   哈姆雷特: 0,
   苏格拉底: 1,
   哈利波特: 2,
};

const emit = defineEmits(['update:activeIndex']);
function setActiveIndex(index: number) {
   emit('update:activeIndex', index);
}
function isActive() {
   return props.activeIndex === indexMap[props.name];
}
</script>

<template>
   <div>
      <div
         class="flex flex-col justify-center items-center border-2 border-gray-200 p-16 gap-8 rounded cursor-pointer hover:shadow-lg transition-all duration-300 ease-in-out"
         @click="setActiveIndex(props.activeIndex)"
         :class="isActive() ? 'ai-card-active' : ''"
      >
         <!-- 圆div -->
         <div
            class="w-40 h-40 rounded-full flex justify-center items-center shadow-lg border-gray-200 select-none"
         >
            <img :src="`images/roles/${map[props.name]}`" />
         </div>

         <span>
            {{ props.name }}
         </span>
      </div>
   </div>
</template>

<style scoped>
.ai-card-active {
   border-color: #e5e7eb; /* 浅灰色边框 */
   border-style: solid;
   box-shadow:
      0 8px 25px rgba(0, 0, 0, 0.1),
      0 0 0 2px rgba(59, 130, 246, 0.1); /* 柔和阴影 + 蓝色光晕 */
   transform: translateY(-2px); /* 轻微上浮效果 */
   background: linear-gradient(145deg, #ffffff, #f8fafc); /* 微妙渐变背景 */
}
</style>
