<template>
  <div class="url-status-check">
    <b>URL status is correct:</b>
    <cdx-info-chip :status=" isCorrect ? 'success' : 'error' ">
      {{ isCorrect ? 'Yes' : 'No' }}
    </cdx-info-chip> <div class="explanation">(Linkcheck says URL is "{{ $props.desc }}" and the template says "{{ $props.templateUrlStatus }}")</div>
  </div>
</template>

<script lang="ts">
import { CdxInfoChip } from '@wikimedia/codex'
import { defineComponent, computed } from 'vue'

export default defineComponent({
  name: 'UrlStatusCheck',
  components: { CdxInfoChip },
  props: {
    templateUrlStatus: {
      type: String,
      required: true
    },
    desc: {
      type: String,
      required: true
    }
  },
  setup(props) {
    const isCorrect = computed(() => {
      const { templateUrlStatus, desc } = props

      // Case 1: Both agree it’s dead/spammy
      if (
        templateUrlStatus === 'dead' &&
        (desc === 'dead' || desc === 'down' || desc === 'spammy')
      ) {
        return true
      }

      // Case 2: Template says dead, linkcheck disagrees
      if (
        templateUrlStatus === 'dead' &&
        desc !== 'dead' &&
        desc !== 'down' &&
        desc !== 'spammy'
      ) {
        return false
      }

      // Case 3: Template says live, linkcheck says not ok
      if (templateUrlStatus === 'live' && desc !== 'ok') {
        return false
      }

      // Case 4: Template says live, linkcheck says ok
      if (templateUrlStatus === 'live' && desc === 'ok') {
        return true
      }

      // Fallback (anything else is incorrect)
      return false
    })

    return { isCorrect }
  }
})
</script>

<style lang="less" scoped>
.url-status-check {
  display: flex;
  align-content: center;
}
.explanation {
  display: inline-block;
  margin-left: 10px;
  font-style: italic;
}
</style>
