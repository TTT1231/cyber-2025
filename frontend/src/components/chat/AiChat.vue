<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, useTemplateRef, nextTick } from 'vue';
import type { BubbleListItemProps, BubbleListProps } from 'vue-element-plus-x/types/BubbleList';
import { chatApi } from '@/apis/chat';
import { useRoute } from 'vue-router';
import { getSession } from '@/apis/session';
import { getRoles } from '@/apis/role';

type MessageRole = 'user' | 'ai';
type ModelOption = 'DeepSeek' | 'GPT-4' | 'Claude' | 'Gemini';
type ThinkingStatus = 'start' | 'thinking' | 'end' | 'error';

interface ChatMessage extends BubbleListItemProps {
   key: number;
   role: MessageRole;
   showThinking?: boolean;
   thinkingStatus?: ThinkingStatus;
   thinkingContent?: string;
}

interface ChatResponse {
   audio_url: string;
   ai_text: string;
   session_id: number;
   status: string;
   message: string;
}

const userInputValue = ref('');
const userInputLoading = ref(false);
const isSelectThinking = ref(false);
const showDropdown = ref(false);
const selectedModel = ref<ModelOption>('DeepSeek');
const modelOptions: ModelOption[] = ['DeepSeek', 'GPT-4', 'Claude', 'Gemini'];
const chatArea = useTemplateRef<HTMLDivElement>('chat-content-area');
const userInputArea = useTemplateRef<HTMLDivElement>('user-input-area');
const roleName = (useRoute().query.role as string) || '';
const sessionId = ref<number | undefined>(undefined);
const remoteTTSWAV = ref<string>('');
const audioPlayer = useTemplateRef<HTMLAudioElement>('audioPlayer');
const audioPlaying = ref(false);

const emits = defineEmits<{
   (e: 'emit:chat-starting', value: boolean): void;
}>();

const props = defineProps<{
   maxHeight?: number;
}>();

const toggleDropdown = (): void => {
   showDropdown.value = !showDropdown.value;
};

const selectModel = (model: ModelOption): void => {
   selectedModel.value = model;
   showDropdown.value = false;
};

const handleClickOutside = (event: MouseEvent): void => {
   const target = event.target as HTMLElement;
   if (!target.closest('.dropdown-container')) {
      showDropdown.value = false;
   }
};

let messageCounter = 0;
const list = ref<BubbleListProps<ChatMessage>['list']>([]);

watch(
   () => list.value.length,
   newLength => {
      if (newLength === 0) {
         emits('emit:chat-starting', false);
      }
   }
);

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

const playRemoteAudio = async () => {
   if (!remoteTTSWAV.value) return;

   try {
      await audioPlayer.value!.play();
      audioPlaying.value = true;
   } catch {}
};

