// Service worker for the home-screen web app.
// Pages always come from the network (the data changes daily) and the browser's
// normal cache handles static files. With no connection, a short message is shown
// instead of the browser's error page.

const OFFLINE_PAGE = `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Offline</title>
</head>
<body style="margin:0;height:100vh;display:flex;align-items:center;justify-content:center;background:#1f2d35;color:#fff;font-family:verdana,sans-serif;text-align:center">
  <div>
    <h3>You're offline</h3>
    <p style="color:rgb(179,197,210)">Reconnect to see the latest grades.</p>
  </div>
</body>
</html>`;

self.addEventListener("install", () => self.skipWaiting());

self.addEventListener("activate", (event) => event.waitUntil(self.clients.claim()));

self.addEventListener("fetch", (event) => {
  if (event.request.mode !== "navigate") {
    return; // everything except page loads goes straight to the network
  }
  event.respondWith(
    fetch(event.request).catch(
      () => new Response(OFFLINE_PAGE, { headers: { "Content-Type": "text/html; charset=utf-8" } })
    )
  );
});
