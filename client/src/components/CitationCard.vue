<template>
    <cdx-card v-if="$props.data && $props.data['url_info'][ 'desc' ] === 'ok'" :icon="cdxIconSuccess" :class="`card-type-${$props.data['url_info'][ 'desc' ]}`">
        <template #title>
			{{ $props.data && $props.data['title'] }} 
            <cdx-info-chip v-if="$props.data['url_info'][ 'desc' ] !== 'ok'">
                Detected issue: URL might be {{ $props.data['url_info'][ 'desc' ]  }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['publication_date' ]">
                Published on: {{ $props.data['publication_date' ] }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['access-date' ]">
                Retrieved on: {{ $props.data['access-date' ] }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['archive_url']">
                <a :href="$props.data['archive_url']" target="_blank" class="link-general-chip">Already has archive.org link</a>
            </cdx-info-chip>

		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> <a :href="$props.data['url_info']['url']" target="_blank" class="link-general">{{ $props.data['url_info']['url'] }}</a>
            <br>
            <cdx-info-chip status="notice">
                Status code: {{ $props.data['url_info'][ 'status' ] }}
            </cdx-info-chip>
		</template>
    </cdx-card>
    <cdx-card v-if="$props.data && ( $props.data['url_info'][ 'desc' ] === 'spammy' || $props.data['url_info'][ 'desc' ] === 'redirect')" :icon="cdxIconAlert" :class="`card-type-${$props.data['url_info'][ 'desc' ]}`">
        <template #title>
			{{ $props.data && $props.data['title'] }}
            <cdx-info-chip v-if="$props.data['url_info'][ 'desc' ] !== 'ok'">
                Detected issue: URL might be {{ $props.data['url_info'][ 'desc' ] }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['publication_date' ]">
                Published on: {{ $props.data['publication_date' ] }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['access-date' ]">
                Retrieved on: {{ $props.data['access-date' ] }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['archive_url']">
                <a :href="$props.data['archive_url']" target="_blank" class="link-general-chip">Already has archive.org link</a>
            </cdx-info-chip>
            <cdx-info-chip v-if="!$props.data['archive_url'] && $props.data['url_info']['archives']['status'] === 1">
                <a :href="$props.data['url_info']['archives']['archive_url']" target="_blank" class="link-general-chip">Archive.org archived copy available</a>
            </cdx-info-chip>
		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> <a :href="$props.data['url_info']['url']" target="_blank" class="link-general">{{ $props.data['url_info']['url'] }}</a>
            <br>
            <span v-for="url in $props.data['url_info']['history']" :key="url['url']">
                <cdx-icon :icon="cdxIconArrowNext" /> <a :href="url['url']" target="_blank" class="link-general">{{ url['url'] }}</a><br>
            </span>
            <cdx-info-chip status="notice">
                Status code: {{ $props.data['url_info'][ 'status' ] }}
            </cdx-info-chip>
            <cdx-info-chip status="notice" v-if="$props.data['url_info']['timeout']">
            Request timed out
            </cdx-info-chip>

		</template>
    </cdx-card>
    <cdx-card v-if="$props.data && ($props.data['url_info'][ 'desc' ] === 'down' || $props.data['url_info'][ 'desc' ] === 'dead')" :icon="cdxIconError" :class="`card-type-${$props.data['url_info'][ 'desc' ]}`">
        <template #title>
			{{ $props.data && $props.data['title'] }}
            <cdx-info-chip v-if="$props.data['url_info'][ 'desc' ] !== 'ok'">
                Detected issue: URL might be {{ $props.data['url_info'][ 'desc' ]  }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['publication_date' ]">
                Published on: {{ $props.data['publication_date' ] }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['access-date' ]">
                Retrieved on: {{ $props.data['access-date' ] }}
            </cdx-info-chip>
            <cdx-info-chip v-if="$props.data['archive_url']">
                <a :href="$props.data['archive_url']" target="_blank" class="link-general-chip">
                    Already has archive.org link
                </a>
            </cdx-info-chip>
            <cdx-info-chip v-if="!$props.data['archive_url'] && $props.data['url_info']['archives']['status'] === 1">
                <a :href="$props.data['url_info']['archives']['archive_url']" target="_blank" class="link-general-chip"> Archive.org archived copy available </a>
            </cdx-info-chip>
		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> <a :href="$props.data['url_info']['url']" target="_blank" class="link-general">{{ $props.data['url_info']['url'] }}</a>
            <br>
            <cdx-info-chip status="notice" v-if="$props.data['url_info']['status'] !== 1337">
                Status code: {{ $props.data['url_info'][ 'status' ] }}
            </cdx-info-chip>
            <cdx-info-chip status="notice" v-if="$props.data['url_info']['timeout']">
            Request timed out
            </cdx-info-chip>
            <cdx-info-chip status="notice" v-if="$props.data['url_info']['blocked']">
            Status might be incorrect
            </cdx-info-chip>
            <cdx-info-chip status="notice" v-if="$props.data['url_info']['blocked']">
            Requests are blocked by website owner
            </cdx-info-chip>
		</template>
    </cdx-card>
    <br>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
import { CdxCard, CdxIcon, CdxInfoChip } from '@wikimedia/codex';
import { cdxIconLink, cdxIconSuccess, cdxIconAlert, cdxIconError, cdxIconArrowNext, cdxIconCalendar } from '@wikimedia/codex-icons';

export default defineComponent({
    components: { CdxCard, CdxIcon, CdxInfoChip },
    props: {
        "data": Object
    },
    data: () => ( {
		cdxIconLink,
        cdxIconSuccess,
        cdxIconAlert,
        cdxIconError,
        cdxIconArrowNext,
        cdxIconCalendar
	} ),
    setup( props ) {
        if ( !props.data ) {
            return;
        }
    },
})
</script>

<style lang="less" scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';
.card-type-ok {
    color: @color-success;
}

.card-type-down {
    color: @color-warning;
}

.card-type-dead {
    color: @color-destructive;
}

.card-type-spammy {
    color: @color-warning;
}

.card-type-redirect {
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