<template>
  <el-config-provider :locale="zhCn">
    <div id="app">
      <el-container v-if="isLoggedIn">
        <el-aside width="200px">
          <div class="logo">Web中台AI</div>
          <el-menu
            :default-active="currentRoute"
            router
            background-color="#304156"
            text-color="#bfcbd9"
            active-text-color="#409EFF"
          >
            <el-menu-item index="/dashboard">
              <el-icon><DataAnalysis /></el-icon>
              <span>数据仪表盘</span>
            </el-menu-item>
            <el-menu-item index="/staff">
              <el-icon><User /></el-icon>
              <span>人员管理</span>
            </el-menu-item>
            <el-menu-item index="/project">
              <el-icon><FolderOpened /></el-icon>
              <span>项目管理</span>
            </el-menu-item>
            <el-menu-item index="/reimburse">
              <el-icon><Receipt /></el-icon>
              <span>报销管理</span>
            </el-menu-item>
            <el-menu-item index="/salary">
              <el-icon><Money /></el-icon>
              <span>提成薪资</span>
            </el-menu-item>
            <el-menu-item index="/surplus">
              <el-icon><Wallet /></el-icon>
              <span>溢量台账</span>
            </el-menu-item>
            <el-menu-item index="/sign">
              <el-icon><Location /></el-icon>
              <span>任务签到</span>
            </el-menu-item>
          </el-menu>
        </el-aside>
        <el-container>
          <el-header>
            <div class="header-content">
              <span class="title">Web中台AI系统</span>
              <el-dropdown @command="handleCommand">
                <span class="user-info">
                  <el-icon><Avatar /></el-icon>
                  {{ username }}
                </span>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="logout">退出登录</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </el-header>
          <el-main>
            <router-view />
          </el-main>
        </el-container>
      </el-container>
      <router-view v-else />
    </div>
  </el-config-provider>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from './store'
import { ElConfigProvider } from 'element-plus'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const isLoggedIn = computed(() => userStore.isLoggedIn)
const username = computed(() => userStore.username)
const currentRoute = computed(() => route.path)

const handleCommand = (command) => {
  if (command === 'logout') {
    userStore.logout()
    router.push('/login')
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Source Han Sans CN', 'PingFang SC', sans-serif;
}

#app {
  height: 100vh;
}

.el-aside {
  background-color: #304156;
}

.logo {
  height: 60px;
  line-height: 60px;
  text-align: center;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  background-color: #263445;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.1);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 100%;
}

.title {
  font-size: 16px;
  font-weight: 600;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 5px;
  cursor: pointer;
}

.el-main {
  background-color: #f5f7fa;
}
</style>