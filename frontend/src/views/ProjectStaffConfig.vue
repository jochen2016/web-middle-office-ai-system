<template>
  <div class="page-container">
    <el-page-header @back="router.back()" title="返回项目列表">
      <template #content>
        <span class="title">项目人员提成配置</span>
      </template>
    </el-page-header>

    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>配置列表</span>
          <el-button type="primary" @click="handleAdd">新增配置</el-button>
        </div>
      </template>

      <el-table :data="tableData" stripe border>
        <el-table-column prop="staff_name" label="员工姓名" />
        <el-table-column prop="staff_level" label="职级" />
        <el-table-column prop="default_day_commission" label="职级默认提成" />
        <el-table-column prop="custom_day_commission" label="自定义提成">
          <template #default="{ row }">
            {{ row.custom_day_commission ?? '-' }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" link @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="dialogVisible" title="配置人员提成" width="400px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="选择员工" required>
          <el-select v-model="form.staff_id" filterable>
            <el-option v-for="s in staffList" :key="s.id" :label="s.name" :value="s.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="自定义人天提成">
          <el-input-number v-model="form.custom_day_commission" :min="0" />
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
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getProjectStaffConfigList, saveProjectStaffConfig, deleteProjectStaffConfig, getStaffList } from '@/api'

const route = useRoute()
const router = useRouter()
const projectId = route.params.id
const tableData = ref([])
const staffList = ref([])
const dialogVisible = ref(false)
const form = ref({})

const loadData = async () => {
  try {
    const res = await getProjectStaffConfigList(projectId)
    tableData.value = res.data.list
  } catch (e) { /* error handled */ }
}

const loadStaffList = async () => {
  try {
    const res = await getStaffList({ page: 1, page_size: 100 })
    staffList.value = res.data.list
  } catch (e) { /* error handled */ }
}

const handleAdd = () => {
  form.value = { staff_id: null, custom_day_commission: null }
  dialogVisible.value = true
}

const handleEdit = (row) => {
  form.value = { id: row.id, staff_id: row.staff_id, custom_day_commission: row.custom_day_commission }
  dialogVisible.value = true
}

const handleSave = async () => {
  try {
    await saveProjectStaffConfig({ ...form.value, project_id: projectId })
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { /* error handled */ }
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确认删除？', '提示', { type: 'warning' })
    await deleteProjectStaffConfig(row.id)
    ElMessage.success('删除成功')
    loadData()
  } catch (e) { /* error handled */ }
}

onMounted(() => { loadData(); loadStaffList() })
</script>

<style scoped>
.page-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.title { font-size: 16px; font-weight: 600; }
</style>