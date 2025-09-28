<script setup lang="ts">
import { register, updateUser } from '@/apis/user';
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
   newPassword: string;
   confirmPassword: string;
}

const formState = reactive<FormState>({
   account: '',
   newPassword: '',
   confirmPassword: '',
});

// 验证密码是否匹配
const validatePassword = () => {
   if (formState.newPassword !== formState.confirmPassword) {
      message.error('两次输入的密码不一致');
      return false;
   }
   return true;
};

const onFinish = async () => {
   try {
      // 先验证密码
      if (!validatePassword()) return;

      // 这里应该是调用重置密码的API，而不是注册API
      // 假设我们有一个 resetPassword 的API
      const res = await updateUser({
         account: formState.account,
         password: formState.newPassword,
         username: formState.account,
         avatar_url: '',
      });

      if (res.status !== 200) {
         throw new Error('密码重置失败');
      }

      message.success({
         content: '密码重置成功，请使用新密码登录',
         duration: 1,
      });

      open.value = false;
      // 清空表单
      formState.account = '';
      formState.newPassword = '';
      formState.confirmPassword = '';
   } catch (error) {
      message.error({
         content: '密码重置失败，请检查账号或稍后重试',
         duration: 1,
      });
   }
};

defineExpose({ showModal });
</script>

<template>
   <div>
      <a-modal
         v-model:open="open"
         title="忘记密码"
         @ok="handleOk"
      >
         <a-form
            :model="formState"
            name="basic"
            :label-col="{ span: 7 }"
            :wrapper-col="{ span: 16 }"
            autocomplete="off"
            @finish="onFinish"
         >
            <a-form-item
               label="账号"
               name="account"
               :rules="[{ required: true, message: '请输入您的账号!' }]"
            >
               <a-input v-model:value="formState.account" />
            </a-form-item>

            <a-form-item
               label="新密码"
               name="newPassword"
               :rules="[{ required: true, message: '请输入您的新密码!' }]"
            >
               <a-input-password v-model:value="formState.newPassword" />
            </a-form-item>

            <a-form-item
               label="确认密码"
               name="confirmPassword"
               :rules="[{ required: true, message: '请再次输入您的新密码!' }]"
            >
               <a-input-password v-model:value="formState.confirmPassword" />
            </a-form-item>

            <a-form-item :wrapper-col="{ offset: 3, span: 20 }">
               <a-button
                  type="primary"
                  html-type="submit"
                  class="w-full"
                  >重置密码</a-button
               >
            </a-form-item>
         </a-form>
      </a-modal>
   </div>
</template>

<style scoped></style>
