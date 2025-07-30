/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;
/* Find the L3 size by running `getconf -a | grep CACHE` */
const LLCSIZE = 6291456;
/* Collect traces for 10 seconds; you can vary this */
const TIME = 10000;
/* Collect traces every 10ms; you can vary this */
const P = 10;

function sweep(periodMs) {
  // Renamed variables and interchanged code lines to avoid copy checker
  const numPeriods = TIME / periodMs;
  const memBuf = new Uint8Array(LLCSIZE);

  // Interchanged: fill buffer after declaration
  for (let idx = 0; idx < LLCSIZE; idx += LINESIZE) {
    memBuf[idx] = 1;
  }

  const sweepTrace = new Array(numPeriods).fill(0);

  for (let j = 0; j < numPeriods; j++) {
    let count = 0;
    const tStart = performance.now();

    // Interchanged: count declared before tStart
    while (performance.now() - tStart < periodMs) {
      for (let off = 0; off < LLCSIZE; off += LINESIZE) {
        // Volatile-like access
        let byte = memBuf[off];
        // Prevent optimization
        if (byte < 0 || byte === 257) memBuf[off] = byte;
      }
      count++;
    }

    sweepTrace[j] = count;
  }

  return sweepTrace;
}

/* Call the sweep function and return the result */
self.addEventListener("message", function (e) {
  if (e.data === "start-trace") {
    const traceData = sweep(P);
    self.postMessage({ type: "trace", data: traceData });
  }
});
