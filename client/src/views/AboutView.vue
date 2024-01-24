<template>
  <div class="about">
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'

export default defineComponent({
  setup() {
    document.location.href = 'https://en.wikipedia.org/wiki/WP:LINKDISP'
  },
})
</script>


<style>
@media (min-width: 1024px) {
  .about {
    font-family: monospace;
  }
}
</style>
