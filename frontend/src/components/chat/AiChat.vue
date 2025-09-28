<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, useTemplateRef } from 'vue';
import type { BubbleListItemProps, BubbleListProps } from 'vue-element-plus-x/types/BubbleList';
import { createSession, sendMessage } from '@/apis/user';
// 定义消息角色枚举
type MessageRole = 'user' | 'ai';

// 定义模型选项类型
type ModelOption = 'DeepSeek' | 'GPT-4' | 'Claude' | 'Gemini';

// 思考状态类型
type ThinkingStatus = 'start' | 'thinking' | 'end' | 'error';

// 扩展气泡列表项类型，增加自定义属性
interface ChatMessage extends BubbleListItemProps {
   key: number;
   role: MessageRole;
   showThinking?: boolean; // 是否显示思考组件
   thinkingStatus?: ThinkingStatus; // 思考状态
   thinkingContent?: string; // 思考内容
}

const userInputValue = ref('');
const userInputLoading = ref(false);
const isSelectThinking = ref(false);
const showDropdown = ref(false);
const selectedModel = ref<ModelOption>('DeepSeek');
const modelOptions: ModelOption[] = ['DeepSeek', 'GPT-4', 'Claude', 'Gemini'];
const chatArea = useTemplateRef<HTMLDivElement>('chat-content-area');
const userInputArea = useTemplateRef<HTMLDivElement>('user-input-area');

const emits = defineEmits<{
   (e: 'emit:chat-starting', value: boolean): void;
}>();
const props = defineProps<{
   /**
    * @description 对话列表最大高度，超过就显示滚动条
    * @default 400 单位px
    */
   maxHeight?: number;
}>();

// 切换下拉菜单显示状态
const toggleDropdown = (): void => {
   showDropdown.value = !showDropdown.value;
};

// 选择模型
const selectModel = (model: ModelOption): void => {
   selectedModel.value = model;
   showDropdown.value = false;
};

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent): void => {
   const target = event.target as HTMLElement;
   if (!target.closest('.dropdown-container')) {
      showDropdown.value = false;
   }
};

// 消息计数器，用于生成唯一 key
let messageCounter = 0;

// 生成 AI 回答内容
const generateAIResponse = (): string => {
   const responses = [
      `你好很高心认识你，请多多指教 ~ 缘分让我们在这里相遇，期待在接下来的交流中互相学习、共同成长。无论是技术难题还是生活趣事，我都愿意成为你忠实的倾听者和伙伴`,
      `这是一个很棒的问题！让我为你详细解答... 你的思考角度非常独特，这个问题触及到了很多关键细节。我相信通过深入分析，我们不仅能找到解决方案，还能挖掘出更多有价值的知识点。`,
      ` 每一个新技能的学习都是自我提升的宝贵机会，你现在迈出的这一步，正在为未来的成就奠定坚实基础。保持这份热情，你会收获意想不到的成长！`,
   ];
   return responses[Math.floor(Math.random() * responses.length)];
};

// 流式生成AI回答
const generateStreamingAIResponse = (messageKey: number): void => {
   const fullContent = generateAIResponse();
   const messageIndex = list.value.findIndex(msg => msg.key === messageKey);

   if (messageIndex === -1) return;

   // 设置初始状态 - 关闭loading，开启typing和isFog
   list.value[messageIndex].loading = false;
   list.value[messageIndex].typing = true;
   list.value[messageIndex].isFog = true;
   list.value[messageIndex].content = '';

   let currentIndex = 0;
   const streamInterval = setInterval(() => {
      const messageCurrentIndex = list.value.findIndex(msg => msg.key === messageKey);

      if (messageCurrentIndex === -1 || currentIndex >= fullContent.length) {
         clearInterval(streamInterval);
         // 流式生成完成，关闭typing和isFog效果
         if (messageCurrentIndex !== -1) {
            list.value[messageCurrentIndex].typing = false;
            list.value[messageCurrentIndex].isFog = false;
         }
         userInputLoading.value = false;
         return;
      }

      // 逐字符添加内容
      list.value[messageCurrentIndex].content += fullContent[currentIndex];
      currentIndex++;
   }, 50); // 每50ms添加一个字符
};

