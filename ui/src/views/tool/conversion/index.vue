<template>
  <LayoutContainer header="文档转换">
    <el-alert title="该功能暂未开发" type="warning" :closable="false" />
<!--    <el-upload-->
<!--      class="upload-demo"-->
<!--      drag-->
<!--      action="#"-->
<!--      :auto-upload="false"-->
<!--      :limit="1"-->
<!--      :on-exceed="handleExceed"-->
<!--      multiple>-->
<!--      <i class="el-icon-upload"></i>-->
<!--      <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>-->
<!--      <div class="el-upload__tip" slot="tip">只能上传pdf文件，且不超过500kb</div>-->
<!--    </el-upload>-->
  </LayoutContainer>
</template>
<script setup lang="ts">
// import {genFileId, UploadInstance, UploadProps, UploadRawFile} from "element-plus";

import { ref } from 'vue'
import { genFileId } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile } from 'element-plus'

const upload = ref<UploadInstance>()

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
}
</script>
<style lang="scss" scoped>
</style>
