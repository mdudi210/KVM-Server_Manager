<template>
  <div>
    <router-view/>
  </div>
</template>

<script>
export default {
  name: 'App',
  }
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 0px;
}
li {
  list-style: none;
}
.header {
  margin: 10px;
}
.body {
  margin: 20px;
}
</style>