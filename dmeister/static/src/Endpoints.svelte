<script>
  import Loader from "./common/Loader.svelte";
  import EndpointTable from "./EndpointTable.svelte";
  export let services = []

  let endpoints = fetch(`/api/endpoints`, {
    credentials: "same-origin"
  })
    .then(resp => resp.json())
    .then(json => json.endpoints);

</script>

<div>
  {#await endpoints}
    <Loader />
  {:then response}
    <EndpointTable endpoints={response} services={services} />
  {:catch error}
    <p>Error retrieving endpoints/services: {error.message}</p>
  {/await}
</div>
