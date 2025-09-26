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
    <div v-if="showResults && isCached" class="maho-text-wrapper"><i>This result is cached from a previous run conducted <template v-if="cachedTimeExists"><abbr :title="cachedTime.toUTCString()">{{ formatRelativeTime(cachedTime) }}</abbr></template><template v-else>within the last 24 hours</template>, to get a fresh run, <a :href="`/analyze/${ $route.params.articleName }?nocache=yes`">use this link</a>.</i></div>
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
                <div v-for="data in actualData" :key="data.uid">
                    <citation-card v-bind:data="data"></citation-card>
                </div>
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
        const totalCount = ref( 0 );
        const isCached = ref( false );
        const cachedTimeExists = ref( false );
        const cachedTime = ref( new Date() );
        const currentlySelectedTab = ref( 'all' );
        let selectedTabName = 'all';
        const route = useRoute();
        let buttons = ref<Button[]>([
            {
                originalLabel: 'All',
                label: 'All',
                number: 0,
                value: 'all'
            },
            {
                originalLabel: 'No issues',
                label: 'No issues',
                number: 0,
                value: 'ok'
            },
            {
                originalLabel: 'Redirects',
                label: 'Redirects',
                number: 0,
                value: 'redirect'
            },
            {
                originalLabel: 'Potentially spammy links',
                label: 'Potentially spammy links',
                number: 0,
                value: 'spammy'
            },
            {
                originalLabel: 'Links that could be down',
                label: 'Links that could be down',
                number: 0,
                value: 'down'
            },
            {
                originalLabel: 'Links that could be dead',
                label: 'Links that could be dead',
                number: 0,
                value: 'dead'
            },
            {
                originalLabel: 'Already has a archive.org link',
                label: 'Already has a archive.org link',
                number: 0,
                value: 'archive'
            },
            {
                originalLabel: 'Does not have a archive.org link',
                label: 'Does not have a archive.org link',
                number: 0,
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
            isCached.value = json['cached'];
            totalCitationCount = json['count'];
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
            updateButtons(fetchedData);
        }

        initData().catch( () => {
            showResults.value = true;
            erroredOut.value = true;
        } );

        function updateButtons(fetchedData: any[]) {
            const counts: Record<string, number> = {
                all: fetchedData.length,
                ok: fetchedData.filter((e) => e['url_info']['desc'] === "ok").length,
                redirect: fetchedData.filter((e) => e['url_info']['desc'] === "redirect").length,
                spammy: fetchedData.filter((e) => e['url_info']['desc'] === "spammy").length,
                down: fetchedData.filter((e) => e['url_info']['desc'] === "down").length,
                dead: fetchedData.filter((e) => e['url_info']['desc'] === "dead").length,
                archive: fetchedData.filter((e) => e.archive_url).length,
                notarchive: fetchedData.filter((e) => !e.archive_url).length,
            }

            buttons.value = buttons.value
                .map((btn: Button) => {
                const num = counts[btn.value] ?? 0
                return {
                    ...btn,
                    number: num,
                    originalLabel: btn.originalLabel,
                    label: num > 0 ? `${btn.originalLabel} (${num})` : btn.label,
                    disabled: num === 0 && btn.value !== 'all',
                }
                })
        }


        function onClickButtonGroup( value: string ) {
            selectedTabName = value;
            currentlySelectedTab.value = value;
            fetchedData = fetchedData.sort( ( a: any, b:any ) => ( b['crawl_time'] - a['crawl_time'] ) );
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
            formatRelativeTime,
            notSuccess,
            isCached,
            cachedTime,
            cachedTimeExists,
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
