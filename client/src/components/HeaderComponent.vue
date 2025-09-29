<template>
    <nav class="nav">
        <router-link class="active" to="/" target="_blank">
            <cdx-icon :icon="cdxIconLink"></cdx-icon>
            link-dispenser
        </router-link>
        <a class="right" href="https://en.wikipedia.org/wiki/WP:LINKDISP" target="_blank"><small>(docs)</small></a>
        <a class="right less-link-padding" href="https://gitlab.wikimedia.org/toolforge-repos/link-dispenser" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/3/35/GitLab_icon.svg" class="right-icon-img" /></a>
        <a class="right less-link-padding" href="https://phabricator.wikimedia.org/maniphest/task/edit/form/43/?projects=Tool-link-dispenser&subscribers=Soda" target="_blank"><img src="https://upload.wikimedia.org/wikipedia/commons/1/10/Ic_bug_report_48px.svg" class="right-icon-img"></a>
    </nav>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { RouterLink } from 'vue-router'
import { CdxIcon } from '@wikimedia/codex';
import { cdxIconLink } from '@wikimedia/codex-icons';

export default defineComponent({
    data: () => ( {
        cdxIconLink
    }),
    components: {
        CdxIcon,
        RouterLink
    },
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

    a:not(.less-link-padding) {
        float: left;
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
