<script setup lang="ts">
import Header from './components/HeaderComponent.vue'
</script>

<template>
  <header>

    <Header />

  </header>

  <div class="wrapper">
    <RouterView />
  </div>
</template>

<style lang="less" scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';

.wrapper {
  padding: @spacing-100;
  padding-top: @spacing-0;
}
</style>
