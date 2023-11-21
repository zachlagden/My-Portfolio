$(document).ready(function () {
    $(".mobile-nav-toggle").click(function () {
        $(".navigation").toggle();
        $(".mobile-nav-toggle").toggle();
        $(".close_nav").toggle();
    });
    $(".close_nav").click(function () {
        $(".navigation").toggle();
        $(".mobile-nav-toggle").toggle();
        $(".close_nav").toggle();
    });

    // Initialize a flag variable
    let hasWidthChanged = false;

    // Function to handle width change
    function handleWidthChange() {
        const currentWidth = $("body").width();

        if (currentWidth > 750 && !hasWidthChanged) {
            $(".mobile-nav-toggle").hide();
            $(".navigation").show();
            $(".close_nav").hide();

            // Set the flag to true to indicate that the function has run for this width range
            hasWidthChanged = true;
        } else if (currentWidth <= 750 && hasWidthChanged) {
            $(".mobile-nav-toggle").show();
            $(".navigation").hide();

            // Reset the flag when the width goes below 750px
            hasWidthChanged = false;
        }
    }


    // Initial call
    handleWidthChange();

    // Attach a resize event listener
    $(window).on('resize', handleWidthChange);
});