<template>
  <div class="register-container">
    <h2>Register</h2>
    <form @submit.prevent="handleRegister">
      <div>
        <label>Username:</label>
        <input v-model="username" required />
      </div>
      <div>
        <label>Email:</label>
        <input v-model="email" type="email" required />
      </div>
      <div>
        <label>Password:</label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">Register</button>
    </form>
    <p>
      Already have an account? <router-link to="/login">Login</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { register } from '@/api/user';
import { useRouter } from 'vue-router';

const username = ref('');
const email = ref('');
const password = ref('');
const router = useRouter();

const handleRegister = async () => {
  try {
    await register({
      uname: username.value,
      email: email.value,
      pwd: password.value,
    });
    alert('Registration successful! Please login.');
    router.push('/login');
  } catch (error) {
    alert('Registration failed: ' + (error.response?.data?.detail || error.message));
  }
};
</script>

<style scoped>
.register-container {
  max-width: 300px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 5px;
}
div {
  margin-bottom: 10px;
}
label {
  display: block;
}
input {
  width: 100%;
  padding: 5px;
}
button {
  width: 100%;
  padding: 8px;
  background-color: #008CBA;
  color: white;
  border: none;
  cursor: pointer;
}
button:hover {
  background-color: #007bb5;
}
</style>
