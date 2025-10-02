<template>
    <div class="wrapper">
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
    <div v-if="showResults && isCached" class="maho-text-wrapper"><i>This result is cached from a previous run conducted <template v-if="cachedTimeExists"><abbr :title="cachedTime.toUTCString()">{{ formatRelativeTime(cachedTime) }}</abbr></template><template v-else>within the last 24 hours</template>, to get a fresh run, <a :href="`/llmanalyze/${ $route.params.articleName }?nocache=yes`">use this link</a>.</i></div>
    <div>
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
                    <cdx-message type="warning" inline>No URLs in the article that meet this criteria.</cdx-message>
                </div>
            </div>
            <br>
            <template v-for="data in actualData" :key="data.uid">
                <citation-card v-bind:data="data" :considerLLM="true"></citation-card>
            </template>
        </div>
    </template>
    </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref, type Ref } from 'vue'
import { CdxMessage, CdxProgressBar, CdxToggleButtonGroup } from '@wikimedia/codex';
import { useRoute } from 'vue-router';
import CitationCard from '../components/CitationCard.vue'

type Button = {
    originalLabel: string;
    label: string;
    number: number;
    value: string;
    disabled?: boolean;
};

export default defineComponent({
    name: 'AnalyzedResult',
    components: { CdxProgressBar, CitationCard, CdxToggleButtonGroup, CdxMessage },
    setup() {
        const showResults = ref( false );
        const notSuccess = ref( false );
        let totalCitationCount = 0;
        let totalCitationCountRef = ref( 0 );
        let fetchedData: any[] = [];
        const actualData: Ref<any[]> = ref( [] );
        const erroredOut = ref( false );
        const isCached = ref( false );
        const cachedTimeExists = ref( false );
        const cachedTime = ref( new Date() );
        const totalCount = ref( 0 );
        const badRequestCount = ref( 0 );
        const currentlySelectedTab = ref( 'hallucinated' );
        let selectedTabName = 'hallucinated';
        const route = useRoute();
        let buttons = ref<Button[]>([
            {
                originalLabel: 'All',
                label: 'All',
                number: 0,
                value: 'all'
            },
            {
                originalLabel: 'Potentially LLM hallucinated',
                label: 'Potentially LLM hallucinated',
                number: 0,
                value: 'hallucinated'
            },
            {
                originalLabel: 'Unsure if LLM hallucinated',
                label: 'Unsure if LLM hallucinated',
                number: 0,
                value: 'unsure'
            },
            {
                originalLabel: 'Potentially not hallucinated',
                label: 'Potentially not hallucinated',
                number: 0,
                value: 'nothallucinated'
            }
        ]);
        const pagename = route.params.articleName;
        const nocache = new URL( location.href ).searchParams.get( 'nocache' );
        const recache = new URL( location.href ).searchParams.get( 'recache' );
        const forcecache = new URL( location.href ).searchParams.get( 'forcecache' );

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
            isCached.value = json['cached'];
            if ( json['computed_on'] ) {
                cachedTime.value = new Date( json['computed_on'] );
                cachedTimeExists.value = true;
            }
            totalCitationCountRef.value = totalCitationCount;
            await fetchData( runid );
        }

        setTimeout( () => {
            if ( fetchData.length === 0 ) {
                erroredOut.value = true;
                notSuccess.value = true;
            }
        }, 10 * 60 * 1000 );

        async function fetchData( runid: string ) {
            const resp = await fetch( `/api/fetch_analysis/${runid}` );
            const json = await resp.json();
            if ( totalCitationCount > json.length ) {
                console.log( totalCitationCount, json.length )
                setTimeout( () => { 
                    fetchData( runid ).catch( () => {
                        badRequestCount.value += 1;
                        if ( badRequestCount.value >= 10 ) {
                            showResults.value = true;
                            erroredOut.value = true;
                            notSuccess.value = true;
                        }
                    } );
                }, 2 * 1000 );
            } else {
                showResults.value = true;
            }
                        document.title = `Results for ${ pagename }`;
            if ( isCached.value ) {
                document.title = `(Cached) Results for ${ pagename }`;
                if ( totalCitationCount  !== json.length ) {
                    // This is a cached result, but the count is different, so we need to hard refresh
                    // and purge the cache for a new run.
                    window.location.href = `/analyze/${ pagename }?forcecache=yes`;
                }
            }
            fetchedData = json;
            totalCount.value = json.length;
            onClickButtonGroup( selectedTabName );
            updateButtons(fetchedData);
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

            if ( value === 'hallucinated' ) {
                actualData.value = fetchedData.filter( ( elem: any ) => elem['hallucinated'] && !elem['hallucinated_unsure'] )
                return;
            }

            if ( value === 'unsure' ) {
                actualData.value = fetchedData.filter( ( elem: any ) => elem['hallucinated_unsure'] )
                return;
            }

            if ( value === 'nothallucinated' ) {
                actualData.value = fetchedData.filter( ( elem: any ) => !elem['hallucinated'] )
                return;
            }

            actualData.value = fetchedData.filter( ( elem: any ) => elem['url_info']['desc'] === value )
        }

        function updateButtons(fetchedData: any[]) {
            const counts = {
                all: fetchedData.length,
                hallucinated: fetchedData.filter(
                (e) => e.hallucinated && !e.hallucinated_unsure
                ).length,
                unsure: fetchedData.filter((e) => e.hallucinated_unsure).length,
                nothallucinated: fetchedData.filter((e) => !e.hallucinated).length,
            }

            buttons.value = buttons.value
                .map((btn: Button) => {
                const num = counts[btn.value as keyof typeof counts] ?? 0
                return {
                    ...btn,
                    originalLabel: btn.originalLabel as string,
                    number: num,
                    label: num > 0 ? `${btn.originalLabel} (${num})` : btn.label,
                }
                })
        }

        function formatRelativeTime(date: Date) {
            const rtf = new Intl.RelativeTimeFormat("en", { numeric: "auto" })
            const now = new Date()
            const diffSeconds = Math.floor((date.getTime() - now.getTime()) / 1000)

            const ranges = {
                year: 60 * 60 * 24 * 365,
                month: 60 * 60 * 24 * 30,
                day: 60 * 60 * 24,
                hour: 60 * 60,
                minute: 60,
                second: 1,
            }

            for (const [unit, secondsInUnit] of Object.entries(ranges)) {
                if (Math.abs(diffSeconds) >= secondsInUnit || unit === "second") {
                return rtf.format(Math.round(diffSeconds / secondsInUnit), unit as Intl.RelativeTimeFormatUnit)
                }
            }
        }

        return {
            showResults,
            fetchedData,
            actualData,
            buttons,
            notSuccess,
            isCached,
            cachedTime,
            cachedTimeExists,
            formatRelativeTime,
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
