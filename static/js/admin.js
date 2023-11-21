$(document).ready(function () {
  // DOM elements
  const messageElement = $("#message");
  const loaderElement = $("#loader");

  // Function to display messages
  function showMessage(message, isError = false) {
    messageElement.html(message);
    messageElement.addClass(isError ? "error" : "success");
    messageElement.show();
  }

  // Function to handle error responses
  function handleErrorResponse(xhr) {
    let errorMessage = "Update failed. Please try again.";

    try {
      const errorResponse = JSON.parse(xhr.responseText);
      if (errorResponse && errorResponse.error) {
        errorMessage = `Update failed: ${errorResponse.error}`;
      }
    } catch (e) {
      console.log(xhr.responseText);
    }

    showMessage(errorMessage, true);
  }

  // Event handler for the update button click
  $("#SOTWUpdateButton").click(function () {
    const inputValue = $("#customInput").val();
    const apiUrl = `/api/v1/song_of_the_week/?song_url=${inputValue}`;

    messageElement.hide();
    loaderElement.show();

    // Send a PUT request to the API using jQuery
    $.ajax({
      type: "PUT",
      url: apiUrl,
      success: function (data) {
        loaderElement.hide();
        showMessage("Update successful!");
      },
      error: function (xhr, status, error) {
        loaderElement.hide();

        if (xhr.status === 400 || xhr.status === 500) {
          handleErrorResponse(xhr);
        } else {
          showMessage("Update failed. Please try again.", true);
        }
      },
    });
  });
});
