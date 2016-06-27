var startBatchCrawling = false;
var idx = 0, finished = 0;

chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) {
  if (changeInfo.status == "complete" && startBatchCrawling) {
    chrome.tabs.sendMessage(tabId, {caller:{mi:'AnalyzePage', tab:tabId}, time:new Date().getTime()},
                            function(response) {
      chrome.tabs.sendMessage(tabId, {caller:{mi:'AnalyzePage', tab:tabId}, time:new Date().getTime()},
                                function(response) {
        var filename = tab.url.replace(/\//g, '%E2').replace(/:/g, '%3A').replace(/\?/g, '%3F');
        // 1: Download the merging results
        chrome.downloads.download({url:'data:text/html,' + response.msg[0].replace(/\n/g, '<br/>'),
                                   filename:filename+".txt", conflictAction:"overwrite"}, function (downloadId0) {
          // 2: Download the DT xml
          chrome.downloads.download({url:'data:text/html,' + response.msg[1], filename:filename+"-DT.xml",
                                     conflictAction:"overwrite"}, function (downloadId1) {
            // 2: Download the VT xml
            chrome.downloads.download({url:'data:text/html,' + response.msg[2], filename:filename+"-VT.xml",
                                       conflictAction:"overwrite"}, function (downloadId2) {
              // 3: Download the BT xml
              chrome.downloads.download({url:'data:text/html,' + response.msg[3], filename:filename+"-BT.xml",
                                         conflictAction:"overwrite"}, function (downloadId3) {
                /*/ TODO: 4: take screenshot of full pages
                chrome.windows.getCurrent({}, function(window) {
                  chrome.tabs.captureVisibleTab(window.id, {format: 'png'}, function(dataURI) {
                    chrome.tabs.create({url:dataURI, active:false});
                  }); // chrome.tabs.captureVisibleTab(window.id, {format: 'png'}, function(dataURI) { ... });
                }); // chrome.windows.getCurrent({}, function(window) { .. });*/
                chrome.tabs.remove(tabId);
                finished ++;
                if (idx++ < URLS.length)
                  chrome.tabs.create({url:URLS[idx], active:true});
              }); // chrome.downloads.download( ... );  // download the BT xml
            }); // chrome.downloads.download( ... );  // download the VT xml
          }); // chrome.downloads.download( ... );  // download the DT xml
        }); // chrome.downloads.download( ... );  // download the merging results
      }); // chrome.tabs.sendMessage(tabId, {...}, function(response) { ... });
    }); // chrome.tabs.sendMessage(tabId, {...}, function(response) { ... });
  } // if (changeInfo.status == "complete")
}); // chrome.tabs.onUpdated.addListener(function(tabId, changeInfo, tab) { ... });

chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) {
  if (request.msg == "startBatchCrawling") {
    for (idx = 0; idx < GROUP_SIZE && idx < URLS.length; idx++)
      chrome.tabs.create({url:URLS[idx], active:true});
    startBatchCrawling = true;
  } // if (request.msg == "startBatchCrawling")
}); // chrome.runtime.onMessage.addListener(function(request, sender, sendResponse) { ... });
