import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import LibraryView from '../views/LibraryView.vue'
import ReaderView from '../views/ReaderView.vue'
import LoginView from '../views/LoginView.vue'
import BookDetailView from '../views/BookDetailView.vue'
import ChatView from '../views/ChatView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      component: LoginView,
      name: 'login',
      meta: { requiresAuth: false }
    },
    {
      path: '/',
      component: LibraryView,
      name: 'home',
      meta: { requiresAuth: true }
    },
    {
      path: '/library',
      component: LibraryView,
      name: 'library',
      meta: { requiresAuth: true }
    },
    {
      path: '/books/:id',
      component: BookDetailView,
      name: 'book-detail',
      meta: { requiresAuth: true }
    },
    {
      path: '/reader/:id?',
      component: ChatView,
      name: 'reader',
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/chat',
      component: ChatView,
      name: 'chat',
      meta: { requiresAuth: true }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

router.beforeEach((to, _from, next) => {
  const authStore = useAuthStore()

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login' })
  } else if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'library' })
  } else {
    next()
  }
})

export default router
