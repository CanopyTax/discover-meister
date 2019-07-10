<script>
  import Loader from "./common/Loader.svelte";
  import EndpointTable from "./EndpointTable.svelte";

  let endpoints = fetch(`/api/endpoints`, {
    credentials: "same-origin"
  })
    .then(resp => resp.json())
    .then(json => json.endpoints);
</script>

<div>
  {#await endpoints}
    <Loader />
  {:then endpoints}
    <EndpointTable {endpoints} />
  {:catch error}
    <p>Error retrieving services: {error.message}</p>
  {/await}
</div>
