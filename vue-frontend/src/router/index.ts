import { createRouter, createWebHistory } from 'vue-router'
import LibraryView from '../views/LibraryView.vue'
import ReaderView from '../views/ReaderView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: LoginView,
      name: 'login'
    },
    {
      path: '/library',
      component: LibraryView,
      name: 'library'
    },
    {
      path: '/reader/:id?',
      component: ReaderView,
      name: 'reader'
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

export default router
