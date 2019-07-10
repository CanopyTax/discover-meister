<script>
  import LoaderIcon from './Loader-icon.svelte'

  let size = 'large'

</script>
<style>
  .loader {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    padding: 0 36px;
    margin-top: 60px;
  }

  .loader div{
    float: left;
    border-radius: 50%;
    opacity: 0.2;
  }

  .loader div:first-child {
    animation: firstball 1350ms infinite linear;
  }
  .loader div:nth-child(2) {
    animation: secondball 1350ms infinite linear;
  }
  .loader div:last-child {
    animation: thirdball 1350ms infinite linear;
  }

  @keyframes firstball {
    0% {
      opacity: 0;
      transform: scale(0.5);
    }
    13% {
      opacity: 0.9;
      transform: scale(1.03);
    }
    26% {
      opacity: 1;
      transform: scale(0.95);
    }
    33% {
      transform: scale(1);
    }
    34% {
      opacity: 0.2;
    }
  }

  @keyframes secondball {
    32% {
      opacity: 0.2;
      transform: scale(1);
    }
    33% {
      opacity: 0;
      transform: scale(0.5);
    }
    46% {
      opacity: 0.9;
      transform: scale(1.03);
    }
    59% {
      opacity: 1;
      transform: scale(0.95);
    }
    66% {
      transform: scale(1);
    }
    67% {
      opacity: 0.2;
    }
  }

  @keyframes thirdball {
    67% {
      opacity: 0.2;
      transform: scale(1);
    }
    68% {
      opacity: 0;
      transform: scale(0.5);
    }
    81% {
      opacity: 0.9;
      transform: scale(1.03);
    }
    94% {
      opacity: 1;
      transform: scale(0.95);
    }
    100% {
      transform: scale(1);
    }
  }

  .dot {
    width: 8px;
    height: 8px;
    margin-left: 8px;
  }

  .large-dot {
    width: 48px;
    height: 48px;
    margin-left: 48px;
  }
</style>

<div class="loader">
  <div
    class='{size === "small" ? "dot" : "large-dot"}'
  >
    <LoaderIcon />
  </div>
  <div
    class='{size === "small" ? "dot" : "large-dot"}'
  >
    <LoaderIcon />
  </div>
  <div
    class='{size === "small" ? "dot" : "large-dot"}'
  >
    <LoaderIcon />
  </div>
</div>
