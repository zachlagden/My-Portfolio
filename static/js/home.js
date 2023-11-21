// Output "Hello world!" to the console
console.log("Hello world!");

// Get a reference to the audio element using jQuery
const audioElement = $("#song")[0]; // Use [0] to access the DOM element

// Function to toggle the song play/pause
function toggleSongOfTheWeek() {
    // Check if the audio is currently paused
    if (audioElement.paused) {
        // If paused, play the audio
        audioElement.play();
        $('.icon').removeClass("fa-play");
        $('.icon').addClass("fa-pause"); // Update button icon
        console.log("[MUSIC] paused.");

        if (audioElement.currentTime < 1) {
            $.ajax({
                type: "POST",
                url: "/api/v1/song_of_the_week",
                success: function (data) {
                    console.log("[STATS] logged play");
                },
                error: function (xhr, status, error) {
                    console.log("[STATS] error logging play");
                }
            });
        }

    } else {
        // If playing, pause the audio
        audioElement.pause();
        $('.icon').removeClass("fa-pause");
        $('.icon').addClass("fa-play"); // Update button icon
        console.log("[MUSIC] playing.");
    }
}

// Event listener for when the audio ends
audioElement.addEventListener("ended", function () {
    audioElement.currentTime = 0; // Reset audio to the beginning
    $('.icon').removeClass("fa-pause");
    $('.icon').addClass("fa-play"); // Update button icon
});
