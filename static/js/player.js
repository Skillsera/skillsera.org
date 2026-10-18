function videoPlayer() {
  return {
    embedUrl: null,

    play(url, start, stop) {
      const videoId = extractVideoId(url);
      if (!videoId) return;

      let embed = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
      if (start) embed += `&start=${start}`;
      if (stop) embed += `&end=${stop}`;
      this.embedUrl = embed;

      this.$nextTick(() => {
        const container = this.$el.querySelector('.video-player-container');
        if (container) container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      });
    },
  };
}

function extractVideoId(url) {
  const patterns = [
    /youtube\.com\/watch\?v=([A-Za-z0-9_\-]{11})/,
    /youtu\.be\/([A-Za-z0-9_\-]{11})/,
    /youtube\.com\/embed\/([A-Za-z0-9_\-]{11})/,
  ];
  for (const re of patterns) {
    const m = re.exec(url);
    if (m) return m[1];
  }
  return null;
}
