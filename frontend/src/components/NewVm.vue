<template>
  <div class="new-vm-page">
    <TopBar :username="username" :role="role" />

    <div class="panel">
      <h2>Admin VM Provisioning</h2>
      <p>Create brand-new VMs or clone from templates.</p>

      <AlertMsg ref="alertRef" />

      <form @submit.prevent="submit" class="form">
        <label>
          Provision Type
          <select v-model="actionType" required>
            <option value="new">Create New VM</option>
            <option value="clone">Clone Template VM</option>
          </select>
        </label>

        <label>
          OS Type
          <select v-model="vmType" required>
            <option value="Linux">Linux</option>
            <option value="Windows">Windows</option>
          </select>
        </label>

        <label>
          VM Name
          <input v-model.trim="vmName" placeholder="example-vm-01" required />
        </label>

        <div class="actions">
          <button type="submit" :disabled="submitting">
            {{ submitting ? 'Submitting...' : submitLabel }}
          </button>
          <button type="button" class="secondary" @click="$router.push({ name: 'VmHome' })">
            Back to Dashboard
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { clearAuthState, getAuthState } from '../../auth/session';
import TopBar from './TopBar.vue';
import AlertMsg from './Alert.vue';
import { apiClient } from '@/config/api';

export default {
  name: 'VmAdmin',
  components: {
    TopBar,
    AlertMsg,
  },
  data() {
    return {
      username: 'Admin',
      role: 'admin',
      actionType: 'new',
      vmType: 'Linux',
      vmName: '',
      submitting: false,
    };
  },
  computed: {
    submitLabel() {
      return this.actionType === 'new' ? 'Create VM' : 'Clone VM';
    },
  },
  mounted() {
    const auth = getAuthState();
    this.username = auth.user.username || 'Admin';
    this.role = auth.user.role || 'user';
  },
  methods: {
    async submit() {
      if (!/^[A-Za-z0-9._-]{1,63}$/.test(this.vmName)) {
        this.$refs.alertRef.show('VM name must be 1-63 chars and use only letters, numbers, dot, underscore, or hyphen.');
        return;
      }

      this.submitting = true;
      const endpoint = this.actionType === 'new' ? '/vm/new' : '/vm/clone';

      try {
        await apiClient.post(endpoint, {
          vmtoinstall: this.vmType,
          name: this.vmName,
        });

        this.$refs.alertRef.show(
          `${this.vmName} ${this.actionType === 'new' ? 'creation' : 'clone'} request accepted.`
        );
        this.vmName = '';
      } catch (error) {
        const status = error.response?.status;
        const detail = error.response?.data?.detail;

        if (status === 401) {
          clearAuthState();
          this.$router.push({ name: 'Login' });
          return;
        }

        if (status === 403) {
          this.$refs.alertRef.show('Access denied. Admin role is required.');
          this.$router.push({ name: 'VmHome' });
          return;
        }

        this.$refs.alertRef.show(String(detail || 'Failed to submit VM request'));
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>

<style scoped>
.new-vm-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f9fc, #e3f2fd);
  padding: 0.8rem 1rem 1.5rem;
}

.panel {
  max-width: 640px;
  margin: 1rem auto;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.08);
  padding: 1.5rem;
  text-align: left;
}

h2 {
  margin: 0;
  color: #1d4e89;
}

p {
  margin: 0.6rem 0 1.2rem;
  color: #4f5d75;
}

.form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

label {
  font-weight: 600;
  color: #2f3e46;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

select,
input {
  border: 1px solid #cad2c5;
  border-radius: 8px;
  padding: 10px 12px;
  font-size: 0.95rem;
}

.actions {
  display: flex;
  gap: 0.7rem;
}

button {
  border: none;
  border-radius: 8px;
  padding: 10px 14px;
  cursor: pointer;
  font-weight: 700;
  background: #1976d2;
  color: #fff;
}

button.secondary {
  background: #edf2f4;
  color: #1d3557;
}

button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .actions {
    flex-direction: column;
  }
}
</style>
