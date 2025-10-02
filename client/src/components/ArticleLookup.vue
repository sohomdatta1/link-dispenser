<template>
	<div>
		<cdx-field class="field">
			<cdx-lookup
				v-model:selected="selection"
				:menu-items="menuItems"
				:menu-config="menuConfig"
				@input="onInput"
				@load-more="onLoadMore"
			>
				<template #no-results>
					No results found.
				</template>
			</cdx-lookup>
			<template #label>
				Select a page to analyze
			</template>
			<template #help-text>
				Start typing the name of a English Wikipedia article to analyze
			</template>
		</cdx-field>

		<cdx-checkbox
			v-model="checkLLM">
				Check for LLM citation patterns
		</cdx-checkbox>

		<cdx-checkbox
			v-model="bypassCache">
				Bypass cache and force re-analysis
		</cdx-checkbox>

		<cdx-button
			:disabled="!selection"
			@click="onAnalyzeClick"
		>
			Analyze page
		</cdx-button>
	</div>
</template>

<script lang="ts">
import { defineComponent, ref, type Ref } from 'vue';
import { CdxLookup, CdxField, CdxCheckbox, CdxButton } from '@wikimedia/codex';

export default defineComponent( {
	name: 'ArticleLookup',
	components: { CdxLookup, CdxField, CdxCheckbox, CdxButton },
	setup() {
		const selection: Ref<any> = ref( null );
		const menuItems: Ref<any[]> = ref( [] );
		const currentSearchTerm = ref( '' );
		const checkLLM = ref( false );
		const bypassCache = ref( false );

		function fetchResults( searchTerm: string ) {
			const params = new URLSearchParams( {
				"action": "query",
				"format": "json",
				"list": "search",
				"utf8": "1",
				"formatversion": "2",
				"srsearch": `${searchTerm}`,
				"srinfo": "",
				"srprop": "",
				"srnamespace": "*",
				"origin": "*"
			} );

			return fetch( `https://en.wikipedia.org/w/api.php?${ params.toString() }` )
				.then( ( response ) => response.json() );
		}

		function onInput( value: string ) {
			currentSearchTerm.value = value;

			if ( !value ) {
				menuItems.value = [];
				return;
			}

			fetchResults( value )
				.then( ( data ) => {
					if ( currentSearchTerm.value !== value ) {
						return;
					}

					if ( !data.query.search || data.query.search.length === 0 ) {
						menuItems.value = [];
						return;
					}

					const results = data.query.search.map( ( result: any ) => {
						return {
							label: result.title,
							value: result.title
						};
					} );

					menuItems.value = results;
				} )
				.catch( () => {
					menuItems.value = [];
				} );
		}

		function deduplicateResults( results: any[] ) {
			const seen = new Set( menuItems.value.map( ( result ) => result.value ) );
			return results.filter( ( result ) => !seen.has( result.value ) );
		}

		function onLoadMore() {
			if ( !currentSearchTerm.value ) {
				return;
			}

			fetchResults( currentSearchTerm.value )
				.then( ( data ) => {
					if ( !data.search || data.search.length === 0 ) {
						return;
					}

					const results = data.search.map( ( result: any ) => {
						return {
							label: result.label,
							value: result.id,
							description: result.description
						};
					} );

					const deduplicatedResults = deduplicateResults( results );
					menuItems.value.push( ...deduplicatedResults );
				} );
		}

		function onAnalyzeClick() {
			if ( selection.value ) {
				const basePath = checkLLM.value ? '/llmanalyze' : '/analyze';
				const cacheBypass = bypassCache.value ? new URLSearchParams({ 'nocache': 'yes' }) : '';
				document.location.href = `${basePath}/${encodeURIComponent(selection.value)}${cacheBypass}`;
			}
		}

		const menuConfig = {
			visibleItemLimit: 6
		};

		return {
			selection,
			menuItems,
			menuConfig,
			checkLLM,
			bypassCache,
			onInput,
			onLoadMore,
			onAnalyzeClick
		};
	}
} );
</script>

<style lang='less' scoped>
@import '@wikimedia/codex-design-tokens/theme-wikimedia-ui.less';
.field {
	padding-top: @spacing-100;
}
</style>
