<template>
    <base-results-view :isLLMAnalysis="false" analysisType="analyze" />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import BaseResultsView from './BaseResultsView.vue'

export default defineComponent({
    name: 'AnalyzedResultsView',
    components: { BaseResultsView }
})
</script>
