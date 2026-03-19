<template>
  <main class="login-prompt">
    <div class="card">
      <h1 class="title">Log in required</h1>
      <p class="body">
        You need to log in with Wikimedia OAuth to use this tool.
        <p v-if="nextPath !== '/'" class="subtle">
          After logging in, you will return to <code>{{ nextPath }}</code>.
        </p>
      </p>

      <cdx-button class="login-button" type="button" @click="startLogin">Log in</cdx-button>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CdxButton } from '@wikimedia/codex'

const route = useRoute()
const router = useRouter()

const authenticated = ref(false)

function normalizeNext(raw: unknown): string {
  if (typeof raw !== 'string' || raw.length === 0) {
    return '/'
  }

  // Only allow same-origin paths.
  if (!raw.startsWith('/') || raw.startsWith('//') || raw.includes('://')) {
    return '/'
  }

  // Avoid looping back to this page.
  if (raw.startsWith('/auth/login')) {
    return '/'
  }

  return decodeURI(raw).replace(/ /g, '_')
}

const nextPath = computed(() => normalizeNext(route.query.next))
const loginUrl = computed(() => `/login?next=${encodeURIComponent(nextPath.value)}`)

function startLogin() {
  window.location.href = loginUrl.value
}

onMounted(async () => {
  try {
    const resp = await fetch('/api/whoami')
    const json = await resp.json()
    authenticated.value = Boolean(json?.authenticated)
  } catch (_) {
    authenticated.value = false
  }

  if (authenticated.value) {
    router.replace(nextPath.value)
  }
})
</script>

<style lang="less" scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';

.login-prompt {
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

.title {
  margin: 0;
  font-size: @font-size-xx-large;
}

.body {
  margin: @spacing-75 0 @spacing-150;
  color: @color-subtle;
}

.subtle {
  margin: @spacing-150 0 0;
  font-size: @font-size-small;
}

code {
  font-family: @font-family-monospace;
}
</style>
