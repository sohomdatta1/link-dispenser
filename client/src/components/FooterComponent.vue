<template>
    <div class="footer"><small>Powered by <a href="https://wikimediafoundation.org/" target="_blank">Wikimedia Foundation</a>'s <a href="https://toolforge.org/" target="_blank">Toolforge</a> | Built with <a href="https://vuejs.org/" target="_blank">Vue.js</a> and <a href="https://www.mediawiki.org/wiki/REST_API" target="_blank">MediaWiki REST API</a> (and Citoid, the doi.org API, the CrossRef API and others)</small> </div>
</template>

<style lang="less" scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';
@import ( reference ) '@wikimedia/codex/mixins/link.less';
.footer {
    background-color: @background-color-interactive-subtle;
    text-align: center;
    padding: @spacing-100;
    font-family: @font-family-monospace;

    a {
        .cdx-mixin-link();
    }
}
</style>