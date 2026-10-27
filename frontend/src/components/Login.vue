<template>
  <div class="login-container">
    <div class="login-card">
      <h2 class="title">Welcome Back</h2>
      <p class="subtitle">Please login to continue</p>
      <AlertMsg ref="alertRef"></AlertMsg>

      <select v-model="authProvider" class="auth-type">
        <option value="local">Local Login</option>
        <option value="ad">Active Directory Login</option>
      </select>

      <input
        type="text"
        placeholder="Enter your Username"
        v-model="username"
        required
        ref="usernameInput"
        @keyup.enter="$refs.passwordInput.focus()"
        @keyup.down="$refs.passwordInput.focus()"
      >

      <input
        type="password"
        placeholder="Enter your Password"
        v-model="password"
        ref="passwordInput"
        @keyup.enter="loginUser"
        @keyup.up="$refs.usernameInput.focus()"
        required
      >
      <p v-if="loginFailed">Incorrect username or password</p>

      <button @click="loginUser" ref="login-btn">Login</button>
    </div>
  </div>
</template>

<script>
import AlertMsg from './Alert.vue';
import { clearAuthState, setAuthFromLogin } from '../../auth/session';
import { login } from '@/services/login';

export default {
  name: 'LogIn',
  components: {
    AlertMsg,
  },
  data() {
    return {
      username: '',
      password: '',
      authProvider: 'local',
      loginFailed: false,
    };
  },
  methods: {
    async loginUser() {
      this.loginFailed = false;
      clearAuthState();

      try {
        const response = await login(this.username, this.password, this.authProvider);

        if (response.status === 200) {
          setAuthFromLogin(response.data);
          this.$router.push({ name: 'VmHome' });
          return;
        }

        this.password = '';
        this.loginFailed = true;
        this.$refs.alertRef.show('Incorrect username or password');
      } catch (error) {
        this.password = '';
        this.loginFailed = true;
        this.$refs.alertRef.show(`Login Failed: ${error.response?.data?.detail || error.message}`);
      }
    },
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: linear-gradient(135deg, #e3f2fd, #f6f9fc);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  padding: 1rem;
}

.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.title {
  margin-bottom: 0.5rem;
  font-size: 1.8rem;
  font-weight: bold;
  color: #1976d2;
}

.subtitle {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
}

.auth-type,
input {
  width: 100%;
  padding: 12px;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  font-size: 14px;
  outline: none;
  transition: all 0.3s ease;
}

.auth-type:focus,
input:focus {
  border-color: #1976d2;
  box-shadow: 0 0 6px rgba(25, 118, 210, 0.4);
}

button {
  width: 100%;
  padding: 12px;
  background: #1976d2;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
}

button:hover {
  background: #125aa1;
  transform: translateY(-1px);
}

button:active {
  transform: scale(0.98);
}

p {
  font-size: 1rem;
  font-weight: bold;
  color: red;
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
    border-radius: 12px;
  }

  .title {
    font-size: 1.5rem;
  }

  .subtitle {
    font-size: 0.8rem;
  }

  .auth-type,
  input,
  button {
    font-size: 14px;
    padding: 10px;
  }
}
</style>
