<script>
  import Loader from "./common/Loader.svelte";

  const services = new Promise(resolve =>
    setTimeout(
      () =>
        resolve({
          services: [
            {
              name: "anakin",
              protocols: { http: { host: "http://anakin.skywalker" } },
              meta: { master: false, squad: "council" },
              endpoints: "{host}/services/anakin/endpoints"
            },
            {
              name: "palpatine",
              protocols: { http: { host: "http://pal.sith" } },
              meta: { master: false, squad: "sith" },
              endpoints: "{host}/services/anakin/endpoints"
            },
            {
              name: "vader",
              protocols: { http: { host: "http://vader.sith" } },
              meta: { master: false, squad: "sith" },
              endpoints: "{host}/services/anakin/endpoints"
            },
            {
              name: "yoda",
              protocols: { http: { host: "http://yoda.jedi" } },
              meta: { master: false, squad: "council" },
              endpoints: "{host}/services/anakin/endpoints"
            },
            {
              name: "anakin2",
              protocols: { http: { host: "http://anakin.skywalker" } },
              meta: { master: false, squad: "council" },
              endpoints: "{host}/services/anakin/endpoints"
            },
            {
              name: "palpatine2",
              protocols: { http: { host: "http://pal.sith" } },
              meta: { master: false, squad: "sith" },
              endpoints: "{host}/services/anakin/endpoints"
            },
            {
              name: "vader2",
              protocols: { http: { host: "http://vader.sith" } },
              meta: { master: false, squad: "sith" },
              endpoints: "{host}/services/anakin/endpoints"
            },
            {
              name: "yoda2",
              protocols: { http: { host: "http://yoda.jedi" } },
              meta: { master: false, squad: "council" },
              endpoints: "{host}/services/anakin/endpoints"
            }
          ]
        }),
      1000
    )
  ).then(resp => resp.services);
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
    font-weight:bold;
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
</style>

<div>
  {#await services}
    <Loader />
  {:then services}
    <table>
      <thead>
        <tr>
          <th>Service name</th>
          <th>Protocols</th>
          <th>Squad</th>
        </tr>
      </thead>
      <tbody>
        {#each services as service (service.name)}
          <tr>
            <td>{service.name}</td>
            <td>{Object.keys(service.protocols).join(', ')}</td>
            <td>{service.meta.squad}</td>
          </tr>
        {/each}
      </tbody>
    </table>
  {:catch error}
    <p>Error retrieving services: {error.message}</p>
  {/await}
</div>
