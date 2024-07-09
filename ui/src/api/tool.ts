import { postStream } from '@/request/index'

const prefix = '/tool'

/**
 * 多模态图片对话
 * @param 参数
 * chat_id: string
 * data
 */
const postImageChatMessage: (data: any) => Promise<any> = (data) => {
  return postStream(`${prefix}/image_chat`, data)
}

export default {
  postImageChatMessage
}