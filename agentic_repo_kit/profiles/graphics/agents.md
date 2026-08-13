## Graphics and GPU work

Do not infer the rendering pipeline from UI settings alone. Observe the relevant API/backend, device/queue/swapchain/resource descriptors, formats, resolutions, synchronization, barriers, render/depth targets, shader/pipeline identifiers, and timing paths needed by the question.

Prefer objective validation: frame/resource captures, event sequences, descriptors/state dumps, screenshot or pixel comparisons, and timing distributions. The acceptance oracle must prove the intended checkpoint or graphics state: a changed frame/hash, nonzero pixel delta, or generic GPU activity is not sufficient evidence of a particular screen/resource/state transition unless that change itself is the claim. Use checkpoint-specific regions, descriptors, event/resource identities, or other semantic invariants when full-frame/global thresholds would be misleading.

Keep expensive tracing out of hot paths unless explicitly running a diagnostic mode; avoid per-draw/per-frame filesystem I/O, allocations, global locks, and unbounded logging.
