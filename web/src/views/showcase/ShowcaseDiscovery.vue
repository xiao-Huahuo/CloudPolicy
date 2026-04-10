<template>
  <div class="sc-discovery">
    <ShowcaseHeader :transparent-top="true" top-text="light" />
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
.sc-discovery {
  min-height: 100vh;
  background: var(--discovery-page-bg);
  transition: background 0.45s ease;
}
.sc-discovery-body { padding-top: 64px; }
</style>
