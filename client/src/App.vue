<script setup lang="ts">
import Header from './components/HeaderComponent.vue'
import FooterComponent from './components/FooterComponent.vue'
</script>

<template>
  <div class="link-dispenser-app">
    <header>

      <Header></Header>

    </header>

    <div class="wrapper">
      <RouterView></RouterView>
    </div>

    <footer>
        <FooterComponent></FooterComponent>
      </footer>
    </div>
</template>

<style lang="less" scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';

.wrapper {
  padding: @spacing-100;
  padding-top: @spacing-0;
  flex: 1;
}

.link-dispenser-app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  box-sizing: border-box;
}
</style>
