import { hasPermission } from '@/utils/permission/index'
import Layout from '@/layout/main-layout/index.vue'
import { Role } from '@/utils/permission/type'
const settingRouter = {
  path: '/setting',
  name: 'Setting',
  meta: { icon: 'Setting', title: '系统设置', permission: 'SETTING:READ' },
  redirect: () => {
    if (hasPermission(new Role('ADMIN'), 'AND')) {
      return '/user'
    }
    return '/team'
  },
  component: Layout,
  children: [
    {
      path: '/user',
      name: 'User',
      meta: {
        icon: 'User',
        iconActive: 'UserFilled',
        title: '用户管理',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'Setting',
        permission: new Role('ADMIN')
      },
      component: () => import('@/views/user-manage/index.vue')
    },
    {
      path: '/team',
      name: 'Team',
      meta: {
        icon: 'app-team',
        iconActive: 'app-team-active',
        title: '团队成员',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'Setting'
      },
      component: () => import('@/views/team/index.vue')
    },
    {
      path: '/template',
      name: 'Template',
      meta: {
        icon: 'app-template',
        iconActive: 'app-template-active',
        title: '模型设置',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'Setting'
      },
      component: () => import('@/views/template/index.vue')
    },
    {
      path: '/email',
      name: 'Email',
      meta: {
        icon: 'Message',
        title: '邮箱设置',
        activeMenu: '/setting',
        parentPath: '/setting',
        parentName: 'Setting',
        permission: new Role('ADMIN')
      },
      component: () => import('@/views/email/index.vue')
    }
  ]
}

export default settingRouter
