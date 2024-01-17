<template>
    <cdx-progress-bar aria--label="Analyzing" v-if="!showResults" inline />
    <div v-if="!showResults">
        Analyzing [[{{ $route.params.articleName }}]], this might take a <i>while.....</i> I'd suggest grabbing a cup of coffee, taking a walk or doing some other activity
    </div>
    <template v-if="showResults">
        <cdx-toggle-button-group
        :model-value="currentlySelectedTab"
		:buttons="buttons"
		@update:modelValue="onClickButtonGroup"
	>
        </cdx-toggle-button-group>
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
        let fetchedData: any[] = [];
        const actualData: Ref<any[]> = ref( [] );
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
                label: 'Potentially spammy link',
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
            fetchedData = data['template_info']
            actualData.value = fetchedData;
            showResults.value = true;
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
            onClickButtonGroup,
            currentlySelectedTab
        }
    },
})
</script>
