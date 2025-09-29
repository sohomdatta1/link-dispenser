<template>
    <div class="citoid-data">
        <cdx-message v-if="!$props.data['url_info']['citoid'].length || $props.data['url_info']['citoid'].length == 0" type="warning" inline>No citoid data found</cdx-message>
        <div v-if="$props.data['url_info']['citoid'].length && $props.data['url_info']['citoid'].length != 0">
            <div v-if="$props.data['url_info']['citoid'][0]['title']"><b>Citoid title</b>: {{ $props.data['url_info']['citoid'][0]['title'] }}</div>
            <div v-if=" $props.data['url_info']['citoid'][0]['author']"><b>Citoid identified authors</b>: 
            <span v-for="(author, idx) in $props.data['url_info']['citoid'][0]['author']" :key="idx">
                <span v-if="Array.isArray(author)">
                    <span v-for="name in author.slice(0,-1)" :key="name">{{ name }}&nbsp;</span>
                    <span v-for="name in author.slice(-1)" :key="name">{{ name }}</span>
                </span>
                <template v-else>{{ author }}</template>
                <span v-if="idx !== $props.data['url_info']['citoid'][0]['author'].length - 1">, </span>
            </span>
            </div>
            <div v-if="$props.data['url_info']['citoid'][0] && $props.data['url_info']['citoid'][0]['websiteTitle']"><b>Citoid website</b>: {{ $props.data['url_info']['citoid'][0]['websiteTitle'] }}</div>
            <!-- <div v-if="$props.data['url_info']['citoid'] && $props.data['url_info']['citoid'] && $props.data['url_info']['citoid'][0]['abstractNote']">
                Abstract:
                <pre class="abstract">
                {{ $props.data['url_info']['citoid'][0]['abstractNote'] }}
                </pre>
            </div> -->
        </div>
        <details v-if="$props.data['url_info']['citoid'].length && $props.data['url_info']['citoid'].length != 0">
            <summary>Full Citoid data ({{ Object.keys($props.data['url_info']['citoid'][0]).length }} fields)</summary>
            <pre class="abstract-code"><code> {{ JSON.stringify($props.data['url_info']['citoid'][0], null, 2) }} </code></pre>
        </details>
    </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { CdxAccordion, CdxMessage } from '@wikimedia/codex';

export default defineComponent({
    components: { CdxAccordion, CdxMessage },
    props: {
        "data": {
            type: Object,
            required: true
        }
    },
    setup( props ) {
        if ( !props.data ) {
            return;
        }
    },
})
</script>

<style lang="less" scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';
.abstract {
    margin: 0;
    white-space: normal;
}
.abstract-code {
    margin: 0;
}
</style>