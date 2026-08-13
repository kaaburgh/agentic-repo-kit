## Graphics and GPU work

Do not infer the rendering pipeline from UI settings alone. Observe the relevant API/backend, device/queue/swapchain/resource descriptors, formats, resolutions, synchronization, barriers, render/depth targets, shader/pipeline identifiers, and timing paths needed by the question.

Prefer objective validation: frame/resource captures, event sequences, descriptors/state dumps, screenshot or pixel comparisons, and timing distributions. Keep expensive tracing out of hot paths unless explicitly running a diagnostic mode; avoid per-draw/per-frame filesystem I/O, allocations, global locks, and unbounded logging.
