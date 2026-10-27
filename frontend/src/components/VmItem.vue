<template>
  <div class="vm-card" :class="[statusClass, statusChangeClass]">
    <div class="vm-info">
      <p class="vm-name"><strong>{{ vm.Name }}</strong></p>
      <p class="vm-status">
        Status: <span :class="statusTextClass">{{ vm.State }}</span>
      </p>
    </div>

    <AlertMsg ref="alertRef" />

    <div class="vm-actions">
      <button
        v-if="vm.State === 'shut off'"
        class="action-btn start-btn"
        :disabled="changing_state"
        @click="changeState('start')"
      >
        <span v-if="!changing_state">Start</span>
        <span v-else>Changing...</span>
      </button>

      <button
        v-if="vm.State === 'running'"
        class="action-btn shutdown-btn"
        :disabled="changing_state"
        @click="changeState('shutdown')"
      >
        <span v-if="!changing_state">Shut Down</span>
        <span v-else>Changing...</span>
      </button>

      <button
        v-if="vm.State === 'running'"
        class="action-btn reboot-btn"
        :disabled="changing_state"
        @click="changeState('reboot')"
      >
        <span v-if="!changing_state">Reboot</span>
        <span v-else>Changing...</span>
      </button>
    </div>
  </div>
</template>

<script>
import { clearAuthState } from '../../auth/session';
import AlertMsg from './Alert.vue';
import { apiClient } from '@/config/api';

export default {
  name: 'VmItem',
  components: {
    AlertMsg,
  },
  props: {
    vm: {
      type: Object,
      required: true,
    },
  },
  data() {
    return {
      changing_state: false,
    };
  },
  computed: {
    statusClass() {
      return this.vm.State === 'running' ? 'status-running' : 'status-stopped';
    },
    statusTextClass() {
      return this.vm.State === 'running' ? 'text-green' : 'text-red';
    },
    statusChangeClass() {
      return this.changing_state ? 'disable-status' : 'enable-status';
    },
  },
  methods: {
    async changeState(nextState) {
      this.changing_state = true;

      try {
        const response = await apiClient.post('/vm/state', {
          state: nextState,
          name: this.vm.Name,
          expected_state: this.vm.State,
        });

        const updated = response.data?.Body;
        this.$emit('vm-updated', {
          vm_name: this.vm.Name,
          current_state: updated?.current_state || this.vm.State,
        });

        this.$refs.alertRef.show(
          `${this.vm.Name} state changed to ${updated?.current_state || 'updated'}`
        );
      } catch (error) {
        const status = error.response?.status;
        const detail = error.response?.data?.detail;

        if (status === 401) {
          clearAuthState();
          this.$router.push({ name: 'Login' });
          return;
        }

        if (status === 403) {
          this.$refs.alertRef.show('Access denied for this action.');
          return;
        }

        if (status === 409) {
          const msg =
            typeof detail === 'string'
              ? detail
              : detail?.message ||
                `State conflict for ${this.vm.Name}. Current state is ${detail?.current_state || 'unknown'}.`;
          this.$refs.alertRef.show(msg);
          this.$emit('refresh-requested');
          return;
        }

        this.$refs.alertRef.show(String(detail || 'Failed to update VM state'));
      } finally {
        this.changing_state = false;
      }
    },
  },
};
</script>

<style scoped>
.vm-card {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 16px;
  margin-bottom: 16px;
  transition: all 0.3s ease;
  border-left: 6px solid transparent;
}

.status-running {
  border-left-color: #28a745;
}

.status-stopped {
  border-left-color: #dc3545;
}

.disable-status {
  background: #f0f0f0;
}

.enable-status {
  background: white;
}

.vm-info {
  margin-bottom: 12px;
}

.vm-name {
  font-size: 1.1rem;
  color: #1976d2;
  margin: 0 0 4px 0;
}

.vm-status {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.text-green {
  color: #28a745;
  font-weight: 600;
}

.text-red {
  color: #dc3545;
  font-weight: 600;
}

.vm-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  flex: 1;
  min-width: 80px;
  padding: 8px 12px;
  font-size: 0.9rem;
  font-weight: 500;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.start-btn {
  background: #28a745;
  color: white;
}

.shutdown-btn {
  background: #dc3545;
  color: white;
}

.reboot-btn {
  background: #ffc107;
  color: #333;
}

.action-btn:hover:enabled {
  opacity: 0.85;
  transform: translateY(-1px);
}

.action-btn:disabled {
  background: #ccc;
  cursor: not-allowed;
}

@media (max-width: 600px) {
  .vm-card {
    padding: 12px;
  }

  .vm-actions {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}
</style>
