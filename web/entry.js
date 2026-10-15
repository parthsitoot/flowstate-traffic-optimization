/* A file opened from Finder cannot serve the Python API. Use the hosted app. */
(function (root) {
  const hostedApp = 'https://flowstate-traffic-optimization.vercel.app/';
  const entryRedirect = protocol => protocol === 'file:' ? hostedApp : null;
  const destination = root.location && entryRedirect(root.location.protocol);
  if (destination) root.location.replace(destination);
})(globalThis);
