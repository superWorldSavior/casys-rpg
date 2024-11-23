// Core imports
import { createRouter, createWebHistory } from 'vue-router'

// Store imports
import { useAuthStore } from '../stores/auth'

// View imports
import LibraryView from '../views/LibraryView.vue'
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
      meta: { requiresAuth: false }
    },
    {
      path: '/books/:id',
      component: BookDetailView,
      name: 'book-detail',
      meta: { requiresAuth: false }
    },
    {
      path: '/reader/:id?',
      component: ChatView,
      name: 'reader',
      props: true,
      meta: { requiresAuth: false }
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// Commenté pour simplifier l'authentification
router.beforeEach((_to, _from, next) => {
  next()
})

export default router
