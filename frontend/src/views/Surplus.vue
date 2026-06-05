<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <span>溢量台账管理</span>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目">
          <el-select v-model="searchForm.project_id" clearable filterable>
            <el-option v-for="p in projectList" :key="p.id" :label="p.project_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="searchForm.status" clearable>
            <el-option label="待兑付" value="pending" />
            <el-option label="已兑付" value="finished" />
            <el-option label="作废" value="cancel" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="handleExport">导出</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" stripe border>
        <el-table-column prop="project_name" label="项目名称" />
        <el-table-column prop="customer_project_name" label="客户项目名" />
        <el-table-column prop="customer_project_code" label="客户项目编号" />
        <el-table-column prop="customer_surplus_man_day" label="溢量人天" />
        <el-table-column prop="surplus_income" label="溢量营收">
          <template #default="{ row }">
            ¥{{ row.surplus_income }}
          </template>
        </el-table-column>
        <el-table-column prop="surplus_man_day_status" label="兑付状态">
          <template #default="{ row }">
            <el-tag :type="row.surplus_man_day_status === 'pending' ? 'warning' : row.surplus_man_day_status === 'finished' ? 'success' : 'info'">
              {{ row.surplus_man_day_status === 'pending' ? '待兑付' : row.surplus_man_day_status === 'finished' ? '已兑付' : '作废' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link v-if="row.surplus_man_day_status === 'pending'" @click="handleFinish(row)">兑付</el-button>
            <el-button type="danger" link v-if="row.surplus_man_day_status === 'pending'" @click="handleCancel(row)">作废</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
        style="margin-top: 20px; justify-content: flex-end"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { getProjectList, updateProject } from '@/api'

const searchForm = ref({ project_id: null, status: '' })
const tableData = ref([])
const projectList = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })

const loadData = async () => {
  try {
    const res = await getProjectList({ ...searchForm.value, page: pagination.page, page_size: pagination.pageSize })
    tableData.value = res.data.list.filter(p => p.customer_surplus_man_day > 0)
    pagination.total = tableData.value.length
  } catch (e) { /* error handled */ }
}

const loadProjectList = async () => {
  try {
    const res = await getProjectList({ page: 1, page_size: 100 })
    projectList.value = res.data.list
  } catch (e) { /* error handled */ }
}

const handleFinish = async (row) => {
  try {
    await updateProject({ id: row.id, surplus_man_day_status: 'finished' })
    ElMessage.success('已兑付')
    loadData()
  } catch (e) { /* error handled */ }
}

const handleCancel = async (row) => {
  try {
    await updateProject({ id: row.id, surplus_man_day_status: 'cancel' })
    ElMessage.success('已作废')
    loadData()
  } catch (e) { /* error handled */ }
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

onMounted(() => { loadData(); loadProjectList() })
</script>

<style scoped>
.page-container { padding: 20px; }
.search-form { margin-bottom: 20px; }
</style>