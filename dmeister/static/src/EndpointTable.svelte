<script>
  import Empty from "./common/Empty.svelte";
  import Droid from './common/icons/droid.svelte';
  export let endpoints = [];
  export let services = [];
  export let emptyMessage = "There are no endpoints registered!";
  const serviceDocs = services.reduce((acc, service) => {
    if (service.meta && service.meta.api_documentation) {
      acc[service.name] = service.meta.api_documentation
    }
    return acc
  }, {})

</script>

<style>
  table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 16px;
  }
  th {
    font-size: 15px;
    color: white;
    text-shadow: 0 0 0.625em white, 0 0 1.5625em white,
      -0.0625em 0 0.125em rgba(0, 0, 0, 0.5);
    line-height: 1.4;
    text-transform: uppercase;
    background-color: #393939a3;
    font-weight: bold;
    padding: 18px;
  }
  th,
  td {
    font-weight: unset;
    padding-right: 10px;
  }
  th {
    text-align: left;
  }
  td {
    font-family: Lato-Regular;
    font-size: 15px;
    color: #c0c0c0;
    line-height: 1.4;
    background-color: #222222b8;
    padding: 18px;
  }

  tr:hover td {
    cursor: pointer;
    background-color: #222222f8;
  }

  .actions {
    opacity: 0;
    transition: 100ms linear opacity;
  }

  .actions a {
    margin: 0;
    position: relative;
  }

  tr:hover .actions {
    opacity: 1;
  }
</style>

{#if !endpoints || !endpoints.length}
  <Empty message={emptyMessage} />
{:else}
  <table>
    <thead>
      <tr>
        <th>Service name</th>
        <th>Path</th>
        <th>Methods</th>
        <th>Deprecated</th>
        <th />
      </tr>
    </thead>
    <tbody>
      {#each endpoints as endpoint}
        <tr>
          <td>{endpoint.service}</td>
          <td>
            <pre>
               {endpoint.path.length > 85 ? endpoint.path.substring(0, 85) + '...' : endpoint.path}

            </pre>
          </td>
          <td>{endpoint.methods.join(', ')}</td>
          <td>{endpoint.deprecated}</td>
          <td>
            {#if serviceDocs[endpoint.service]}
              <div class="actions">
                <a href="{serviceDocs[endpoint.service]}" title="Documentation"><Droid /></a>
              </div>
            {/if}
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
{/if}
