import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login, getCurrentUser } from '@/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  const isLoggedIn = computed(() => !!token.value)

  async function loginAction(username, password) {
    const res = await login(username, password)
    token.value = res.access_token
    localStorage.setItem('token', res.access_token)
    return res
  }

  async function fetchUserInfo() {
    if (!token.value) return null
    const res = await getCurrentUser()
    userInfo.value = res
    return res
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
  }

  return {
    token,
    userInfo,
    isLoggedIn,
    loginAction,
    fetchUserInfo,
    logout
  }
})