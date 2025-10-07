<template>
    <previous-analysis-view :isLLMAnalysis="false" />
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import PreviousAnalysisView from './PreviousAnalysisView.vue'

export default defineComponent({
    name: 'AnalysisView',
    components: { PreviousAnalysisView }
})
</script>
