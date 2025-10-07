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
    <div v-if="showResults && isCached" class="maho-text-wrapper"><i>This result is cached from a previous run conducted <template v-if="cachedTimeExists"><abbr :title="cachedTime.toUTCString()">{{ formatRelativeTime(cachedTime) }}</abbr></template><template v-else>within the last 24 hours</template>, to get a fresh run, <a :href="`${analysisType}/${ $route.params.articleName }?nocache=yes`">use this link</a>.</i></div>
    <div>
        <template v-if="!notSuccess && !erroredOut">
            <div>
                <div class="floating-header">
                    <div class="title-and-link-wrapper">
                        <h1 class="title-of-run-page">Results for <a :href='`https://en.wikipedia.org/wiki/${ $route.params.articleName }`'>{{ $route.params.articleName }}</a></h1>
                        <div v-if="!erroredOut && permanentLink" class="permanent-link-wrapper">
                            <div class="link-container">
                                <a :href="permanentLink" class="link-url cdx-docs-link" target="_blank" rel="noopener noreferrer">{{ permanentLink }}</a>
                            </div>
                            <cdx-button @click="copyToClipboard" weight="quiet"  class="copy-url-button"> <template v-if="copySuccess"><cdx-icon :icon="cdxIconCheck" /> Copied permanent URL to this run</template> <template v-else> <cdx-icon :icon="cdxIconCopy" /> Copy permanent URL to this run</template></cdx-button>
                        </div>
                        <div v-else class="permanent-link-wrapper">
                            <i>Generating permanent link...</i>
                        </div>
                    </div>
                    <div class="suggested-filters">
                        Suggested filters:
                        <cdx-toggle-button-group
                            :model-value="currentlySelectedTab"
                            :buttons="buttons"
                            @update:modelValue="onClickButtonGroup"
                            class="filter-button-group"
                        >
                            <template #default="{ button }">
                            {{ button.originalLabel }}
                            <span>
                                ({{ button.number }})
                            </span>
                        </template>
                        </cdx-toggle-button-group>
                    </div>
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
                <div v-for="data in actualData" :key="data.uid">
                    <citation-card v-bind:data="data" :considerLLM="isLLMAnalysis" class="citation-card-data"></citation-card>
                </div>
            </div>
        </template>
    </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref, type Ref } from 'vue'
import { CdxMessage, CdxProgressBar, CdxToggleButtonGroup, CdxButton, CdxIcon } from '@wikimedia/codex';
import { useRoute } from 'vue-router';
import CitationCard from '../components/CitationCard.vue'
import { cdxIconCheck, cdxIconCopy } from '@wikimedia/codex-icons';

type Button = {
    originalLabel: string;
    label: string;
    number: number;
    value: string;
    disabled?: boolean;
};

