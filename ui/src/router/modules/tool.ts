import Layout from '@/layout/main-layout/index.vue'

const datasetRouter = {
  path: '/tool',
  name: 'Tool',
  meta: { icon: 'Tools', title: '工具箱', permission: 'TOOL:READ' },
  redirect: '/image-chat',
  component: Layout,
  children: [
      {
      path: '/image-chat',
      name: 'ImageChat',
      meta: {
        icon: 'ChatDotRound',
        iconActive: 'ChatDotRound',
        title: '图片问答',
        activeMenu: '/tool',
        parentPath: '/tool',
        parentName: 'Tool'
      },
      component: () => import('@/views/tool/image-chat/index.vue')
    },
    {
      path: '/ocr',
      name: 'Ocr',
      meta: {
        icon: 'Picture',
        iconActive: 'Picture',
        title: '图片识别',
        activeMenu: '/tool',
        parentPath: '/tool',
        parentName: 'Tool'
      },
      component: () => import('@/views/tool/ocr/index.vue')
    },
    {
      path: '/conversion',
      name: 'Conversion',
      meta: {
        icon: 'DocumentCopy',
        iconActive: 'DocumentCopy',
        title: '文档转换',
        activeMenu: '/tool',
        parentPath: '/tool',
        parentName: 'Tool'
      },
      component: () => import('@/views/tool/conversion/index.vue')
    },
    {
      path: '/address-check',
      name: 'AddressCheck',
      meta: {
        icon: 'Guide',
        iconActive: 'Guide',
        title: '地址识别',
        activeMenu: '/tool',
        parentPath: '/tool',
        parentName: 'Tool'
      },
      component: () => import('@/views/tool/address-check/index.vue')
    },
    {
      path: '/uie',
      name: 'UIE',
      meta: {
        icon: 'Collection',
        iconActive: 'Collection',
        title: '信息抽取',
        activeMenu: '/tool',
        parentPath: '/tool',
        parentName: 'Tool'
      },
      component: () => import('@/views/tool/uie/index.vue')
    },
    {
      path: '/contract-fill',
      name: 'ContractFill',
      meta: {
        icon: 'SetUp',
        iconActive: 'SetUp',
        title: '合同抽取',
        activeMenu: '/tool',
        parentPath: '/tool',
        parentName: 'Tool'
      },
      component: () => import('@/views/tool/contract-fill/index.vue')
    }
  ]
}

export default datasetRouter
