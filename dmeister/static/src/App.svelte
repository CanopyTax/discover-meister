<script>
  import { imperialBackground } from "imperial-style";
  import { Router, Link, Route } from "svelte-routing";
  import Services from "./Services.svelte";
  import Endpoints from "./Endpoints.svelte";
  import Logo from "./common/Logo.svelte";

  /* imperialBackground(); */

  let activeUrl = window.location.pathname;

  export let url = "";
</script>

<style>
  h1 {
    color: white;
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
    background: white;
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
    text-shadow: 0 0 0.625em #bc1e22, 0 0 1.5625em #bc1e22,
      -0.0625em 0 0.125em rgba(0, 0, 0, 0.5);
    font-size: 1.5rem;
    display: block;
    margin-top: 5vh;
  }

  :global(a:visited) {
    color: white;
  }

  .content {
    grid-area: content;
    color: white;
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
    top: -2px;
    color: red;
    font-size: 26px;
  }
</style>

<Router {url}>
  <div class="grid-container">
    <div class="bar" />
    <div class="nav-menu">
      <div class="link-wrapper" on:click="{() => activeUrl = '/'}">
        {#if activeUrl === '/'}
          <span class="active">/</span>
        {/if}
        <Link to="/">Services</Link>
      </div>
      <div class="link-wrapper" on:click="{() => activeUrl = '/endpoints'}">
        {#if activeUrl === '/endpoints'}
          <span class="active">/</span>
        {/if}
        <Link to="endpoints">Endpoints</Link>
      </div>
    </div>
    <div class="content">
      <Route path="/">
        <Services />
      </Route>
      <Route path="endpoints">
        <Endpoints />
      </Route>
    </div>
    <div class="primary-navbar">
      <Logo />
      <h1>Discover Meister</h1>
    </div>
  </div>
</Router>
