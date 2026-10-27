<template>
  <header class="topbar">
    <div class="logo">
      <h2>⚙ <span class="vm-text">VM Manager</span></h2>
    </div>
    <div class="user-section">
      <button 
        @click="togglePanel" 
        :aria-expanded="isPanelVisible"
        aria-label="User Profile"
        title="User Profile">
        {{ avatarLetter }}
      </button>
      <ProfileMenu 
        :role="role" 
        :username="username" 
        :isVisible="isPanelVisible" 
        @close="closeSidePanel"
      />
    </div>
  </header>
</template>

<script>
import ProfileMenu from './Menu.vue'

export default {
  name: 'TopBar',
  components: { ProfileMenu },
  props: {
    username: { type: String, required: true },
    role: { type: String, required: false }
  },
  data() {
    return { isPanelVisible: false };
  },
  computed: {
    avatarLetter() {
      const name = this.username || 'U';
      return name.charAt(0).toUpperCase();
    }
  },
  methods: {
    togglePanel() {
      this.isPanelVisible = !this.isPanelVisible;
    },
    closeSidePanel() {
      this.isPanelVisible = false;
    }
  }
};
</script>

<style scoped>
.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 1rem;
  background: linear-gradient(90deg, #d21919, #2196f3);
  color: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  margin-bottom: 1rem;
  flex-wrap: nowrap;
}

.logo h2 {
  margin: 0;
  font-size: 1.8rem;
  font-weight: 200;
  white-space: nowrap;
}

.vm-text {
  display: inline;
}

/* Profile Button */
.user-section {
  display: flex;
  align-items: center;
}

.user-section button {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: #fff;
  color: #d21919;
  border: none;
  font-weight: bold;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s, transform 0.2s;
}

.user-section button:hover,
.user-section button:focus {
  background: #f0f0f0;
  transform: scale(1.05);
}

/* Hide VM text automatically when space is tight */
@media (max-width: 350px) {
  .vm-text {
    display: none;
  }
}
</style>
