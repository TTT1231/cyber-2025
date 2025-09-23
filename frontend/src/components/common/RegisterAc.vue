<script setup lang="ts">
import { ref } from 'vue';
const open = ref<boolean>(false);

const showModal = () => {
   open.value = true;
};

const handleOk = (e: MouseEvent) => {
   console.log(e);
   open.value = false;
};
defineExpose({ showModal });
</script>

<template>
   <a-modal
      v-model:open="open"
      title="Basic Modal"
      @ok="handleOk"
   >
      <p>Some contents...</p>
      <p>Some contents...</p>
      <p>Some contents...</p>
   </a-modal>
</template>

<style scoped></style>
