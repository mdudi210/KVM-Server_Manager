<template>
  <div class="flex flex-col items-center justify-center h-screen text-center bg-gray-100">
    <h1 class="text-6xl font-bold text-red-500">404</h1>
    <p class="text-2xl font-semibold mt-4">Page Not Found</p>
    <p class="text-gray-600 mt-2">
      Oops! The page you are looking for doesn’t exist or has been moved.
    </p>

    <router-link
      to="/"
      class="mt-6 px-6 py-3 bg-blue-600 text-white text-lg rounded-xl shadow hover:bg-blue-700 transition"
    >
      Go Home
    </router-link>
  </div>
</template>

<script setup>

</script>
