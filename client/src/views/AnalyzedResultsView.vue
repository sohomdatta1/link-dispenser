<template>
    <cdx-progress-bar aria--label="Analyzing" v-if="!showResults" inline />
    <div v-if="!showResults" class="maho-text-wrapper">
        <div>Analyzing <a :href='`https://en.wikipedia.org/wiki/${ $route.params.articleName }`'>{{ $route.params.articleName }}</a>, this might take a while..... I'd suggest grabbing a cup of coffee, taking a walk or doing some other activity. ({{ totalCount }}/{{ totalCitationCountRef }} URLs processed)</div>
    </div>
    <div v-if="showResults && notSuccess" class="maho-text-wrapper">
        This article does not exist.
    </div>
    <div v-if="showResults && erroredOut" class="maho-text-wrapper">
        Something definitely went wrong here. Please report this URL to [[en:User talk:Sohom_Datta]] or sohom_#0 on Discord.
    </div>
    <template v-if="!notSuccess && !erroredOut">
        <div>
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
        </div>
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
        const notSuccess = ref( false );
        let totalCitationCount = 0;
        let totalCitationCountRef = ref( 0 );
        let fetchedData: any[] = [];
        const actualData: Ref<any[]> = ref( [] );
        const erroredOut = ref( false );
        const totalCount = ref( 0 );
        const currentlySelectedTab = ref( 'all' );
        let selectedTabName = 'all';
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
                label: 'Potentially spammy links',
                number: 0,
                value: 'spammy'
            },
            {
                label: 'Links that could be down',
                number: 0,
                value: 'down'
            },
            {
                label: 'Links that could be dead',
                number: 0,
                value: 'dead'
            },
            {
                label: 'Already has a archive.org link',
                value: 'archive'
            },
            {
                label: 'Does not have a archive.org link',
                value: 'notarchive'
            }
        ]);
        const pagename = route.params.articleName;
        const nocache = new URL( location.href ).searchParams.get( 'nocache' );
        const recache = new URL( location.href ).searchParams.get( 'recache' );

        async function initData() {
            const resp = await fetch( `/api/push_analysis/${ encodeURIComponent( String( pagename ) ) }?cache=${ nocache ? recache || Math.random() : 'yes' }` )
            const json = await resp.json();
            if ( !json['exists'] ) {
                showResults.value = true;
                notSuccess.value = true;
                return;
            }
            const runid = json['rid'];
            totalCitationCount = json['count'];
            totalCitationCountRef.value = totalCitationCount;
            await fetchData( runid );
        }

        setTimeout( () => {
            if ( fetchData.length === 0 ) {
                erroredOut.value = true;
                notSuccess.value = true;
            }
        }, 5 * 61 * 1000 )

        async function fetchData( runid: string ) {
            const resp = await fetch( `/api/fetch_analysis/${runid}` );
            const json = await resp.json();
            if ( totalCitationCount > json.length ) {
                console.log( totalCitationCount, json.length )
                setTimeout( () => { 
                    fetchData( runid ).catch( () => {
                        showResults.value = true;
                        erroredOut.value = true;
                    } )
                }, 2 * 1000 );
            } else {
                showResults.value = true;
            }
            document.title = `Results for ${ pagename }`
            fetchedData = json;
            totalCount.value = json.length;
            onClickButtonGroup( selectedTabName );
        }

        initData().catch( () => {
            showResults.value = true;
            erroredOut.value = true;
        } );

        function onClickButtonGroup( value: string ) {
            selectedTabName = value;
            currentlySelectedTab.value = value;
            if ( value === 'all' ) {
                actualData.value = fetchedData;
                return;
            }

            if ( value === 'archive' ) {
                actualData.value = fetchedData.filter( ( elem: any ) => elem['archive_url'] )
                return;
            }

            if ( value === 'notarchive' ) {
                actualData.value = fetchedData.filter( ( elem: any ) => !elem['archive_url'] )
                return;
            }

            actualData.value = fetchedData.filter( ( elem: any ) => elem['url_info']['desc'] === value )
        }

        return {
            showResults,
            fetchedData,
            actualData,
            buttons,
            notSuccess,
            erroredOut,
            totalCitationCountRef,
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

.wrapper {
    padding-top: 0;
}

.cdx-docs-link {
	.cdx-mixin-link();
}
</style>
