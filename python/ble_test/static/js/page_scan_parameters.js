// Fetch initial values from Flask endpoint
document.addEventListener("DOMContentLoaded", function() {
  fetch('/get_initial_config')
    .then(response => response.json())
    .then(data => {
      document.getElementById("keep_data").checked = data.keep_data;
      document.getElementById("scan_new_tags").checked = data.scan_new_tags;
      document.getElementById("maximum_retries").value = data.maximum_retries;

      document.getElementById("scan_max_scans").value = data.scan_max_scans;
      document.getElementById("connect_max_retry").value = data.connect_max_retry;
      document.getElementById("connect_timeout").value = data.connect_timeout;
      document.getElementById("max_BoldTags").value = data.max_BoldTags;

      // Set radio buttons based on the enabled tags value
            if (data.enable_disable_tags === 'enable') {
                document.getElementById('enabled').checked = true;
            } else if (data.enable_disable_tags === 'disable') {
                document.getElementById('disabled').checked = true;
            } else {
                document.getElementById('none').checked = true;
            }
    })
    .catch((error) => console.error('Error loading initial configuration:', error));
});

function saveConfig() {
  // Get the values from form fields
  const keepData = document.getElementById("keep_data").checked;
  const scanNewTags = document.getElementById("scan_new_tags").checked;
  const enable_disable_tags = document.querySelector('input[name="enable_disable_tags"]:checked').value;
  const maximumRetries = parseInt(document.getElementById("maximum_retries").value, 10);

  const scan_max_scans = parseInt(document.getElementById("scan_max_scans").value, 4);
  const connect_max_retry = parseInt(document.getElementById("connect_max_retry").value, 3);
  const connect_timeout = parseInt(document.getElementById("connect_timeout").value, 15);
  const max_BoldTags = parseInt(document.getElementById("max_BoldTags").value, 10);


  // Prepare data as JSON
  const data = {
    keep_data: keepData,
    scan_new_tags: scanNewTags,
    enable_disable_tags: enable_disable_tags,
    maximum_retries: maximumRetries,

    scan_max_scans: scan_max_scans,
    connect_max_retry: connect_max_retry,
    connect_timeout: connect_timeout,
    max_BoldTags: max_BoldTags

  };

  // Send data to the Flask endpoint
  fetch('/save_config', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(data)
  })
  .then(response => response.json())
  .then(data => {
    if (data.status === 'success') {
      alert("Configuration saved successfully!");
    } else {
      alert("Error saving configuration: " + data.message);
    }
  })
  .catch((error) => {
    console.error('Error:', error);
    alert("Failed to save configuration.");
  });
}