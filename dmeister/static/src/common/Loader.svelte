<script>
  import Logo from './Logo.svelte';
</script>
<style>
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    25% {
      transform: rotate(90deg);
    }
    50% {
      transform: rotate(180deg);
    }
    75% {
      transform: rotate(270deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
  .spin {
    animation: spin 2550ms;
    animation-timing-function: linear;
  }
  .wrapper {
    width: 100%;
    height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
  }
</style>

<div class="wrapper">
  <div class="spin">
    <Logo />
  </div>
</div>
