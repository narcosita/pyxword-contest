let autoRefresh;


function refreshBodyContent() {
  $('.body-content').load(
    window.location.href + ' .body-content'
  );
}

function setupRefreshBodyContent(interval) {
  if (autoRefresh) {
    clearInterval(autoRefresh);
  }

  if (interval) {
    setInterval(refreshBodyContent, interval);
  }
}


window.setupRefreshBodyContent = setupRefreshBodyContent;
