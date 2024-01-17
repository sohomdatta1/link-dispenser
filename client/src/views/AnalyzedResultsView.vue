<template>
    <cdx-progress-bar aria--label="Analyzing" v-if="!showResults" inline />
    <div v-if="!showResults" class="maho-text-wrapper">
        <div>Analyzing <a :href='`https://en.wikipedia.org/wiki/${ $route.params.articleName }`'>{{ $route.params.articleName }}</a>, this might take a while..... I'd suggest grabbing a cup of coffee, taking a walk or doing some other activity</div>
    </div>
    <div v-if="showResults && !success" class="maho-text-wrapper">
        This article does not exist.
    </div>
    <template v-if="showResults && success">
        <div class="floating-header">
            <div>
                <h1>Results for <a :href='`https://en.wikipedia.org/wiki/${ $route.params.articleName }`'>{{ $route.params.articleName }}</a></h1>
            </div>
            <cdx-toggle-button-group
            :model-value="currentlySelectedTab"
            :buttons="buttons"
            @update:modelValue="onClickButtonGroup"
        >
            </cdx-toggle-button-group>
            <br>
            <div v-if="actualData.length !== 0 && currentlySelectedTab !== 'all'">
                <div>{{ actualData.length }} out of {{ totalCount }} URLs in the article that meet this criteria.</div>
            </div>
            <div v-if="currentlySelectedTab === 'all'">
                <div>{{ totalCount }} URLs detected in the article.</div>
            </div>
            <div v-if="actualData.length === 0">
                <div>No URLs in the article that meet this criteria.</div>
            </div>
        </div>
        <br>
        <template v-for="data in actualData" :key="data.uid">
            <citation-card v-bind:data="data"></citation-card>
        </template>
    </template>
</template>
<script lang="ts">
import { defineComponent, ref, type Ref } from 'vue'
import { CdxProgressBar, CdxToggleButtonGroup } from '@wikimedia/codex';
import { useRoute } from 'vue-router';
import CitationCard from '../components/CitationCard.vue'

export default defineComponent({
    name: 'AnalyzedResult',
    components: { CdxProgressBar, CitationCard, CdxToggleButtonGroup },
    setup() {
        const showResults = ref( false );
        const success = ref( false );
        let fetchedData: any[] = [];
        const actualData: Ref<any[]> = ref( [] );
        const totalCount = ref( 0 );
        const currentlySelectedTab = ref( 'all' );
        const route = useRoute();
        let buttons = ref([
            {
                label: 'All',
                number: 0,
                value: 'all'
            },
            {
                label: 'No issues',
                number: 0,
                value: 'ok'
            },
            {
                label: 'Redirects',
                number: 0,
                value: 'redirect'
            },
            {
                label: 'Potentially sammy links',
                number: 0,
                value: 'spammy'
            },
            {
                label: 'Links that could be down',
                number: 0,
                value: 'down'
            },
            {
                label: 'Links that are dead',
                number: 0,
                value: 'dead'
            }
        ]);
        const pagename = route.params.articleName;
        fetch( `/api/analyze/${pagename}` )
            .then( response => response.json() )
            .then( ( data: any ) => {
                if ( !data['exists'] ) {
                    showResults.value = true;
                    return;
                }
                document.title = `Results for ${pagename}`
                fetchedData = data['template_info']
                actualData.value = fetchedData;
                showResults.value = true;
                success.value = true;
                totalCount.value = fetchedData.length;
                buttons.value = [
                    {
                        label: 'All',
                        number: data['template_info'].length,
                        value: 'all'
                    },
                    {
                        label: 'No issues',
                        number: data['template_info'].filter( ( elem: any ) => elem['url_infos']['desc'] === 'ok' ).length,
                        value: 'ok'
                    },
                    {
                        label: 'Redirects',
                        number: data['template_info'].filter( ( elem: any ) => elem['url_infos']['desc'] === 'redirect' ).length,
                        value: 'redirect'
                    },
                    {
                        label: 'Potentially spammy link',
                        number: data['template_info'].filter( ( elem: any ) => elem['url_infos']['desc'] === 'spammy' ).length,
                        value: 'spammy'
                    },
                    {
                        label: 'Links that could be down',
                        number: data['template_info'].filter( ( elem: any ) => elem['url_infos']['desc'] === 'down' ).length,
                        value: 'down'
                    },
                    {
                        label: 'Links that are dead',
                        number: data['template_info'].filter( ( elem: any ) => elem['url_infos']['desc'] === 'dead' ).length,
                        value: 'dead'
                    }
                ];
        } )

        function onClickButtonGroup( value: string ) {
            if ( value === 'all' ) {
                actualData.value = fetchedData;
                currentlySelectedTab.value = value;
                return;
            }

            actualData.value = fetchedData.filter( ( elem: any ) => elem['url_infos']['desc'] === value )

            currentlySelectedTab.value = value;
        }

        return {
            showResults,
            fetchedData,
            actualData,
            buttons,
            success,
            totalCount,
            onClickButtonGroup,
            currentlySelectedTab
        }
    },
})
</script>

<style lang="less">
// Note: you must import the design tokens before importing the link mixin
@import ( reference ) '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';
@import ( reference ) '@wikimedia/codex/mixins/link.less';

.maho-text-wrapper {
    display: flex;
    font-family: monospace;
    justify-content: center;
    align-items: center;
}

.cdx-docs-link {
	.cdx-mixin-link();
}
</style>
