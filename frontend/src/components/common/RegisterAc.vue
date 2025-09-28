<script setup lang="ts">
import { register } from '@/apis/user';
import { defHttp } from '@/utils/https';
import { message } from 'ant-design-vue';
import { reactive, ref } from 'vue';
const open = ref<boolean>(false);

const showModal = () => {
   open.value = true;
};

const handleOk = () => {
   open.value = false;
};

interface FormState {
   account: string;
   password: string;
}

const formState = reactive<FormState>({
   account: '',
   password: '',
});
const onFinish = async () => {
   try {
      const res = await register({
         username: formState.account,
         account: formState.account,
         avatar_url: '',
         password: formState.password,
      });
      if (res.status !== 200) {
         throw new Error('注册失败');
      } else {
         message.success({
            content: '注册成功，请登录',
            duration: 1,
         });
         open.value = false;
         return;
      }
   } catch {
      message.error({
         content: '注册失败，请稍后重试',
         duration: 1,
      });
      return;
   }
};
defineExpose({ showModal });
</script>

<template>
   <div>
      <a-modal
         v-model:open="open"
         title="注册账号"
         @ok="handleOk"
      >
         <a-form
            :model="formState"
            name="basic"
            :label-col="{ span: 5 }"
            :wrapper-col="{ span: 16 }"
            autocomplete="off"
            @finish="onFinish"
         >
            <a-form-item
               label="Account"
               name="account"
               :rules="[{ required: true, message: 'Please input your account!' }]"
            >
               <a-input v-model:value="formState.account" />
            </a-form-item>

            <a-form-item
               label="Password"
               name="password"
               :rules="[{ required: true, message: 'Please input your password!' }]"
            >
               <a-input-password v-model:value="formState.password" />
            </a-form-item>

            <a-form-item :wrapper-col="{ offset: 1, span: 20 }">
               <a-button
                  type="primary"
                  html-type="submit"
                  class="w-full"
                  >注册</a-button
               >
            </a-form-item>
         </a-form>
      </a-modal>
   </div>
</template>

<style scoped></style>
