<script>
  import DeathStar from './icons/death_star.svelte'
  import Shuttle from './icons/lambda_shuttle.svelte'
  import VaderTie from './icons/vader_tie.svelte'
  import Tie from './icons/tie_fighter.svelte'
  import Destroyer from './icons/star_destroyer.svelte'

  function randomNumber () {
    const max = 5
    const min = 0
    return (Math.random() * (max - min + 1) ) << 0
  }

  let icon = randomNumber()
</script>

<div>
  {#if icon === 0}
    <DeathStar />
  {:else if icon === 1}
    <Destroyer />
  {:else if icon === 2}
    <Shuttle />
  {:else if icon === 3}
    <VaderTie />
  {:else}
    <Tie />
  {/if}
</div>
