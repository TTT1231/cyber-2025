<script setup lang="ts">
import type { SelectValue } from 'ant-design-vue/es/select';
import { ref } from 'vue';
import { reactive } from 'vue';
import ForgetPw from './ForgetPw.vue';
import RegisterAc from './RegisterAc.vue';

import { useRouter } from 'vue-router';

interface FormState {
   username: string;
   password: string;
   remember: boolean;
}
const currentRouter = useRouter();
const formState = reactive<FormState>({
   username: '',
   password: '',
   remember: true,
});

const forgetPwRef = ref<InstanceType<typeof ForgetPw> | null>(null);
const registerAcRef = ref<InstanceType<typeof RegisterAc> | null>(null);

const onFinish = () => {
   currentRouter.push({
      name: 'ai-role-display',
   });
};

const onFinishFailed = (errorInfo: any) => {
   console.log('Failed:', errorInfo);
};
const value1 = ref('student');
const handleChange = (value: SelectValue) => {
   value1.value = value?.toString()!;
};
</script>

<template>
   <div class="w-full h-full flex justify-center flex-col p-3 gap-5">
      <span class="flex flex-col">
         <h1 class="text-3xl font-bold leading-9 tracking-tight lg:text-4xl">欢迎回来 👋🏻</h1>
         <span class="mt-4 text-gray-500">请输入您的账号和密码继续</span>
      </span>

      <div class="flex justify-center w-full">
         <a-form
            :model="formState"
            name="basic"
            :label-col="{ span: 8 }"
            autocomplete="off"
            class="max-w-[400px] w-full"
            @finish="onFinish"
            @finishFailed="onFinishFailed"
         >
            <a-form-item name="role">
               <a-select
                  ref="select"
                  v-model:value="value1"
                  @change="handleChange"
               >
                  <a-select-option value="student">学生</a-select-option>
                  <a-select-option value="other">其他</a-select-option>
               </a-select>
            </a-form-item>
            <a-form-item
               name="username"
               :rules="[{ required: true, message: 'Please input your username!' }]"
            >
               <a-input
                  v-model:value="formState.username"
                  placeholder="请输入用户名"
               />
            </a-form-item>

            <a-form-item
               name="password"
               :rules="[{ required: true, message: 'Please input your password!' }]"
            >
               <a-input-password
                  v-model:value="formState.password"
                  placeholder="请输入密码"
               />
            </a-form-item>

            <a-form-item>
               <div class="flex justify-between items-center">
                  <a-checkbox v-model:checked="formState.remember">记住我</a-checkbox>
                  <span
                     class="text-blue-500 underline cursor-pointer active:scale-95 select-none"
                     @click="forgetPwRef?.showModal()"
                  >
                     忘记密码?
                  </span>
               </div>
            </a-form-item>

            <a-form-item class="w-full">
               <a-button
                  type="primary"
                  html-type="submit"
                  class="w-full active:scale-95"
               >
                  登录
               </a-button>
            </a-form-item>
         </a-form>
      </div>
      <!-- 注册对话框 -->
      <div class="ml-4 flex justify-center">
         还没有账号？
         <span
            class="text-blue-600 cursor-pointer underline active:scale-95 select-none ml-1"
            @click="registerAcRef?.showModal()"
         >
            注册
         </span>
      </div>

      <!-- 忘记密码对话框 -->
      <ForgetPw ref="forgetPwRef" />

      <!-- 注册对话框 -->
      <RegisterAc ref="registerAcRef" />
   </div>
</template>

<style scoped></style>
