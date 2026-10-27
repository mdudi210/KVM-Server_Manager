<template>
  <transition name="fade">
    <div v-if="visible" class="alert-box">
      <p>{{ currentMessage }}</p>
    </div>
  </transition>
</template>

<script>
export default {
  name: "AlertMsg",
  props: {
    message: {
      type: String,
      default: "There is some problem in backend"
    },
    duration: {
      type: Number,
      default: 3000
    }
  },
  data() {
    return {
      visible: false,
      currentMessage: this.message 
    }
  },
  methods: {
    show(msg) {
      this.currentMessage = msg || this.message
      this.visible = true
      setTimeout(() => {
        this.visible = false
      }, this.duration)
    }
  }
}
</script>

<style scoped>
.alert-box {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #ff4d4f;
  color: white;
  padding: 16px 24px;
  border-radius: 8px;
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  z-index: 1000;
  font-size: 16px;
  text-align: center;
}

.fade-enter-active, .fade-leave-active {
  transition: opacity 0.5s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
