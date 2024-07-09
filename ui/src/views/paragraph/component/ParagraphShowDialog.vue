<template>
  <el-dialog
    :title="title"
    v-model="dialogVisible"
    width="60%"
    class="paragraph-dialog"
    destroy-on-close
  >
    <el-row v-loading="loading">
      <el-col>
        <el-scrollbar height="500" wrap-class="paragraph-scrollbar">
          <div class="p-24" style="padding-bottom: 8px">
            <ParagraphForm ref="paragraphFormRef" :data="detail" :isEdit="false" />
          </div>
        </el-scrollbar>
      </el-col>
    </el-row>
  </el-dialog>
</template>
<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep, debounce } from 'lodash'

import ParagraphForm from '@/views/paragraph/component/ParagraphForm.vue'
import ProblemComponent from '@/views/paragraph/component/ProblemComponent.vue'
import paragraphApi from '@/api/paragraph'
import useStore from '@/stores'

const props = defineProps({
  title: String
})

const { paragraph } = useStore()

const route = useRoute()
const {
  params: { id, documentId }
} = route as any

const emit = defineEmits(['refresh'])

const paragraphFormRef = ref<any>()

const dialogVisible = ref<boolean>(false)

const loading = ref(false)
const detail = ref<any>({})
const document_id = ref('')
const dataset_id = ref('')
const cloneData = ref(null)

watch(dialogVisible, (bool) => {
  if (!bool) {
    detail.value = {}
    cloneData.value = null
  }
})

const open = (data: any) => {
  detail.value.title = data.title
  detail.value.content = data.content
  cloneData.value = cloneDeep(detail.value)
  dialogVisible.value = true
}

defineExpose({ open })
</script>
<style lang="scss" scope>

</style>
