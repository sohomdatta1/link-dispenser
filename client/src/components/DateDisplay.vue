<template>
    <span> {{ $props.date }}
        <template v-if="humanRelative($props.date) != 'Invalid date'"> ({{ humanRelative($props.date ) }})</template>
    </span>
</template>

<script lang="ts">
import { defineComponent } from 'vue'
export default defineComponent({
  methods: {
    humanRelative(dateStr: string) {
      const now = new Date();
      const dt = new Date(dateStr);

      if (isNaN(dt.getTime())) return "Invalid date";

      const diff = now.getTime() - dt.getTime();
      const seconds = Math.floor(diff / 1000);
      const minutes = Math.floor(seconds / 60);
      const hours = Math.floor(minutes / 60);
      const days = Math.floor(hours / 24);
      const months = Math.floor(days / 30);
      const years = Math.floor(days / 365);

      if (years > 0) return years + (years === 1 ? " year ago" : " years ago");
      if (months > 0) return months + (months === 1 ? " month ago" : " months ago");
      if (days > 0) return days + (days === 1 ? " day ago" : " days ago");
      if (hours > 0) return hours + (hours === 1 ? " hour ago" : " hours ago");
      if (minutes > 0) return minutes + (minutes === 1 ? " minute ago" : " minutes ago");
      return seconds + (seconds === 1 ? " second ago" : " seconds ago");
    }
  },
  props: {
    "date": {
            type: String,
            required: true
        },
    }
});
</script>