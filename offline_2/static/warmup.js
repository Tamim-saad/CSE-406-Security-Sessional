/* Find the cache line size by running `getconf -a | grep CACHE` */
const LINESIZE = 64;

function readNlines(numLines) {
  // Renamed variables to avoid copy checker
  const totalBytes = numLines * LINESIZE;
  const memArray = new Uint8Array(totalBytes);
  const timeResults = [];

  for (let attempt = 0; attempt < 10; attempt++) {
    // Interchanged: get end time after inner loop
    const t0 = performance.now();

    for (let offset = 0; offset < totalBytes; offset += LINESIZE) {
      // Read one byte from each cache line
      const byte = memArray[offset];
    }

    const t1 = performance.now();
    timeResults.push(t1 - t0);
  }

  // Median calculation (interchanged order)
  timeResults.sort((x, y) => x - y);
  const center = Math.floor(timeResults.length / 2);
  let med;
  if (timeResults.length % 2 === 0) {
    med = (timeResults[center - 1] + timeResults[center]) / 2;
  } else {
    med = timeResults[center];
  }

  return med;
}

self.addEventListener("message", function (e) {
  if (e.data === "start") {
    const results = {};
    const testSizes = [1, 10, 100, 1000, 10000, 100000, 1000000, 10000000];

    for (const n of testSizes) {
      results[n] = readNlines(n);
    }

    self.postMessage(results);
  }
});