export default defineComponent({
    name: 'BaseResultsView',
    components: { CdxProgressBar, CitationCard, CdxToggleButtonGroup, CdxMessage, CdxButton, CdxIcon },
    data: () => ( {
        cdxIconCheck,
        cdxIconCopy
    } ),
    props: {
        isLLMAnalysis: {
            type: Boolean,
            default: false
        },
        analysisType: {
            type: String,
            default: 'analyze'
        }
    },
    setup(props) {
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
        const badRequestCount = ref( 0 );
        const currentlySelectedTab = ref( props.isLLMAnalysis ? 'hallucinated' : 'all' );
        let selectedTabName = props.isLLMAnalysis ? 'hallucinated' : 'all';
        const permanentLink = ref( '' );
        const copySuccess = ref( false );
        const route = useRoute();
        
        let buttons = ref<Button[]>(props.isLLMAnalysis ? [
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
        ] : [
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
                originalLabel: 'Potentially spammy',
                label: 'Potentially spammy',
                number: 0,
                value: 'spammy'
            },
            {
                originalLabel: 'Down',
                label: 'Links that could be down',
                number: 0,
                value: 'down'
            },
            {
                originalLabel: 'Dead',
                label: 'Links that could be dead',
                number: 0,
                value: 'dead'
            },
            {
                originalLabel: 'Archived',
                label: 'Archived',
                number: 0,
                value: 'archive'
            },
            {
                originalLabel: 'No archive.org link',
                label: 'Does not have a archive.org link',
                number: 0,
                value: 'notarchive'
            }
        ]);
        
        const pagename = route.params.articleName;
        const nocache = new URL( location.href ).searchParams.get( 'nocache' );
        const recache = new URL( location.href ).searchParams.get( 'recache' );
        const forcecache = new URL( location.href ).searchParams.get( 'forcecache' );

        async function initData() {
            const resp = await fetch( `/api/push_analysis/${ encodeURIComponent( String( pagename ) ) }?cache=${ nocache ? recache || Math.random() : 'yes' }${ forcecache ? '&forcecache=yes': '' }` )
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
            document.title = `(Cached) Results for ${ pagename }`;
            if ( isCached.value ) {
                document.title = `(Cached) Results for ${ pagename }`;
                if ( totalCitationCount  !== json.length ) {
                    // This is a cached result, but the count is different, so we need to hard refresh
                    // and purge the cache for a new run.
                    window.location.href = `/${props.analysisType}/${ pagename }?forcecache=yes`;
                }
            }
            fetchedData = json;
            totalCount.value = json.length;
            onClickButtonGroup( selectedTabName );
            updateButtons(fetchedData);
            
            // Generate permanent link
            const baseUrl = window.location.origin;
            const analysisType = props.isLLMAnalysis ? 'llmanalysis' : 'analysis';
            permanentLink.value = `${baseUrl}/${analysisType}/${runid}`;
        }

        initData().catch( () => {
            showResults.value = true;
            erroredOut.value = true;
        } );

        function updateButtons(fetchedData: any[]) {
            const counts = props.isLLMAnalysis ? {
                all: fetchedData.length,
                hallucinated: fetchedData.filter(
                (e) => e.hallucinated && !e.hallucinated_unsure
                ).length,
                unsure: fetchedData.filter((e) => e.hallucinated_unsure).length,
                nothallucinated: fetchedData.filter((e) => !e.hallucinated).length,
            } : {
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
                const num = counts[btn.value as keyof typeof counts] ?? 0
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

            if ( props.isLLMAnalysis ) {
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
            } else {
                if ( value === 'archive' ) {
                    actualData.value = fetchedData.filter( ( elem: any ) => elem['archive_url'] )
                    return;
                }

                if ( value === 'notarchive' ) {
                    actualData.value = fetchedData.filter( ( elem: any ) => !elem['archive_url'] )
                    return;
                }
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

        async function copyToClipboard() {
            try {
                await navigator.clipboard.writeText(permanentLink.value);
                copySuccess.value = true;
                setTimeout(() => {
                    copySuccess.value = false;
                }, 2000);
            } catch (err) {
                console.error('Failed to copy: ', err);
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = permanentLink.value;
                document.body.appendChild(textArea);
                textArea.select();
                try {
                    document.execCommand('copy');
                    copySuccess.value = true;
                    setTimeout(() => {
                        copySuccess.value = false;
                    }, 2000);
                } catch (fallbackErr) {
                    console.error('Fallback copy failed: ', fallbackErr);
                }
                document.body.removeChild(textArea);
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
            currentlySelectedTab,
            permanentLink,
            copySuccess,
            copyToClipboard
        }
    },
})
</script>

<style lang="less">
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

.floating-header {
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
    padding: 0.5rem 0;
    border-bottom: 1px solid #e0e0e0;
}

.permanent-link-wrapper {
    display: flex;
    padding: @spacing-25;
    padding-left: 0;
    align-content: center;
    width: fit-content;
}

.link-container {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
}

.link-container a {
    display: inline-block;
    border: @border-subtle;
    padding: @spacing-50;
}

.link-url {
    .cdx-mixin-link();
    font-family: @font-family-monospace;
}

.copy-url-button.cdx-button.cdx-button--weight-quiet, .cdx-button.cdx-button--fake-button--enabled.cdx-button--weight-quiet {
    align-self: flex-end;
    background: @background-color-neutral-subtle;
}

.link-url:hover {
    text-decoration: underline;
}

.title-of-run-page {
    width: fit-content;
    margin: 0;
    font-size: @font-size-xx-large;
    font-weight: bold;
    margin-top: @spacing-25;
    > a {
        .cdx-mixin-link();
    }
}

.maho-text-wrapper > div > a {
    .cdx-mixin-link();
}

.filter-button-group {
    margin-top: @spacing-50;
    > .cdx-toggle-button {
        margin-right: @spacing-25;
    }
}

.citation-card-data {
    margin-bottom: @spacing-25;
}

.cdx-docs-link {
	.cdx-mixin-link();
}
</style>
