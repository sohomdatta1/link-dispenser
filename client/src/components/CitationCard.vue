<template>
    <cdx-card v-if="$props.data && $props.data['url_infos'][ 'desc' ] === 'ok'" :icon="cdxIconSuccess" :class="`card-type-${$props.data['url_infos'][ 'desc' ]}`">
        <template #title>
			{{ $props.data && $props.data['title'] }} 
            <cdx-info-chip v-if="$props.data['url_infos'][ 'desc' ] !== 'ok'">
                Detected issue: URL might be {{ $props.data['url_infos'][ 'desc' ]  }}
            </cdx-info-chip>&nbsp;
            <cdx-info-chip>
                Retrieved on: {{ $props.data['access-date' ] }}
            </cdx-info-chip>
		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> {{ $props.data['url_infos']['url'] }}
            <br>
            <cdx-info-chip status="notice" v-if="$props.data['url_infos']['status'] !== 1337">
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
            </cdx-info-chip>
		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> {{ $props.data['url_infos']['url'] }}
            <template v-for="url in $props.data['url_infos']['history']" :key="url['url']">
                <cdx-icon :icon="cdxIconArrowNext" /> {{ url['url'] }}
            </template>
            <br>
            <cdx-info-chip status="notice" v-if="$props.data['url_infos']['status'] !== 1337">
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
            </cdx-info-chip>
		</template>

        <template #description v-if="$props.data">
            <cdx-icon :icon="cdxIconLink" /> {{ $props.data['url_infos']['url'] }}
            <br>
            <cdx-info-chip status="notice" v-if="$props.data['url_infos']['status'] !== 1337">
                Status code: {{ $props.data['url_infos'][ 'status' ] }}
            </cdx-info-chip>
		</template>
    </cdx-card>
    <br>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import { CdxCard, CdxIcon, CdxInfoChip } from '@wikimedia/codex';
import { cdxIconLink, cdxIconSuccess, cdxIconAlert, cdxIconError, cdxIconArrowNext } from '@wikimedia/codex-icons';

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
        cdxIconArrowNext
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
</style>