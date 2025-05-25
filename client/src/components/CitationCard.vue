<template>
  <div>
    <cdx-card
      v-if="$props.data"
      :icon="iconForDesc($props.data['url_info']['desc'])"
      :class="`card-type-${$props.data['url_info']['desc']}`"
    >
      <template #title>
        {{ $props.data['title'] }}
        <cdx-info-chip v-if="$props.data['url_info']['desc'] !== 'ok'">
          Detected issue: URL might be {{ $props.data['url_info']['desc'] }}
        </cdx-info-chip>
        <cdx-info-chip v-if="$props.data['publication_date']">
          Published on: {{ $props.data['publication_date'] }}
        </cdx-info-chip>
        <cdx-info-chip v-if="$props.data['access-date']">
          Retrieved on: {{ $props.data['access-date'] }}
        </cdx-info-chip>
        <cdx-info-chip v-if="$props.data['hallucinated'] && considerLLM">
          Could be LLM generated
        </cdx-info-chip>
        <cdx-info-chip v-if="$props.data['citoid'] && considerLLM">
          Citoid data does not exists
        </cdx-info-chip>
        <cdx-info-chip v-else-if="$props.data['title_similarity'] < 0.7 && considerLLM">
          Citoid title is very dissimilar from actual title
        </cdx-info-chip>
         <cdx-info-chip v-else-if="$props.data['hallucinated_doi']">
          DOI provided does not exist
        </cdx-info-chip>
        <cdx-info-chip v-if="$props.data['archive_url'] && !considerLLM">
          <a :href="$props.data['archive_url']" target="_blank" class="link-general-chip">
            Already has archive.org link
          </a>
        </cdx-info-chip>
        <cdx-info-chip
          v-if="!$props.data['archive_url'] && $props.data['url_info']['archives']?.status === 1"
        >
          <a
            :href="$props.data['url_info']['archives']['archive_url'] && !considerLLM"
            target="_blank"
            class="link-general-chip"
          >
            Archive.org archived copy available
          </a>
        </cdx-info-chip>
      </template>

      <template #description>
        <cdx-icon :icon="cdxIconLink" class="link-icon" />
        <a :href="$props.data['url_info']['url']" target="_blank" class="link-general">
          {{ $props.data['url_info']['url'] }}
        </a>
        <br />

        <template v-if="['spammy', 'redirect'].includes($props.data['url_info']['desc'])">
          <span v-for="url in $props.data['url_info']['history']" :key="url['url']">
            <cdx-icon :icon="cdxIconArrowNext" />
            <a :href="url['url']" target="_blank" class="link-general">{{ url['url'] }}</a>
            <br />
          </span>
        </template>

        <cdx-info-chip status="notice" v-if="$props.data['url_info']['status'] !== 1337">
          Status code: {{ $props.data['url_info']['status'] }}
        </cdx-info-chip>
        <cdx-info-chip status="notice" v-if="$props.data['url_info']['timeout']">
          Request timed out
        </cdx-info-chip>

        <template v-if="['down', 'dead'].includes($props.data['url_info']['desc'])">
          <cdx-info-chip status="notice" v-if="$props.data['url_info']['blocked']">
            Status might be incorrect
          </cdx-info-chip>
          <cdx-info-chip status="notice" v-if="$props.data['url_info']['blocked']">
            Requests are blocked by website owner
          </cdx-info-chip>
        </template>

        <citoid-dump v-bind:data="$props.data" />
      </template>
    </cdx-card>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { CdxCard, CdxIcon, CdxInfoChip } from '@wikimedia/codex';
import { cdxIconLink, cdxIconSuccess, cdxIconAlert, cdxIconError, cdxIconArrowNext, cdxIconCalendar } from '@wikimedia/codex-icons';
import CitoidDump from './CitoidDump.vue';

export default defineComponent({
    components: { CdxCard, CdxIcon, CdxInfoChip, CitoidDump },
    props: {
        "data": Object,
        considerLLM: Boolean,
    },
    data: () => ( {
		cdxIconLink,
        cdxIconSuccess,
        cdxIconAlert,
        cdxIconError,
        cdxIconArrowNext,
        cdxIconCalendar
	} ),
    methods: {
        iconForDesc(desc: string) {
            if (desc === 'ok') return this.cdxIconSuccess;
            if (desc === 'spammy' || desc === 'redirect') return this.cdxIconAlert;
            if (desc === 'down' || desc === 'dead' || desc === 'hallucinated') return this.cdxIconError;
            return this.cdxIconLink; // fallback icon if needed
        },
    },
    setup( props ) {
        if ( !props.data ) {
            return;
        }
    },
})
</script>

<style lang="less">
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';
.card-type-ok .cdx-icon {
    color: @color-icon-success;
}

.card-type-down .cdx-icon {
    color: @color-icon-warning;
}

.card-type-dead .cdx-icon {
    color: @color-destructive;
}

.card-type-spammy .cdx-icon {
    color: @color-icon-warning;
}

.link-icon {
    margin-right: @spacing-25;
}

.card-type-redirect .cdx-icon {
    color: @color-progressive;
}

.link-general {
    color: inherit;
    text-decoration: none;
}

.link-general-chip {
    color: inherit;
}
.cdx-info-chip {
    margin-left: 5px;
}
</style>