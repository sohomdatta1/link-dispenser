<template>
    <nav class="nav">
        <router-link class="active" to="/">
            <cdx-icon :icon="cdxIconLink"></cdx-icon>
            link-dispenser
        </router-link>
        <button v-if="isAuthenticated" class="right auth-button" type="button" @click="startLogout"><small>Log out</small></button>
        <a v-if="isAuthenticated" class="user-name" href="https://en.wikipedia.org/wiki/Special:MyPage"><small>{{ user }}</small></a>
        <button v-else class="right auth-button" type="button" @click="startLogin"><small>Log in</small></button>
        <a class="right less-link-padding" href="https://gitlab.wikimedia.org/toolforge-repos/link-dispenser" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/3/35/GitLab_icon.svg" class="right-icon-img" /></a>
        <a class="right less-link-padding" href="https://phabricator.wikimedia.org/maniphest/task/edit/form/43/?projects=Tool-link-dispenser&subscribers=Soda" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/1/10/Ic_bug_report_48px.svg" class="right-icon-img"></a>
        <a class="right" href="https://en.wikipedia.org/wiki/WP:LINKDISP" target="_blank"><small>(docs)</small></a>
    </nav>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { RouterLink } from 'vue-router'
import { CdxIcon } from '@wikimedia/codex';
import { cdxIconLink } from '@wikimedia/codex-icons';

export default defineComponent({
    data: () => ( {
        cdxIconLink,
        isAuthenticated: false,
        user: ''
    }),
    components: {
        CdxIcon,
        RouterLink
    },
    methods: {
        async loadAuthState() {
            try {
                const response = await fetch('/api/whoami');
                const json = await response.json();
                this.isAuthenticated = Boolean(json?.authenticated);
                this.user = json?.user?.username || '';
            } catch (_) {
                this.isAuthenticated = false;
            }
        },
        startLogin() {
            const url = new URL(window.location.href);
            const fromQuery = url.searchParams.get('next');
            const next = (fromQuery && fromQuery.startsWith('/') && !fromQuery.startsWith('//') && !fromQuery.includes('://'))
                ? fromQuery
                : window.location.pathname + window.location.search;
            window.location.href = `/login?next=${encodeURIComponent(next)}`;
        },
        startLogout() {
            window.location.href = '/logout';
        }
    },
    mounted() {
        this.loadAuthState();
    }
})
</script>

<style lang="less" scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';

.nav {
  background-color: @background-color-interactive-subtle;
  overflow: hidden;
  font-family: @font-family-monospace;

  .right-icon-img {
    width: @size-150;
    height: @size-150;
  }

  .auth-button, .user-name {
    float: right;
    background: none;
    border: none;
    padding: @spacing-100 @spacing-75;
    font-size: @font-size-large;
    cursor: pointer;
    font-family: @font-family-monospace;
  }

  .auth-button {
    background: @background-color-base;
    color: @color-progressive;;
  }

  .auth-button:hover {
    color: @color-progressive--hover;
  }

    a:not(.user-name):not(.auth-button) {
        float: left;
    }

    a:not(.less-link-padding) {
        color: @color-base;
        text-align: center;
        padding: @spacing-100 @spacing-75;
        text-decoration: none;
        font-size: @font-size-large;
    }

    .less-link-padding{
        float: left;
        color: @color-base;
        text-align: center;
        padding: @spacing-75 @spacing-75;
        text-decoration: none;
        font-size: @font-size-large;
    }

    .cdx-icon {
        color: @color-progressive;
    }

    a:hover {
        color: @color-base--hover;
    }

    a.right {
        float: right;
    }

    a.active {
        background-color: @background-color-progressive-subtle;
        color: @color-progressive;
        text-decoration: none;
    }

}

</style>
