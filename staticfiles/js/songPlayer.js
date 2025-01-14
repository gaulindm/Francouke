function initializeYouTubePlayer(metadata) {
    const container = document.getElementById('youtube-player-container');
    const videoUrl = metadata.youtube;
    const videoId = new URL(videoUrl).searchParams.get('v') || videoUrl.split('youtu.be/')[1];

        // Log the extracted videoId for debugging
        console.log(`Extracted videoId: ${videoId}`);

    if (!videoId) {
        container.innerHTML = `<p>Invalid YouTube URL. Cannot play video.</p>`;
        return;
    }

    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${videoId}?autoplay=1`;
    iframe.width = "100%";
    iframe.height = "200px";
    iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
    iframe.allowFullscreen = true;

    iframe.onerror = () => {
        container.innerHTML = `
            <p>Unable to load the video. <a href="${videoUrl}" target="_blank">Watch on YouTube</a></p>
        `;
    };

    container.innerHTML = ''; // Clear existing iframe
    container.appendChild(iframe);
}