// 开始思考过程
const startThinkingProcess = (messageKey: number): void => {
   const messageIndex = list.value.findIndex(msg => msg.key === messageKey);
   if (messageIndex === -1) return;

   // 开始思考状态
   list.value[messageIndex].thinkingStatus = 'thinking';

   // 模拟思考过程 - 3秒思考时间
   setTimeout(() => {
      if (messageIndex !== -1 && list.value[messageIndex]) {
         // 思考完成，更新状态和内容
         list.value[messageIndex].thinkingStatus = 'end';
         list.value[messageIndex].thinkingContent =
            '深度思考完成：基于多维度分析和深层推理，我为您提供以下详细解答...';

         // 思考完成后，添加正常的 AI 回答
         setTimeout(() => {
            addNormalAIResponse();
         }, 1000);
      }
   }, 3000); // 3秒思考时间
};

// 添加普通 AI 回答（不带思考）
const addNormalAIResponse = (): void => {
   messageCounter++;
   const aiMessage: ChatMessage = {
      key: messageCounter,
      role: 'ai',
      placement: 'start',
      content: '',
      loading: true,
      shape: 'corner',
      variant: 'filled',
      isMarkdown: false,
      typing: false,
      isFog: false,
      avatarSize: '24px',
      avatarGap: '12px',
   };

   list.value.push(aiMessage);

   // 模拟 AI 思考时间，然后开始流式生成
   setTimeout(() => {
      generateStreamingAIResponse(aiMessage.key);
   }, 1000);
};

// 添加用户消息
const addUserMessage = (content: string): void => {
   messageCounter++;
   const userMessage: ChatMessage = {
      key: messageCounter,
      role: 'user',
      placement: 'end',
      content,
      loading: false,
      shape: 'corner',
      variant: 'outlined',
      isMarkdown: false,
      typing: false,
      isFog: false,
      avatarSize: '24px',
      avatarGap: '12px',
   };
   list.value.push(userMessage);
};

// 添加 AI 消息
const addAIMessage = (): void => {
   messageCounter++;

   // 如果用户选择了深度思考，先添加 Thinking 消息
   if (isSelectThinking.value) {
      const thinkingMessage: ChatMessage = {
         key: messageCounter,
         role: 'ai',
         placement: 'start',
         content: '',
         loading: false,
         shape: 'corner',
         variant: 'filled',
         isMarkdown: false,
         typing: false,
         isFog: false,
         avatarSize: '24px',
         avatarGap: '12px',
         showThinking: true, // 标识这是一个思考消息
         thinkingStatus: 'start', // 思考状态
         thinkingContent: '正在深度思考中...', // 思考内容
      };

      list.value.push(thinkingMessage);

      // 开始思考过程
      startThinkingProcess(messageCounter);
      return;
   }

   // 普通 AI 消息
   const aiMessage: ChatMessage = {
      key: messageCounter,
      role: 'ai',
      placement: 'start',
      content: '',
      loading: true,
      shape: 'corner',
      variant: 'filled',
      isMarkdown: false,
      typing: false,
      isFog: false,
      avatarSize: '24px',
      avatarGap: '12px',
   };

   list.value.push(aiMessage);

   // 模拟 AI 思考时间，然后开始流式生成
   setTimeout(() => {
      generateStreamingAIResponse(aiMessage.key);
   }, 1000);
};

const list = ref<BubbleListProps<ChatMessage>['list']>([]);

// 使用 watch 监听 list 的变化
watch(
   () => list.value.length,
   newLength => {
      if (newLength === 0) {
         emits('emit:chat-starting', false);
      }
   }
);

const handleSubmit = () => {
   if (userInputLoading.value || !userInputValue.value.trim()) return;

   const userMessage = userInputValue.value.trim();
   userInputLoading.value = true;

   // 如果是第一条消息，发送开始聊天事件
   if (list.value.length === 0) {
      emits('emit:chat-starting', true);
   }

   // 添加用户消息
   addUserMessage(userMessage);

   // 清空输入框
   userInputValue.value = '';

   // 模拟 AI 回答延迟
   setTimeout(() => {
      addAIMessage();
   }, 500);
};

const handleCancel = () => {
   if (userInputLoading.value === true) {
      // 取消当前 AI 回答
      userInputLoading.value = false;

      // 如果最后一条消息是 AI 消息且正在加载，则移除它
      const lastMessage = list.value[list.value.length - 1];
      if (lastMessage && lastMessage.role === 'ai' && lastMessage.loading) {
         list.value.pop();
      }
   }
};

// 清空聊天记录 - 预留功能
// const clearChat = () => {
//    list.value = [];
//    userInputLoading.value = false;
// };

