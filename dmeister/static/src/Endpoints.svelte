<script>
  import Loader from "./common/Loader.svelte";
  import EndpointTable from "./EndpointTable.svelte";

  let endpoints = fetch(`/api/endpoints`, {
    credentials: "same-origin"
  })
    .then(resp => resp.json())
    .then(json => json.endpoints);


  let services = fetch(`/api/services`, {
    credentials: "same-origin"
  })
    .then(resp => resp.json())
    .then(json => json.services);

  let both = Promise.all([endpoints, services])
</script>

<div>
  {#await both}
    <Loader />
  {:then response}
    <EndpointTable endpoints={response[0]} services={response[1]} />
  {:catch error}
    <p>Error retrieving services: {error.message}</p>
  {/await}
</div>
