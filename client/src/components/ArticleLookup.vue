<template>
    <cdx-typeahead-search
		id="typeahead-search-pending-state"
		form-action="/analyze"
		button-label="Analyze"
		search-results-label="Search results"
		:search-results="searchResults"
		:search-footer-url="searchFooterUrl"
		:show-thumbnail="true"
		:highlight-query="true"
		:auto-expand-width="true"
		placeholder="Analyze a specific page"
		@input="onInput"
		@submit="onSubmit"
		@search-result-click="onSearchClick"
	>
		<template #default>
			<input
				type="hidden"
				name="language"
				value="en"
			>
			<input
				type="hidden"
				name="title"
				value="Analyze page"
			>
		</template>
		<template #search-results-pending>
			Loading potential article results...
		</template>
	</cdx-typeahead-search>
</template>

<script lang="ts">
import { defineComponent, ref, type Ref } from 'vue';
import { CdxTypeaheadSearch } from '@wikimedia/codex';

export default defineComponent( {
	name: 'TypeaheadSearchPendingState',
	components: { CdxTypeaheadSearch },
	setup() {
		const searchResults: Ref<any[]> = ref( [] );
		const searchFooterUrl = ref( '' );
		const currentSearchTerm = ref( '' );

		/**
		 * Format search results for consumption by TypeaheadSearch.
		 *
		 * @param pages
		 * @return
		 */
		function adaptApiResponse( pages: Array<any> ) {
			return pages.map( ( { id, title, description, thumbnail } ) => ( {
				label: title,
				value: id,
				description: description,
				thumbnail: thumbnail ? {
					url: thumbnail.url,
					width: thumbnail.width,
					height: thumbnail.height
				} : undefined
			} ) );
		}

		function onInput( value: string ) {
			// Internally track the current search term.
			currentSearchTerm.value = value;

			// Unset search results and the search footer URL if there is no value.
			if ( !value || value === '' ) {
				searchResults.value = [];
				searchFooterUrl.value = '';
				return;
			}

			fetch(
				`https://en.wikipedia.org/w/rest.php/v1/search/title?q=${ encodeURIComponent( value ) }&limit=10`
			).then( ( resp ) => resp.json() )
				.then( ( data: any ) => {
					// Make sure this data is still relevant first.
					if ( currentSearchTerm.value === value ) {
						// If there are results, format them into an array of
						// SearchResults to be passed into TypeaheadSearch for
						// display as a menu of suggestions.
						searchResults.value = data.pages && data.pages.length > 0 ?
							adaptApiResponse( data.pages ) :
							[];

						// Set the search footer URL to a link to the search
						// page for the current search query.
						searchFooterUrl.value = `https://en.wikipedia.org/w/index.php?title=Special%3ASearch&fulltext=1&search=${ encodeURIComponent( value ) }`;

					}
				} ).catch( () => {
					// On error, reset search results and search footer URL.
					searchResults.value = [];
					searchFooterUrl.value = '';
				} );
		}
		function onSubmit () {
			document.location.href = `/analyze/${currentSearchTerm.value}`
		}

		function onSearchClick() {
			document.location.href = `/analyze/${currentSearchTerm.value}`
		}

		return {
			searchResults,
			searchFooterUrl,
			onInput,
			onSubmit,
			onSearchClick
		};
	}
} );
</script>
