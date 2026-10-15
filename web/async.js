/* Keep one camera request in flight and display only the latest requested frame.
 * Repeated visible queues reuse a bounded cache, reducing hosted API requests.
 */
(function (root) {
  class LatestFrameLoader {
    constructor(load, display, onError, capacity = 64) {
      this.load = load;
      this.display = display;
      this.onError = onError;
      this.capacity = capacity;
      this.cache = new Map();
      this.currentKey = null;
      this.pending = null;
      this.active = null;
    }

    request(key) {
      this.currentKey = key;
      this.pending = key;
      if (!this.active) {
        this.active = this.drain().finally(() => { this.active = null; });
      }
      return this.active;
    }

    async drain() {
      while (this.pending !== null) {
        const key = this.pending;
        this.pending = null;
        try {
          let value = this.cache.get(key);
          if (value === undefined) {
            value = await this.load(key);
            this.cache.set(key, value);
            if (this.cache.size > this.capacity) this.cache.delete(this.cache.keys().next().value);
          }
          const isCurrent = () => key === this.currentKey;
          if (isCurrent()) await this.display(value, isCurrent);
        } catch (error) {
          if (key === this.currentKey) this.onError(error);
        }
      }
    }
  }

  function connectionMessage(location = root.location) {
    if (location?.protocol === 'file:') return 'This file needs the online app to run predictions. Open FlowState online using the link below.';
    if (['localhost','127.0.0.1','::1','[::1]'].includes(location?.hostname))
      return 'The local server is unavailable. Keep python3 app.py running, then try again. You can also open the online app.';
    return 'The connection was interrupted. Check your internet connection and try again.';
  }

  async function requestJSON(url, {fetcher = root.fetch.bind(root), timeoutMs = 65000, retries = 1} = {}) {
    if (root.location?.protocol === 'file:') throw Error(connectionMessage());
    for (let attempt = 0; attempt <= retries; attempt++) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), timeoutMs);
      try {
        const response = await fetcher(url, {signal: controller.signal, cache: 'no-store'});
        let body;
        try { body = await response.json(); }
        catch { throw Object.assign(Error('The server returned an unexpected response. Please retry.'), {retryable: true}); }
        if (!response.ok) throw Object.assign(Error(body.error || `Server error (${response.status}). Please retry.`), {retryable: response.status >= 500});
        return body;
      } catch (error) {
        const network = error instanceof TypeError || error.name === 'AbortError';
        if (attempt < retries && (network || error.retryable)) continue;
        if (error.name === 'AbortError') throw Error('The server took too long. Please retry.');
        if (network) throw Error(connectionMessage());
        throw error;
      } finally { clearTimeout(timeout); }
    }
  }

  root.FlowStateAsync = { LatestFrameLoader, requestJSON };
  if (typeof module !== 'undefined' && module.exports) module.exports = { LatestFrameLoader, requestJSON, connectionMessage };
})(globalThis);
