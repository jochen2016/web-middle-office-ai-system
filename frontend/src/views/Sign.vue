<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>任务签到管理</span>
        </div>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="签到记录" name="records">
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="员工">
              <el-select v-model="searchForm.staff_id" clearable filterable>
                <el-option v-for="s in staffList" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="项目">
              <el-select v-model="searchForm.project_id" clearable filterable>
                <el-option v-for="p in projectList" :key="p.id" :label="p.project_name" :value="p.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="状态">
              <el-select v-model="searchForm.sign_status" clearable>
                <el-option label="待签到" value="pending" />
                <el-option label="成功" value="success" />
                <el-option label="失败" value="failed" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadSignData">查询</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="signList" stripe border>
            <el-table-column prop="staff_name" label="员工" />
            <el-table-column prop="project_name" label="项目" />
            <el-table-column prop="sign_address" label="签到地址" />
            <el-table-column prop="sign_status" label="状态">
              <template #default="{ row }">
                <el-tag :type="row.sign_status === 'success' ? 'success' : row.sign_status === 'failed' ? 'danger' : 'warning'">
                  {{ row.sign_status === 'success' ? '成功' : row.sign_status === 'failed' ? '失败' : '待签到' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="sign_time" label="签到时间" />
            <el-table-column prop="source" label="来源" />
          </el-table>

          <el-pagination
            v-model:current-page="pagination.page"
            v-model:page-size="pagination.pageSize"
            :total="pagination.total"
            :page-sizes="[10, 20, 50]"
            layout="total, sizes, prev, pager, next"
            style="margin-top: 20px; justify-content: flex-end"
          />
        </el-tab-pane>

        <el-tab-pane label="死信任务" name="dead">
          <el-table :data="deadTaskList" stripe border>
            <el-table-column prop="task_id" label="任务ID" />
            <el-table-column prop="task_type" label="任务类型" />
            <el-table-column prop="source" label="来源" />
            <el-table-column prop="create_time" label="创建时间" />
            <el-table-column prop="error_msg" label="错误信息" show-overflow-tooltip />
            <el-table-column prop="retry_count" label="重试次数" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button type="primary" link @click="handleRetry(row)">重试</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getSignList, getDeadTaskList, retryDeadTask, getStaffList, getProjectList } from '@/api'

const activeTab = ref('records')
const searchForm = ref({ staff_id: null, project_id: null, sign_status: '' })
const signList = ref([])
const deadTaskList = ref([])
const staffList = ref([])
const projectList = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const loadSignData = async () => {
  try {
    const res = await getSignList({ ...searchForm.value, page: pagination.page, page_size: pagination.pageSize })
    signList.value = res.data.list
    pagination.total = res.total
  } catch (e) { /* error handled */ }
}

const loadDeadTaskData = async () => {
  try {
    const res = await getDeadTaskList({ page: 1, page_size: 100 })
    deadTaskList.value = res.data.list
  } catch (e) { /* error handled */ }
}

const handleRetry = async (row) => {
  try {
    await retryDeadTask({ task_id: row.task_id, task_type: row.task_type })
    ElMessage.success('任务已重新入队')
    loadDeadTaskData()
  } catch (e) { /* error handled */ }
}

const loadStaffList = async () => {
  try {
    const res = await getStaffList({ page: 1, page_size: 100 })
    staffList.value = res.data.list
  } catch (e) { /* error handled */ }
}

const loadProjectList = async () => {
  try {
    const res = await getProjectList({ page: 1, page_size: 100 })
    projectList.value = res.data.list
  } catch (e) { /* error handled */ }
}

onMounted(() => { loadSignData(); loadDeadTaskData(); loadStaffList(); loadProjectList() })
</script>

<style scoped>
.page-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>