// 格式化时间显示
const formatTime = (): string => {
   const now = new Date();
   const hours = now.getHours();
   const minutes = now.getMinutes();
   const period = hours >= 12 ? '下午' : '上午';
   const displayHours = hours > 12 ? hours - 12 : hours === 0 ? 12 : hours;
   return `${period} ${displayHours}:${minutes.toString().padStart(2, '0')}`;
};

//动态计算对话区域width赋值给输入框
function dynamicComputedWidth() {
   return chatArea.value?.clientWidth;
}
onMounted(() => {
   const res = sendMessage({
      session_id: 19,
      role: 1,
      content: '你好',
      message_type: 'text',
      metadata: {},
   });

   console.log('消息返回：', res); // 这里就是后端返回的数据
   document.addEventListener('click', handleClickOutside);
   userInputArea.value!.style.width = dynamicComputedWidth() + 'px';

   // 监听窗口大小变化，动态调整输入框宽度
   const resizeObserver = new ResizeObserver(() => {
      userInputArea.value!.style.width = dynamicComputedWidth() + 'px';
   });
   resizeObserver.observe(chatArea.value!);
});

onUnmounted(() => {
   document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
   <div class="w-full">
      <div class="flex justify-center items-center flex-col flex-nowrap w-full">
         <!--TODO 对话列表 -->
         <div
            class="w-full"
            ref="chat-content-area"
         >
            <BubbleList
               :list="list"
               :max-height="props.maxHeight ? props.maxHeight + 'px' : '400px'"
            >
               <template #avatar="{ item }">
                  <div v-if="item.role === 'user'">
                     <svg
                        t="1758719735233"
                        class="icon"
                        viewBox="0 0 1024 1024"
                        version="1.1"
                        xmlns="http://www.w3.org/2000/svg"
                        p-id="16043"
                        width="32"
                        height="32"
                     >
                        <path
                           d="M508.928 589.824c-149.504 0-270.336-121.856-270.336-270.336S359.424 48.128 508.928 48.128s270.336 121.856 270.336 270.336-120.832 271.36-270.336 271.36z m0-463.872c-106.496 0-192.512 86.016-192.512 192.512S403.456 512 508.928 512c106.496 0 192.512-86.016 192.512-192.512s-86.016-193.536-192.512-193.536zM772.096 989.184H246.784c-97.28 0-176.128-78.848-176.128-176.128s78.848-176.128 176.128-176.128h525.312c97.28 0 176.128 78.848 176.128 176.128s-78.848 176.128-176.128 176.128zM246.784 711.68c-56.32 0-102.4 46.08-102.4 102.4s46.08 102.4 102.4 102.4h525.312c56.32 0 102.4-46.08 102.4-102.4s-46.08-102.4-102.4-102.4H246.784z"
                           fill="#4C4C4C"
                           p-id="16044"
                        ></path>
                        <path
                           d="M756.736 836.608h-93.184c-21.504 0-38.912-17.408-38.912-38.912s17.408-38.912 38.912-38.912h93.184c21.504 0 38.912 17.408 38.912 38.912s-17.408 38.912-38.912 38.912z"
                           fill="#FFA028"
                           p-id="16045"
                        ></path>
                     </svg>
                  </div>
                  <div v-else>
                     <svg
                        t="1758720056070"
                        class="icon"
                        viewBox="0 0 1024 1024"
                        version="1.1"
                        xmlns="http://www.w3.org/2000/svg"
                        p-id="17596"
                        width="32"
                        height="32"
                     >
                        <path
                           d="M832 839.9H203.3c-10.8 0-19.6-8.8-19.6-19.6V547.5c0-109.8 89.3-199.2 199.2-199.2h269.4c109.8 0 199.2 89.4 199.2 199.2v272.8c0.1 10.8-8.7 19.6-19.5 19.6z m-609.1-39.2h589.5V547.5c0-88.2-71.8-160-160-160H382.9c-88.2 0-160 71.8-160 160v253.2z"
                           fill="#1E94FC"
                           p-id="17597"
                        ></path>
                        <path
                           d="M665.8 609.2H369.5c-33.1 0-60-26.9-60-60s26.9-60 60-60h296.4c33.1 0 60 26.9 60 60-0.1 33.1-27 60-60.1 60z m-296.3-80.8c-11.5 0-20.8 9.3-20.8 20.8S358 570 369.5 570h296.4c11.5 0 20.8-9.4 20.8-20.8 0-11.5-9.3-20.8-20.8-20.8H369.5z"
                           fill="#28E3C4"
                           p-id="17598"
                        ></path>
                        <path
                           d="M192.1 730.4h-44.9c-15.8 0-28.6-12.8-28.6-28.6V612c0-15.8 12.8-28.6 28.6-28.6h44.9c10.8 0 19.6 8.8 19.6 19.6s-8.8 19.6-19.6 19.6h-34.3v68.6h34.3c10.8 0 19.6 8.8 19.6 19.6s-8.8 19.6-19.6 19.6zM883.6 730.4h-44.9c-10.8 0-19.6-8.8-19.6-19.6s8.8-19.6 19.6-19.6H873v-68.6h-34.3c-10.8 0-19.6-8.8-19.6-19.6s8.8-19.6 19.6-19.6h44.9c15.8 0 28.6 12.8 28.6 28.6v89.8c0 15.8-12.8 28.6-28.6 28.6zM627.7 384.7c-4.4 0-8.9-1.5-12.6-4.6-8.3-6.9-9.4-19.3-2.4-27.6l139.2-166.1c6.9-8.3 19.3-9.4 27.6-2.4 8.3 6.9 9.4 19.3 2.4 27.6L642.7 377.7c-3.9 4.6-9.4 7-15 7zM403.1 384.7c-5.6 0-11.1-2.4-15-7L248.9 211.5c-7-8.3-5.9-20.7 2.4-27.6 8.3-7 20.6-5.9 27.6 2.4l139.2 166.1c7 8.3 5.9 20.7-2.4 27.6-3.6 3.2-8.1 4.7-12.6 4.7z"
                           fill="#1E94FC"
                           p-id="17599"
                        ></path>
                        <path
                           d="M780.3 218.9c-23.4 0-42.5-19-42.5-42.5s19-42.5 42.5-42.5 42.5 19 42.5 42.5-19 42.5-42.5 42.5z m0-44.9c-1.4 0-2.5 1.1-2.5 2.5s1.1 2.5 2.5 2.5 2.5-1.1 2.5-2.5-1.1-2.5-2.5-2.5zM250.5 218.9c-23.4 0-42.5-19-42.5-42.5s19-42.5 42.5-42.5 42.5 19 42.5 42.5-19.1 42.5-42.5 42.5z m0-44.9c-1.4 0-2.5 1.1-2.5 2.5s1.1 2.5 2.5 2.5 2.5-1.1 2.5-2.5-1.2-2.5-2.5-2.5z"
                           fill="#1E94FC"
                           p-id="17600"
                        ></path>
                     </svg>
                  </div>
               </template>
               <!-- 自定义内容区域 -->
               <template #content="{ item }">
                  <!-- 如果是思考消息，显示 Thinking 组件 -->
                  <div
                     v-if="item.showThinking"
                     class="thinking-container"
                  >
                     <Thinking
                        :status="item.thinkingStatus || 'start'"
                        :content="item.thinkingContent || ''"
                        :autoCollapse="true"
                        color="#64748b"
                     />
                  </div>
                  <!-- 普通消息内容 -->
                  <div v-else>
                     {{ item.content }}
                  </div>
               </template>

               <!-- 自定义底部内容 -->
               <template #footer="{ item }">
                  <div
                     v-if="item.role === 'ai' && !item.showThinking"
                     class="footer-wrapper"
                  >
                     <div class="footer-container">
                        <svg
                           t="1758719489857"
                           class="icon"
                           viewBox="0 0 1024 1024"
                           version="1.1"
                           xmlns="http://www.w3.org/2000/svg"
                           p-id="4727"
                           width="16"
                           height="16"
                        >
                           <path
                              d="M912 520C912 295.04 728.96 112 504 112c-13.504 0-26.832 0.704-40 1.984v80.704c13.136-1.6 26.432-2.688 40-2.688C684.864 192 832 339.136 832 520c0 112.608-57.264 211.808-144 270.832V640h-80v288h288v-80h-150.192C846.448 773.632 912 654.448 912 520z m-736 0c0-112.608 57.264-211.808 144-270.832V400h80V112H112v79.84h150.192C161.552 266.208 96 385.552 96 520 96 744.96 279.04 928 504 928c13.504 0 26.832-0.704 40-1.984v-80.704c-13.136 1.6-26.432 2.688-40 2.688C323.136 848 176 700.864 176 520z"
                              fill="#565D64"
                              p-id="4728"
                           ></path>
                        </svg>
                     </div>
                     <div class="footer-time">
                        {{ formatTime() }}
                     </div>
                  </div>
               </template>
            </BubbleList>
         </div>
      </div>

      <!-- TODO输入框 -->
      <div
         class="absolute bottom-4"
         ref="user-input-area"
      >
         <Sender
            v-model="userInputValue"
            variant="updown"
            :auto-size="{ minRows: 3, maxRows: 6 }"
            clearable
            allow-speech
            placeholder="你好，欢迎您！！"
            :loading="userInputLoading"
            @submit="handleSubmit"
            @cancel="handleCancel"
         >
            <!-- TODO下方选择模型和深度思考 -->
            <template #prefix>
               <div class="flex flex-row flex-nowrap gap-1 items-center">
                  <div class="relative dropdown-container">
                     <!-- 下拉菜单 -->
                     <div
                        v-if="showDropdown"
                        class="absolute left-0 bottom-full mb-1 bg-white border rounded shadow px-2 py-2 z-10 min-w-max"
                        @click.stop
                     >
                        <div class="flex flex-col gap-1">
                           <div
                              v-for="model in modelOptions"
                              :key="model"
                              class="flex flex-col flex-nowrap gap-0.5 hover:bg-gray-100 cursor-pointer px-2 py-1 rounded"
                              @click="selectModel(model)"
                           >
                              <span class="text-sm">{{ model }}</span>
                              <span
                                 class="text-xs text-gray-600"
                                 v-if="model === 'DeepSeek'"
                                 >全能处理深度思考</span
                              >
                              <span
                                 class="text-xs text-gray-600"
                                 v-else-if="model === 'GPT-4'"
                                 >OpenAI 最新模型</span
                              >
                              <span
                                 class="text-xs text-gray-600"
                                 v-else-if="model === 'Claude'"
                                 >Anthropic 智能助手</span
                              >
                              <span
                                 class="text-xs text-gray-600"
                                 v-else-if="model === 'Gemini'"
                                 >Google 多模态模型</span
                              >
                           </div>
                        </div>
                     </div>

                     <!-- 选择器按钮 -->
                     <span
                        class="border border-gray-400 rounded-4xl p-1 text-sm cursor-pointer flex items-center gap-1 hover:bg-gray-50"
                        @click.stop="toggleDropdown"
                     >
                        {{ selectedModel }}
                        <!-- 箭头图标 -->
                        <svg
                           :class="{ 'rotate-180': showDropdown }"
                           class="w-3 h-3 transition-transform duration-200"
                           fill="none"
                           stroke="currentColor"
                           viewBox="0 0 24 24"
                        >
                           <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M19 9l-7 7-7-7"
                           ></path>
                        </svg>
                     </span>
                  </div>
                  <span
                     @click="isSelectThinking = !isSelectThinking"
                     class="border rounded-4xl p-1 text-sm text-gray-700 border-gray-400 cursor-pointer"
                     :style="{
                        backgroundColor: isSelectThinking ? '#ecfeff' : '',
                        color: isSelectThinking ? '#181d1d' : '',
                     }"
                  >
                     R1·深度思考
                  </span>
               </div>
            </template>
         </Sender>
      </div>
   </div>
</template>

<style>
.selected-thinking {
   background-color: #ecfeff;
   color: #181d1d;
}

.footer-wrapper {
   display: flex;
   align-items: center;
   justify-content: space-between;
   margin-top: 4px;
   font-size: 12px;
   color: #999;
}

.footer-container {
   display: flex;
   align-items: center;
   gap: 4px;
   cursor: pointer;
}

.refresh-icon {
   color: #999;
}

/* 悬停时旋转效果现在通过 Tailwind 类条件性应用 */
@keyframes spin {
   from {
      transform: rotate(0deg);
   }
   to {
      transform: rotate(360deg);
   }
}

.animate-spin {
   animation: spin 1s linear infinite;
}

.footer-time {
   font-size: 12px;
   color: #999;
}

/* Thinking 组件样式优化 */
.thinking-container {
   max-width: 280px;
   margin: 4px 0;
}

/* 覆盖 Thinking 组件的默认样式 */
.thinking-container :deep(.el-thinking) {
   font-size: 12px;
}

.thinking-container :deep(.el-thinking__button) {
   padding: 4px 8px;
   font-size: 11px;
   border-radius: 12px;
   height: auto;
   min-height: 24px;
}

.thinking-container :deep(.el-thinking__content) {
   padding: 8px 12px;
   font-size: 11px;
   line-height: 1.4;
   border-radius: 8px;
}
</style>
