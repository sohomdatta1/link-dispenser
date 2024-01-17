<template>
    <cdx-card v-if="$props.data && $props.data['url_infos'][ 'desc' ] === 'ok'" :icon="cdxIconSuccess" :class="`card-type-${$props.data['url_infos'][ 'desc' ]}`">
        <template #title>
			{{ $props.data && $props.data['title'] }} 
            <cdx-info-chip v-if="$props.data['url_infos'][ 'desc' ] !== 'ok'">
                Detected issue: URL might be {{ $props.data['url_infos'][ 'desc' ]  }}
            </cdx-info-chip>&nbsp;
            <cdx-info-chip>
                Retrieved on: {{ $props.data['access-date' ] }}
            </cdx-info-chip>&nbsp;
            <cdx-info-chip v-if="$props.data['archive_url']">
                <a :href="$props.data['archive_url']" target="_blank" class="link-general-chip">Already has archive.org link</a>
            </cdx-info-chip>

		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> <a :href="$props.data['url_infos']['url']" target="_blank" class="link-general">{{ $props.data['url_infos']['url'] }}</a>
            <br>
            <cdx-info-chip status="notice">
                Status code: {{ $props.data['url_infos'][ 'status' ] }}
            </cdx-info-chip>
		</template>
    </cdx-card>
    <cdx-card v-if="$props.data && ( $props.data['url_infos'][ 'desc' ] === 'spammy' || $props.data['url_infos'][ 'desc' ] === 'redirect')" :icon="cdxIconAlert" :class="`card-type-${$props.data['url_infos'][ 'desc' ]}`">
        <template #title>
			{{ $props.data && $props.data['title'] }}
            <cdx-info-chip v-if="$props.data['url_infos'][ 'desc' ] !== 'ok'">
                Detected issue: URL might be {{ $props.data['url_infos'][ 'desc' ] }}
            </cdx-info-chip>&nbsp;
            <cdx-info-chip>
                Retrieved on: {{ $props.data['access-date' ] }}
            </cdx-info-chip>&nbsp;
            <cdx-info-chip v-if="$props.data['archive_url']">
                <a :href="$props.data['archive_url']" target="_blank" class="link-general-chip">Already has archive.org link</a>
            </cdx-info-chip>
            <cdx-info-chip v-if="!$props.data['archive_url'] && $props.data['url_infos']['archives']['status'] === 1">
                <a :href="$props.data['url_infos']['archives']['archive_url']" target="_blank" class="link-general-chip">Archive.org archived copy available</a>
            </cdx-info-chip>
		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> <a :href="$props.data['url_infos']['url']" target="_blank" class="link-general">{{ $props.data['url_infos']['url'] }}</a>
            <br>
            <template v-for="url in $props.data['url_infos']['history']" :key="url['url']">
                <cdx-icon :icon="cdxIconArrowNext" /> <a :href="url['url']" target="_blank" class="link-general">{{ url['url'] }}</a><br>
            </template>
            <cdx-info-chip status="notice">
                Status code: {{ $props.data['url_infos'][ 'status' ] }}
            </cdx-info-chip>

		</template>
    </cdx-card>
    <cdx-card v-if="$props.data && ($props.data['url_infos'][ 'desc' ] === 'down' || $props.data['url_infos'][ 'desc' ] === 'dead')" :icon="cdxIconError" :class="`card-type-${$props.data['url_infos'][ 'desc' ]}`">
        <template #title>
			{{ $props.data && $props.data['title'] }}
            <cdx-info-chip v-if="$props.data['url_infos'][ 'desc' ] !== 'ok'">
                Detected issue: URL might be {{ $props.data['url_infos'][ 'desc' ]  }}
            </cdx-info-chip>&nbsp;
            <cdx-info-chip>
                Retrieved on: {{ $props.data['access-date' ] }}
            </cdx-info-chip>&nbsp;
            <cdx-info-chip v-if="$props.data['archive_url']">
                <a :href="$props.data['archive_url']" target="_blank" class="link-general-chip">
                    Already has archive.org link
                </a>
            </cdx-info-chip>
            <cdx-info-chip v-if="!$props.data['archive_url'] && $props.data['url_infos']['archives']['status'] === 1">
                <a :href="$props.data['url_infos']['archives']['archive_url']" target="_blank" class="link-general-chip"> Archive.org archived copy available </a>
            </cdx-info-chip>
		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> <a :href="$props.data['url_infos']['url']" target="_blank" class="link-general">{{ $props.data['url_infos']['url'] }}</a>
            <br>
            <cdx-info-chip status="notice" v-if="$props.data['url_infos']['status'] !== 1337">
                Status code: {{ $props.data['url_infos'][ 'status' ] }}
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
</style>