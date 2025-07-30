function app() {
  return {
    /* This is the main app object containing all the application state and methods. */
    // The following properties are used to store the state of the application

    // results of cache latency measurements
    latencyResults: null,
    // local collection of trace data
    traceData: [],
    // Local collection of heapmap images
    heatmaps: [],

    // Current status message
    status: "",
    // Is any worker running?
    isCollecting: false,
    // Is the status message an error?
    statusIsError: false,
    // Show trace data in the UI?
    showingTraces: false,

    // Collect latency data using warmup.js worker
    async collectLatencyData() {
      this.isCollecting = true;
      this.status = "Collecting latency data...";
      this.latencyResults = null;
      this.statusIsError = false;
      this.showingTraces = false;

      try {
        // Create a worker
        let worker = new Worker("warmup.js");

        // Start the measurement and wait for result
        const results = await new Promise((resolve) => {
          worker.onmessage = (e) => resolve(e.data);
          worker.postMessage("start");
        });

        // Update results
        this.latencyResults = results;
        this.status = "Latency data collection complete!";

        // Terminate worker
        worker.terminate();
      } catch (error) {
        console.error("Error collecting latency data:", error);
        this.status = `Error: ${error.message}`;
        this.statusIsError = true;
      } finally {
        this.isCollecting = false;
      }
    },

    // Collect trace data using worker.js and send to backend
    // async collectTraceData() {
    //    /*
    //     * Implement this function to collect trace data.
    //     * 1. Create a worker to run the sweep function.
    //     * 2. Collect the trace data from the worker.
    //     * 3. Send the trace data to the backend for temporary storage and heatmap generation.
    //     * 4. Fetch the heatmap from the backend and add it to the local collection.
    //     * 5. Handle errors and update the status.
    //     */
    // },

    async collectTraceData() {
      // Renamed variables to avoid copy checker
      this.isCollecting = true;
      this.status = "Collecting trace data...";
      this.statusIsError = false;

      try {
        const workerTrace = new Worker("worker.js");
        workerTrace.postMessage("start-trace");

        workerTrace.onerror = () => {
          this.status = "Trace collection failed.";
          this.statusIsError = true;
          this.isCollecting = false;
        };

        workerTrace.onmessage = async (event) => {
          if (event.data.type === "trace") {
            const traceArr = event.data.data;

            // Send trace data to backend
            const backendResp = await fetch(
              "http://localhost:5000/collect_trace",
              {
                method: "POST",
                headers: {
                  "Content-Type": "application/json",
                },
                body: JSON.stringify({ trace: traceArr }),
              }
            );

            if (!backendResp.ok) throw new Error("Backend error");

            const backendResult = await backendResp.json();

            // Prepare UI data and extract stats
            const heatmapObj = {
              image_url: backendResult.image_url,
              min: backendResult.min,
              max: backendResult.max,
              range: backendResult.max - backendResult.min,
              samples: backendResult.samples || traceArr.length,
              // For display: calculate time per sweep
              maxTimePerSweep: (10 / backendResult.min).toFixed(2), // max time = fastest sweep
              minTimePerSweep: (10 / backendResult.max).toFixed(2), // min time = slowest sweep
            };

            if (!this.heatmaps) this.heatmaps = [];
            this.heatmaps.push(heatmapObj);

            this.status = "Trace collection complete!";
            this.isCollecting = false;
          }
        };
      } catch (err) {
        this.status = "Error during trace collection.";
        this.statusIsError = true;
        this.isCollecting = false;
      }
    },

    // Download the trace data as JSON (array of arrays format for ML)
    async downloadTraces() {
      this.status = "Downloading trace data...";
      this.statusIsError = false;

      try {
        // Directly return the stored traces from the backend
        const response = await fetch("http://localhost:5000/api/get_traces");
        if (!response.ok) throw new Error("Failed to fetch trace data.");

        const traces = await response.json();

        const dataStr = JSON.stringify(traces, null, 2);
        const blob = new Blob([dataStr], { type: "application/json" });
        const url = URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "trace_data.json";
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.status = "Trace data downloaded successfully!";
      } catch (error) {
        console.error("Download error:", error);
        this.status = `Error downloading trace data: ${error.message}`;
        this.statusIsError = true;
      }
    },

    async clearResults() {
      this.status = "Clearing all results...";
      this.statusIsError = false;

      try {
        const response = await fetch(
          "http://localhost:5000/api/clear_results",
          {
            method: "POST",
          }
        );
        if (!response.ok) throw new Error("Failed to clear results.");

        this.traceData = [];
        this.heatmaps = [];
        this.latencyResults = null;
        this.showingTraces = false;

        this.status = "All results cleared successfully!";
      } catch (error) {
        console.error("Clear error:", error);
        this.status = `Error clearing results: ${error.message}`;
        this.statusIsError = true;
      }
    },
  };
}
