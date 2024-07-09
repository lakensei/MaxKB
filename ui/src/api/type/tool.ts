import { type Dict } from '@/api/type/common'
import { type Ref } from 'vue'
interface ImageChatFormType {
  model_id: string
  image_src: string
  multiple_rounds_dialogue: boolean
  prologue: string
}

export type { ImageChatFormType }