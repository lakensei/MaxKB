<template>

    <LayoutContainer>
      <template #header>
        <div class="flex-between w-full">
        <h4>
          文档检索
          <el-text type="info" class="ml-4">根据文档内容检索相关文档</el-text>
        </h4>
        <el-popover :visible="popoverVisible" placement="right-end" :width="500" trigger="click">
        <template #reference>
          <el-button icon="Setting" @click="settingChange('open')">参数设置</el-button>
        </template>
        <div class="mb-16">
          <div class="title mb-8">检索模式</div>
          <el-radio-group
            v-model="cloneForm.search_mode"
            class="card__radio"
            @change="changeHandle"
          >
            <el-card
              shadow="never"
              class="mb-16"
              :class="cloneForm.search_mode === 'embedding' ? 'active' : ''"
            >
              <el-radio value="embedding" size="large">
                <p class="mb-4">向量检索</p>
                <el-text type="info">通过向量距离计算与用户问题最相似的文本分段</el-text>
              </el-radio>
            </el-card>
            <el-card
              shadow="never"
              class="mb-16"
              :class="cloneForm.search_mode === 'keywords' ? 'active' : ''"
            >
              <el-radio value="keywords" size="large">
                <p class="mb-4">全文检索</p>
                <el-text type="info">通过关键词检索，返回包含关键词最多的文本分段</el-text>
              </el-radio>
            </el-card>
            <el-card
              shadow="never"
              class="mb-16"
              :class="cloneForm.search_mode === 'blend' ? 'active' : ''"
            >
              <el-radio value="blend" size="large">
                <p class="mb-4">混合检索</p>
                <el-text type="info"
                  >同时执行全文检索和向量检索，再进行重排序，从两类查询结果中选择匹配用户问题的最佳结果</el-text
                >
              </el-radio>
            </el-card>
          </el-radio-group>
        </div>
        <el-row :gutter="20">
          <el-col :span="12">
            <div class="mb-16">
              <div class="title mb-8">相似度高于</div>
              <el-input-number
                v-model="cloneForm.similarity"
                :min="0"
                :max="cloneForm.search_mode === 'blend' ? 2 : 1"
                :precision="3"
                :step="0.1"
                :value-on-clear="0"
                controls-position="right"
                class="w-full"
              />
            </div>
          </el-col>
          <el-col :span="12">
            <div class="mb-16">
              <div class="title mb-8">返回分段数 TOP</div>
              <el-input-number
                v-model="cloneForm.top_number"
                :min="1"
                :max="100"
                controls-position="right"
                class="w-full"
              />
            </div>
          </el-col>
        </el-row>

        <div class="text-right">
          <el-button @click="popoverVisible = false">取消</el-button>
          <el-button type="primary" @click="settingChange('close')">确认</el-button>
        </div>
      </el-popover>
      </div>
      </template>
      <div class="document-search main-calc-height">
      <div class="document-search__operate p-24">
      <div class="operate-textarea flex">
        <el-input
          ref="quickInputRef"
          v-model="inputValue"
          type="textarea"
          placeholder="请输入"
          :autosize="{ minRows: 1, maxRows: 8 }"
          @keydown.enter="sendChatHandle($event)"
        />
        <div class="operate">
          <el-button
            text
            class="sent-button"
            :disabled="isDisabledChart || loading"
            @click="sendChatHandle"
          >
            <img v-show="isDisabledChart || loading" src="@/assets/icon_send.svg" alt="" />
            <img
              v-show="!isDisabledChart && !loading"
              src="@/assets/icon_send_colorful.svg"
              alt=""
            />
          </el-button>
        </div>
      </div>
    </div>
      <div class="document-search__main p-16" v-loading="loading">
        <el-scrollbar>
          <div class="document-search-height">
            <el-empty v-if="first" :image="emptyImg" description="文件列表" />
            <el-empty v-else-if="documentDetail.length == 0" description="未检索到文件" />
            <el-row v-else>
              <el-col
                v-for="(item, index) in documentDetail"
                :key="index"
                class="p-8"
              >
                <DocumentCard
                  shadow="hover"
                  :title="item.document_name || '-'"
                  class="document-card layout-bg layout-bg cursor"
                >
                  <div class="active-button primary">
                    <a :href="item.document_meta?.source_url" :download="item.document_name">下载</a>
                  </div>
                  <template #body>
                    <div v-for="(paragraph, i) in item.paragraph_list" :key="i" class="paragraph-title break-all mt-12 primary">
                      <p @click="editParagraph(paragraph)" class="content">{{ paragraph.title || paragraph.content }}</p>
                    </div>
                  </template>
                </DocumentCard>
              </el-col>
            </el-row>
          </div>
        </el-scrollbar>
      </div>

      <ParagraphDialog ref="ParagraphDialogRef" :title="title" @refresh="refresh" />
      </div>
    </LayoutContainer>


