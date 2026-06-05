import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue')
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/views/Dashboard.vue')
  },
  {
    path: '/staff',
    name: 'Staff',
    component: () => import('@/views/Staff.vue')
  },
  {
    path: '/project',
    name: 'Project',
    component: () => import('@/views/Project.vue')
  },
  {
    path: '/project/:id/staff-config',
    name: 'ProjectStaffConfig',
    component: () => import('@/views/ProjectStaffConfig.vue')
  },
  {
    path: '/reimburse',
    name: 'Reimburse',
    component: () => import('@/views/Reimburse.vue')
  },
  {
    path: '/salary',
    name: 'Salary',
    component: () => import('@/views/Salary.vue')
  },
  {
    path: '/surplus',
    name: 'Surplus',
    component: () => import('@/views/Surplus.vue')
  },
  {
    path: '/sign',
    name: 'Sign',
    component: () => import('@/views/Sign.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router