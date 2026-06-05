<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>项目管理</span>
          <el-button type="primary" @click="handleAdd">新增项目</el-button>
        </div>
      </template>

      <el-form :inline="true" :model="searchForm" class="search-form">
        <el-form-item label="项目名称">
          <el-input v-model="searchForm.project_name" placeholder="请输入项目名称" clearable />
        </el-form-item>
        <el-form-item label="项目类型">
          <el-select v-model="searchForm.project_type" placeholder="请选择" clearable>
            <el-option label="人天项目" value="day_project" />
            <el-option label="整包项目" value="package_project" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadData">查询</el-button>
        </el-form-item>
      </el-form>

      <el-table :data="tableData" stripe border>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="project_name" label="项目名称" />
        <el-table-column prop="customer_project_name" label="客户项目名" />
        <el-table-column prop="customer_project_code" label="客户项目编号" />
        <el-table-column prop="project_type" label="项目类型">
          <template #default="{ row }">
            <el-tag :type="row.project_type === 'day_project' ? 'success' : 'warning'">
              {{ row.project_type === 'day_project' ? '人天' : '整包' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="fixed_package_amount" label="固定包干价">
          <template #default="{ row }">
            {{ row.fixed_package_amount ? '¥' + row.fixed_package_amount : '-' }}
          </template>
        </el-table-column>
        <el-table-column prop="customer_surplus_man_day" label="溢量人天" />
        <el-table-column prop="status" label="状态">
          <template #default="{ row }">
            <el-tag>{{ row.status }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button type="primary" link @click="handleEdit(row)">编辑</el-button>
            <el-button type="primary" link @click="goToStaffConfig(row)">人员配置</el-button>
            <el-button type="primary" link @click="showProfit(row)">利润</el-button>
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

    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="700px">
      <el-form :model="form" label-width="120px">
        <el-form-item label="项目名称" required>
          <el-input v-model="form.project_name" />
        </el-form-item>
        <el-form-item label="客户内部项目名">
          <el-input v-model="form.customer_project_name" />
        </el-form-item>
        <el-form-item label="客户内部项目编号">
          <el-input v-model="form.customer_project_code" />
        </el-form-item>
        <el-form-item label="公司名称">
          <el-input v-model="form.company_name" />
        </el-form-item>
        <el-form-item label="项目地址">
          <el-input v-model="form.address" />
        </el-form-item>
        <el-form-item label="项目类型" required>
          <el-select v-model="form.project_type">
            <el-option label="人天项目" value="day_project" />
            <el-option label="整包项目" value="package_project" />
          </el-select>
        </el-form-item>
        <el-form-item label="固定包干总价" v-if="form.project_type === 'package_project'">
          <el-input-number v-model="form.fixed_package_amount" :min="0" />
        </el-form-item>
        <el-form-item label="合同金额">
          <el-input-number v-model="form.contract_amount" :min="0" />
        </el-form-item>
        <el-form-item label="溢量人天">
          <el-input-number v-model="form.customer_surplus_man_day" :min="0" />
        </el-form-item>
        <el-form-item label="溢量兑付状态">
          <el-select v-model="form.surplus_man_day_status">
            <el-option label="待兑付" value="pending" />
            <el-option label="已兑付" value="finished" />
            <el-option label="作废" value="cancel" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="profitVisible" title="项目利润详情" width="600px">
      <el-descriptions :column="2" border v-if="profitData">
        <el-descriptions-item label="项目名称">{{ profitData.project_name }}</el-descriptions-item>
        <el-descriptions-item label="项目类型">{{ profitData.project_type === 'day_project' ? '人天' : '整包' }}</el-descriptions-item>
        <el-descriptions-item label="真实营收">¥{{ profitData.real_revenue }}</el-descriptions-item>
        <el-descriptions-item label="人力成本">¥{{ profitData.real_cost_man_day }}</el-descriptions-item>
        <el-descriptions-item label="差旅成本">¥{{ profitData.real_cost_travel }}</el-descriptions-item>
        <el-descriptions-item label="真实毛利">¥{{ profitData.real_gross_profit }}</el-descriptions-item>
        <el-descriptions-item label="溢量人天">{{ profitData.surplus_man_day }}</el-descriptions-item>
        <el-descriptions-item label="溢量营收">¥{{ profitData.surplus_income }}</el-descriptions-item>
        <template v-if="profitData.project_type === 'package_project'">
          <el-descriptions-item label="整包成本预算">¥{{ profitData.package_cost_budget }}</el-descriptions-item>
          <el-descriptions-item label="整包成本剩余">¥{{ profitData.package_cost_surplus }}</el-descriptions-item>
          <el-descriptions-item label="风险状态">
            <el-tag :type="profitData.package_risk_status === 'normal' ? 'success' : profitData.package_risk_status === 'warning' ? 'warning' : 'danger'">
              {{ profitData.package_risk_status }}
            </el-tag>
          </el-descriptions-item>
        </template>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getProjectList, createProject, updateProject, getProjectProfit } from '@/api'

const router = useRouter()
const searchForm = ref({ project_name: '', customer_project_name: '', customer_project_code: '', project_type: '' })
const tableData = ref([])
const pagination = reactive({ page: 1, pageSize: 20, total: 0 })
const dialogVisible = ref(false)
const dialogTitle = ref('')
const form = ref({})
const profitVisible = ref(false)
const profitData = ref(null)

const loadData = async () => {
  try {
    const res = await getProjectList({ ...searchForm.value, page: pagination.page, page_size: pagination.pageSize })
    tableData.value = res.data.list
    pagination.total = res.total
  } catch (e) { /* error handled */ }
}

const handleAdd = () => {
  form.value = { project_type: 'day_project', status: 'active', customer_surplus_man_day: 0 }
  dialogTitle.value = '新增项目'
  dialogVisible.value = true
}

const handleEdit = (row) => {
  form.value = { ...row }
  dialogTitle.value = '编辑项目'
  dialogVisible.value = true
}

const handleSave = async () => {
  try {
    if (form.value.id) {
      await updateProject(form.value)
    } else {
      await createProject(form.value)
    }
    ElMessage.success('保存成功')
    dialogVisible.value = false
    loadData()
  } catch (e) { /* error handled */ }
}

const goToStaffConfig = (row) => {
  router.push(`/project/${row.id}/staff-config`)
}

const showProfit = async (row) => {
  try {
    const res = await getProjectProfit(row.id)
    profitData.value = res.data
    profitVisible.value = true
  } catch (e) { /* error handled */ }
}

onMounted(loadData)
</script>

<style scoped>
.page-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.search-form { margin-bottom: 20px; }
</style>