<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>人员管理</span>
          <el-button type="primary" @click="handleAdd">新增员工</el-button>
        </div>
      </template>
      
      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="姓名">
          <el-input v-model="searchForm.name" placeholder="请输入姓名" clearable />
        </el-form-item>
        <el-form-item label="职级">
          <el-select v-model="searchForm.staff_level" placeholder="请选择" clearable>
            <el-option label="P0" value="p0" />
            <el-option label="P1-1" value="p1-1" />
            <el-option label="P1-2" value="p1-2" />
            <el-option label="P1-3" value="p1-3" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" stripe border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="name" label="姓名" />
        <el-table-column prop="department" label="部门" />
        <el-table-column prop="staff_level" label="职级">
          <template #default="{ row }">
            <el-tag>{{ row.staff_level }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="base_salary" label="底薪" />
        <el-table-column prop="default_day_price" label="对外单价" />
        <el-table-column prop="default_day_commission" label="提成单价" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag :type="row.status === 'active' ? 'success' : 'info'">{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="600px">
      <el-form :model="form" label-width="100px">
        <el-form-item label="姓名" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="飞书UID">
          <el-input v-model="form.feishu_uid" />
        </el-form-item>
        <el-form-item label="部门">
          <el-input v-model="form.department" />
        </el-form-item>
        <el-form-item label="职级" required>
          <el-select v-model="form.staff_level">
            <el-option label="P0" value="p0" />
            <el-option label="P1-1" value="p1-1" />
            <el-option label="P1-2" value="p1-2" />
            <el-option label="P1-3" value="p1-3" />
          </el-select>
        </el-form-item>
        <el-form-item label="底薪">
          <el-input-number v-model="form.base_salary" :min="0" />
        </el-form-item>
        <el-form-item label="对外结算单价" required>
          <el-input-number v-model="form.default_day_price" :min="0" />
        </el-form-item>
        <el-form-item label="人天提成单价" required>
          <el-input-number v-model="form.default_day_commission" :min="0" />
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
import { ElMessage, ElMessageBox } from 'element-plus'
import { getStaffList, createStaff, updateStaff, deleteStaff } from '@/api'

const searchForm = ref({ name: '', staff_level: '' })
const tableData = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({})

const LEVEL_PRICE_MAP = {
  'p0': { day_price: 600, day_commission: 50 },
  'p1-1': { day_price: 800, day_commission: 120 },
  'p1-2': { day_price: 1000, day_commission: 220 },
  'p1-3': { day_price: 1200, day_commission: 300 }
}

const loadData = async () => {
  try {
    const res = await getStaffList({
      ...searchForm.value,
      page: pagination.page,
      page_size: pagination.pageSize
    })
    tableData.value = res.data.list
    pagination.total = res.total
  } catch (e) { /* error handled */ }
}

const handleAdd = () => {
  form.value = { staff_level: 'p0', base_salary: 0, default_day_price: 600, default_day_commission: 50 }
  dialogTitle.value = '新增员工'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  form.value = { ...row }
  dialogTitle.value = '编辑员工'
  dialogVisible.value = true
}

const handleSave = async () => {
  try {
    if (form.value.id) {
      await updateStaff(form.value)
    } else {
      await createStaff(form.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { /* error handled */ }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除该员工？', '提示', { type: 'warning' })
    await deleteStaff(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { /* error handled */ }
}

onMounted(loadData)
</script>

<style scoped>
.page-container {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.search-form {
  margin-bottom: 20px;
}
</style>