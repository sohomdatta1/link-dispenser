<template>
  <div>
    <cdx-card
      v-if="$props.data"
      :icon="iconForDesc($props.data['url_info']['desc'])"
      :class="`card-type-${$props.data['url_info']['desc']}`"
    >
      <template #title>
        {{ $props.data['title'] }}

        <div class="chip-row" v-if="$props.data['url_info']['desc'] !== 'ok' || ($props.data['hallucinated'] && considerLLM) || (!$props.data['citoid'] && considerLLM) || ($props.data['hallucinated_doi'] && considerLLM) || ($props.data['title_similarity'] < 0.7 && considerLLM)">
          <b>Issue(s):</b>
          <cdx-info-chip v-if="$props.data['url_info']['desc'] !== 'ok' && $props.data['url_info']['desc'] !== 'redirect'">
            URL might be {{ $props.data['url_info']['desc'] }}
          </cdx-info-chip>
          <cdx-info-chip v-if="$props.data['url_info']['desc'] === 'redirect'">
            URL is a {{ $props.data['url_info']['desc'] }}
          </cdx-info-chip>
          <cdx-info-chip v-if="$props.data['hallucinated'] && considerLLM">
            Could be LLM generated
          </cdx-info-chip>
          <cdx-info-chip v-if="$props.data['gpt']">
            Has GPT utm tag in URL
          </cdx-info-chip>
          <cdx-info-chip v-if="$props.data['citoid'] && considerLLM">
            Citoid data does not exist
          </cdx-info-chip>
          <cdx-info-chip v-else-if="$props.data['title_similarity'] < 0.7 && considerLLM">
            Citoid title is very dissimilar
          </cdx-info-chip>
          <cdx-info-chip v-else-if="$props.data['hallucinated_doi'] && considerLLM">
            DOI does not exist
          </cdx-info-chip>
          <cdx-info-chip v-if="$props.data['valid_isbn'] === false">
            Invalid ISBN checksum
          </cdx-info-chip>
        </div>
      </template>

      <template #description>
        <cdx-icon :icon="cdxIconLink" class="link-icon" />
        <a :href="$props.data['url_info']['url']" target="_blank" class="link-general">
          {{ $props.data['url_info']['url'] }}
        </a>
        <cdx-info-chip status="notice" v-if="$props.data['url_info']['status'] < 400 &&$props.data['url_info']['status'] !== 1337">
          HTTP status code: {{ $props.data['url_info']['status'] }}
        </cdx-info-chip>
        <cdx-info-chip status="warning" v-if="$props.data['url_info']['status'] >= 400 &&$props.data['url_info']['status'] !== 1337">
          HTTP status code: {{ $props.data['url_info']['status'] }}
        </cdx-info-chip>
        <cdx-info-chip status="warning" v-if="$props.data['url_info']['timeout']">
          Request timed out
        </cdx-info-chip>
        <cdx-info-chip status="warning" v-if="$props.data['url_info']['blocked']">
          Requests blocked by site owner
        </cdx-info-chip>
        <TemplateURLStatus
          v-if="$props.data['template_url_status'] && $props.data['url_info']['desc'] && !considerLLM"
          :templateUrlStatus="$props.data['template_url_status']"
          :desc="$props.data['url_info']['desc']"
        />

        <div>
            <span v-for="url in $props.data['url_info']['history']" :key="url['url']">
              <cdx-icon :icon="cdxIconArrowNext" />
              <a :href="url['url']" target="_blank" class="link-general">{{ url['url'] }}</a>

              <br />
            </span>
        </div>

        <div class="chip-row">
          <div v-if="$props.data['archive_url'] && !considerLLM">
            <b>Archived:</b> <a :href="$props.data['archive_url']" target="_blank" class="link-general">{{ $props.data['archive_url'] }}</a>
          </div>
          <div v-if="$props.data['archive_date'] && !considerLLM">
            <b>Archive date:</b> <date-display :date="$props.data['archive_date']" />
          </div>

          <div v-if="$props.data['publication_date']">
            <b>Published:</b> <date-display :date="$props.data['publication_date']" />
          </div>
          <div v-else>
            <b>Published:</b> <span class="warn"><cdx-icon :icon="cdxIconAlert"/> No publication date found</span>
          </div>
          <div v-if="$props.data['access_date']">
            <b>Retrieved:</b> <date-display :date="$props.data['access_date']" />
          </div>
          <div v-else-if="!$props.data['doi']  && !$props.data['isbn']">
            <b>Retrieved:</b> <span class="warn"><cdx-icon :icon="cdxIconAlert"/> No retrieval date found</span>
          </div>
          <div v-if="$props.data['valid_isbn'] === false">
            <b>ISBN:</b> {{ $props.data['isbn'] }} <span class="warn"><cdx-icon :icon="cdxIconAlert"/> Invalid ISBN checksum</span>
          </div>
          <div v-else-if="$props.data['isbn'] && !considerLLM">
            <b>ISBN:</b> {{ $props.data['isbn'] }} <cdx-info-chip status="success" v-if="$props.data['isbn_in_openlibrary'] === true">ISBN exists in OpenLibrary</cdx-info-chip>
          </div>
          <div v-if="$props.data['doi'] && !considerLLM">
            <b>DOI:</b> <a :href="`${$props.data['doi']}`" target="_blank" class="link-general">{{ $props.data['doi'].replace('https://doi.org/', '') }}</a>
            <span v-if="$props.data['doi_info']['doi_valid'] === false || $props.data['doi_does_not_exist'] === true">
                <cdx-info-chip status="warning" >
                  DOI does not exist in CrossRef
                </cdx-info-chip>
                <cdx-info-chip status="success" >
                  DOI resolves through dx.doi.org
                </cdx-info-chip>
            </span>
           
            <cdx-info-chip status="success" v-else-if="$props.data['doi_does_not_exist'] === false">
              DOI exists in CrossRef
            </cdx-info-chip>
            <cdx-info-chip status="error" v-if="$props.data['doi_info']['doi_valid'] === false">
              DOI could not be validated
            </cdx-info-chip>
          </div>
          <citoid-dump v-bind:data="$props.data" v-if="considerLLM" />
          <details>
            <summary>Input citation data</summary>
            <pre class="abstract"> {{ $props.data['input'] }}</pre>
        </details>
        </div>
      </template>
    </cdx-card>
  </div>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { CdxCard, CdxIcon, CdxInfoChip, CdxMessage } from '@wikimedia/codex';
import { cdxIconLink, cdxIconSuccess, cdxIconAlert, cdxIconError, cdxIconArrowNext, cdxIconCalendar } from '@wikimedia/codex-icons';
import CitoidDump from './CitoidDump.vue';
import TemplateURLStatus from './URLStatus.vue';
import DateDisplay from './DateDisplay.vue';

export default defineComponent({
    components: { CdxCard, CdxIcon, CdxInfoChip, CitoidDump, CdxMessage, TemplateURLStatus, DateDisplay },
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
.card-type-ok > .cdx-icon {
    color: @color-icon-success;
}

.warn {
    color: @color-icon-warning;
    > .cdx-icon {
      color: @color-icon-warning;
    }
}

.card-type-down > .cdx-icon {
    color: @color-icon-warning;
}

.card-type-dead > .cdx-icon {
    color: @color-destructive;
}

.card-type-spammy > .cdx-icon {
    color: @color-icon-warning;
}

.card-type-redirect > .cdx-icon {
    color: @color-progressive;
}

.link-icon {
    margin-right: @spacing-25;
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

.abstract {
    margin: 0;
    white-space: normal;
}
</style>