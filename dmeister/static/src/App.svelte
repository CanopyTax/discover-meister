<script>
  import { imperialBackground } from "imperial-style";
  import { Router, Link, Route } from "svelte-routing";
  import Loader from "./common/Loader.svelte";
  import Services from "./Services.svelte";
  import Endpoints from "./Endpoints.svelte";
  import EndpointTable from "./EndpointTable.svelte";
  import Logo from "./common/Logo.svelte";

  imperialBackground({animate: false});

  let activeUrl = window.location.pathname;
  let searchString = "";
  let searchResults = null;
  let timeout;

  let services = fetch(`/api/services`, {
    credentials: "same-origin"
  })
    .then(resp => resp.json())
    .then(json => json.services);

  $: if (searchString && searchString.length) {
    clearInterval(timeout);
    timeout = setTimeout(fetchSearchResults, 500);
  }

  $: if (!searchString) {
    clearInterval(timeout);
    searchResults = null;
  }

  function fetchSearchResults() {
    searchResults = fetch(
      `/api/endpoints?path=${encodeURIComponent(searchString)}`,
      {
        credentials: "same-origin"
      }
    )
      .then(resp => resp.json())
      .then(json => json.endpoints);
  }

  export let url = "";
</script>

<style>
  h1 {
    color: var(--white);
  }
  .app-header {
    display: flex;
    align-items: center;
  }
  h1 {
    margin-bottom: 0;
    margin-left: 16px;
  }

  .grid-container {
    display: grid;
    grid-template-columns: 200px 1.5fr;
    grid-template-rows: 100px 5px 1.9fr;
    grid-template-areas: "primary-navbar primary-navbar" "bar bar" "nav-menu content";
    padding: 0 16px;
  }

  .bar {
    grid-area: bar;
    background: var(--white);
    box-shadow: rgb(255, 255, 255) 0px 0px 0.625em,
      rgb(255, 255, 255) 0px 0px 1.5625em,
      rgba(0, 0, 0, 0.5) -0.0625em 0px 0.125em;
  }

  .nav-menu {
    grid-area: nav-menu;
  }

  :global(a) {
    text-transform: uppercase;
    color: white;
    text-shadow: 0 0 0.625em #bc1e22, 0 0 1.5625em var(--red),
      -0.0625em 0 0.125em rgba(0, 0, 0, 0.5);
    font-size: 1.5rem;
    display: block;
    margin-top: 5vh;
  }

  :global(a:visited) {
    color: var(--white);
  }

  .content {
    grid-area: content;
    color: var(--white);
    padding: 24px;
  }

  .primary-navbar {
    grid-area: primary-navbar;
    display: flex;
    align-items: center;
  }

  .link-wrapper {
    position: relative;
  }

  .active {
    width: 20px;
    height: 20px;
    position: absolute;
    font-weight: bold;
    left: -15px;
    top: -6px;
    color: var(--red);
    font-size: 26px;
  }

  .search {
    margin: 0 0 0 24px;
    width: calc(100% - 330px);
    max-width: 800px;
    background: transparent;
    color: var(--white);
  }

  .inactive {
    display: none;
  }
  .search-results {
    display: none;
  }
  .search-results.activate {
    display: block;
  }
</style>

<Router {url}>
  <div class="grid-container">
    <div class="bar" />
    <div class="nav-menu">
      <div
        class="link-wrapper"
        on:click={() => {
          searchString = '';
          activeUrl = '/';
        }}>
        {#if activeUrl === '/'}
          <span class="active">/</span>
        {/if}
        <Link to="/">Services</Link>
      </div>
      <div
        class="link-wrapper"
        on:click={() => {
          searchString = '';
          activeUrl = '/endpoints';
        }}>
        {#if activeUrl === '/endpoints'}
          <span class="active">/</span>
        {/if}
        <Link to="endpoints">Endpoints</Link>
      </div>
    </div>
    <div class="content">
      <div class="search-results" class:activate={searchString}>
        {#if searchResults}
          {#await searchResults}
            <Loader />
          {:then results}
            {#await services}
              <Loader />
            {:then serviceResults}
              <EndpointTable
                services={serviceResults}
                emptyMessage="There are no search results found"
                endpoints={results} />
            {/await}
          {:catch error}
            <p>Error searching services: {error.message}</p>
          {/await}
        {/if}
      </div>
      <div class:inactive={searchString}>
        <Route path="/">
          {#await services}
            <Loader />
          {:then results}
            <Services services={results}/>
          {/await}
        </Route>
        <Route path="endpoints">
          {#await services}
            <Loader />
          {:then results}
            <Endpoints services={results} />
          {/await}
        </Route>
      </div>
    </div>
    <div class="primary-navbar">
      <Logo />
      <h1>Discover Meister</h1>
      <input
        bind:value={searchString}
        class="search"
        type="text"
        placeholder="Search by endpoint" />
    </div>
  </div>
</Router>
