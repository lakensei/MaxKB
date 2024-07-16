<template>
  <el-card shadow="hover" class="document-box" @mouseenter="cardEnter()" @mouseleave="cardLeave()">
    <div class="card-header">
      <slot name="header">
        <div class="title flex align-center">
          <slot name="icon">
            <AppAvatar class="mr-12" shape="square" :size="24">
              <img :src="getImgUrl(title)" alt="" height="16" />
            </AppAvatar>
          </slot>
          <auto-tooltip :content="title" style="width: 65%">
            {{ title }}
          </auto-tooltip>
        </div>
      </slot>
    </div>
    <div class="card-body" v-if="$slots.body">
      <slot name="body" />
    </div>
    <slot />
    <slot name="mouseEnter" v-if="$slots.mouseEnter && show" />
    <div class="card-footer" v-if="$slots.footer">
      <slot name="footer" />
    </div>
  </el-card>
</template>
<script setup lang="ts">
import { ref, useSlots } from 'vue'
import { getImgUrl } from '@/utils/utils'
const slots = useSlots()
defineOptions({ name: 'DocumentCard' })
const props = defineProps({
  title: {
    type: String,
    required: true
  }
})

const show = ref(false)
function cardEnter() {
  show.value = true
}
function cardLeave() {
  show.value = false
}
</script>
<style lang="scss" scoped>
.document-box {
  font-size: 14px;
  position: relative;
  //min-height: var(--card-min-height);
  //min-width: var(--card-min-width);
  border-radius: 8px;
}
</style>
