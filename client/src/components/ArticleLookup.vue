<template>
	<cdx-field>
		<cdx-lookup
			v-model:selected="selection"
			:menu-items="menuItems"
			:menu-config="menuConfig"
			@input="onInput"
			@load-more="onLoadMore"
			@update:selected="onAnalyzeSelected"
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
</template>

<script lang="ts">
import { defineComponent, ref, type Ref } from 'vue';
import { CdxLookup, CdxField } from '@wikimedia/codex';

export default defineComponent( {
	name: 'ArticleLookup',
	components: { CdxLookup, CdxField },
	setup() {
		const selection: Ref<any> = ref( null );
		const menuItems: Ref<any[]> = ref( [] );
		const currentSearchTerm = ref( '' );

		/**
		 * Get search results.
		 *
		 * @param {string} searchTerm
		 * @param {number} offset Optional result offset
		 *
		 * @return {Promise}
		 */
		function fetchResults( searchTerm: string ) {
			const params = new URLSearchParams( {
				"action": "query",
				"format": "json",
				"list": "search",
				"utf8": "1",
				"formatversion": "2",
				"srsearch": `intitle: ${searchTerm}`,
				"srinfo": "",
				"srprop": "",
				"origin": "*"
			} );

			return fetch( `https://en.wikipedia.org/w/api.php?${ params.toString() }` )
				.then( ( response ) => response.json() );
		}

		/**
		 * Handle lookup input.
		 *
		 * TODO: this should be debounced.
		 *
		 * @param {string} value
		 */
		function onInput( value: string ) {
			// Internally track the current search term.
			currentSearchTerm.value = value;

			// Do nothing if we have no input.
			if ( !value ) {
				menuItems.value = [];
				return;
			}

			fetchResults( value )
				.then( ( data ) => {
					// Make sure this data is still relevant first.
					if ( currentSearchTerm.value !== value ) {
						return;
					}

					// Reset the menu items if there are no results.
					if ( !data.query.search || data.query.search.length === 0 ) {
						menuItems.value = [];
						return;
					}

					// Build an array of menu items.
					const results = data.query.search.map( ( result: any ) => {
						return {
							label: result.title,
							value: result.title
						};
					} );

					// Update menuItems.
					menuItems.value = results;
				} )
				.catch( () => {
					// On error, set results to empty.
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

					// Update menuItems.
					const deduplicatedResults = deduplicateResults( results );
					menuItems.value.push( ...deduplicatedResults );
				} );
		}

		function onAnalyzeSelected( selected: string ) {
			if ( selected !== null ) {
				document.location.href = `/analyze/${selected}`
			}
		}

		const menuConfig = {
			visibleItemLimit: 6
		};

		return {
			selection,
			menuItems,
			menuConfig,
			onAnalyzeSelected,
			onInput,
			onLoadMore
		};
	}
} );
</script>