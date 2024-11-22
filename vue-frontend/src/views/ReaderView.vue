<template>
  <div class="reader">
    <div class="content">
      <!-- Reader content will be displayed here -->
    </div>
    <div class="controls">
      <!-- Reader controls will be added here -->
    </div>
  </div>
</template>

<script setup lang="ts">
// Reader component logic will be added here
</script>

<style scoped>
.reader {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.content {
  flex: 1;
  padding: 1rem;
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.6;
}

.controls {
  padding: 1rem;
  display: flex;
  justify-content: center;
  gap: 1rem;
  background-color: #f8f9fa;
  border-top: 1px solid #e9ecef;
}
</style>
