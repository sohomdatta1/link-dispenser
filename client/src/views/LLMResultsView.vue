<template>
    <base-results-view :isLLMAnalysis="true" analysisType="llmanalyze" />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import BaseResultsView from './BaseResultsView.vue'

export default defineComponent({
    name: 'LLMResultsView',
    components: { BaseResultsView }
})
</script>
