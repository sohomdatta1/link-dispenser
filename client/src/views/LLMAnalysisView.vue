<template>
    <previous-analysis-view :isLLMAnalysis="true" />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import PreviousAnalysisView from './PreviousAnalysisView.vue'

export default defineComponent({
    name: 'LLMAnalysisView',
    components: { PreviousAnalysisView }
})
</script>
