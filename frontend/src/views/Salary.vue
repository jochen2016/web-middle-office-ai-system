<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <span>提成薪资管理</span>
      </template>

      <el-tabs v-model="activeTab">
        <el-tab-pane label="提成录入" name="commission">
          <el-form :inline="true" :model="searchForm" class="search-form">
            <el-form-item label="员工">
              <el-select v-model="searchForm.staff_id" clearable filterable>
                <el-option v-for="s in staffList" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="loadCommissionData">查询</el-button>
              <el-button type="primary" @click="handleAddCommission">新增提成</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="commissionList" stripe border>
            <el-table-column prop="staff_name" label="员工" />
            <el-table-column prop="project_name" label="项目" />
            <el-table-column prop="commission_type" label="提成类型">
              <template #default="{ row }">
                <el-tag>{{ row.commission_type === 'day' ? '人天' : row.commission_type === 'both' ? '人天+奖金' : '奖金' }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="day_commission_amount" label="人天提成" />
            <el-table-column prop="package_bonus_amount" label="整包奖金" />
            <el-table-column prop="total_commission" label="总提成" />
            <el-table-column prop="settle_status" label="结算状态" />
          </el-table>
        </el-tab-pane>

        <el-tab-pane label="月度薪资核算" name="salary">
          <el-form inline>
            <el-form-item label="选择员工">
              <el-select v-model="salaryForm.staff_id" filterable>
                <el-option v-for="s in staffList" :key="s.id" :label="s.name" :value="s.id" />
              </el-select>
            </el-form-item>
            <el-form-item label="月份">
              <el-date-picker v-model="salaryForm.month" type="month" value-format="YYYY-MM" />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="handleCreateSalaryBill">生成工资单</el-button>
            </el-form-item>
          </el-form>

          <el-table :data="salaryBillList" stripe border>
            <el-table-column prop="staff_name" label="员工" />
            <el-table-column prop="month" label="月份" />
            <el-table-column prop="base_salary_total" label="底薪" />
            <el-table-column prop="day_commission_total" label="人天提成" />
            <el-table-column prop="package_bonus_total" label="整包奖金" />
            <el-table-column prop="commission_total" label="提成合计" />
            <el-table-column prop="reimburse_total" label="报销合计" />
            <el-table-column prop="final_salary" label="最终薪资">
              <template #default="{ row }">
                <b>¥{{ row.final_salary }}</b>
              </template>
            </el-table-column>
            <el-table-column prop="status" label="状态" />
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <el-dialog v-model="dialogVisible" title="新增提成" width="500px">
      <el-form :model="form" label-width="120px">
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
        <el-form-item label="提成类型" required>
          <el-select v-model="form.commission_type">
            <el-option label="仅人天提成" value="day" />
            <el-option label="人天+整包奖金" value="both" />
          </el-select>
        </el-form-item>
        <el-form-item label="项目人天数">
          <el-input-number v-model="form.project_day_commission" :min="0" />
        </el-form-item>
        <el-form-item label="人天提成金额">
          <el-input-number v-model="form.day_commission_amount" :min="0" />
        </el-form-item>
        <el-form-item label="整包奖金金额" v-if="form.commission_type === 'both'">
          <el-input-number v-model="form.package_bonus_amount" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveCommission">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { addStaffCommission, createSalaryBill, getStaffList, getProjectList } from '@/api'

const activeTab = ref('commission')
const searchForm = ref({ staff_id: null })
const commissionList = ref([])
const salaryBillList = ref([])
const staffList = ref([])
const projectList = ref([])
const dialogVisible = ref(false)
const form = ref({ commission_type: 'day', project_day_commission: 0, day_commission_amount: 0, package_bonus_amount: 0 })
const salaryForm = ref({ staff_id: null, month: '' })

const loadCommissionData = async () => {
  commissionList.value = []
}

const handleAddCommission = () => {
  form.value = { commission_type: 'day', project_day_commission: 0, day_commission_amount: 0, package_bonus_amount: 0 }
  dialogVisible.value = true
}

const handleSaveCommission = async () => {
  try {
    await addStaffCommission(form.value)
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadCommissionData()
  } catch (e) { /* error handled */ }
}

const handleCreateSalaryBill = async () => {
  if (!salaryForm.value.staff_id || !salaryForm.value.month) {
    ElMessage.warning('请选择员工和月份')
    return
  }
  try {
    await createSalaryBill(salaryForm.value)
    ElMessage.success('工资单已生成')
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

onMounted(() => { loadStaffList(); loadProjectList() })
</script>

<style scoped>
.page-container { padding: 20px; }
.search-form { margin-bottom: 20px; }
</style>