<template>
    <div class="wrapper">
    <div v-if="loading" class="maho-text-wrapper">
        <div>Loading previous analysis...</div>
    </div>
    <div v-if="!loading && notSuccess" class="maho-text-wrapper">
        This analysis does not exist or has expired.
    </div>
    <div v-if="!loading && erroredOut" class="maho-text-wrapper">
        Something definitely went wrong here. Please report this URL to [[en:User talk:Sohom_Datta]] or sohom_#0 on Discord.
    </div>
    <div v-if="!loading && isCached" class="maho-text-wrapper"><i>You are viewing the archived results from a previous run conducted <template v-if="cachedTimeExists"><abbr :title="cachedTime.toUTCString()">{{ formatRelativeTime(cachedTime) }}</abbr></template><template v-else>within the last 24 hours</template>. To get a fresh run, use <a :href="`/${ isLLMAnalysis ? 'llmanalyze' : 'analyze' }/${ articleName }?nocache=yes`">this link</a>.</i></div>
    <div>
        <template v-if="!loading && !notSuccess && !erroredOut">
            <div>
                <div class="floating-header">
                    <div>
                        <h1 class="title-of-run-page">Results for <a :href='`https://en.wikipedia.org/wiki/${ articleName }`'>{{ articleName }}</a></h1>
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
                <br>
                <div v-for="data in actualData" :key="data.uid">
                    <citation-card v-bind:data="data" :considerLLM="isLLMAnalysis"></citation-card>
                </div>
            </div>
        </template>
    </div>
    </div>
</template>

<script lang="ts">
import { defineComponent, ref, type Ref } from 'vue'
import { CdxMessage, CdxToggleButtonGroup } from '@wikimedia/codex';
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
    name: 'PreviousAnalysisView',
    components: { CitationCard, CdxToggleButtonGroup, CdxMessage },
    props: {
        isLLMAnalysis: {
            type: Boolean,
            default: false
        }
    },
    setup(props) {
        const loading = ref(true);
        const notSuccess = ref(false);
        const erroredOut = ref(false);
        const isCached = ref(false);
        const cachedTimeExists = ref(false);
        const cachedTime = ref(new Date());
        const articleName = ref('');
        let fetchedData: any[] = [];
        const actualData: Ref<any[]> = ref([]);
        const totalCount = ref(0);
        const currentlySelectedTab = ref(props.isLLMAnalysis ? 'hallucinated' : 'all');
        let selectedTabName = props.isLLMAnalysis ? 'hallucinated' : 'all';
        const route = useRoute();
        
        // Define buttons based on analysis type
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
                label: 'Potentially spammy links',
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
                label: 'Already has a archive.org link',
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

        async function initData() {
            const uuid = route.params.uuid;
            try {
                // First check if the permanent link exists
                const existsResp = await fetch(`/api/permanent_result_link_exists/${uuid}`);
                const existsJson = await existsResp.json();
                
                if (!existsJson.exists) {
                    notSuccess.value = true;
                    loading.value = false;
                    return;
                }
                
                // Get the article data
                const articleResp = await fetch(`/api/get_analysis/${uuid}`);
                const articleJson = await articleResp.json();
                
                if (!articleJson || !articleJson['article_name']) {
                    notSuccess.value = true;
                    loading.value = false;
                    return;
                }
                
                articleName.value = articleJson['article_name'];
                
                // Get the analysis data
                const dataResp = await fetch(`/api/fetch_analysis/${uuid}`);
                const dataJson = await dataResp.json();
                
                fetchedData = dataJson || [];
                totalCount.value = fetchedData.length;
                
                if (articleJson['computed_on']) {
                    cachedTime.value = new Date(articleJson['computed_on']);
                    cachedTimeExists.value = true;
                    isCached.value = true;
                }
                
                document.title = `Results for ${articleName.value}`;
                onClickButtonGroup(selectedTabName);
                updateButtons(fetchedData);
                loading.value = false;
            } catch (error) {
                console.error('Error fetching analysis:', error);
                erroredOut.value = true;
                loading.value = false;
            }
        }

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

        function onClickButtonGroup(value: string) {
            selectedTabName = value;
            currentlySelectedTab.value = value;
            fetchedData = fetchedData.sort((a: any, b: any) => (b['crawl_time'] - a['crawl_time']));
            if (value === 'all') {
                actualData.value = fetchedData;
                return;
            }

            if (props.isLLMAnalysis) {
                if (value === 'hallucinated') {
                    actualData.value = fetchedData.filter((elem: any) => elem['hallucinated'] && !elem['hallucinated_unsure'])
                    return;
                }

                if (value === 'unsure') {
                    actualData.value = fetchedData.filter((elem: any) => elem['hallucinated_unsure'])
                    return;
                }

                if (value === 'nothallucinated') {
                    actualData.value = fetchedData.filter((elem: any) => !elem['hallucinated'])
                    return;
                }
            } else {
                if (value === 'archive') {
                    actualData.value = fetchedData.filter((elem: any) => elem['archive_url'])
                    return;
                }

                if (value === 'notarchive') {
                    actualData.value = fetchedData.filter((elem: any) => !elem['archive_url'])
                    return;
                }
            }

            actualData.value = fetchedData.filter((elem: any) => elem['url_info']['desc'] === value)
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

        // Initialize data when component mounts
        initData();

        return {
            loading,
            notSuccess,
            erroredOut,
            isCached,
            cachedTime,
            cachedTimeExists,
            articleName,
            actualData,
            buttons,
            totalCount,
            onClickButtonGroup,
            currentlySelectedTab,
            formatRelativeTime
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

.floating-header {
    position: sticky;
    top: 0;
    background: white;
    z-index: 10;
    padding: 1rem 0;
    border-bottom: 1px solid #e0e0e0;
}

.cdx-docs-link {
	.cdx-mixin-link();
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

.suggested-filters {
    margin-top: @spacing-100;
}

.maho-text-wrapper a {
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

</style>
