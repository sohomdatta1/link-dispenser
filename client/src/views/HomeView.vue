<script setup lang="ts">
import ArticleLookup from '../components/ArticleLookup.vue'
</script>

<template>
  <main class="home">
    <div class="card">
      <ArticleLookup />
    </div>
  </main>
</template>

<style lang="less" scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';

.home {
  display: flex;
  justify-content: center;
  padding: @spacing-200 @spacing-100;
}

.card {
  width: min(48rem, 100%);
  border: @border-subtle;
  border-radius: @border-radius-base;
  padding: @spacing-150;
  background: @background-color-base;
}
</style>
