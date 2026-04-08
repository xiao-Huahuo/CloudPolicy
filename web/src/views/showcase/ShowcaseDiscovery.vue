<template>
  <div class="sc-discovery">
    <ShowcaseHeader />
    <div class="sc-discovery-body">
      <DiscoveryHome />
    </div>
  </div>
</template>

<script setup>
import ShowcaseHeader from '@/components/showcase/ShowcaseHeader.vue'
import DiscoveryHome from '@/views/DiscoveryHome.vue'
</script>

<style scoped>
.sc-discovery { min-height: 100vh; background: var(--content-bg, #f4f5f7); }
.sc-discovery-body { padding-top: 64px; }
</style>
