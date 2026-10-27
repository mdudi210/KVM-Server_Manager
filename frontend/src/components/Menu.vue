<template>
  <div v-if="isVisible" class="side-panel-overlay" @click.self="closePanel">
    <div class="side-panel-content">

      <div class="side-panel-header">
        <div class="user-info">
          <img :src="profilePhoto" alt="Profile" class="profile-photo" />
          <span class="username">{{ formattedUsername }}</span>
        </div>
        <button class="close-btn" @click="closePanel">✕</button>
      </div>

      <div class="side-panel-body">
        <h4>{{ isAdmin ? 'Admin Dashboard' : 'User Dashboard'}}</h4>
        <div v-if="isAdmin" class="admin-menu">
          <button class="admin-link" @click="goToAdminVm">Create/Clone VM</button>
        </div>
        <slot></slot>
      </div>

      <div class="side-panel-footer">
        <button @click="logout" class="logout-btn">Logout</button>
      </div>
    </div>
  </div>
</template>

<script>
import { clearAuthState } from '../../auth/session';
import { apiClient } from '@/config/api';

export default {
  name: 'ProfileMenu',
  props: {
    isVisible: { type: Boolean, required: true },
    username: { type: String, default: '' },
    profilePhoto: { type: String, default: 'https://via.placeholder.com/35' },
    role: { type: String, default: '' },
  },
  computed: {
    isAdmin() {
      return this.role == 'admin';
    },
    formattedUsername() {
      return this.username.charAt(0).toUpperCase() + this.username.slice(1);
    },
  },
  methods: {
    closePanel() {
      this.$emit('close');
    },
    async logout() {
      try {
        await apiClient.post('/logout');
      } catch (error) {
        // best-effort logout
      }
      clearAuthState();
      this.$router.push({ name: 'Login' });
    },
    goToAdminVm() {
      this.closePanel();
      this.$router.push({ name: 'VmAdmin' });
    },
  },
};
</script>

<style scoped>
.side-panel-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: flex-end;
  z-index: 1000;
  animation: fadeIn 0.3s ease-in-out;
}

.side-panel-content {
  width: 300px;
  max-width: 90%;
  height: 100%;
  background: #fff;
  display: flex;
  flex-direction: column;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.2);
  transform: translateX(0);
  animation: slideIn 0.3s ease-out;
}

.side-panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border-bottom: 1px solid #ddd;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.username {
  font-weight: bold;
  font-size: 1rem;
  color: #333;
}

.profile-photo {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.3rem;
  cursor: pointer;
  color: #555;
}

.close-btn:hover {
  color: #d21919;
}

.side-panel-body {
  flex: 1;
  padding: 20px;
  overflow-y: auto;
}

.side-panel-body h4 {
  font-size: 1.1rem;
  color: #d21919;
  margin-bottom: 15px;
}

.side-panel-footer {
  padding: 15px;
  border-top: 1px solid #ddd;
}

.logout-btn {
  width: 100%;
  padding: 10px;
  background: #2196f3;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: 0.3s ease;
}

.logout-btn:hover {
  background: #0d6efd;
}

.admin-menu {
  color: black;
  padding-left: 0px;
  margin-left: 0px;
}

.admin-link {
  border: none;
  background: #f3f8ff;
  color: #0d6efd;
  width: 100%;
  text-align: left;
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
}

.admin-link:hover {
  background: #e7f0ff;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
  }
  to {
    transform: translateX(0);
  }
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>