const pauseRemoteAudio = () => {
   audioPlayer.value!.pause();
   audioPlaying.value = false;
};
const handleSubmit = async () => {
   if (userInputLoading.value || !userInputValue.value.trim()) return;

   const userMessage = userInputValue.value.trim();
   userInputLoading.value = true;

   if (list.value.length === 0) {
      emits('emit:chat-starting', true);
   }

   addUserMessage(userMessage);
   userInputValue.value = '';

   try {
      if (!sessionId.value) {
         throw new Error('会话未初始化');
      }

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
         showThinking: isSelectThinking.value,
         thinkingStatus: isSelectThinking.value ? 'thinking' : undefined,
         thinkingContent: isSelectThinking.value ? '正在深度思考中...' : undefined,
      };
      list.value.push(aiMessage);

      const res = await chatApi<ChatResponse>({
         text: userMessage,
         session_id: sessionId.value,
         role_name: roleName,
      });

      if (res.status === 200 && res.data.status === 'success') {
         const messageIndex = list.value.findIndex(msg => msg.key === messageCounter);
         remoteTTSWAV.value = res.data.audio_url;

         nextTick(() => {
            playRemoteAudio();
         });

         if (messageIndex !== -1) {
            list.value[messageIndex].loading = false;
            list.value[messageIndex].typing = true;
            list.value[messageIndex].isFog = true;

            if (isSelectThinking.value) {
               setTimeout(() => {
                  list.value[messageIndex].thinkingStatus = 'end';
                  list.value[messageIndex].thinkingContent = '思考完成，生成回答中...';
               }, 3000); // 深度思考的延时
            }

            let currentIndex = 0;
            const fullContent = res.data.ai_text;

            // 音频同步
            audioPlayer.value!.onloadedmetadata = () => {
               const duration = audioPlayer.value!.duration; // 获取音频总时长（秒）
               const totalChars = fullContent.length;

               const interval = (duration * 1000) / totalChars; // 每个字符的时间间隔（毫秒）

               const streamInterval = setInterval(() => {
                  if (currentIndex >= fullContent.length) {
                     clearInterval(streamInterval);
                     list.value[messageIndex].typing = false;
                     list.value[messageIndex].isFog = false;
                     list.value[messageIndex].showThinking = false;
                     userInputLoading.value = false;
                     return;
                  }

                  list.value[messageIndex].content += fullContent[currentIndex];
                  currentIndex++;
               }, interval);
            };
         }
      } else {
         throw new Error(res.data.message || '聊天API返回错误');
      }
   } catch (error) {
      console.error('聊天失败:', error);
      const messageIndex = list.value.findIndex(msg => msg.key === messageCounter);
      if (messageIndex !== -1) {
         list.value[messageIndex].loading = false;
         list.value[messageIndex].content = '抱歉，聊天服务暂时不可用，请稍后再试。';
      }
      userInputLoading.value = false;
   }
};

const handleCancel = () => {
   if (userInputLoading.value === true) {
      userInputLoading.value = false;
      const lastMessage = list.value[list.value.length - 1];
      if (lastMessage && lastMessage.role === 'ai' && lastMessage.loading) {
         list.value.pop();
      }
      pauseRemoteAudio();
   }
};

const formatTime = (): string => {
   const now = new Date();
   const hours = now.getHours();
   const minutes = now.getMinutes();
   const period = hours >= 12 ? '下午' : '上午';
   const displayHours = hours > 12 ? hours - 12 : hours === 0 ? 12 : hours;
   return `${period} ${displayHours}:${minutes.toString().padStart(2, '0')}`;
};

function dynamicComputedWidth() {
   return chatArea.value?.clientWidth;
}

onMounted(async () => {
   try {
      const res = await getRoles();
      let roleId: number | undefined = undefined;
      if (res.status === 200) {
         res.data.forEach((item, index) => {
            if (item.name === roleName) {
               roleId = index;
            }
         });
         if (roleId === undefined) throw new Error('角色信息在数据库中找不到');
      } else {
         throw new Error('数据库api请求失败');
      }

      const getSessionRes = await getSession(roleId + 1);
      if (getSessionRes.status === 200) {
         sessionId.value = getSessionRes.data.id;
      } else {
         throw new Error('数据库api获取session失败');
      }
   } catch (e) {
      console.error('初始化聊天失败', e);
   }

   document.addEventListener('click', handleClickOutside);
   userInputArea.value!.style.width = dynamicComputedWidth() + 'px';

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
               <template #content="{ item }">
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
                  <div v-else>
                     {{ item.content }}
                  </div>
               </template>
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
      <div class="hidden">
         <audio
            ref="audioPlayer"
            :src="remoteTTSWAV"
            autoplay
         />
      </div>
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
            <template #prefix>
               <div class="flex flex-row flex-nowrap gap-1 items-center">
                  <div class="relative dropdown-container">
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

                     <span
                        class="border border-gray-400 rounded-4xl p-1 text-sm cursor-pointer flex items-center gap-1 hover:bg-gray-50"
                        @click.stop="toggleDropdown"
                     >
                        {{ selectedModel }}
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

.footer-time {
   font-size: 12px;
   color: #999;
}

.thinking-container {
   max-width: 280px;
   margin: 4px 0;
}

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
