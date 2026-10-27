import { createRouter, createWebHistory } from 'vue-router';

import { isAuthenticated } from '../auth/auth';
import Login from './components/Login.vue';
import NewVm from './components/NewVm.vue';
import NotFound from './components/NotFound.vue';
import VmHome from './components/Home.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { requiresAuth: false },
  },
  {
    path: '/',
    name: 'VmHome',
    component: VmHome,
    meta: { requiresAuth: true },
  },
  {
    path: '/admin/vms',
    name: 'VmAdmin',
    component: NewVm,
    meta: { requiresAuth: true },
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: { requiresAuth: false },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const authed = await isAuthenticated();
    if (!authed) {
      next({ name: 'Login' });
      return;
    }
  }

  if (to.name === 'Login') {
    const authed = await isAuthenticated();
    if (authed) {
      next({ name: 'VmHome' });
      return;
    }
  }

  next();
});

export default router;
