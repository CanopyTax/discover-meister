<script>
  import Loader from "./common/Loader.svelte";
  import Empty from "./common/Empty.svelte";
  import Droid from './common/icons/droid.svelte';

  export let services = []

</script>

<style>
  table {
    width: 100%;
    border-collapse: collapse;
    border-radius: 16px;
  }
  th {
    font-size: 15px;
    color: var(--white);
    text-shadow: 0 0 0.625em var(--white), 0 0 1.5625em var(--white),
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

<div>
  {#await services}
    <Loader />
  {:then services}
    {#if !services || !services.length}
      <Empty message="There are no registered services!" />
    {:else}
      <table>
        <thead>
          <tr>
            <th>Service name</th>
            <th>Protocols</th>
            <th>Squad</th>
            <th />
          </tr>
        </thead>
        <tbody>
          {#each services as service}
            <tr>
              <td>{service.name}</td>
              <td>{Object.keys(service.protocols).join(', ')}</td>
              <td>{service.meta.squad}</td>
              <td>
                {#if service.meta.api_documentation}
                  <div class="actions">
                    <a href="{service.meta.api_documentation}" title="Documentation"><Droid /></a>
                  </div>
                {/if}
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    {/if}
  {:catch error}
    <p>Error retrieving services: {error.message}</p>
  {/await}
</div>
