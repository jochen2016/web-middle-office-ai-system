import axios from 'axios'
import { ElMessage } from 'element-plus'

const request = axios.create({
  baseURL: '/api/v1',
  timeout: 30000
})

// 请求拦截器
request.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器
request.interceptors.response.use(
  response => {
    const res = response.data
    if (res.code !== 0) {
      ElMessage.error(res.msg || '请求失败')
      return Promise.reject(res)
    }
    return res
  },
  error => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    ElMessage.error(error.message || '网络错误')
    return Promise.reject(error)
  }
)

// ============ 认证 ============
export const login = (username, password) => 
  request.post('/auth/login', { username, password })

export const getCurrentUser = () => request.get('/auth/current')

// ============ 项目 ============
export const getProjectList = (params) => request.get('/project/get', { params })
export const createProject = (data) => request.post('/project/create', data)
export const updateProject = (data) => request.put('/project/update', data)
export const getProjectProfit = (projectId) => request.get('/project/profit/get', { params: { project_id: projectId } })

export const saveProjectStaffConfig = (data) => request.post('/project/staff/config/save', data)
export const getProjectStaffConfigList = (projectId) => request.get('/project/staff/config/list', { params: { project_id: projectId } })
export const deleteProjectStaffConfig = (id) => request.delete('/project/staff/config/del', { params: { id } })

// ============ 合同 ============
export const getContractList = (params) => request.get('/contract/list', { params })
export const updateContractPayment = (data) => request.put('/contract/payment/update', data)

// ============ 员工 ============
export const getStaffList = (params) => request.get('/staff/list', { params })
export const createStaff = (data) => request.post('/staff/create', data)
export const updateStaff = (data) => request.put('/staff/update', data)
export const deleteStaff = (id) => request.delete('/staff/delete', { params: { id } })
export const getStaffSalaryConfig = (staffId) => request.get('/salary/staff/config', { params: { staff_id: staffId } })

// ============ 签到 ============
export const createSignTask = (data) => request.post('/sign/task/create', data)
export const getSignList = (params) => request.get('/sign/list', { params })

// ============ 报销 ============
export const createReimburse = (data) => request.post('/reimburse/create', data)
export const getStaffMonthReimburse = (params) => request.get('/reimburse/staff/month', { params })

// ============ 提成薪资 ============
export const addStaffCommission = (data) => request.post('/staff/commission/add', data)
export const createSalaryBill = (data) => request.post('/salary/bill/create', data)

// ============ 任务 ============
export const getDeadTaskList = (params) => request.get('/task/dead/list', { params })
export const retryDeadTask = (data) => request.post('/task/retry', data)

export default request