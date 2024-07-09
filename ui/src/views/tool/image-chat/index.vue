<template>
  <LayoutContainer header="图片问答">
    <div class="image-chat main-calc-height">
      <el-row>
        <el-col :span="10">
          <el-scrollbar>
          <el-form
            :model="imageChatForm"
            label-position="top"
            require-asterisk-position="right"
            class="p-24"
          >
            <el-form-item>
              <template #label>
                <div class="flex-between">
                  <span>多模态大模型</span>
                  <div>
                    多轮问答
                    <el-switch
                      size="small"
                      v-model="imageChatForm.multiple_rounds_dialogue"
                    ></el-switch>
                  </div>
                </div>
              </template>
              <el-select
                v-model="imageChatForm.model_id"
                placeholder="请选择模型"
                filterable
                class="w-full"
                popper-class="select-model"
              >
                <el-option
                  v-for="(item, index) in vlmModelList"
                  :key="index"
                  :label="item.key"
                  :value="item.value"
                >
                </el-option>
              </el-select>
            </el-form-item>

            <el-upload
              drag
              action="#"
              :auto-upload="false"
              :show-file-list="false"
              :on-change="handleChange"
              multiple>
                <i class="el-icon-upload"></i>
              <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
              <div class="el-upload__tip" slot="tip">只能上传jpg/png文件，且不超过500kb</div>
            </el-upload>
            <el-image
                class="img-block mt-12"
                v-if="imageChatForm.image_src"
                :src="imageChatForm.image_src"
                fit="contain"
                :zoom-rate="1.2"
                :max-scale="7"
                :min-scale="0.2"
                :preview-src-list="[imageChatForm.image_src]"
            >
            </el-image>
            </el-form>
          </el-scrollbar>
        </el-col>
        <el-col :span="14" class="p-24 border-l">
          <h4 class="title-decoration-1 mb-16">
          聊天
          </h4>
          <div class="dialog-bg">
            <div class="scrollbar-height mt-24">
              <AiImageChat :data="imageChatForm"></AiImageChat>
            </div>
          </div>
        </el-col>
      </el-row>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import {UploadProps} from "element-plus";
import {KeyValue} from "@/api/type/common";
import {blobToBase64} from "@/utils/utils";
import ModelApi from '@/api/model';
import {ImageChatFormType} from "@/api/type/tool";
import AiImageChat from "./component/Chat.vue";
const vlmModelList = ref<Array<KeyValue<string, string>>>([])
const vlmModelLoading = ref<boolean>(false)

const imageChatForm = ref<ImageChatFormType>({
  model_id: '',
  image_src: '',
  multiple_rounds_dialogue: false,
  prologue: "请先选择图片再对我进行提问"
})

const initVlmModelList = () => {
  ModelApi.getModel({model_type: 'MLLM'}, vlmModelLoading).then((ok) => {
    vlmModelList.value = ok.data.map(item => ({
      key: item.name,
      value: item.id
    }));
    if (vlmModelList.value.length > 0) {
      imageChatForm.value.model_id = vlmModelList.value[0].value // 默认选择第一个
    }
  })
}
const handleChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  blobToBase64(uploadFile.raw).then((res) =>{
    const base64String = res.split(',')[1];
    imageChatForm.value.image_src = "data:image/jpeg;base64," + base64String
  })
}
onMounted(() => {
  initVlmModelList()
})
</script>
<style lang="scss" scoped>
.image-chat {
  .dialog-bg {
    border-radius: 8px;
    background: var(--dialog-bg-gradient-color);
    overflow: hidden;
    box-sizing: border-box;
  }
  .scrollbar-height-left {
    height: calc(var(--app-main-height) - 64px);
  }
  .scrollbar-height {
    height: calc(var(--app-main-height) - 160px);
  }
  .img-block {
    width: 100%;
    height: 480px;
  }
}
</style>