</template>
<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import datasetApi from '@/api/dataset'
import ParagraphDialog from '@/views/paragraph/component/ParagraphShowDialog.vue'
import DocumentCard from './component/DocumentCard.vue'
import { arraySort } from '@/utils/utils'
import emptyImg from '@/assets/document-search-empty.png'
import type { DocumentSearchData } from '@/api/type/document'

const route = useRoute()
const {
  meta: { activeMenu },
  params: { id }
} = route as any

const ParagraphDialogRef = ref()
const loading = ref(false)
const documentDetail = ref<DocumentSearchData[]>([])
const title = ref('')
const inputValue = ref('')
const formInline = ref({
  similarity: 0.6,
  top_number: 5,
  search_mode: 'blend'
})

// 第一次加载
const first = ref(true)

const cloneForm = ref<any>({})

const popoverVisible = ref(false)
// const questionTitle = ref('')

const isDisabledChart = computed(() => !inputValue.value)

function changeHandle(val: string) {
  if (val === 'keywords') {
    cloneForm.value.similarity = 0
  } else {
    cloneForm.value.similarity = 0.6
  }
}

function settingChange(val: string) {
  if (val === 'open') {
    popoverVisible.value = true
    cloneForm.value = cloneDeep(formInline.value)
  } else if (val === 'close') {
    popoverVisible.value = false
    formInline.value = cloneDeep(cloneForm.value)
  }
}

function editParagraph(row: any) {
  title.value = '分段详情'
  ParagraphDialogRef.value.open(row)
}

function sendChatHandle(event: any) {
  if (!event.ctrlKey) {
    // 如果没有按下组合键ctrl，则会阻止默认事件
    event.preventDefault()
    if (!isDisabledChart.value && !loading.value) {
      getDocumentList()
    }
  } else {
    // 如果同时按下ctrl+回车键，则会换行
    inputValue.value += '\n'
  }
}
function getDocumentList() {
  const obj = {
    query_text: inputValue.value,
    ...formInline.value
  }
  datasetApi.getDatasetDocumentSearch(id, obj, loading).then((res) => {
    documentDetail.value = res.data && arraySort(res.data, 'comprehensive_score', true)
    // questionTitle.value = inputValue.value
    // inputValue.value = ''
    first.value = false
  })

}

function refresh() {
  documentDetail.value = []
  getDocumentList()
}

onMounted(() => {})
</script>
<style lang="scss" scoped>
.document-search {
  min-width: 700px;
  width: 70%;
  margin: 0 auto;
  .question-title {
    .avatar {
      float: left;
    }
    .content {
      padding-left: 40px;
      .text {
        padding: 6px 0;
      }
    }
  }

  &__operate {
    .operate-textarea {
      box-shadow: 0px 6px 24px 0px rgba(31, 35, 41, 0.08);
      background-color: #ffffff;
      border-radius: 8px;
      border: 1px solid #ffffff;
      box-sizing: border-box;

      &:has(.el-textarea__inner:focus) {
        border: 1px solid var(--el-color-primary);
      }

      :deep(.el-textarea__inner) {
        border-radius: 8px !important;
        box-shadow: none;
        resize: none;
        padding: 12px 16px;
      }
      .operate {
        padding: 6px 10px;
        .sent-button {
          max-height: none;
          .el-icon {
            font-size: 24px;
          }
        }
        :deep(.el-loading-spinner) {
          margin-top: -15px;
          .circular {
            width: 31px;
            height: 31px;
          }
        }
      }
    }
  }
}
.document-search {
  &__header {
    position: absolute;
    right: calc(var(--app-base-px) * 3);
  }

  .document-search-height {
    height: calc(var(--app-main-height) - 170px);
  }
  .document-card {
    //height: 210px;
    border: 1px solid var(--app-layout-bg-color);
    &:hover {
      background: #ffffff;
      border: 1px solid var(--el-border-color);
    }
    &.disabled {
      background: var(--app-layout-bg-color);
      border: 1px solid var(--app-layout-bg-color);
      :deep(.description) {
        color: var(--app-border-color-dark);
      }
      :deep(.title) {
        color: var(--app-border-color-dark);
      }
    }
    :deep(.description) {
      -webkit-line-clamp: 5 !important;
      height: 110px;
    }
    .active-button {
      position: absolute;
      right: 16px;
      top: 16px;
    }
  }
}
.paragraph-title {
  .content {
      display: -webkit-box;
      //height: var(--app-card-box-description-height, 40px);
      -webkit-box-orient: vertical;
      -webkit-line-clamp: 2;
      overflow: hidden;
    }
}
</style>
