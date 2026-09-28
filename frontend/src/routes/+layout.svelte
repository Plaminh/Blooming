<script lang="ts">
  import "$lib/shared/styles/tokens.css";
  import "$lib/shared/styles/global.css";

  import { onMount } from "svelte";
  import { api } from "$lib/api";
  import { desktop } from "$lib/platform/desktopWindow";
  import type { UserSettingsResponse } from "$lib/api/types";

  onMount(() => {
    let disposed = false;
    let polling = false;
    let appliedToken: string | null = null;
    let interval: ReturnType<typeof setInterval> | undefined;
    async function poll() {
      if (disposed || polling) return;
      polling = true;
      try {
        const token = localStorage.getItem("blooming_access_token");
        if (!token) {
          appliedToken = null;
          await desktop.setTrayAlert(false);
          return;
        }
        if (appliedToken !== token) {
          const settings: UserSettingsResponse = await api.get("/me/settings");
          await desktop.reconcileSettings(settings);
          appliedToken = token;
        }
        const reminders: { id: string }[] = await api.get("/reminders/due");
        await desktop.setTrayAlert(reminders.length > 0);
      } catch (error: unknown) {
        console.warn("Desktop reminders could not refresh.", error);
      } finally {
        polling = false;
      }
    }
    const refresh = () => {
      void poll();
    };
    void desktop
      .isReminderOwner()
      .then((ownsReminders) => {
        if (disposed || !ownsReminders) return;
        void poll();
        interval = setInterval(refresh, 60000);
        window.addEventListener("storage", refresh);
        window.addEventListener("focus", refresh);
      })
      .catch((error: unknown) => {
        console.warn("Desktop reminder initialization failed.", error);
      });
    return () => {
      disposed = true;
      clearInterval(interval);
      window.removeEventListener("storage", refresh);
      window.removeEventListener("focus", refresh);
    };
  });

  let { children } = $props();
</script>

{@render children()}
