<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon blue"><el-icon><FolderOpened /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">{{ stats.projectCount }}</div>
            <div class="stat-label">项目总数</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon green"><el-icon><TrendCharts /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">¥{{ stats.totalRevenue }}</div>
            <div class="stat-label">总营收</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon orange"><el-icon><Money /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">¥{{ stats.totalCost }}</div>
            <div class="stat-label">总成本</div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-icon red"><el-icon><Wallet /></el-icon></div>
          <div class="stat-content">
            <div class="stat-value">¥{{ stats.totalProfit }}</div>
            <div class="stat-label">总毛利</div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>项目预警</span>
          </template>
          <el-table :data="warningProjects" stripe>
            <el-table-column prop="project_name" label="项目名称" />
            <el-table-column prop="risk_status" label="风险状态">
              <template #default="{ row }">
                <el-tag :type="row.risk_status === '亏损' ? 'danger' : 'warning'">
                  {{ row.risk_status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="cost_surplus" label="剩余成本" />
          </el-table>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>月度提成报销数据</span>
          </template>
          <div ref="chartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const stats = ref({
  projectCount: 12,
  totalRevenue: 856000,
  totalCost: 423000,
  totalProfit: 433000
})

const warningProjects = ref([
  { project_name: 'XX项目A', risk_status: '亏损', cost_surplus: '-¥12,500' },
  { project_name: 'XX项目B', risk_status: '预警', cost_surplus: '¥3,200' }
])

const chartRef = ref(null)

onMounted(() => {
  if (chartRef.value) {
    const chart = echarts.init(chartRef.value)
    chart.setOption({
      tooltip: { trigger: 'axis' },
      legend: { data: ['提成', '报销'] },
      xAxis: { type: 'category', data: ['1月', '2月', '3月', '4月', '5月', '6月'] },
      yAxis: { type: 'value' },
      series: [
        { name: '提成', type: 'bar', data: [12000, 15000, 18000, 14000, 20000, 22000] },
        { name: '报销', type: 'bar', data: [8000, 9500, 11000, 9000, 12000, 13500] }
      ]
    })
  }
})
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  display: flex;
  align-items: center;
  padding: 20px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  margin-right: 20px;
}

.stat-icon.blue { background: #e6f7ff; color: #1890ff; }
.stat-icon.green { background: #f6ffed; color: #52c41a; }
.stat-icon.orange { background: #fff7e6; color: #fa8c16; }
.stat-icon.red { background: #fff1f0; color: #ff4d4f; }

.stat-value {
  font-size: 24px;
  font-weight: bold;
}

.stat-label {
  color: #999;
  margin-top: 5px;
}
</style>