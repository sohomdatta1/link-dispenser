<template>
    <div class="citoid-data">
        <cdx-message v-if="!$props.data['url_info']['citoid'].length || $props.data['url_info']['citoid'].length == 0" type="warning" inline>No citoid data found</cdx-message>
        <div v-if="$props.data['url_info']['citoid'].length && $props.data['url_info']['citoid'].length != 0">
            <div v-if="$props.data['url_info']['citoid'][0]['title']">Citoid title: {{ $props.data['url_info']['citoid'][0]['title'] }}</div>
            <div v-if=" $props.data['url_info']['citoid'][0]['author']">Citoid identified authors: 
            <span v-for="(author, idx) in $props.data['url_info']['citoid'][0]['author']" :key="idx">
                <span v-if="Array.isArray(author)">
                    <span v-for="name in author" :key="name">{{ name }}&nbsp;</span>
                </span>
                <template v-else>{{ author }}&nbsp;</template>
                <span v-if="idx !== $props.data['url_info']['citoid'][0]['author'].length - 1">, </span>
            </span>
            </div>
            <div v-if="$props.data['url_info']['citoid'][0] && $props.data['url_info']['citoid'][0]['websiteTitle']">Citoid website: {{ $props.data['url_info']['citoid'][0]['websiteTitle'] }}</div>
            <!-- <div v-if="$props.data['url_info']['citoid'] && $props.data['url_info']['citoid'] && $props.data['url_info']['citoid'][0]['abstractNote']">
                Abstract:
                <pre class="abstract">
                {{ $props.data['url_info']['citoid'][0]['abstractNote'] }}
                </pre>
            </div> -->
        </div>
        <cdx-accordion class="citation-data">
            <template #title>Input citation data</template>
            <pre class="abstract"> {{ $props.data['input'] }} </pre>
        </cdx-accordion>
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
.citation-data, .citoid-data {
    margin-top: @spacing-50;
}
</style>