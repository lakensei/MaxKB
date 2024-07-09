<template>
  <LayoutContainer header="图片识别">
    <div class="vllm-chat main-calc-height">
      <el-row>
        <el-col :span="10">

          <el-form
              ref="applicationFormRef"
              :model="form"
              label-position="top"
              require-asterisk-position="right"
              class="p-24"
          >
            <el-form-item
                @click.prevent
            >
              <template #label>
                <div class="flex-between">
                  <span>上传图片</span>
                  <div>
                    <el-button type="primary" link @click="toOcr(1)">
                      版面分析
                    </el-button>
                    <el-button type="primary" link @click="toOcr(2)">
                      表格识别
                    </el-button>
                    <el-button type="primary" link @click="toOcr(3)">
                      文字识别
                    </el-button>
                  </div>
                </div>
              </template>
            </el-form-item>
            <div class="img-block">
              <el-scrollbar>
                <el-upload
                    drag
                    action="#"
                    :auto-upload="false"
                    :show-file-list="false"
                    :on-change="handleChange"
                    multiple>
                  <el-image
                      v-if="form.image_src"
                      :src="form.image_src"
                  />
                  <template v-else>
                    <i class="el-icon-upload"></i>
                    <div class="el-upload__text">将文件拖到此处，或<em>点击上传</em></div>
                    <div class="el-upload__tip" slot="tip">只能上传jpg/png文件，且不超过500kb</div>
                  </template>

                </el-upload>
              </el-scrollbar>
            </div>
          </el-form>
        </el-col>
        <el-col :span="14" class="p-24 border-l">
          <p>耗时： <span>123</span>ms</p>
          <div id="layout-box"></div>
        </el-col>
      </el-row>
    </div>
  </LayoutContainer>
</template>
<script setup lang="ts">
import {reactive, ref} from 'vue'
import {UploadProps} from "element-plus";
import {blobToBase64} from "@/utils/utils";

const form = reactive<{
  ocr_type: string,
  image_src: string,
  [propName: string]: any
}>({
  ocr_type: '',
  image_src: '',
})
const imgFile = ref(null)

function toOcr(type) {
  console.log(type)
  layoutCanvas()
}

const handleChange: UploadProps['onChange'] = (uploadFile, uploadFiles) => {
  imgFile.value = uploadFile.raw
  blobToBase64(uploadFile.raw).then((res) => {
    const base64String = res.split(',')[1];
    form.image_src = "data:image/jpeg;base64," + base64String
  })
}

const layoutCanvas = () => {
  // 创建FileReader读取文件
  const reader = new FileReader();
  const file = imgFile.value;

  // 当读取完成时执行的回调函数
  reader.onload = function (event) {
    const img = new Image();

    // 图片加载完成后执行的回调函数
    img.onload = function () {
      // 创建canvas元素
      const container = document.getElementById('layout-box');
      console.log(container);
      const canvas = document.createElement('canvas');

      const ctx = canvas.getContext('2d');
      // 设置canvas的尺寸为图片的尺寸

      let scale = 1;
      canvas.width = img.width;
      canvas.height = img.height;
      // canvas.height = canvas.height / scale;
      if (img.width > container.clientWidth) {
        canvas.width = container.clientWidth;
        const ratio = img.width / img.height;
        canvas.height = canvas.width / ratio;
        scale = container.clientWidth / img.width
      }
      // 清除之前的绘制
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      // 绘制图片
      ctx.drawImage(img, 0, 0, canvas.width, canvas.height);

      // 假设这是从后端得到的坐标
      const originalBox = {x1: 261, y1: 66, x2: 978, y2: 125};
      const box = {
        x1: originalBox.x1 * scale,
        y1: originalBox.y1 * scale,
        x2: originalBox.x2 * scale,
        y2: originalBox.y2 * scale,
      };
      // 设置画笔颜色和线宽
      ctx.strokeStyle = 'red';
      ctx.lineWidth = 2;

      // 画框
      ctx.strokeRect(box.x1, box.y1, box.x2 - box.x1, box.y2 - box.y1);
      container.appendChild(canvas);
    };

    // 开始读取文件为DataURL
    if (typeof event.target.result === "string") {
      img.src = event.target.result;
    }
  };

  // 读取文件
  reader.readAsDataURL(file);
}

</script>
<style lang="scss" scoped>
.img-block {
  width: 100%;
  height: 700px;
}
#layout-box {
  height: 700px;
  overflow-y: auto;
}
</style>
