function initializeYouTubePlayer(videoUrl) {
    const container = document.getElementById('youtube-player-container');
    const videoId = new URL(videoUrl).searchParams.get('v') || videoUrl.split('youtu.be/')[1];

    const iframe = document.createElement('iframe');
    iframe.src = `https://www.youtube.com/embed/${videoId}`;
    iframe.width = "100%";
    iframe.height = "200px";
    iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
    iframe.allowFullscreen = true;

    iframe.onerror = () => {
        container.innerHTML = `
            <p>This video cannot be embedded. <a href="${videoUrl}" target="_blank">Watch on YouTube</a></p>
        `;
    };

    container.innerHTML = ''; // Clear existing iframe
    container.appendChild(iframe);
}
