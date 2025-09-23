<script setup lang="ts">
import { ref } from 'vue';
const open = ref<boolean>(false);

const showModal = () => {
   open.value = true;
};

const handleOk = () => {
   open.value = false;
};

defineExpose({ showModal });
</script>

<template>
   <div>
      <a-modal
         v-model:open="open"
         title="Basic Modal"
         @ok="handleOk"
      >
         <p>Some contents...</p>
         <p>Some contents...</p>
         <p>Some contents...</p>
      </a-modal>
   </div>
</template>

<style scoped></style>
