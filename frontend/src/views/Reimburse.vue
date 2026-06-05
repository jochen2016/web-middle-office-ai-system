<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>报销管理</span>
          <el-button type="primary" @click="handleAdd">OCR上传</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="员工">
          <el-select v-model="searchForm.staff_id" clearable filterable>
            <el-option v-for="s in staffList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="报销类型">
          <el-select v-model="searchForm.reimburse_type" clearable>
            <el-option label="普通报销" value="default" />
            <el-option label="抵税抵扣" value="deduction" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
          <el-button @click="handleExport">导出</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" stripe border>
        <el-table-column prop="invoice_no" label="发票号" />
        <el-table-column prop="staff_name" label="员工" />
        <el-table-column prop="project_name" label="项目" />
        <el-table-column prop="invoice_amount" label="金额">
          <template #default="{ row }">
            ¥{{ row.invoice_amount }}
          </template>
        </el-table-column>
        <el-table-column prop="invoice_date" label="发票日期" />
        <el-table-column prop="reimburse_type" label="类型">
          <template #default="{ row }">
            <el-tag :type="row.reimburse_type === 'default' ? 'success' : 'warning'">
              {{ row.reimburse_type === 'default' ? '普通' : '抵税' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="check_status" label="审核状态" />
        <el-table-column prop="settle_status" label="结算状态" />
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

    <el-dialog v-model="dialogVisible" title="新增报销" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="员工" required>
          <el-select v-model="form.staff_id" filterable>
            <el-option v-for="s in staffList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目" required>
          <el-select v-model="form.project_id" filterable>
            <el-option v-for="p in projectList" :key="p.id" :label="p.project_name" :value="p.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="发票号" required>
          <el-input v-model="form.invoice_no" />
        </el-form-item>
        <el-form-item label="发票金额" required>
          <el-input-number v-model="form.invoice_amount" :min="0" />
        </el-form-item>
        <el-form-item label="报销类型" required>
          <el-select v-model="form.reimburse_type">
            <el-option label="普通报销" value="default" />
            <el-option label="抵税抵扣" value="deduction" />
          </el-select>
        </el-form-item>
        <el-form-item label="文件">
          <el-input v-model="form.file_url" placeholder="文件URL" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="form.remark" type="textarea" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { createReimburse, getStaffList, getProjectList } from '@/api'

const searchForm = ref({ staff_id: null, reimburse_type: '' })
const tableData = ref([])
const staffList = ref([])
const projectList = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const dialogVisible = ref(false)
const form = ref({ reimburse_type: 'default' })

const loadData = async () => {
  // 实际调用API
  tableData.value = []
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

const handleAdd = () => {
  form.value = { reimburse_type: 'default' }
  dialogVisible.value = true
}

const handleSave = async () => {
  try {
    await createReimburse(form.value)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { /* error handled */ }
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}

onMounted(() => { loadData(); loadStaffList(); loadProjectList() })
</script>

<style scoped>
.page-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>